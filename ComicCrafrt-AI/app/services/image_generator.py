import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import PANELS_DIR, settings


def sanitize_filename(value: str) -> str:
    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value,
    )

    return value.strip("_") or "panel"


def _placeholder_image(
    prompt: str,
    panel_number: int,
) -> Path:

    width = 1024
    height = 768

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (30, 30, width - 30, height - 30),
        outline="black",
        width=8,
    )

    title = f"ComicCraft - Panel {panel_number}"

    draw.text(
        (70, 70),
        title,
        fill="black",
    )

    wrapped = prompt[:400]

    draw.text(
        (70, 150),
        wrapped,
        fill="black",
    )

    filename = (
        f"panel_{panel_number}_placeholder.png"
    )

    path = PANELS_DIR / filename

    image.save(path)

    return path


def _huggingface_image(
    prompt: str,
    panel_number: int,
) -> Path:

    if not settings.hf_token:
        raise RuntimeError(
            "HF_TOKEN is required when IMAGE_PROVIDER=hf."
        )

    from huggingface_hub import InferenceClient

    client = InferenceClient(
        provider="hf-inference",
        api_key=settings.hf_token,
    )

    enhanced_prompt = f"""
Comic book illustration.

{prompt}

Requirements:
- strong visual storytelling
- expressive character
- cinematic composition
- clean line art
- coherent lighting
- no text
- no speech bubbles
"""

    image = client.text_to_image(
        enhanced_prompt,
        model=settings.hf_image_model,
    )

    filename = (
        f"panel_{panel_number}_"
        f"{sanitize_filename(prompt[:40])}.png"
    )

    path = PANELS_DIR / filename

    image.save(path)

    return path


def _local_diffusers_image(
    prompt: str,
    panel_number: int,
) -> Path:

    import torch
    from diffusers import StableDiffusionPipeline

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    dtype = (
        torch.float16
        if device == "cuda"
        else torch.float32
    )

    pipe = StableDiffusionPipeline.from_pretrained(
        settings.local_image_model,
        torch_dtype=dtype,
    )

    pipe = pipe.to(device)

    enhanced_prompt = f"""
comic book illustration,
{prompt},
detailed character,
dynamic composition,
cinematic lighting,
clean line art,
high quality
"""

    result = pipe(
        enhanced_prompt,
        num_inference_steps=20,
    )

    image = result.images[0]

    filename = (
        f"panel_{panel_number}_local.png"
    )

    path = PANELS_DIR / filename

    image.save(path)

    return path


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    provider = settings.image_provider.lower()

    if provider == "placeholder":
        path = _placeholder_image(
            prompt,
            panel_number,
        )

    elif provider == "hf":
        path = _huggingface_image(
            prompt,
            panel_number,
        )

    elif provider == "local_diffusers":
        path = _local_diffusers_image(
            prompt,
            panel_number,
        )

    else:
        raise ValueError(
            "Unknown IMAGE_PROVIDER. "
            "Use placeholder, hf, or local_diffusers."
        )

    return str(path)
