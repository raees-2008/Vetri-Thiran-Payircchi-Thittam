from pathlib import Path
from typing import Dict, List


def build_comic_layout(
    panel_data: List[Dict],
) -> List[Dict]:

    layout = []

    for panel in panel_data:

        image_path = Path(
            panel["image_path"]
        )

        layout.append(
            {
                "panel_number": panel["panel_number"],
                "title": panel["title"],
                "scene_description": panel[
                    "scene_description"
                ],
                "image_prompt": panel[
                    "image_prompt"
                ],
                "caption": panel["caption"],
                "narration": panel["narration"],
                "dialogue": panel["dialogue"],
                "image_path": str(image_path),
                "image_url": (
                    "/static/panels/"
                    + image_path.name
                ),
            }
        )

    layout.sort(
        key=lambda item: item["panel_number"]
    )

    return layout
