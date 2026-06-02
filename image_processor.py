import os
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_BOLD = os.path.join(FONTS_DIR, "Sarabun-Bold.ttf")
FONT_REGULAR = os.path.join(FONTS_DIR, "Sarabun-Regular.ttf")


def process(source_path, output_path, line1, line2):
    img = Image.open(source_path).convert("RGBA")
    w, h = img.size

    rect_h = int(h * 0.20)
    rect_top = h - rect_h

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([(0, rect_top), (w, h)], fill=(0, 0, 0, int(255 * 0.60)))
    img = Image.alpha_composite(img, overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    font1 = ImageFont.truetype(FONT_BOLD, 52)
    font2 = ImageFont.truetype(FONT_REGULAR, 36)

    bbox1 = draw.textbbox((0, 0), line1, font=font1)
    bbox2 = draw.textbbox((0, 0), line2, font=font2)
    text1_w = bbox1[2] - bbox1[0]
    text1_h = bbox1[3] - bbox1[1]
    text2_w = bbox2[2] - bbox2[0]
    text2_h = bbox2[3] - bbox2[1]

    gap = 12
    total_text_h = text1_h + gap + text2_h
    text_block_top = rect_top + (rect_h - total_text_h) // 2

    x1 = (w - text1_w) // 2
    y1 = text_block_top - bbox1[1]

    x2 = (w - text2_w) // 2
    y2 = y1 + text1_h + gap - bbox2[1]

    draw.text((x1, y1), line1, font=font1, fill=(255, 255, 255))
    draw.text((x2, y2), line2, font=font2, fill=(255, 255, 255))

    img.save(output_path, "JPEG", quality=95)
