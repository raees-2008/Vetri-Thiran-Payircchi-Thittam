from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    app_name: str = "ComicCraft"
    debug: bool = True

    gemini_api_key: str = ""

    gemini_outline_model: str = "gemini-2.5-flash"
    gemini_story_model: str = "gemini-2.5-pro"

    hf_token: str = ""

    image_provider: str = "placeholder"

    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"

    local_image_model: str = "runwayml/stable-diffusion-v1-5"

    panel_count: int = 5

    max_prompt_length: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"

PANELS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
