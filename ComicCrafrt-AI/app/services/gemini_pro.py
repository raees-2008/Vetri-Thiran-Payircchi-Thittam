import json
from typing import List

from app.config import settings
from app.models import (
    PanelOutline,
    PanelStory,
    PromptRequest,
)


def _fallback_story(
    request: PromptRequest,
    outline: List[PanelOutline],
) -> List[PanelStory]:

    results = []

    for panel in outline:

        results.append(
            PanelStory(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                image_prompt=panel.image_prompt,
                caption=(
                    f"{request.setting} — "
                    f"the adventure continues."
                ),
                narration=(
                    f"{request.character_name} moves forward with "
                    f"determination, facing whatever comes next."
                ),
                dialogue=(
                    f"{request.character_name}: "
                    f"\"I won't give up now!\""
                ),
            )
        )

    return results


def generate_story(
    request: PromptRequest,
    outline: List[PanelOutline],
) -> List[PanelStory]:

    if not settings.gemini_api_key:
        return _fallback_story(
            request,
            outline,
        )

    try:
        from google import genai

        client = genai.Client(
            api_key=settings.gemini_api_key,
        )

        outline_json = json.dumps(
            [
                panel.model_dump()
                for panel in outline
            ],
            indent=2,
        )

        prompt = f"""
You are a professional comic-book writer.

Turn the following five-panel outline into a complete comic story.

User information:

Story:
{request.story_prompt}

Character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Outline:
{outline_json}

For every panel produce:

- panel number
- title
- scene description
- image prompt
- caption
- narration
- dialogue

Writing requirements:

1. Preserve continuity.
2. Keep the character consistent.
3. Make the dialogue natural.
4. Make narration concise enough for a comic page.
5. Make image prompts visually descriptive.
6. Respect the requested tone.
7. Return exactly five panels.
8. Do not use markdown.
"""

        response = client.models.generate_content(
            model=settings.gemini_story_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[PanelStory],
            },
        )

        if response.parsed:
            return response.parsed

        parsed = json.loads(response.text)

        return [
            PanelStory.model_validate(item)
            for item in parsed
        ]

    except Exception as exc:
        print(
            "Gemini story generation failed. "
            f"Using fallback story. Error: {exc}"
        )

        return _fallback_story(
            request,
            outline,
        )
    