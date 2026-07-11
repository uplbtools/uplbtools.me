#!/usr/bin/env python3
"""Generate public/og.png (1200x630) for Open Graph embeds."""

from __future__ import annotations

import colorsys
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path(__file__).resolve().parent / "fonts"
ICON = ROOT / "public" / "icon.png"
GITHUB_SVG = ROOT / "public" / "brand/github-light.svg"
PHOTO = ROOT / "public" / "uplb-bg.webp"
OUT = ROOT / "public" / "og.png"

W, H = 1200, 630
PAD = 72
TEXT_MAX = 520
ICON_SIZE = 76
GH_ICON = 20

WHITE = (255, 255, 255)
INK_ON_DARK = (24, 18, 17)
CREAM = (248, 236, 234)


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
    layer = Image.new("RGBA", (W, H))
    px = layer.load()
    for y in range(H):
        for x in range(W):
            bottom = max(0.0, (y - H * 0.12) / (H * 0.88)) ** 1.25
            vignette = 1.0 - 0.24 * ((2 * x / (W - 1) - 1) ** 2)
            alpha = int(70 + 175 * bottom * vignette)
            alpha = min(alpha, 235)
            px[x, y] = (*hsl_to_rgb(5, 50, 16), alpha)
    img.paste(layer, (0, 0), layer)


def draw_column_scrim(canvas: Image.Image, x: int, y: int, w: int, h: int) -> None:
    scrim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scrim)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=24, fill=(18, 8, 8, 168))
    scrim = scrim.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(scrim, (x, y))


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def load_github_icon(size: int) -> Image.Image:
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        subprocess.run(
            [
                "rsvg-convert",
                "-w",
                str(size),
                "-h",
                str(size),
                str(GITHUB_SVG),
                "-o",
                tmp.name,
            ],
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
    draw.text((x + 1, y + 2), text, fill=(INK_ON_DARK[0], INK_ON_DARK[1], INK_ON_DARK[2], 160), font=font)
    draw.text((x, y), text, fill=fill, font=font)


def draw_wordmark(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    brand_font: ImageFont.FreeTypeFont,
) -> None:
    draw_shadow_text(draw, (x, y), "uplb", brand_font, WHITE)
    uplb_w, _ = measure(draw, "uplb", brand_font)
    dot_x = x + uplb_w
    draw_shadow_text(draw, (dot_x, y), ".", brand_font, CREAM)
    dot_w, _ = measure(draw, ".", brand_font)
    draw_shadow_text(draw, (dot_x + dot_w, y), "tools", brand_font, WHITE)


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
    draw.text((x + left_w, y), mid, fill=(255, 255, 255, 150), font=regular)
    mid_w, _ = measure(draw, mid, regular)
    draw.text((x + left_w + mid_w, y), right, fill=WHITE, font=emphasis)


def main() -> None:
    base = Image.new("RGB", (W, H), hsl_to_rgb(5, 45, 16))
    paste_cover(base, Image.open(PHOTO).convert("RGB"))
    canvas = base.convert("RGBA")
    draw_overlay(canvas)
    draw = ImageDraw.Draw(canvas)

    brand = ImageFont.truetype(FONTS / "Inter-SemiBold.ttf", 42)
    title_lead = ImageFont.truetype(FONTS / "Inter-Regular.ttf", 34)
    title = ImageFont.truetype(FONTS / "Raleway-Bold.ttf", 72)
    sub_emphasis = ImageFont.truetype(FONTS / "Inter-SemiBold.ttf", 27)
    sub_regular = ImageFont.truetype(FONTS / "Inter-Regular.ttf", 27)
    meta = ImageFont.truetype(FONTS / "Inter-Regular.ttf", 20)

    text_x = PAD
    block_bottom = H - PAD

    meta_text = "Open source on GitHub"
    _, meta_h = measure(draw, meta_text, meta)
    _, sub_h = measure(draw, "Room TBA", sub_emphasis)
    _, title_h = measure(draw, "UP Los Baños", title)
    _, lead_h = measure(draw, "Campus tools for", title_lead)
    _, brand_h = measure(draw, "uplb.tools", brand)

    meta_y = block_bottom - meta_h
    sub_y = meta_y - 36 - sub_h
    title2_y = sub_y - 22 - title_h
    title1_y = title2_y - 6 - lead_h
    brand_y = title1_y - 30 - brand_h
    icon_y = brand_y + max(0, (brand_h - ICON_SIZE) // 2)

    scrim_top = brand_y - 28
    scrim_h = block_bottom - scrim_top + 20
    draw_column_scrim(canvas, text_x - 28, scrim_top, TEXT_MAX + 56, scrim_h)
    draw = ImageDraw.Draw(canvas)

    icon = Image.open(ICON).convert("RGBA")
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
    canvas.paste(icon, (text_x, icon_y), icon)

    wordmark_x = text_x + ICON_SIZE + 18
    draw_wordmark(draw, wordmark_x, brand_y, brand)

    draw.text((text_x, title1_y), "Campus tools for", fill=(255, 255, 255, 188), font=title_lead)
    draw_shadow_text(draw, (text_x, title2_y), "UP Los Baños", title, WHITE)
    draw_sub_line(draw, text_x, sub_y, "Room TBA", "Elbi GradeSim", sub_regular, sub_emphasis)

    gh = load_github_icon(GH_ICON)
    gh_y = meta_y + max(0, (meta_h - GH_ICON) // 2)
    canvas.paste(gh, (text_x, gh_y), gh)
    draw.text((text_x + GH_ICON + 10, meta_y), meta_text, fill=(255, 255, 255, 165), font=meta)

    _, title2_w = measure(draw, "UP Los Baños", title)
    assert title2_w <= TEXT_MAX

    canvas.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
