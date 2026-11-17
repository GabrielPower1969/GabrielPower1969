# github-profile

Source for the GitHub profile of GabrielPower1969: avatar, README banner, README text.
The published copy goes to the special repo `GabrielPower1969/GabrielPower1969` (README.md + assets/).

## Commands
- `python3 scripts/build_banner.py` → `assets/banner-light.svg`, `assets/banner-dark.svg`
- `python3 scripts/build_cards.py` → four achievement cards `assets/card-*-{light,dark}.svg` (facts in CARDS)
- Avatar: `swift scripts/cutout.swift` (Vision cut-out) → `python3 scripts/retouch.py` → `python3 scripts/build_avatar3d.py <photo> <cutout> "#002FA7" assets/avatar.png "#FFC400"` (upload by hand)
- `preview.html` = whole-page mockup (serve the folder over http; file:// is fine too)

## Invariants
- Palette: Klein Bauhaus (chosen 2026-11-18): ultramarine #002FA7 on white, #6B8CFF on GitHub dark, yellow #FFC400 as the only accent, ink #16181D, white.
- Design language: tanishmittal.com (white page, black compact type, thin rules, handwritten note);
  typewriter opening like onemorething.today / lovefrom.com; the final full stop is the blue guide dot
  (marekvataha.com's orange dot, recoloured).
- Text in the banner is converted to paths (GitHub's image proxy blocks web fonts in SVG).
- Avatar elements stay inside the inscribed circle (GitHub crops to a circle).
- Fonts: Newsreader + Caveat in fonts/ (OFL); Inter from ~/Library/Fonts.
