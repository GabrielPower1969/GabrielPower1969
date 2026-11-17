#!/usr/bin/env python3
"""Gentle portrait retouch on skin only: even out lighting (lift shadows, tame hot spots),
then light edge-aware smoothing. Eyes, glasses, hair and the headphones are left alone.
Usage: python3 scripts/retouch.py <photo.png> <cutout.png> <out-photo.png> <out-cutout.png>"""
import sys
import numpy as np
from PIL import Image, ImageFilter
photo, cutp, outp, outc = sys.argv[1:5]
im = Image.open(photo).convert("RGB")
alpha = Image.open(cutp).getchannel("A")
a = np.asarray(im).astype(np.float32)
ycc = np.asarray(im.convert("YCbCr")).astype(np.float32)
Y, Cb, Cr = ycc[..., 0], ycc[..., 1], ycc[..., 2]
skin = ((Cb > 77) & (Cb < 130) & (Cr > 133) & (Cr < 178) & (Y > 40)).astype(np.float32)
skin *= (np.asarray(alpha) > 128)
sk = Image.fromarray((skin * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(6))
m = np.asarray(sk).astype(np.float32) / 255
# 1. Lighting: local mean luminance of skin vs overall skin mean.
def blur(x, r):
    # x in 0..255; blur at quarter size for speed, then scale back up
    img = Image.fromarray(np.clip(x, 0, 255).astype(np.uint8))
    small = img.resize((img.width // 4, img.height // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / 4))
    return np.asarray(small.resize(img.size, Image.BILINEAR)).astype(np.float32)
num = blur(Y * skin, 22); den = blur(skin * 255, 22) / 255 + 1e-3
illum = num / den
target = (Y * skin).sum() / skin.sum()
gain = np.clip((target + 2) / np.maximum(illum, 1), 0.88, 1.18)
gain = 1 + (gain - 1) * 0.9
lit = np.clip(a * gain[..., None], 0, 255)
# 1b. Hard-edged cast shadows (e.g. a band across the forehead): compare each skin pixel with the
# bright envelope of nearby skin and lift what falls in a shadow, keeping fine detail.
Yl = lit.mean(axis=2)
env_img = Image.fromarray(np.clip(Yl * skin, 0, 255).astype(np.uint8))
small = env_img.resize((env_img.width // 2, env_img.height // 2), Image.BILINEAR)
small = small.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10))
env = np.asarray(small.resize(env_img.size, Image.BILINEAR)).astype(np.float32)
base = blur(Yl, 6)  # broad tone, without pores and lines
shade = np.clip(base / np.maximum(env, 1), 0.55, 1.0)
lift = np.clip((1 / shade) ** 0.42, 1, 1.30)
lit = np.clip(lit * (1 + (lift - 1) * m)[..., None], 0, 255)
# 2. Smoothing: blur, but only where the skin has little fine detail.
sm = np.asarray(Image.fromarray(lit.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.2))).astype(np.float32)
edges = np.asarray(Image.fromarray(lit.astype(np.uint8)).convert("L").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(2))).astype(np.float32)
flat = np.clip(1 - edges / 28, 0, 1)
w_s = (m * flat * 0.35)[..., None]
smooth = lit * (1 - w_s) + sm * w_s
# keep a touch of texture back so skin does not look plastic
tex = a - np.asarray(im.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)
smooth = smooth + tex * 0.4 * m[..., None]
w = m[..., None]
res = np.clip(a * (1 - w) + smooth * w, 0, 255).astype(np.uint8)
out = Image.fromarray(res)
out.save(outp)
c = out.convert("RGBA"); c.putalpha(alpha); c.save(outc)
print("skin px", int(skin.sum()), "target Y", round(float(target), 1))
