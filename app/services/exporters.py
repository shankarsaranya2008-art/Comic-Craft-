"""
ComicCraft - PDF Exporter

Creates a readable A4 PDF containing the generated comic panels.
"""

from __future__ import annotations

import os
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF

from app.config import settings


# ============================================================
# Font discovery
# ============================================================

def _find_font() -> str | None:
    """
    Find a Unicode-capable font available on the current system.
    """

    candidates = [
        # ----------------------------------------------------
        # Windows
        # ----------------------------------------------------
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/Arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/Calibri.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),

        # ----------------------------------------------------
        # Linux
        # ----------------------------------------------------
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),

        # ----------------------------------------------------
        # macOS
        # ----------------------------------------------------
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    return None


# ============================================================
# Safe text handling
# ============================================================

def _text(value: Any) -> str:
    """
    Convert any value into safe printable text.

    Also normalizes unusual whitespace so PDF rendering is more
    predictable.
    """

    if value is None:
        return ""

    value = str(value)

    # Normalize line endings.
    value = value.replace("\r\n", "\n").replace("\r", "\n")

    # Remove problematic control characters while preserving
    # newline and tab.
    value = "".join(
        char
        for char in value
        if char in ("\n", "\t") or ord(char) >= 32
    )

    return value.strip()


def _wrap_text(value: Any, width: int = 80) -> str:
    """
    Wrap text before sending it to fpdf2.

    This is intentionally defensive. It prevents extremely long
    unbroken Gemini-generated strings from causing:

        Not enough horizontal space to render a single character
    """

    value = _text(value)

    if not value:
        return ""

    paragraphs = value.split("\n")
    wrapped_paragraphs: list[str] = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            wrapped_paragraphs.append("")
            continue

        # textwrap breaks long words as well.
        lines = textwrap.wrap(
            paragraph,
            width=width,
            break_long_words=True,
            break_on_hyphens=False,
            replace_whitespace=True,
            drop_whitespace=True,
        )

        if lines:
            wrapped_paragraphs.extend(lines)
        else:
            wrapped_paragraphs.append("")

    return "\n".join(wrapped_paragraphs)


def _clean_filename(value: str) -> str:
    """
    Make a safe filename.
    """

    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value)
    value = value.strip("_")

    return value or "comic"


# ============================================================
# PDF helper functions
# ============================================================

def _set_body_font(pdf: FPDF, font_path: str | None, size: float = 11) -> None:
    """
    Set the normal body font.
    """

    if font_path:
        pdf.set_font("ComicFont", "", size)
    else:
        pdf.set_font("Helvetica", "", size)


def _set_bold_font(
    pdf: FPDF,
    font_path: str | None,
    size: float = 11,
) -> None:
    """
    Set the bold font.
    """

    if font_path:
        pdf.set_font("ComicFont", "B", size)
    else:
        pdf.set_font("Helvetica", "B", size)


def _write_block(
    pdf: FPDF,
    value: Any,
    font_path: str | None,
    *,
    font_size: float = 11,
    line_height: float = 6,
    bold: bool = False,
) -> None:
    """
    Write a text block using an explicit safe width.

    Explicitly setting the width is important because width=0 can
    sometimes produce horizontal-space errors when the cursor is
    near the page boundary.
    """

    value = _wrap_text(value)

    if not value:
        return

    if bold:
        _set_bold_font(pdf, font_path, font_size)
    else:
        _set_body_font(pdf, font_path, font_size)

    # A4 width = 210 mm.
    # 15 mm left + 15 mm right margin = 180 mm usable width.
    text_width = 180

    pdf.set_x(15)

    pdf.multi_cell(
        text_width,
        line_height,
        value,
        border=0,
        align="L",
    )

    pdf.ln(2)


# ============================================================
# Save PDF
# ============================================================

def save_pdf(
    layout: list[dict],
    title: str = "ComicCraft Comic",
) -> str:
    """
    Save the generated comic as a PDF.

    Parameters
    ----------
    layout:
        List of panel dictionaries produced by build_comic_layout().

    title:
        PDF title.

    Returns
    -------
    str
        Absolute path to the generated PDF.
    """

    # --------------------------------------------------------
    # Make sure export directory exists.
    # --------------------------------------------------------

    export_dir = Path(settings.exports_dir)

    export_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Generate unique filename.
    # --------------------------------------------------------

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_title = _clean_filename(title)

    output = export_dir / f"{safe_title}_{timestamp}.pdf"

    # --------------------------------------------------------
    # Create PDF.
    # --------------------------------------------------------

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    # --------------------------------------------------------
    # Add Unicode font if available.
    # --------------------------------------------------------

    font_path = _find_font()

    if font_path:
        try:
            pdf.add_font(
                "ComicFont",
                "",
                font_path,
            )

            pdf.add_font(
                "ComicFont",
                "B",
                font_path,
            )
        except Exception as exc:
            print(
                "[ComicCraft] Could not load Unicode font: "
                f"{exc}"
            )
            font_path = None

    # --------------------------------------------------------
    # One page per comic panel.
    # --------------------------------------------------------

    for panel in layout:

        pdf.add_page()

        # ----------------------------------------------------
        # Panel title
        # ----------------------------------------------------

        panel_number = _text(
            panel.get("panel_number", "")
        )

        panel_title = _text(
            panel.get("title", "")
        )

        _set_bold_font(
            pdf,
            font_path,
            18,
        )

        title_text = f"Panel {panel_number}: {panel_title}"

        # Explicit width prevents horizontal-space errors.
        pdf.set_x(15)

        pdf.multi_cell(
            180,
            9,
            _wrap_text(title_text, 70),
            border=0,
            align="L",
        )

        pdf.ln(3)

        # ----------------------------------------------------
        # Image
        # ----------------------------------------------------

        image_path = _text(
            panel.get("image_path", "")
        )

        if image_path and os.path.exists(image_path):

            try:
                pdf.image(
                    image_path,
                    x=15,
                    y=32,
                    w=180,
                    h=120,
                    keep_aspect_ratio=True,
                )

            except Exception as exc:

                print(
                    "[ComicCraft] Could not add image "
                    f"'{image_path}': {exc}"
                )

                # Draw an image placeholder.
                pdf.set_xy(15, 32)
                pdf.rect(
                    15,
                    32,
                    180,
                    120,
                )

                _set_body_font(
                    pdf,
                    font_path,
                    11,
                )

                pdf.set_xy(20, 88)

                pdf.multi_cell(
                    170,
                    7,
                    "Comic panel image could not be loaded.",
                    align="C",
                )

        else:

            # ------------------------------------------------
            # Image missing placeholder
            # ------------------------------------------------

            pdf.set_xy(15, 32)

            pdf.rect(
                15,
                32,
                180,
                120,
            )

            _set_body_font(
                pdf,
                font_path,
                11,
            )

            pdf.set_xy(20, 88)

            pdf.multi_cell(
                170,
                7,
                "Comic panel image is unavailable.",
                align="C",
            )

        # ----------------------------------------------------
        # Scene description
        # ----------------------------------------------------

        pdf.set_y(158)

        _set_bold_font(
            pdf,
            font_path,
            11,
        )

        _write_block(
            pdf,
            "Scene:",
            font_path,
            font_size=11,
            line_height=6,
            bold=True,
        )

        _write_block(
            pdf,
            panel.get("scene_description", ""),
            font_path,
            font_size=11,
            line_height=6,
        )

        # ----------------------------------------------------
        # Caption
        # ----------------------------------------------------

        caption = _text(
            panel.get("caption", "")
        )

        if caption:

            _write_block(
                pdf,
                "Caption:",
                font_path,
                font_size=11,
                line_height=6,
                bold=True,
            )

            _write_block(
                pdf,
                caption,
                font_path,
                font_size=11,
                line_height=6,
            )

        # ----------------------------------------------------
        # Narration
        # ----------------------------------------------------

        narration = _text(
            panel.get("narration", "")
        )

        if narration:

            _write_block(
                pdf,
                "Narration:",
                font_path,
                font_size=11,
                line_height=6,
                bold=True,
            )

            _write_block(
                pdf,
                narration,
                font_path,
                font_size=11,
                line_height=6,
            )

        # ----------------------------------------------------
        # Dialogue
        # ----------------------------------------------------

        dialogue = _text(
            panel.get("dialogue", "")
        )

        if dialogue:

            _write_block(
                pdf,
                "Dialogue:",
                font_path,
                font_size=11,
                line_height=6,
                bold=True,
            )

            _write_block(
                pdf,
                dialogue,
                font_path,
                font_size=11,
                line_height=6,
            )

    # --------------------------------------------------------
    # Write PDF.
    # --------------------------------------------------------

    pdf.output(str(output))

    print(
        f"[ComicCraft] PDF created successfully: {output}"
    )

    return str(output)