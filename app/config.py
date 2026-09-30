from pathlib import Path
import os

from dotenv import load_dotenv


# ============================================================
# Base directory
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# Settings
# ============================================================

class Settings:
    ai_provider: str = os.getenv("AI_PROVIDER", "gemini").lower()

    app_name: str = os.getenv("APP_NAME", "ComicCraft")

    debug: bool = (
        os.getenv("DEBUG", "true").lower() == "true"
    )

    # --------------------------------------------------------
    # Gemini
    # --------------------------------------------------------

    gemini_api_key: str = os.getenv(
        "GEMINI_API_KEY",
        ""
    )

    gemini_flash_model: str = os.getenv(
        "GEMINI_FLASH_MODEL",
        "gemini-2.5-flash"
    )

    gemini_pro_model: str = os.getenv(
        "GEMINI_PRO_MODEL",
        "gemini-2.5-pro"
    )

    # --------------------------------------------------------
    # Hugging Face / Image generation
    # --------------------------------------------------------

    hf_token: str = os.getenv(
        "HF_TOKEN",
        ""
    )

    image_provider: str = os.getenv(
        "IMAGE_PROVIDER",
        "placeholder"
    ).lower()

    image_model: str = os.getenv(
        "IMAGE_MODEL",
        "stable-diffusion-v1-5/stable-diffusion-v1-5"
    )

    image_device: str = os.getenv(
        "IMAGE_DEVICE",
        "auto"
    ).lower()

    image_steps: int = int(
        os.getenv("IMAGE_STEPS", "25")
    )

    image_width: int = int(
        os.getenv("IMAGE_WIDTH", "512")
    )

    image_height: int = int(
        os.getenv("IMAGE_HEIGHT", "512")
    )

    # --------------------------------------------------------
    # Directories
    # --------------------------------------------------------

    static_dir: Path = BASE_DIR / "static"

    panels_dir: Path = static_dir / "panels"

    exports_dir: Path = static_dir / "exports"

    templates_dir: Path = BASE_DIR / "templates"

    # --------------------------------------------------------
    # Directory initialization
    # --------------------------------------------------------

    def ensure_directories(self) -> None:

        self.static_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.panels_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.exports_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.templates_dir.mkdir(
            parents=True,
            exist_ok=True
        )


settings = Settings()

settings.ensure_directories()