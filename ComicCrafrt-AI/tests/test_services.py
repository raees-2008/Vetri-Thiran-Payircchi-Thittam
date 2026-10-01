from app.models import PromptRequest

from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.layout_builder import build_comic_layout


def sample_request():
    return PromptRequest(
        story_prompt=(
            "A brave fox explores an enchanted forest."
        ),
        character_name="Luna",
        setting="Enchanted Forest",
        tone="Adventurous",
        art_style="Comic Book",
    )


def test_generate_outline():
    request = sample_request()

    outline = generate_outline(request)

    assert len(outline) == 5

    assert outline[0].panel_number == 1

    assert outline[-1].panel_number == 5


def test_generate_story():
    request = sample_request()

    outline = generate_outline(request)

    story = generate_story(
        request,
        outline,
    )

    assert len(story) == 5

    assert story[0].title

    assert story[0].narration

    assert story[0].dialogue


def test_layout_builder():
    data = [
        {
            "panel_number": 1,
            "title": "Opening",
            "scene_description": "A forest.",
            "image_prompt": "A fox in a forest.",
            "caption": "Morning.",
            "narration": "The adventure begins.",
            "dialogue": "Luna: Hello!",
            "image_path": (
                "static/panels/panel_1.png"
            ),
        }
    ]

    layout = build_comic_layout(data)

    assert len(layout) == 1

    assert (
        layout[0]["image_url"]
        == "/static/panels/panel_1.png"
    )