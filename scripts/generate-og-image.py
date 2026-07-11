#!/usr/bin/env python3
"""Generate public/og.png (1200x630) for Open Graph embeds."""

from __future__ import annotations

import colorsys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path(__file__).resolve().parent / "fonts"
PHOTO = ROOT / "public" / "uplb-bg.webp"
OUT = ROOT / "public" / "og.png"

W, H = 1200, 630
PAD = 72

WHITE = (255, 255, 255)
WHITE_SOFT = (255, 255, 255, 210)
WHITE_DIM = (255, 255, 255, 170)


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
    """Photo + bottom-weighted maroon wash for readable white type."""
    layer = Image.new("RGBA", (W, H))
    px = layer.load()
    for y in range(H):
        t = y / (H - 1)
        for x in range(W):
            bottom = max(0.0, (y - H * 0.18) / (H * 0.82)) ** 1.35
            vignette = 1.0 - 0.22 * ((2 * x / (W - 1) - 1) ** 2)
            alpha = int(55 + 165 * bottom * vignette)
            alpha = min(alpha, 220)
            px[x, y] = (*hsl_to_rgb(5, 50, 18), alpha)
    img.paste(layer, (0, 0), layer)


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def draw_wordmark(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
) -> None:
    draw.text((x, y), "uplb", fill=WHITE, font=font)
    uplb_w = measure(draw, "uplb", font)
    dot_x = x + uplb_w
    draw.text((dot_x, y), ".", fill=(248, 228, 226), font=font)
    dot_w = measure(draw, ".", font)
    draw.text((dot_x + dot_w, y), "tools", fill=WHITE, font=font)


def main() -> None:
    base = Image.new("RGB", (W, H), hsl_to_rgb(5, 45, 16))
    paste_cover(base, Image.open(PHOTO).convert("RGB"))
    canvas = base.convert("RGBA")
    draw_overlay(canvas)
    draw = ImageDraw.Draw(canvas)

    brand = ImageFont.truetype(FONTS / "Raleway-Bold.ttf", 54)
    title = ImageFont.truetype(FONTS / "Raleway-Bold.ttf", 76)
    sub = ImageFont.truetype(FONTS / "Inter-Regular.ttf", 30)
    meta = ImageFont.truetype(FONTS / "Inter-Medium.ttf", 22)

    y = H - PAD - 210
    draw_wordmark(draw, PAD, y, brand)
    y += 78

    draw.text((PAD, y), "Campus tools for UP Los Baños", fill=WHITE, font=title)
    y += 92

    draw.text((PAD, y), "Room TBA  ·  Elbi GradeSim", fill=WHITE_SOFT, font=sub)
    y += 44

    draw.text(
        (PAD, y),
        "Open source on GitHub",
        fill=WHITE_DIM,
        font=meta,
    )

    canvas.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
