from typing import List

from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Main idea for the comic",
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style",
    )
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class PanelStory(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    dialogue: str


class ComicRequest(BaseModel):
    request: PromptRequest


class ComicResponse(BaseModel):
    success: bool
    comic_id: str
    panels: List[PanelStory]
    pdf_url: str
    