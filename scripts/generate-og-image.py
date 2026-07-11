#!/usr/bin/env python3
"""Generate public/og.png (1200x630) for Open Graph embeds."""

from __future__ import annotations

import colorsys
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path(__file__).resolve().parent / "fonts"
ICON = ROOT / "public" / "icon.png"
GITHUB_SVG = ROOT / "public" / "brand/github-light.svg"
PHOTO = ROOT / "public" / "uplb-bg.webp"
OUT = ROOT / "public" / "og.png"

W, H = 1200, 630
PAD_X = 80
PAD_BOTTOM = 64
TEXT_MAX = 500
ICON_SIZE = 68
GH_ICON = 18

WHITE = (255, 255, 255)
CREAM = (248, 236, 234)
SHADOW = (12, 6, 6, 140)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return round(r * 255), round(g * 255), round(b * 255)


def paste_cover(base: Image.Image, overlay: Image.Image) -> None:
    ow, oh = overlay.size
    scale = max(W / ow, H / oh)
    resized = overlay.resize((round(ow * scale), round(oh * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    base.paste(resized.crop((left, top, left + W, top + H)))


def draw_overlay(img: Image.Image) -> None:
    """Full-width bottom fade. No boxed scrim."""
    layer = Image.new("RGBA", (W, H))
    px = layer.load()
    for y in range(H):
        t = y / (H - 1)
        for x in range(W):
            # Strongest wash across full width near the bottom third.
            lift = max(0.0, (y - H * 0.42) / (H * 0.58)) ** 1.15
            alpha = int(30 + 200 * lift)
            alpha = min(alpha, 230)
            px[x, y] = (*hsl_to_rgb(5, 48, 14), alpha)
    img.paste(layer, (0, 0), layer)


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def load_github_icon(size: int) -> Image.Image:
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        subprocess.run(
            ["rsvg-convert", "-w", str(size), "-h", str(size), str(GITHUB_SVG), "-o", tmp.name],
            check=True,
        )
        return Image.open(tmp.name).convert("RGBA")


def draw_shadow_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, ...],
) -> None:
    x, y = xy
    draw.text((x + 1, y + 2), text, fill=SHADOW, font=font)
    draw.text((x, y), text, fill=fill, font=font)


def draw_wordmark(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    brand_font: ImageFont.FreeTypeFont,
) -> int:
    draw_shadow_text(draw, (x, y), "uplb", brand_font, WHITE)
    uplb_w, brand_h = measure(draw, "uplb", brand_font)
    dot_x = x + uplb_w
    draw_shadow_text(draw, (dot_x, y), ".", brand_font, CREAM)
    dot_w, _ = measure(draw, ".", brand_font)
    draw_shadow_text(draw, (dot_x + dot_w, y), "tools", brand_font, WHITE)
    tools_w, _ = measure(draw, "tools", brand_font)
    return uplb_w + dot_w + tools_w, brand_h


def draw_sub_line(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    left: str,
    right: str,
    regular: ImageFont.FreeTypeFont,
    emphasis: ImageFont.FreeTypeFont,
) -> None:
    draw.text((x, y), left, fill=WHITE, font=emphasis)
    left_w, _ = measure(draw, left, emphasis)
    mid = "  ·  "
    draw.text((x + left_w, y), mid, fill=(255, 255, 255, 140), font=regular)
    mid_w, _ = measure(draw, mid, regular)
    draw.text((x + left_w + mid_w, y), right, fill=WHITE, font=emphasis)


def main() -> None:
    base = Image.new("RGB", (W, H), hsl_to_rgb(5, 45, 16))
    paste_cover(base, Image.open(PHOTO).convert("RGB"))
    canvas = base.convert("RGBA")
    draw_overlay(canvas)
    draw = ImageDraw.Draw(canvas)

    brand = ImageFont.truetype(FONTS / "Inter-SemiBold.ttf", 40)
    title_lead = ImageFont.truetype(FONTS / "Inter-Regular.ttf", 32)
    title = ImageFont.truetype(FONTS / "Raleway-Bold.ttf", 68)
    sub_emphasis = ImageFont.truetype(FONTS / "Inter-SemiBold.ttf", 26)
    sub_regular = ImageFont.truetype(FONTS / "Inter-Regular.ttf", 26)
    meta = ImageFont.truetype(FONTS / "Inter-Regular.ttf", 19)

    text_x = PAD_X
    gap_sm = 14
    gap_md = 22
    gap_lg = 28

    meta_text = "Open source on GitHub"
    _, meta_h = measure(draw, meta_text, meta)
    _, sub_h = measure(draw, "Room TBA", sub_emphasis)
    _, title_h = measure(draw, "UP Los Baños", title)
    _, lead_h = measure(draw, "Campus tools for", title_lead)
    _, brand_h = measure(draw, "uplb.tools", brand)

    row_h = max(ICON_SIZE, brand_h)
    block_h = row_h + gap_lg + lead_h + gap_sm + title_h + gap_md + sub_h + gap_lg + meta_h
    block_top = H - PAD_BOTTOM - block_h

    icon_y = block_top + (row_h - ICON_SIZE) // 2
    brand_y = block_top + (row_h - brand_h) // 2
    wordmark_x = text_x + ICON_SIZE + 16

    icon = Image.open(ICON).convert("RGBA")
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
    canvas.paste(icon, (text_x, icon_y), icon)
    draw_wordmark(draw, wordmark_x, brand_y, brand)

    y = block_top + row_h + gap_lg
    draw.text((text_x, y), "Campus tools for", fill=(255, 255, 255, 190), font=title_lead)
    y += lead_h + gap_sm
    draw_shadow_text(draw, (text_x, y), "UP Los Baños", title, WHITE)
    y += title_h + gap_md
    draw_sub_line(draw, text_x, y, "Room TBA", "Elbi GradeSim", sub_regular, sub_emphasis)
    y += sub_h + gap_lg

    gh = load_github_icon(GH_ICON)
    gh_y = y + max(0, (meta_h - GH_ICON) // 2)
    canvas.paste(gh, (text_x, gh_y), gh)
    draw.text((text_x + GH_ICON + 8, y), meta_text, fill=(255, 255, 255, 170), font=meta)

    _, title2_w = measure(draw, "UP Los Baños", title)
    assert title2_w <= TEXT_MAX

    canvas.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
