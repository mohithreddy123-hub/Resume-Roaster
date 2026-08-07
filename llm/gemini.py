# pyrefly: ignore
"""
llm/gemini.py
-------------
Gemini API wrapper for Resume Roaster.
Handles: initialization, sending messages, conversation history,
exponential backoff retries on rate limits, and clean error reporting.
No prompt logic lives here — only the API communication layer.
"""

import time
import random
import google.generativeai as genai
from google.api_core.exceptions import (
    ResourceExhausted,
    ServiceUnavailable,
    GoogleAPIError,
)
from dotenv import load_dotenv
import os

from config import GEMINI_MODEL, GEMINI_MAX_RETRIES, GEMINI_RETRY_DELAY_SECONDS

# Load environment variables from .env
load_dotenv(override=True)


class GeminiError(Exception):
    """Raised when Gemini API fails after all retries."""
    pass


class GeminiRateLimitError(GeminiError):
    """Raised specifically when the API is rate-limited after all retries."""
    pass


class GeminiAPIKeyMissingError(GeminiError):
    """Raised when the API key is not configured."""
    pass


def _get_api_key() -> str:
    """
    Retrieve the Gemini API key from environment variables.

    Raises:
        GeminiAPIKeyMissingError: If the key is missing or empty.
    """
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise GeminiAPIKeyMissingError(
            "Gemini API key is missing. "
            "Please add GEMINI_API_KEY to your .env file."
        )
    return key


def _initialize_model(json_mode: bool = False) -> genai.GenerativeModel:
    """
    Initialize and return the Gemini GenerativeModel.

    Args:
        json_mode: If True, configures the model to output strict JSON.

    Raises:
        GeminiAPIKeyMissingError: If the API key is missing.
        GeminiError: If model initialization fails.
    """
    api_key = _get_api_key()
    try:
        genai.configure(api_key=api_key)
        config_args = {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 2048,
        }
        if json_mode:
            config_args["response_mime_type"] = "application/json"

        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config=genai.GenerationConfig(**config_args),
        )
        return model
    except Exception as e:
        raise GeminiError(
            "Failed to initialize the AI model. Please check your API key."
        ) from e


def _exponential_backoff(attempt: int, base: int) -> float:
    """
    Calculate exponential backoff with jitter.

    Wait = base * 2^(attempt-1) + random jitter (0-2 seconds).
    Example with base=10: 10s, 20s, 40s, 80s, 160s...
    Capped at 120 seconds per wait to avoid unreasonably long hangs.
    """
    wait = min(base * (2 ** (attempt - 1)), 120)
    jitter = random.uniform(0, 2)
    return wait + jitter


def send_message(
    system_prompt: str,
    user_message: str,
    conversation_history: list[dict] | None = None,
    json_mode: bool = False,
) -> str:
    """
    Send a message to Gemini and return the response text.
    Retries automatically on rate limits with exponential backoff.

    Args:
        system_prompt:        The AI personality and behavior instructions.
        user_message:         The user's current message/query.
        conversation_history: List of previous {role, content} dicts.
                              Roles must be "user" or "model".
        json_mode:            If True, requests response in JSON format.

    Returns:
        The AI's response text string.

    Raises:
        GeminiAPIKeyMissingError: If the API key is not set.
        GeminiRateLimitError:     If rate limited after all retries.
        GeminiError:              If all retries are exhausted for other reasons.
    """
    model = _initialize_model(json_mode=json_mode)
    history = conversation_history or []

    # Build Gemini-compatible chat history
    gemini_history = []
    for entry in history:
        role = entry.get("role", "user")
        content = entry.get("content", "")
        if role in ("user", "model") and content:
            gemini_history.append({"role": role, "parts": [content]})

    # Start a chat session with history
    chat = model.start_chat(history=gemini_history)

    # Combine system prompt with user message
    full_message = f"{system_prompt}\n\n---\n\n{user_message}"

    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            response = chat.send_message(full_message)
            return response.text

        except ResourceExhausted as e:
            # 429 Rate limit — wait with exponential backoff then retry
            if attempt < GEMINI_MAX_RETRIES:
                wait_seconds = _exponential_backoff(attempt, GEMINI_RETRY_DELAY_SECONDS)
                time.sleep(wait_seconds)
                # Reset chat for next attempt to avoid stale session state
                chat = model.start_chat(history=gemini_history)
            else:
                raise GeminiRateLimitError(
                    "The AI service is rate-limited right now. "
                    "This usually clears in 30–60 seconds. "
                    "Please wait a moment and try again."
                ) from e

        except ServiceUnavailable as e:
            if attempt < GEMINI_MAX_RETRIES:
                wait_seconds = _exponential_backoff(attempt, GEMINI_RETRY_DELAY_SECONDS)
                time.sleep(wait_seconds)
                chat = model.start_chat(history=gemini_history)
            else:
                raise GeminiError(
                    "The AI service is temporarily unavailable. "
                    "Please try again in a moment."
                ) from e

        except GoogleAPIError as e:
            raise GeminiError(
                "An error occurred while communicating with the AI service. "
                "Please try again."
            ) from e

        except Exception as e:
            raise GeminiError(
                "An unexpected error occurred. Please try again."
            ) from e

    raise GeminiError("AI service failed after multiple attempts. Please try again.")


def build_resume_context(resume_text: str, user_query: str) -> str:
    """
    Build a structured user message combining resume content and user query.

    Args:
        resume_text: The cleaned resume text.
        user_query:  The user's specific question or instruction.

    Returns:
        A formatted string ready to be sent as a user message.
    """
    return (
        f"RESUME CONTENT:\n"
        f"{'=' * 40}\n"
        f"{resume_text}\n"
        f"{'=' * 40}\n\n"
        f"USER REQUEST:\n"
        f"{user_query}"
    )
