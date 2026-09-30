from google.genai import types

from app.config import settings
from app.models import (
    ComicOutline,
    ComicStory,
    PromptRequest,
)
from app.services.mock_ai import generate_story as mock_generate_story

from app.services.gemini_flash import (
    get_gemini_client,
)


# ============================================================
# Generate detailed comic story
# ============================================================

def generate_story(
    request: PromptRequest,
    outline: ComicOutline
) -> ComicStory:
    if settings.ai_provider == "mock":
        return mock_generate_story(request, outline)

    outline_json = outline.model_dump_json(
        indent=2
    )

    prompt = f"""
You are an expert comic book writer.

Expand the following five-panel outline into
a polished comic story.

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

OUTLINE:
{outline_json}

REQUIREMENTS:

1. Return exactly 5 panels.
2. Preserve panel order.
3. Keep the same character throughout.
4. Maintain visual continuity.
5. caption:
   - short
   - atmospheric
   - maximum approximately 18 words

6. narration:
   - concise
   - cinematic
   - maximum approximately 55 words

7. dialogue:
   - natural
   - character appropriate
   - may be empty if unnecessary

8. image_prompt:
   - detailed
   - visually descriptive
   - suitable for Stable Diffusion
   - describe character appearance
   - describe action
   - describe environment
   - describe lighting
   - describe composition
   - describe art style

9. Do NOT include:
   - readable text
   - letters
   - captions
   - speech bubbles
   - logos
   - watermarks

The result must feel like a finished comic story,
not a planning document.

Return ONLY the structured data matching the schema.
"""

    client = get_gemini_client()

    response = client.models.generate_content(

        model=settings.gemini_pro_model,

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=ComicStory,

            temperature=0.95,

            max_output_tokens=7000,
        ),
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty comic story."
        )

    try:

        return ComicStory.model_validate_json(
            response.text
        )

    except Exception as exc:

        raise RuntimeError(
            f"Failed to parse Gemini story: {exc}"
        ) from exc