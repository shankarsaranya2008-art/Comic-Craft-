from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
)

from fastapi.templating import (
    Jinja2Templates,
)

from app.config import settings
from app.models import PromptRequest

from app.services.exporters import (
    save_pdf,
)

from app.services.gemini_flash import (
    generate_outline,
)

from app.services.gemini_pro import (
    generate_story,
)

from app.services.image_generator import (
    generate_image,
)

from app.services.layout_builder import (
    build_comic_layout,
)


# ============================================================
# Router
# ============================================================

router = APIRouter()


# ============================================================
# Templates
# ============================================================

templates = Jinja2Templates(
    directory=str(
        settings.templates_dir
    )
)


# ============================================================
# Complete comic generation pipeline
# ============================================================

def _generate(
    request_data: PromptRequest
):

    # --------------------------------------------------------
    # Step 1: Outline
    # --------------------------------------------------------

    outline = generate_outline(
        request_data
    )

    # --------------------------------------------------------
    # Step 2: Story
    # --------------------------------------------------------

    story = generate_story(
        request_data,
        outline
    )

    # --------------------------------------------------------
    # Step 3: Images
    # --------------------------------------------------------

    image_paths = []

    for panel in story.panels:

        image_path = generate_image(

            panel.image_prompt,

            panel.panel_number
        )

        image_paths.append(
            image_path
        )

    # --------------------------------------------------------
    # Step 4: Layout
    # --------------------------------------------------------

    layout = build_comic_layout(
        story,
        image_paths
    )

    # --------------------------------------------------------
    # Step 5: PDF
    # --------------------------------------------------------

    pdf_path = save_pdf(
        layout
    )

    return layout, pdf_path


# ============================================================
# Homepage
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={
            "title": settings.app_name
        }
    )


# ============================================================
# HTML comic generation
# ============================================================

@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(

    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        data = PromptRequest(

            story_prompt=story_prompt,

            character_name=character_name,

            setting=setting,

            tone=tone,

            art_style=art_style,
        )

        layout, pdf_path = _generate(
            data
        )

        browser_layout = []

        for panel in layout:

            relative_path = Path(
                panel["image_path"]
            ).relative_to(
                settings.static_dir
            )

            image_url = (
                "/static/"
                + str(relative_path)
                .replace("\\", "/")
            )

            browser_layout.append({

                **panel,

                "image_url":
                    image_url
            })

        pdf_name = Path(
            pdf_path
        ).name

        return templates.TemplateResponse(

            request=request,

            name="comic_preview.html",

            context={

                "title":
                    settings.app_name,

                "layout":
                    browser_layout,

                "pdf_name":
                    pdf_name,

                "input":
                    data.model_dump(),
            }
        )

    except Exception as exc:

        return templates.TemplateResponse(

            request=request,

            name="error.html",

            context={

                "title":
                    "Generation Error",

                "error":
                    str(exc)
            },

            status_code=500
        )


# ============================================================
# JSON API
# ============================================================

@router.post(
    "/generate-comic/json"
)
async def generate_json(
    data: PromptRequest
):

    try:

        layout, pdf_path = _generate(
            data
        )

        browser_layout = []

        for panel in layout:

            relative_path = Path(
                panel["image_path"]
            ).relative_to(
                settings.static_dir
            )

            image_url = (
                "/static/"
                + str(relative_path)
                .replace("\\", "/")
            )

            browser_layout.append({

                **panel,

                "image_url":
                    image_url
            })

        pdf_name = Path(
            pdf_path
        ).name

        return {

            "success": True,

            "layout":
                browser_layout,

            "pdf":
                f"/download/{pdf_name}",

            "export_success":
                (
                    "/export-success"
                    f"?filename={pdf_name}"
                ),
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc)
        )


# ============================================================
# Download PDF
# ============================================================

@router.get(
    "/download/{filename}"
)
async def download_pdf(
    filename: str
):

    # Prevent path traversal
    safe_name = Path(
        filename
    ).name

    file_path = (
        settings.exports_dir /
        safe_name
    )

    if not file_path.exists():

        raise HTTPException(

            status_code=404,

            detail="PDF not found."
        )

    return FileResponse(

        path=file_path,

        media_type="application/pdf",

        filename=safe_name
    )


# ============================================================
# Export success
# ============================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(

    request: Request,

    filename: str | None = None
):

    return templates.TemplateResponse(

        request=request,

        name="export_success.html",

        context={

            "title":
                "Export Complete",

            "filename":
                filename
        }
    )


# ============================================================
# Test image endpoint
# ============================================================

@router.post(
    "/test-image"
)
async def test_image(

    prompt: str = Form(...)
):

    try:

        path = generate_image(

            prompt,

            0
        )

        relative_path = Path(
            path
        ).relative_to(
            settings.static_dir
        )

        image_url = (
            "/static/"
            + str(relative_path)
            .replace("\\", "/")
        )

        return {

            "success": True,

            "image_url":
                image_url
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc)
        )