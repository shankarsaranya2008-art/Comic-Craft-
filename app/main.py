from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router


# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(

    title=settings.app_name,

    description=(
        "AI Comic Story Creator using "
        "Gemini and Stable Diffusion."
    ),

    version="1.0.0",
)


# ============================================================
# Static files
# ============================================================

app.mount(

    "/static",

    StaticFiles(
        directory=str(
            settings.static_dir
        )
    ),

    name="static",
)


# ============================================================
# Routes
# ============================================================

app.include_router(
    router
)


# ============================================================
# Health endpoint
# ============================================================

@app.get("/health")
async def health():

    return {

        "status":
            "ok",

        "app":
            settings.app_name,

        "image_provider":
            settings.image_provider,

        "gemini_configured":
            bool(
                settings.gemini_api_key
            ),
    }