from pydantic import BaseModel, Field, field_validator


# ============================================================
# User request
# ============================================================

class PromptRequest(BaseModel):

    story_prompt: str = Field(
        ...,
        min_length=5,
        max_length=2000
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=80
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=120
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=80
    )

    @field_validator("*")
    @classmethod
    def strip_text(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value


# ============================================================
# Gemini outline models
# ============================================================

class PanelOutline(BaseModel):

    panel_number: int

    title: str

    scene_description: str

    image_prompt: str


class ComicOutline(BaseModel):

    panels: list[PanelOutline] = Field(
        ...,
        min_length=5,
        max_length=5
    )


# ============================================================
# Gemini story models
# ============================================================

class PanelStory(BaseModel):

    panel_number: int

    title: str

    scene_description: str

    caption: str

    narration: str

    dialogue: str

    image_prompt: str


class ComicStory(BaseModel):

    panels: list[PanelStory] = Field(
        ...,
        min_length=5,
        max_length=5
    )