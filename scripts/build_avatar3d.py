#!/usr/bin/env python3
"""Pop-out avatar: sharp cut-out subject breaking out of a blurred, blue-tinted disc,
with a contact shadow so it floats above the page. GitHub crops avatars to a circle,
so everything stays inside the inscribed circle.
Usage: python3 scripts/build_avatar3d.py <photo> <cutout.png> <hex-blue> <out.png> [hex-accent]"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance
photo, cutp, blue, out = sys.argv[1:5]
S = 1200
B = tuple(int(blue[i:i+2], 16) for i in (1, 3, 5))
src = Image.open(photo).convert("RGB")
cut = Image.open(cutp).convert("RGBA")
bbox = cut.getchannel("A").point(lambda a: 255 if a > 40 else 0).getbbox()
cut = cut.crop(bbox)
# Fit subject: width 78% of canvas, head top at 9% of canvas.
w = int(S * 0.70); h = int(cut.height * w / cut.width)
cut = cut.resize((w, h), Image.LANCZOS)
src = src.crop(bbox).resize((w, h), Image.LANCZOS)
sx, sy = (S - w) // 2, int(S * 0.13)

page = Image.new("RGBA", (S, S), (240, 245, 251, 255))
cx, cy, r = S // 2, int(S * 0.59), int(S * 0.355)
disc = Image.new("L", (S, S), 0); ImageDraw.Draw(disc).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)

# 1. Disc floats: soft shadow on the page.
sh = Image.new("L", (S, S), 0); ImageDraw.Draw(sh).ellipse((cx - r + 10, cy - r + 34, cx + r - 10, cy + r + 34), fill=110)
page.alpha_composite(Image.merge("RGBA", (*[Image.new("L", (S, S), 10)] * 3, sh.filter(ImageFilter.GaussianBlur(38)))))

# 1b. Optional accent: a small circle tucked behind the disc's upper-right edge.
if len(sys.argv) > 5:
    A = tuple(int(sys.argv[5][i:i+2], 16) for i in (1, 3, 5))
    ar = int(r * 0.26); ax, ay = cx + int(r * 0.74), cy - int(r * 0.74)
    ImageDraw.Draw(page).ellipse((ax - ar, ay - ar, ax + ar, ay + ar), fill=A + (255,))

# 2. Disc fill: the photo's own background, out of focus and washed in blue (depth of field).
bgimg = Image.new("RGB", (S, S), B)
blur = src.filter(ImageFilter.GaussianBlur(28))
bgimg.paste(blur, (sx, sy))
bgimg = ImageEnhance.Color(bgimg).enhance(0.4)
tinted = Image.blend(bgimg, Image.new("RGB", (S, S), B), 0.82)
# light from the top-left
grad = Image.linear_gradient("L").rotate(35).resize((S, S))
tinted = Image.composite(tinted, Image.blend(tinted, Image.new("RGB", (S, S), (255, 255, 255)), 0.18), grad)
page.paste(tinted, (0, 0), disc)
ring = Image.new("L", (S, S), 0); ImageDraw.Draw(ring).ellipse((cx - r, cy - r, cx + r, cy + r), outline=255, width=5)
page.alpha_composite(Image.merge("RGBA", (*[Image.new("L", (S, S), 255)] * 3, ring.point(lambda v: v * 0.55))))

# 3. Subject mask: inside the disc, plus everything above the disc centre (head breaks out).
alpha = Image.new("L", (S, S), 0); alpha.paste(cut.getchannel("A"), (sx, sy))
above = Image.new("L", (S, S), 0); ImageDraw.Draw(above).rectangle((0, 0, S, cy), fill=255)
keep = ImageChops.lighter(disc, above)
alpha = ImageChops.multiply(alpha, keep)
# 4. Subject shadow cast onto the disc and page.
shadow = alpha.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.42))
shadow = ImageChops.offset(shadow, 14, 26)
page.alpha_composite(Image.merge("RGBA", (*[Image.new("L", (S, S), 8)] * 3, shadow)))
# 5. Sharp subject with a hint of extra contrast.
subj = Image.new("RGBA", (S, S), (0, 0, 0, 0)); subj.paste(cut, (sx, sy))
subj = ImageEnhance.Contrast(subj.convert("RGB")).enhance(1.06).convert("RGBA")
subj.putalpha(alpha)
page.alpha_composite(subj)
page = page.convert("RGB")
page.save(out)
page.resize((460, 460), Image.LANCZOS).save(out.replace(".png", "-460.png"))
m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S, S), fill=255)
pv = Image.new("RGB", (S, S), (255, 255, 255)); pv.paste(page, (0, 0), m)
pv.resize((360, 360), Image.LANCZOS).save(out.replace(".png", "-circle.png"))
print("ok")
