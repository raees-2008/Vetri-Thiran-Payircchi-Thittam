import json
from typing import List

from app.models import PanelOutline, PromptRequest
from app.config import settings


def _fallback_outline(request: PromptRequest) -> List[PanelOutline]:
    """
    Offline fallback.

    This allows the application UI and complete pipeline
    to be tested even without a Gemini API key.
    """

    base = request.story_prompt

    return [
        PanelOutline(
            panel_number=1,
            title="The Beginning",
            scene_description=(
                f"{request.character_name} begins an adventure involving {base} "
                f"in {request.setting}."
            ),
            image_prompt=(
                f"comic book illustration, {request.art_style}, "
                f"{request.character_name} in {request.setting}, "
                f"opening scene, cinematic composition"
            ),
        ),
        PanelOutline(
            panel_number=2,
            title="A Strange Discovery",
            scene_description=(
                f"{request.character_name} discovers something unexpected "
                f"while exploring {request.setting}."
            ),
            image_prompt=(
                f"comic book illustration, {request.art_style}, "
                f"{request.character_name} discovering something mysterious "
                f"in {request.setting}"
            ),
        ),
        PanelOutline(
            panel_number=3,
            title="The Challenge",
            scene_description=(
                f"A difficult challenge appears and {request.character_name} "
                f"must decide what to do next."
            ),
            image_prompt=(
                f"comic book illustration, {request.art_style}, "
                f"{request.character_name} facing a dramatic challenge, "
                f"{request.setting}"
            ),
        ),
        PanelOutline(
            panel_number=4,
            title="The Turning Point",
            scene_description=(
                f"{request.character_name} finds a creative way forward "
                f"and the story reaches its turning point."
            ),
            image_prompt=(
                f"comic book illustration, {request.art_style}, "
                f"{request.character_name} overcoming an obstacle, "
                f"dynamic action, {request.setting}"
            ),
        ),
        PanelOutline(
            panel_number=5,
            title="A New Beginning",
            scene_description=(
                f"The adventure concludes with {request.character_name} "
                f"looking toward a hopeful future."
            ),
            image_prompt=(
                f"comic book illustration, {request.art_style}, "
                f"{request.character_name} at the conclusion of an adventure, "
                f"hopeful cinematic scene, {request.setting}"
            ),
        ),
    ]


def generate_outline(request: PromptRequest) -> List[PanelOutline]:
    """
    Generate a structured five-panel comic outline using Gemini.

    Falls back to a deterministic local outline when no API key
    is configured.
    """

    if not settings.gemini_api_key:
        return _fallback_outline(request)

    try:
        from google import genai

        client = genai.Client(
            api_key=settings.gemini_api_key,
        )

        prompt = f"""
You are the outline writer for an AI comic generator.

Create exactly 5 comic panels.

User story:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

- Exactly five panels.
- Keep the same main character throughout.
- Maintain continuity between panels.
- Make each panel visually distinct.
- Create a short panel title.
- Give a concise scene description.
- Give a detailed image-generation prompt.
- Do not include markdown.
- Do not include explanations outside the JSON.
"""

        response = client.models.generate_content(
            model=settings.gemini_outline_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[PanelOutline],
            },
        )

        data = response.parsed

        if data:
            return data

        raw_text = response.text

        parsed = json.loads(raw_text)

        return [
            PanelOutline.model_validate(item)
            for item in parsed
        ]

    except Exception as exc:
        print(
            "Gemini outline generation failed. "
            f"Using fallback outline. Error: {exc}"
        )

        return _fallback_outline(request)
    