"""
llm/gemini.py
-------------
Gemini API wrapper for Resume Roaster.
Handles: initialization, sending messages, conversation history,
retries on failure, and clean error reporting.
No prompt logic lives here — only the API communication layer.
"""

import time
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


def send_message(
    system_prompt: str,
    user_message: str,
    conversation_history: list[dict] | None = None,
    json_mode: bool = False,
) -> str:
    """
    Send a message to Gemini and return the response text.

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
        GeminiError:              If all retries are exhausted.
    """
    model = _initialize_model(json_mode=json_mode)
    history = conversation_history or []

    # Build Gemini-compatible chat history
    # Gemini uses "user" and "model" as role names
    gemini_history = []
    for entry in history:
        role = entry.get("role", "user")
        content = entry.get("content", "")
        if role in ("user", "model") and content:
            gemini_history.append({"role": role, "parts": [content]})

    # Start a chat session with history
    chat = model.start_chat(history=gemini_history)

    # Combine system prompt with user message
    # Gemini Flash doesn't have a dedicated system role in basic API,
    # so we prepend the system prompt to the first user message cleanly.
    full_message = f"{system_prompt}\n\n---\n\n{user_message}"

    last_error: Exception | None = None

    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            response = chat.send_message(full_message)
            return response.text

        except ResourceExhausted as e:
            last_error = e
            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(GEMINI_RETRY_DELAY_SECONDS * attempt)
            else:
                raise GeminiError(
                    "Too many requests to the AI service. "
                    "Please wait a moment and try again."
                ) from e

        except ServiceUnavailable as e:
            last_error = e
            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(GEMINI_RETRY_DELAY_SECONDS * attempt)
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
