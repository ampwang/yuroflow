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


def process(source_path, output_path, line1, line2):
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

    text1_img = _render_text(attr1, w, h1)
    text2_img = _render_text(attr2, w, h2)
    img.paste(text1_img, (0, block_top), mask=text1_img)
    img.paste(text2_img, (0, block_top + h1 + gap), mask=text2_img)

    img.convert("RGB").save(output_path, "JPEG", quality=95)
