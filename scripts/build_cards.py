#!/usr/bin/env python3
"""Build the four animated achievement cards (light + dark) for the profile README.
Same rules as the banner: text is converted to paths, palette is Klein Bauhaus.
Facts come from the fact-checked CV profile and the CITANZ branch data; edit CARDS to change them.
Usage: python3 scripts/build_cards.py   (run from the github-profile folder)"""
from build_banner import SERIF, SANS, glyphs, width, PRIMARY_L, PRIMARY_D, YELLOW, OUT

W, H = 620, 300

CARDS = [
    dict(key="community", label="COMMUNITY  /  CITANZ", big="12 events", unit="in 2026",
         lines=["Christchurch working-group lead, CITANZ",
                "Twice named best working-group member",
                "Leading the national website migration"], motif="circle"),
    dict(key="work", label="WORK  /  TRIMBLE", big="Edge AI", unit="+ Android platform",
         lines=["Systems Engineer at Trimble, since 2025",
                "Android platform: GMS, CTS, VTS, hardening",
                "Edge AI architecture, since 2026"], motif="bars"),
    dict(key="study", label="STUDY  /  DEGREES", big="2 × Master’s", unit="",
         lines=["M.Eng, AI for Computer Vision & Control · Illinois Tech 2026",
                "Master of Applied Data Science, Merit · Canterbury 2025",
                "B.Eng, Materials Science · Shandong Jianzhu 2015"], motif="quarter"),
    dict(key="craft", label="CRAFT  /  SINCE 2015", big="5 companies", unit="2 patents",
         lines=["Huawei → SMIC → bilibili → Qt → Trimble",
                "C/C++ · Python · QML · SQL · Android · embedded Linux",
                "One test cycle cut from 86.5 h to 0.5 h"], motif="steps"),
]


def path(font, text, size, x, y, fill, tracking=0.0):
    d = " ".join(g[1] for g in glyphs(font, text, size, x, y, tracking) if g[1])
    return f'<path d="{d}" fill="{fill}"/>'


def motif(kind, pri, ink):
    # Drawn in a 150x150 box whose top-right corner is the card's top-right corner.
    x0, y0 = W - 150, 0
    if kind == "circle":
        return [f'<circle cx="{x0+82}" cy="{y0+70}" r="52" fill="{pri}"/>',
                f'<circle cx="{x0+124}" cy="{y0+112}" r="18" fill="{YELLOW}"/>',
                f'<rect x="{x0+18}" y="{y0+128}" width="90" height="6" fill="{ink}"/>']
    if kind == "bars":
        return [f'<rect x="{x0+30}" y="{y0+22}" width="22" height="108" fill="{ink}"/>',
                f'<rect x="{x0+62}" y="{y0+50}" width="22" height="80" fill="{pri}"/>',
                f'<rect x="{x0+94}" y="{y0+78}" width="22" height="52" fill="{YELLOW}"/>']
    if kind == "quarter":
        return [f'<path d="M{W} 0 L{W-120} 0 A120 120 0 0 0 {W} 120 Z" fill="{pri}"/>',
                f'<path d="M{x0+20} {y0+134} L{x0+74} {y0+134} L{x0+47} {y0+88} Z" fill="{YELLOW}"/>',
                f'<rect x="{x0+20}" y="{y0+140}" width="54" height="5" fill="{ink}"/>']
    return [f'<rect x="{x0+22}" y="{y0+98}" width="34" height="34" fill="{ink}"/>',
            f'<rect x="{x0+56}" y="{y0+64}" width="34" height="68" fill="{pri}"/>',
            f'<rect x="{x0+90}" y="{y0+30}" width="34" height="102" fill="{pri}"/>',
            f'<circle cx="{x0+107}" cy="{y0+22}" r="12" fill="{YELLOW}"/>']


def build(card, theme):
    if theme == "light":
        bg, ink, muted, line, pri = "#FFFFFF", "#16181D", "#5D6573", "#D1D9E0", PRIMARY_L
    else:
        bg, ink, muted, line, pri = "#0D1117", "#EEF1F6", "#9AA3B2", "#30363D", PRIMARY_D
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="{bg}" stroke="{line}"/>']
    for i, sh in enumerate(motif(card["motif"], pri, ink)):
        b.append(f'<g class="s" style="animation-delay:{0.15 + i * 0.18:.2f}s">{sh}</g>')
    b.append(f'<g class="t" style="animation-delay:.1s">{path(SANS, card["label"], 11.5, 32, 44, muted, 1.5)}</g>')
    big = path(SERIF, card["big"], 58, 30, 122, pri)
    bw = width(SERIF, card["big"], 58)
    unit = path(SANS, card["unit"], 15, 30 + bw + 12, 122, muted) if card["unit"] else ""
    b.append(f'<g class="t" style="animation-delay:.3s">{big}{unit}</g>')
    b.append(f'<line class="r" x1="32" y1="150" x2="{W-32}" y2="150" stroke="{ink}" stroke-width="1"/>')
    for i, ln in enumerate(card["lines"]):
        assert width(SANS, ln, 15.5) < W - 64, ln
        y = 184 + i * 32
        b.append(f'<g class="t" style="animation-delay:{0.75 + i * 0.22:.2f}s">'
                 f'<circle cx="36" cy="{y-5}" r="3.5" fill="{pri}"/>{path(SANS, ln, 15.5, 50, y, ink)}</g>')
    css = (".t{opacity:0;animation:up .7s cubic-bezier(.2,.8,.2,1) both}"
           "@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
           ".s{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .8s cubic-bezier(.3,1.4,.5,1) both}"
           "@keyframes pop{from{opacity:0;transform:scale(.5)}to{opacity:1;transform:scale(1)}}"
           f".r{{stroke-dasharray:{W};stroke-dashoffset:{W};animation:draw .9s ease-out .5s both}}"
           "@keyframes draw{to{stroke-dashoffset:0}}"
           "@media (prefers-reduced-motion:reduce){*{animation:none!important}.t,.s{opacity:1}.r{stroke-dashoffset:0}}")
    label = f'{card["label"]}: {card["big"]} {card["unit"]}. ' + ". ".join(card["lines"])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="{label.replace("&", "and")}"><style>{css}</style>{"".join(b)}</svg>')
    (OUT / f'card-{card["key"]}-{theme}.svg').write_text(svg, encoding="utf-8")
    return len(svg)


if __name__ == "__main__":
    for c in CARDS:
        print(c["key"], [build(c, t) for t in ("light", "dark")])
