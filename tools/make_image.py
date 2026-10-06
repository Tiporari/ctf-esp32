"""Render a flag into a small 1-bit PNG and write it base64-encoded to device/<name>.b64.
Usage: python tools/make_image.py "FLAG{...}" vault.b64 [second line]
"""
import base64, io, sys, pathlib
from PIL import Image, ImageDraw, ImageFont

lines = [sys.argv[1]] + sys.argv[3:]
out = pathlib.Path(__file__).parent.parent / "device" / sys.argv[2]

font = ImageFont.load_default(size=28)
w = max(int(font.getlength(l)) for l in lines) + 40
h = 30 + 44 * len(lines)
img = Image.new("1", (w, h), 0)
d = ImageDraw.Draw(img)
for i, l in enumerate(lines):
    d.text((20, 15 + 44 * i), l, font=font, fill=1)
buf = io.BytesIO()
img.save(buf, "PNG", optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()
out.write_text(b64)
print(f"{out}: {len(buf.getvalue())} bytes PNG, {len(b64)} chars base64, {w}x{h}")
