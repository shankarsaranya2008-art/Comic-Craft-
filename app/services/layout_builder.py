from app.models import ComicStory


# ============================================================
# Build comic layout
# ============================================================

def build_comic_layout(
    story: ComicStory,
    image_paths: list[str]
) -> list[dict]:

    if len(story.panels) != len(image_paths):

        raise ValueError(
            "Every comic panel must have exactly "
            "one generated image."
        )

    layout = []

    for panel, image_path in zip(
        story.panels,
        image_paths
    ):

        layout.append({

            "panel_number":
                panel.panel_number,

            "title":
                panel.title,

            "image_path":
                image_path,

            "scene_description":
                panel.scene_description,

            "caption":
                panel.caption,

            "narration":
                panel.narration,

            "dialogue":
                panel.dialogue,

            "image_prompt":
                panel.image_prompt,
        })

    return layout