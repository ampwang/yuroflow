import os
import math
import ctypes
from PIL import Image, ImageDraw
from Cocoa import (
    NSAttributedString, NSColor, NSFont,
    NSMutableParagraphStyle, NSForegroundColorAttributeName,
    NSFontAttributeName, NSParagraphStyleAttributeName,
)
from CoreText import (
    CTFontManagerRegisterFontsForURL,
    CTFramesetterCreateWithAttributedString,
    CTFramesetterSuggestFrameSizeWithConstraints,
    CTFramesetterCreateFrame,
    CTFrameDraw,
)
from Quartz import (
    CGColorSpaceCreateDeviceRGB,
    CGBitmapContextCreate,
    CGContextSetRGBFillColor,
    CGContextFillRect,
    CGPathCreateWithRect,
    CGRectMake,
    CGSizeMake,
    kCGImageAlphaPremultipliedLast,
    kCGBitmapByteOrder32Big,
)
from Foundation import NSURL

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_BOLD_PATH = os.path.join(FONTS_DIR, "Sarabun-Bold.ttf")
FONT_REGULAR_PATH = os.path.join(FONTS_DIR, "Sarabun-Regular.ttf")
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.jpg")
LOGO_SIZE = 80
LOGO_MARGIN = 30
LABEL_FONT = "Sarabun"
LABEL_SIZE = 18
LABEL_RIGHT = 44

_fonts_registered = False


def _ensure_fonts():
    global _fonts_registered
    if _fonts_registered:
        return
    for path in (FONT_BOLD_PATH, FONT_REGULAR_PATH):
        url = NSURL.fileURLWithPath_(path)
        CTFontManagerRegisterFontsForURL(url, 1, None)
    _fonts_registered = True


def _make_attr_string(text, ct_font):
    para = NSMutableParagraphStyle.alloc().init()
    para.setAlignment_(1)
    attrs = {
        NSFontAttributeName: ct_font,
        NSForegroundColorAttributeName: NSColor.whiteColor(),
        NSParagraphStyleAttributeName: para,
    }
    return NSAttributedString.alloc().initWithString_attributes_(text, attrs)


def _measure_height(attr_str, width):
    setter = CTFramesetterCreateWithAttributedString(attr_str)
    size, _ = CTFramesetterSuggestFrameSizeWithConstraints(
        setter, (0, len(attr_str.string())), None, CGSizeMake(width, 10000), None
    )
    return math.ceil(size.height)


def _render_text(attr_str, width, height):
    colorspace = CGColorSpaceCreateDeviceRGB()
    buf = (ctypes.c_uint8 * (width * height * 4))()
    ctx = CGBitmapContextCreate(
        buf, width, height, 8, width * 4, colorspace,
        kCGImageAlphaPremultipliedLast | kCGBitmapByteOrder32Big,
    )
    CGContextSetRGBFillColor(ctx, 0, 0, 0, 0)
    CGContextFillRect(ctx, CGRectMake(0, 0, width, height))

    setter = CTFramesetterCreateWithAttributedString(attr_str)
    path = CGPathCreateWithRect(CGRectMake(0, 0, width, height), None)
    frame = CTFramesetterCreateFrame(
        setter, (0, len(attr_str.string())), path, None
    )
    CTFrameDraw(frame, ctx)

    return Image.frombytes("RGBA", (width, height), bytes(buf), "raw", "RGBA")


def process(source_path, output_path, line1, line2, brand_label=""):
    _ensure_fonts()

    font_bold = NSFont.fontWithName_size_("Sarabun-Bold", 52)
    font_regular = NSFont.fontWithName_size_("Sarabun", 36)

    img = Image.open(source_path).convert("RGBA")
    w, h = img.size

    rect_h = int(h * 0.20)
    rect_top = h - rect_h

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([(0, rect_top), (w, h)], fill=(0, 0, 0, int(255 * 0.60)))
    img = Image.alpha_composite(img, overlay)

    attr1 = _make_attr_string(line1, font_bold)
    attr2 = _make_attr_string(line2, font_regular)

    h1 = _measure_height(attr1, w)
    h2 = _measure_height(attr2, w)

    gap = 20
    total_h = h1 + gap + h2
    block_top = rect_top + (rect_h - total_h) // 2

    ascender_pad = 10
    descender_pad = 14
    text1_img = _render_text(attr1, w, h1 + ascender_pad + descender_pad)
    text2_img = _render_text(attr2, w, h2 + ascender_pad + descender_pad)
    img.paste(text1_img, (0, block_top - ascender_pad), mask=text1_img)
    img.paste(text2_img, (0, block_top + h1 + gap - ascender_pad), mask=text2_img)

    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo = logo.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)

        circle_mask = Image.new("L", (LOGO_SIZE, LOGO_SIZE), 0)
        ImageDraw.Draw(circle_mask).ellipse((0, 0, LOGO_SIZE - 1, LOGO_SIZE - 1), fill=204)
        logo.putalpha(circle_mask)

        border_img = Image.new("RGBA", (LOGO_SIZE, LOGO_SIZE), (0, 0, 0, 0))
        ImageDraw.Draw(border_img).ellipse((0, 0, LOGO_SIZE - 1, LOGO_SIZE - 1), outline=(40, 57, 76, 204), width=1)
        logo_x = w - LOGO_SIZE - LOGO_MARGIN
        img.paste(logo, (logo_x, LOGO_MARGIN), mask=logo)
        img.paste(border_img, (logo_x, LOGO_MARGIN), mask=border_img)

        if brand_label:
            font_label = NSFont.fontWithName_size_(LABEL_FONT, LABEL_SIZE)
            from Cocoa import NSShadow, NSShadowAttributeName
            shadow = NSShadow.alloc().init()
            shadow.setShadowColor_(NSColor.whiteColor())
            shadow.setShadowBlurRadius_(3)
            shadow.setShadowOffset_((0, 0))
            para = NSMutableParagraphStyle.alloc().init()
            para.setAlignment_(2)
            label_attrs = {
                NSFontAttributeName: font_label,
                NSForegroundColorAttributeName: NSColor.colorWithRed_green_blue_alpha_(40/255, 57/255, 76/255, 0.8),
                NSParagraphStyleAttributeName: para,
                NSShadowAttributeName: shadow,
            }
            label_str = NSAttributedString.alloc().initWithString_attributes_(brand_label, label_attrs)
            label_w = LOGO_SIZE + 20
            label_h = _measure_height(label_str, label_w)
            label_img = _render_text(label_str, label_w, label_h)
            label_x = w - label_w - LABEL_RIGHT
            label_y = LOGO_MARGIN + LOGO_SIZE + 4
            img.paste(label_img, (label_x, label_y), mask=label_img)

    img.convert("RGB").save(output_path, "JPEG", quality=95)
