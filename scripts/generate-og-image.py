#!/usr/bin/env python3
"""Generate public/og.png (1200x630) for Open Graph embeds."""

from __future__ import annotations

import colorsys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path(__file__).resolve().parent / "fonts"
ICON = ROOT / "public" / "icon.png"
PHOTO = ROOT / "public" / "uplb-bg.webp"
OUT = ROOT / "public" / "og.png"

W, H = 1200, 630
PAD = 72
TEXT_MAX = 520
ICON_SIZE = 76

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
    layer = Image.new("RGBA", (W, H))
    px = layer.load()
    for y in range(H):
        for x in range(W):
            bottom = max(0.0, (y - H * 0.18) / (H * 0.82)) ** 1.35
            vignette = 1.0 - 0.22 * ((2 * x / (W - 1) - 1) ** 2)
            alpha = int(55 + 165 * bottom * vignette)
            alpha = min(alpha, 220)
            px[x, y] = (*hsl_to_rgb(5, 50, 18), alpha)
    img.paste(layer, (0, 0), layer)


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_wordmark(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
) -> None:
    draw.text((x, y), "uplb", fill=WHITE, font=font)
    uplb_w, _ = measure(draw, "uplb", font)
    dot_x = x + uplb_w
    draw.text((dot_x, y), ".", fill=(248, 228, 226), font=font)
    dot_w, _ = measure(draw, ".", font)
    draw.text((dot_x + dot_w, y), "tools", fill=WHITE, font=font)


def main() -> None:
    base = Image.new("RGB", (W, H), hsl_to_rgb(5, 45, 16))
    paste_cover(base, Image.open(PHOTO).convert("RGB"))
    canvas = base.convert("RGBA")
    draw_overlay(canvas)
    draw = ImageDraw.Draw(canvas)

    brand = ImageFont.truetype(FONTS / "Raleway-Bold.ttf", 46)
    title = ImageFont.truetype(FONTS / "Raleway-Bold.ttf", 62)
    sub = ImageFont.truetype(FONTS / "Inter-Regular.ttf", 28)
    meta = ImageFont.truetype(FONTS / "Inter-Medium.ttf", 21)

    text_x = PAD
    block_bottom = H - PAD

    meta_text = "Open source on GitHub"
    _, meta_h = measure(draw, meta_text, meta)
    sub_text = "Room TBA  ·  Elbi GradeSim"
    _, sub_h = measure(draw, sub_text, sub)
    _, title_h = measure(draw, "UP Los Baños", title)
    _, brand_h = measure(draw, "uplb.tools", brand)

    meta_y = block_bottom - meta_h
    sub_y = meta_y - 34 - sub_h
    title2_y = sub_y - 18 - title_h
    title1_y = title2_y - 8 - title_h
    brand_y = title1_y - 28 - brand_h
    icon_y = brand_y + max(0, (brand_h - ICON_SIZE) // 2)

    icon = Image.open(ICON).convert("RGBA")
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
    canvas.paste(icon, (text_x, icon_y), icon)

    wordmark_x = text_x + ICON_SIZE + 18
    wordmark_y = brand_y + max(0, (brand_h - brand_h) // 2)
    draw_wordmark(draw, wordmark_x, wordmark_y, brand)

    draw.text((text_x, title1_y), "Campus tools for", fill=WHITE, font=title)
    draw.text((text_x, title2_y), "UP Los Baños", fill=WHITE, font=title)
    draw.text((text_x, sub_y), sub_text, fill=WHITE_SOFT, font=sub)
    draw.text((text_x, meta_y), meta_text, fill=WHITE_DIM, font=meta)

    _, title1_w = measure(draw, "Campus tools for", title)
    _, title2_w = measure(draw, "UP Los Baños", title)
    assert max(title1_w, title2_w) <= TEXT_MAX

    canvas.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
