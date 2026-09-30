"""
ComicCraft - Gemini Flash Service

Generates the structured five-panel comic outline using Gemini.
"""

from __future__ import annotations



import time
from typing import Optional

from google import genai
from google.genai import types

from app.config import settings
from app.models import PromptRequest, ComicOutline
from app.services.mock_ai import generate_outline as mock_generate_outline


_client: Optional[genai.Client] = None


def get_gemini_client() -> genai.Client:
    """
    Create and cache the Gemini client.
    """

    global _client

    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Create a .env file and add your Gemini API key."
            )

        _client = genai.Client(
            api_key=settings.gemini_api_key
        )

    return _client


def get_model_candidates() -> list[str]:
    """
    Return Gemini models in fallback order.
    """

    configured_model = settings.gemini_flash_model

    candidates = [
        configured_model,
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.1-flash-lite",
    ]

    result: list[str] = []

    for model in candidates:
        if model and model not in result:
            result.append(model)

    return result


def _generate_with_retry(
    client: genai.Client,
    prompt: str,
) -> object:
    """
    Try multiple Gemini models with retry handling
    for temporary 503 errors.
    """

    models = get_model_candidates()

    last_error: Optional[Exception] = None

    for model in models:

        for attempt in range(3):

            try:
                print(
                    f"[ComicCraft] Trying Gemini model: "
                    f"{model} | attempt {attempt + 1}/3"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ComicOutline,
                        temperature=0.9,
                        max_output_tokens=4000,
                    ),
                )

                print(
                    f"[ComicCraft] Gemini response received "
                    f"from {model}"
                )

                return response

            except Exception as exc:

                last_error = exc

                error_text = str(exc)

                print(
                    f"[ComicCraft] Gemini error using "
                    f"{model}: {error_text}"
                )

                is_temporary = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text.upper()
                    or "high demand" in error_text.lower()
                    or "temporarily" in error_text.lower()
                )

                if is_temporary and attempt < 2:

                    wait_seconds = 2 ** attempt

                    print(
                        f"[ComicCraft] Temporary Gemini error. "
                        f"Waiting {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)

                    continue

                break

    raise RuntimeError(
        "All configured Gemini models failed. "
        f"Last error: {last_error}"
    )


def generate_outline(
    request: PromptRequest,
) -> ComicOutline:
    if settings.ai_provider == "mock":
        return mock_generate_outline(request)

    """
    Generate a five-panel comic outline.
    """

    prompt = f"""
You are an expert comic book story planner.

Create a coherent five-panel comic outline.

USER STORY IDEA:
{request.story_prompt}

MAIN CHARACTER:
{request.character_name}

SETTING:
{request.setting}

TONE:
{request.tone}

ART STYLE:
{request.art_style}

IMPORTANT REQUIREMENTS:

1. Create exactly 5 panels.

2. Keep the same protagonist throughout all five panels.

3. Maintain visual continuity between panels.

4. Give every panel a clear story purpose.

5. The story should contain:
   - beginning
   - development
   - conflict or turning point
   - resolution

6. scene_description must describe:
   - visible action
   - environment
   - mood

7. image_prompt must contain enough visual information
   for an image-generation model.

8. Do not request text inside generated images.

9. Do not request speech bubbles inside generated images.

10. Do not request logos or watermarks.

11. Make the story engaging and visually expressive.

12. Keep the character's appearance consistent
    throughout all five panels.

13. Make every panel visually distinct.

14. Return exactly five panels.

Return ONLY structured data matching the requested schema.
"""

    client = get_gemini_client()

    response = _generate_with_retry(
        client=client,
        prompt=prompt,
    )

    parsed = getattr(
        response,
        "parsed",
        None,
    )

    if parsed is not None:

        try:

            if isinstance(parsed, ComicOutline):
                return parsed

            return ComicOutline.model_validate(parsed)

        except Exception as exc:

            raise RuntimeError(
                "Gemini returned structured data, "
                "but it could not be validated as ComicOutline: "
                f"{exc}"
            ) from exc

    response_text = getattr(
        response,
        "text",
        None,
    )

    if not response_text:

        raise RuntimeError(
            "Gemini returned an empty comic outline."
        )

    try:

        return ComicOutline.model_validate_json(
            response_text
        )

    except Exception as exc:

        print(
            "[ComicCraft] Raw Gemini response:"
        )

        print(response_text)

        raise RuntimeError(
            f"Failed to parse Gemini outline: {exc}"
        ) from exc