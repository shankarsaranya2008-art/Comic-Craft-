from pathlib import Path
from uuid import uuid4
import hashlib

from PIL import Image, ImageDraw

from app.config import settings


# ============================================================
# Diffusers pipeline
# ============================================================

_pipeline = None


# ============================================================
# Device detection
# ============================================================

def _device() -> str:

    if settings.image_device != "auto":

        return settings.image_device

    try:

        import torch

        if torch.cuda.is_available():

            return "cuda"

        return "cpu"

    except Exception:

        return "cpu"


# ============================================================
# Load Stable Diffusion
# ============================================================

def _load_pipeline():

    global _pipeline

    if _pipeline is not None:

        return _pipeline

    import torch

    from diffusers import (
        StableDiffusionPipeline,
    )

    device = _device()

    if device == "cuda":

        dtype = torch.float16

    else:

        dtype = torch.float32

    kwargs = {
        "torch_dtype": dtype,
        "use_safetensors": True,
    }

    if settings.hf_token:

        kwargs["token"] = settings.hf_token

    print(
        f"Loading Stable Diffusion model: "
        f"{settings.image_model}"
    )

    print(
        f"Image device: {device}"
    )

    _pipeline = StableDiffusionPipeline.from_pretrained(

        settings.image_model,

        **kwargs,
    )

    _pipeline = _pipeline.to(device)

    if device == "cuda":

        try:

            _pipeline.enable_attention_slicing()

        except Exception:

            pass

    return _pipeline


# ============================================================
# Safe filename
# ============================================================

def _safe_filename(text: str) -> str:

    digest = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()[:12]

    return (
        f"panel_"
        f"{digest}_"
        f"{uuid4().hex[:8]}"
        f".png"
    )


# ============================================================
# Placeholder image
#
# Useful for testing the entire application without
# downloading Stable Diffusion.
# ============================================================

def _placeholder(
    prompt: str,
    panel_number: int,
    path: Path
) -> str:

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height
        ),
        "#f5efe2"
    )

    draw = ImageDraw.Draw(image)

    margin = 18

    draw.rectangle(
        (
            margin,
            margin,
            settings.image_width - margin,
            settings.image_height - margin
        ),
        outline="#202020",
        width=6
    )

    title = (
        f"COMICCRAFT - PANEL "
        f"{panel_number}"
    )

    draw.text(
        (40, 45),
        title,
        fill="#202020"
    )

    # Wrap prompt manually
    lines = []

    words = prompt.split()

    current = ""

    for word in words:

        candidate = (
            current + " " + word
        ).strip()

        if len(candidate) > 50:

            lines.append(current)

            current = word

        else:

            current = candidate

    if current:

        lines.append(current)

    lines = lines[:10]

    y = 120

    for line in lines:

        draw.text(
            (40, y),
            line,
            fill="#333333"
        )

        y += 32

    image.save(
        path,
        "PNG"
    )

    return str(path)


# ============================================================
# Generate image
# ============================================================

def generate_image(
    prompt: str,
    panel_number: int
) -> str:

    filename = _safe_filename(
        f"{panel_number}-{prompt}"
    )

    path = (
        settings.panels_dir /
        filename
    )

    # --------------------------------------------------------
    # Placeholder mode
    # --------------------------------------------------------

    if settings.image_provider == "placeholder":

        return _placeholder(
            prompt,
            panel_number,
            path
        )

    # --------------------------------------------------------
    # Validate provider
    # --------------------------------------------------------

    if settings.image_provider != "diffusers":

        raise RuntimeError(
            "Unsupported IMAGE_PROVIDER. "
            "Use 'diffusers' or 'placeholder'."
        )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    pipe = _load_pipeline()

    # --------------------------------------------------------
    # Negative prompt
    # --------------------------------------------------------

    negative_prompt = """
blurry,
low quality,
low resolution,
distorted face,
deformed face,
extra fingers,
malformed hands,
bad anatomy,
duplicate character,
watermark,
logo,
readable text,
letters,
speech bubble,
caption,
typography
"""

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    result = pipe(

        prompt=prompt,

        negative_prompt=negative_prompt,

        num_inference_steps=settings.image_steps,

        width=settings.image_width,

        height=settings.image_height,
    )

    image = result.images[0]

    image.save(
        path,
        "PNG"
    )

    return str(path)