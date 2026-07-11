#!/usr/bin/env python3
"""Generate public/og.png (1200x630) for Open Graph embeds."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / "public" / "icon.png"
OUT = ROOT / "public" / "og.png"
FONT_BOLD = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"

W, H = 1200, 630


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    import colorsys

    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return round(r * 255), round(g * 255), round(b * 255)


def main() -> None:
    img = Image.new("RGB", (W, H))
    px = img.load()
    top = hsl_to_rgb(5, 55, 32)
    bottom = hsl_to_rgb(5, 45, 20)
    for y in range(H):
        t = y / (H - 1)
        color = tuple(round(lerp(top[i], bottom[i], t)) for i in range(3))
        for x in range(W):
            px[x, y] = color

    draw = ImageDraw.Draw(img)
    icon = Image.open(ICON).convert("RGBA")
    icon_size = 240
    icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    icon_x = 96
    icon_y = (H - icon_size) // 2
    img.paste(icon, (icon_x, icon_y), icon)

    title_font = ImageFont.truetype(FONT_BOLD, 92)
    body_font = ImageFont.truetype(FONT_REG, 34)
    text_x = icon_x + icon_size + 64

    draw.text((text_x, 188), "uplb.tools", fill=(255, 255, 255), font=title_font)
    draw.text(
        (text_x, 300),
        "Room TBA and Elbi GradeSim",
        fill=(245, 240, 238),
        font=body_font,
    )
    draw.text(
        (text_x, 358),
        "Open-source campus tools for UP Los Baños",
        fill=(230, 220, 218),
        font=body_font,
    )

    img.save(OUT, optimize=True)
    print(f"Wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
