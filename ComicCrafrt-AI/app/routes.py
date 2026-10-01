import traceback
import uuid

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
)
from fastapi.templating import Jinja2Templates

from app.config import EXPORTS_DIR, settings
from app.models import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


router = APIRouter()

templates = Jinja2Templates(directory="templates")


def create_prompt_request(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> PromptRequest:
    return PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )


def generate_comic(request_data: PromptRequest):
    """
    Complete ComicCraft generation pipeline.

    1. Generate structured outline.
    2. Generate detailed story.
    3. Generate panel images.
    4. Build comic layout.
    5. Export PDF.
    """

    # Step 1: Generate structured outline
    outline = generate_outline(request_data)

    # Step 2: Generate detailed story
    story = generate_story(
        request_data,
        outline,
    )

    # Step 3: Generate panel images
    panel_data = []

    for panel in story:
        image_path = generate_image(
            prompt=panel.image_prompt,
            panel_number=panel.panel_number,
        )

        panel_data.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "scene_description": panel.scene_description,
                "image_prompt": panel.image_prompt,
                "caption": panel.caption,
                "narration": panel.narration,
                "dialogue": panel.dialogue,
                "image_path": image_path,
            }
        )

    # Step 4: Build comic layout
    layout = build_comic_layout(panel_data)

    # Step 5: Create unique comic ID
    comic_id = uuid.uuid4().hex

    # Step 6: Export PDF
    pdf_path = save_pdf(
        layout=layout,
        comic_id=comic_id,
    )

    return {
        "comic_id": comic_id,
        "layout": layout,
        "pdf_path": pdf_path,
    }


# -------------------------------------------------------------------
# HOME PAGE
# -------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
        },
    )


# -------------------------------------------------------------------
# GENERATE COMIC FROM HTML FORM
# -------------------------------------------------------------------

@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        request_data = create_prompt_request(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        result = generate_comic(request_data)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "app_name": settings.app_name,
                "comic_id": result["comic_id"],
                "layout": result["layout"],
                "pdf_url": f"/export/{result['comic_id']}",
            },
        )

    except Exception as exc:
        traceback.print_exc()

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "app_name": settings.app_name,
                "error": str(exc),
            },
            status_code=500,
        )


# -------------------------------------------------------------------
# GENERATE COMIC FROM JSON API
# -------------------------------------------------------------------

@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        result = generate_comic(payload)

        serializable_layout = []

        for panel in result["layout"]:
            serializable_layout.append(
                {
                    "panel_number": panel["panel_number"],
                    "title": panel["title"],
                    "scene_description": panel["scene_description"],
                    "image_prompt": panel["image_prompt"],
                    "caption": panel["caption"],
                    "narration": panel["narration"],
                    "dialogue": panel["dialogue"],
                    "image_url": panel.get(
                        "image_url",
                        panel.get("image_path"),
                    ),
                }
            )

        return JSONResponse(
            content={
                "success": True,
                "comic_id": result["comic_id"],
                "panels": serializable_layout,
                "pdf_url": f"/export/{result['comic_id']}",
            }
        )

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# -------------------------------------------------------------------
# TEST IMAGE GENERATION
# -------------------------------------------------------------------

@router.post("/test-image")
async def test_image(
    prompt: str = Form(...),
):
    try:
        image_path = generate_image(
            prompt=prompt,
            panel_number=999,
        )

        return {
            "success": True,
            "image_path": image_path,
        }

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# -------------------------------------------------------------------
# PDF EXPORT
# -------------------------------------------------------------------

@router.get("/export/{comic_id}")
async def export_comic(comic_id: str):
    """
    Return the generated PDF file.
    """

    pdf_path = EXPORTS_DIR / f"{comic_id}.pdf"

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Comic PDF not found.",
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"comiccraft-{comic_id}.pdf",
    )


# -------------------------------------------------------------------
# EXPORT SUCCESS PAGE
# -------------------------------------------------------------------

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "app_name": settings.app_name,
        },
    )