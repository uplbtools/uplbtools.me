#!/usr/bin/env python3
"""Generate public/og.png (1200x630) for Open Graph embeds."""

from __future__ import annotations

import colorsys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DISPLAY = "/usr/share/fonts/abattis-cantarell-fonts/Cantarell-Bold.otf"
FONT_TITLE = "/usr/share/fonts/abattis-cantarell-fonts/Cantarell-Bold.otf"
FONT_BODY = "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf"
FONT_CHIP = "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Bold.ttf"
ICON = ROOT / "public" / "icon.png"
PHOTO = ROOT / "public" / "uplb-bg.webp"
OUT = ROOT / "public" / "og.png"

W, H = 1200, 630

INK = (38, 34, 33)
BODY = (58, 52, 50)
MUTED = (96, 88, 86)
MAROON = (126, 45, 40)
MAROON_DEEP = (108, 38, 34)
CREAM = (249, 246, 245)
CREAM_EDGE = (236, 228, 226)
PILL_BG = (245, 236, 234)
PILL_BORDER = (220, 198, 194)
WHITE = (255, 255, 255)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return round(r * 255), round(g * 255), round(b * 255)


def rounded_rect(
    size: tuple[int, int],
    radius: int,
    fill: tuple[int, int, int, int],
) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=fill)
    return img


def paste_cover(base: Image.Image, overlay: Image.Image) -> None:
    ow, oh = overlay.size
    scale = max(W / ow, H / oh)
    resized = overlay.resize((round(ow * scale), round(oh * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    base.paste(resized.crop((left, top, left + W, top + H)))


def draw_gradient_overlay(img: Image.Image) -> None:
    overlay = Image.new("RGBA", (W, H))
    px = overlay.load()
    for y in range(H):
        t = y / (H - 1)
        for x in range(W):
            edge = min(x / (W * 0.55), 1.0)
            alpha = int(155 + 70 * t + 35 * edge)
            alpha = min(alpha, 235)
            px[x, y] = (*hsl_to_rgb(5, 52, 24), alpha)
    img.paste(overlay, (0, 0), overlay)


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_wordmark(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    display: ImageFont.FreeTypeFont,
) -> None:
    draw.text((x, y), "uplb", fill=INK, font=display)
    uplb_w, _ = measure(draw, "uplb", display)
    dot_x = x + uplb_w + 2
    dot_y = y + 8
    draw.ellipse((dot_x, dot_y, dot_x + 10, dot_y + 10), fill=MAROON)
    draw.text((dot_x + 16, y), "tools", fill=INK, font=display)


def draw_chip(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    label: str,
    font: ImageFont.FreeTypeFont,
) -> int:
    pad_x, pad_y = 18, 11
    text_w, text_h = measure(draw, label, font)
    chip_w = text_w + pad_x * 2
    chip_h = text_h + pad_y * 2
    chip = rounded_rect((chip_w, chip_h), 999, (*PILL_BG, 255))
    border = ImageDraw.Draw(chip)
    border.rounded_rectangle(
        (0, 0, chip_w - 1, chip_h - 1),
        radius=999,
        outline=(*PILL_BORDER, 255),
        width=1,
    )
    draw._image.paste(chip, (x, y), chip)
    draw.text((x + pad_x, y + pad_y - 1), label, fill=MAROON_DEEP, font=font)
    return chip_w


def main() -> None:
    base = Image.new("RGB", (W, H), hsl_to_rgb(5, 45, 20))
    paste_cover(base, Image.open(PHOTO).convert("RGB"))
    draw_gradient_overlay(base)

    card_w, card_h = 1040, 470
    card_x, card_y = 80, 80
    shadow = rounded_rect((card_w, card_h), 28, (20, 10, 10, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    base_rgba = base.convert("RGBA")
    base_rgba.alpha_composite(shadow, (card_x, card_y + 10))

    card = rounded_rect((card_w, card_h), 28, (*CREAM, 255))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle(
        (0, 0, card_w - 1, card_h - 1),
        radius=28,
        outline=(*CREAM_EDGE, 255),
        width=1,
    )
    card_draw.rectangle((0, 36, 5, card_h - 36), fill=MAROON)
    base_rgba.alpha_composite(card, (card_x, card_y))

    draw = ImageDraw.Draw(base_rgba)
    content_x = card_x + 72
    content_y = card_y + 56

    display = ImageFont.truetype(FONT_DISPLAY, 38)
    title = ImageFont.truetype(FONT_TITLE, 62)
    body = ImageFont.truetype(FONT_BODY, 28)
    chip = ImageFont.truetype(FONT_CHIP, 22)

    icon = Image.open(ICON).convert("RGBA")
    icon = icon.resize((54, 54), Image.Resampling.LANCZOS)
    base_rgba.paste(icon, (content_x, content_y - 4), icon)
    draw_wordmark(draw, content_x + 68, content_y, display)

    headline_y = content_y + 84
    draw.text((content_x, headline_y), "Campus tools for", fill=INK, font=title)
    draw.text((content_x, headline_y + 68), "UP Los Baños", fill=MAROON, font=title)

    body_y = headline_y + 162
    draw.text(
        (content_x, body_y),
        "Room schedules, AMIS grade simulation, and other student-built utilities.",
        fill=BODY,
        font=body,
    )

    chip_y = body_y + 78
    chip_x = content_x
    chip_x += draw_chip(draw, chip_x, chip_y, "Room TBA", chip) + 14
    _, chip_h = measure(draw, "Room TBA", chip)
    chip_h += 22
    draw_chip(draw, chip_x, chip_y, "Elbi GradeSim", chip)

    draw.text(
        (content_x, chip_y + chip_h + 28),
        "Open source on GitHub · Not an official UPLB site",
        fill=MUTED,
        font=body,
    )

    base_rgba.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
