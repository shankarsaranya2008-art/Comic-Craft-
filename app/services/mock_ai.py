"""Local mock AI provider for ComicCraft.

This provider never calls Gemini or any external AI service.
It returns the exact Pydantic models expected by app.models.
"""

from __future__ import annotations

from app.models import (
    ComicOutline,
    ComicStory,
    PanelOutline,
    PanelStory,
)


def generate_outline(request) -> ComicOutline:
    """Generate a deterministic five-panel comic outline."""

    character = request.character_name
    setting = request.setting
    tone = request.tone
    art_style = request.art_style
    story_prompt = request.story_prompt

    scenes = [
        {
            "panel_number": 1,
            "title": "The Beginning",
            "scene_description": (
                f"{character} begins an adventure in {setting}. "
                f"The story starts with: {story_prompt}"
            ),
            "image_prompt": (
                f"{art_style} comic panel. "
                f"Show {character} in {setting}. "
                f"The tone is {tone}. "
                "Establish the main character and the beginning of the adventure."
            ),
        },
        {
            "panel_number": 2,
            "title": "The Problem",
            "scene_description": (
                f"{character} discovers an unexpected problem in {setting}. "
                "Something important has gone wrong."
            ),
            "image_prompt": (
                f"{art_style} comic panel. "
                f"Show {character} facing an unexpected problem in {setting}. "
                f"Keep the character's appearance consistent. "
                f"The tone is {tone}."
            ),
        },
        {
            "panel_number": 3,
            "title": "Things Get Worse",
            "scene_description": (
                f"The problem becomes more difficult for {character}. "
                f"Despite the danger, {character} continues the adventure."
            ),
            "image_prompt": (
                f"{art_style} comic panel. "
                f"Show {character} dealing with a difficult situation in {setting}. "
                "Create visual tension while keeping the character consistent."
            ),
        },
        {
            "panel_number": 4,
            "title": "The Turning Point",
            "scene_description": (
                f"{character} discovers a clever solution and decides to take action. "
                "The situation begins to change."
            ),
            "image_prompt": (
                f"{art_style} comic panel. "
                f"Show {character} discovering a clever solution in {setting}. "
                "Make this feel like the dramatic turning point of the story."
            ),
        },
        {
            "panel_number": 5,
            "title": "The Resolution",
            "scene_description": (
                f"{character} successfully resolves the problem. "
                "The adventure ends on a positive note with the possibility of another adventure."
            ),
            "image_prompt": (
                f"{art_style} comic panel. "
                f"Show {character} after successfully solving the problem in {setting}. "
                "Create a satisfying ending and keep the character visually consistent."
            ),
        },
    ]

    panels = [
        PanelOutline(**scene)
        for scene in scenes
    ]

    return ComicOutline(
        panels=panels
    )


def generate_story(request, outline: ComicOutline) -> ComicStory:
    """Convert the outline into a complete five-panel comic story."""

    character = request.character_name
    setting = request.setting
    tone = request.tone
    art_style = request.art_style

    panels = []

    for panel in outline.panels:

        if panel.panel_number == 1:
            caption = "Every adventure starts somewhere..."
            narration = (
                f"{character} begins an unexpected adventure in {setting}."
            )
            dialogue = (
                f"{character}: Something tells me today will be interesting."
            )

        elif panel.panel_number == 2:
            caption = "But something has gone wrong."
            narration = (
                f"A problem suddenly appears, forcing {character} to react."
            )
            dialogue = (
                f"{character}: Wait... what is happening?"
            )

        elif panel.panel_number == 3:
            caption = "The situation gets worse."
            narration = (
                f"{character} faces the biggest challenge of the adventure."
            )
            dialogue = (
                f"{character}: I have to keep going!"
            )

        elif panel.panel_number == 4:
            caption = "Then, an idea appears."
            narration = (
                f"{character} discovers a clever way to solve the problem."
            )
            dialogue = (
                f"{character}: That's it! I know what to do."
            )

        else:
            caption = "And everything works out."
            narration = (
                f"{character} successfully resolves the adventure."
            )
            dialogue = (
                f"{character}: We did it!"
            )

        image_prompt = (
            f"{art_style} comic book illustration. "
            f"Panel {panel.panel_number}. "
            f"Character: {character}. "
            f"Setting: {setting}. "
            f"Tone: {tone}. "
            f"Scene: {panel.scene_description}. "
            "Maintain consistent character appearance across all panels. "
            "Clean comic composition, expressive characters, detailed background."
        )

        panels.append(
            PanelStory(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                caption=caption,
                narration=narration,
                dialogue=dialogue,
                image_prompt=image_prompt,
            )
        )

    return ComicStory(
        panels=panels
    )