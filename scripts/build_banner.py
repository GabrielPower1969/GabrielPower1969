#!/usr/bin/env python3
"""Build the animated README banner (light + dark) for the GitHub profile.

Text is converted to SVG paths so the banner looks identical everywhere: GitHub serves
README images through a proxy that blocks web fonts inside SVGs.

Design: white page, black type, thin rules (tanishmittal.com); typewriter title whose final
full stop drops in as the blue guide dot (onemorething.today / lovefrom.com / marekvataha.com);
Bauhaus poster shapes in the Klein Bauhaus palette (ultramarine, primary yellow, ink, white).

Usage: python3 scripts/build_banner.py   (run from the github-profile folder)
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
OUT = ROOT / "assets"

PRIMARY_L = "#002FA7"  # Klein-style ultramarine, on white
PRIMARY_D = "#6B8CFF"  # same hue, lifted for GitHub dark
YELLOW = "#FFC400"


def load(path, axes):
    f = TTFont(path)
    if "fvar" in f:
        f = instancer.instantiateVariableFont(f, axes)
    return f


SERIF = load(FONTS / "newsreader-latin-wght-normal.woff2", {"wght": 480})
SANS = load(Path.home() / "Library/Fonts/Inter[opsz,wght].ttf", {"opsz": 24, "wght": 420})
HAND = load(FONTS / "Caveat.ttf", {"wght": 520})


def glyphs(font, text, size, x, y, tracking=0.0):
    """Return [(char, path_d, x_start, advance)] for text set at baseline (x, y)."""
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    upm = font["head"].unitsPerEm
    s = size / upm
    out = []
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            name = cmap[ord("?")]
        adv = font["hmtx"][name][0] * s + tracking
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        out.append((ch, pen.getCommands(), x, adv))
        x += adv
    return out


def static_text(font, text, size, x, y, fill, tracking=0.0, extra=""):
    d = " ".join(g[1] for g in glyphs(font, text, size, x, y, tracking) if g[1])
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def width(font, text, size, tracking=0.0):
    g = glyphs(font, text, size, 0, 0, tracking)
    return g[-1][2] + g[-1][3]


def build(theme):
    W, H = 1280, 400
    if theme == "light":
        bg, ink, muted, rule, accent = "#FFFFFF", "#16181D", "#5D6573", "#16181D", PRIMARY_L
    else:
        bg, ink, muted, rule, accent = "#0D1117", "#EEF1F6", "#9AA3B2", "#EEF1F6", PRIMARY_D

    t0, dt1, pause, dt2 = 0.6, 0.075, 0.55, 0.022
    css = []
    body = []

    # Frame: thin rules and small labels, poster style.
    body.append(f'<rect width="{W}" height="{H}" fill="{bg}"/>')
    body.append(f'<line x1="56" y1="58" x2="1224" y2="58" stroke="{rule}" stroke-width="1" opacity=".9"/>')
    body.append(f'<line x1="56" y1="352" x2="1224" y2="352" stroke="{rule}" stroke-width="1" opacity=".9"/>')
    body.append(static_text(SANS, "GABRIEL CHEN  /  README", 12, 56, 44, ink, tracking=1.6))
    lab = "Nº 01 — 2026"
    body.append(static_text(SANS, lab, 12, 1224 - width(SANS, lab, 12, 1.6), 44, ink, tracking=1.6))
    foot = "onemorething.today"
    body.append(static_text(SANS, foot, 12, 56, 376, muted, tracking=0.6))
    foot2 = "Trimble · FlowGT · CITANZ · Christchurch NZ"
    body.append(static_text(SANS, foot2, 12, 1224 - width(SANS, foot2, 12, 0.6), 376, muted, tracking=0.6))

    # Bauhaus composition (right). Each shape eases in while the title types.
    comp = [
        (f'<circle cx="1018" cy="204" r="128" fill="{accent}"/>', 0.15),
        (f'<path d="M1224 58 L1104 58 A120 120 0 0 0 1224 178 Z" fill="{YELLOW}"/>', 0.35),
        (f'<rect x="878" y="96" width="34" height="210" fill="{ink}"/>', 0.55),
        (f'<rect x="812" y="306" width="412" height="20" fill="{ink}"/>', 0.75),
        (f'<line x1="790" y1="352" x2="1224" y2="96" stroke="{ink}" stroke-width="1"/>', 0.95),
        (f'<circle cx="1018" cy="204" r="150" fill="none" stroke="{ink}" stroke-width="1" stroke-dasharray="2 6"/>', 1.1),
    ]
    for i, (shape, delay) in enumerate(comp):
        body.append(f'<g class="shape" style="animation-delay:{delay:.2f}s">{shape}</g>')

    # Title, typed one glyph at a time.
    title = "Hi, I’m Gabriel"
    gl1 = glyphs(SERIF, title, 92, 52, 178)
    t = t0
    caret1 = []
    for ch, d, x, adv in gl1:
        if d:
            body.append(f'<path class="c" style="animation-delay:{t:.3f}s" d="{d}" fill="{ink}"/>')
        caret1.append((t, x + adv))
        t += dt1
    end1 = t
    # Final full stop = the blue guide dot, dropped in after the last letter.
    dot_x = gl1[-1][2] + gl1[-1][3] + 14
    body.append(
        f'<circle class="dot" style="animation-delay:{end1 + 0.25:.2f}s" cx="{dot_x:.1f}" cy="168" r="10" fill="{accent}"/>'
    )

    # Two sub-lines.
    lines = [
        ("Software engineer at Trimble, building small tools", 25, 236),
        ("for job seekers, families and the CITANZ community.", 25, 272),
    ]
    t = end1 + pause + 0.5
    start2 = t
    caret2 = []
    for text, size, y in lines:
        gl = glyphs(SANS, text, size, 56, y)
        caret2.append((t, gl[0][2], y, True))
        for ch, d, x, adv in gl:
            if d:
                body.append(f'<path class="c" style="animation-delay:{t:.3f}s" d="{d}" fill="{ink}"/>')
            caret2.append((t, x + adv, y, False))
            t += dt2
        t += 0.18
    end2 = t

    # Handwritten note with a drawn arrow toward the composition.
    note = "made in Christchurch"
    body.append(
        f'<g class="note" style="animation-delay:{end2 + 0.2:.2f}s">'
        + static_text(HAND, note, 30, 560, 330, accent)
        + "</g>"
    )
    nx = 560 + width(HAND, note, 30) + 10
    body.append(
        f'<path class="arrow" style="animation-delay:{end2 + 0.55:.2f}s" d="M{nx:.0f} 322 C {nx + 40:.0f} 318, {nx + 70:.0f} 290, {nx + 78:.0f} 262 M{nx + 64:.0f} 274 L{nx + 78:.0f} 262 L{nx + 86:.0f} 278" '
        f'fill="none" stroke="{accent}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    )

    # Carets: one tall for the title, one short for the sub-lines.
    def kf(name, steps, total_start, total_end, y_of):
        dur = total_end - total_start
        frames = []
        for st in steps:
            pct = (st[0] - total_start) / dur * 100
            frames.append(f"{pct:.2f}%{{transform:translate({st[1]:.1f}px,{y_of(st):.1f}px)}}")
        css.append(f"@keyframes {name}{{{''.join(frames)}}}")
        return dur

    c1_start = t0
    steps1 = [(t0 - 0.001, 52 + 2)] + caret1
    dur1 = kf("m1", steps1, c1_start - 0.001, end1 + 0.001, lambda s: 0)
    body.append(
        f'<g class="v1"><g style="animation:m1 {dur1:.3f}s step-end {c1_start - 0.001:.3f}s both">'
        f'<rect class="blink" x="2" y="104" width="3" height="82" fill="{ink}"/></g></g>'
    )
    steps2 = [(s[0] - 0.001, s[1] + 2, s[2]) for s in caret2]
    dur2 = kf("m2", steps2, start2 - 0.002, end2, lambda s: s[2] - 236)
    body.append(
        f'<g class="v2"><g style="animation:m2 {dur2:.3f}s step-end {start2 - 0.002:.3f}s both">'
        f'<rect class="blink" x="0" y="214" width="2" height="27" fill="{ink}"/></g></g>'
    )

    css += [
        ".c{opacity:0;animation:on .01s linear both}",
        "@keyframes on{to{opacity:1}}",
        ".shape{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .9s cubic-bezier(.2,.8,.2,1) both}",
        "@keyframes pop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:scale(1)}}",
        ".dot{opacity:0;transform-box:fill-box;transform-origin:center;animation:drop .75s cubic-bezier(.3,1.5,.5,1) both}",
        "@keyframes drop{0%{opacity:0;transform:translateY(-120px)}25%{opacity:1}100%{opacity:1;transform:translateY(0)}}",
        ".note{opacity:0;animation:fade .6s ease-out both}",
        "@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}",
        ".arrow{stroke-dasharray:200;stroke-dashoffset:200;animation:draw .7s ease-out both}",
        "@keyframes draw{to{stroke-dashoffset:0}}",
        ".blink{animation:blink 1.06s steps(1) infinite}",
        "@keyframes blink{50%{opacity:0}}",
        f".v1{{opacity:0;animation:w1 {end1 + 0.9:.2f}s step-end both}}",
        f"@keyframes w1{{0%{{opacity:1}}100%{{opacity:0}}}}",
        f".v2{{opacity:0;animation:on .01s linear {start2:.2f}s both}}",
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.c,.shape,.dot,.note,.v2{opacity:1}.arrow{stroke-dashoffset:0}.v1{opacity:0}}",
    ]

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Hi, I’m Gabriel. Software engineer at Trimble, building small tools for job seekers, families and the CITANZ community.">'
        f"<title>Hi, I’m Gabriel.</title><style>{''.join(css)}</style>" + "".join(body) + "</svg>"
    )
    (OUT / f"banner-{theme}.svg").write_text(svg, encoding="utf-8")
    return len(svg)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for th in ("light", "dark"):
        print(th, build(th), "bytes")
