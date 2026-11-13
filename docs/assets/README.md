# 🖼️ Documentation images

The files in this directory illustrate K-LCR. They do not certify a
calculation or replace the [methodology](../methodology/README.md), which
holds the regulatory sources and the requirement map.

| File | Role |
| --- | --- |
| `site.css`, `architecture.svg` | Styles and architecture illustration of the [project website](../WEBSITE.md) |
| `K-LCR_social_preview.html` | Source of the social preview image |
| `K-LCR_social_preview.png` | Social preview image, also shown at the top of the README |

<a id="social-preview"></a>

## 🪧 Social preview

`K-LCR_social_preview.html` is the source of `K-LCR_social_preview.png`, the
repository's social preview image: 1280 x 640 px and under GitHub's 1 MB
limit.

- **Layout:** a dark grid background, the `VBA { }` badge, the title
  `K-LCR`, a two-line subtitle, a status pill and, on the right, a tilted
  dashboard of the calculation. The provenance of the layout is in
  [NOTICE.md](../../NOTICE.md).
- **Status:** the pill reads "Prototype 0.2.0" and the line beside it "LCR ·
  Excel / VBA · not validated" (#187). Update them with each release, or when
  the prototype is validated or a host run is recorded.
- **Figures:** every figure is a prototype output, not a validated result:

  | Panel | Figures | Source |
  | --- | --- | --- |
  | Scope TOTAL | LCR 194.8 %; liquidity buffer 3,209.6; excess liquid assets 382.3; outflows 3,173.6; capped inflows 1,525.9; net outflow 1,647.7 (EUR millions) | `compute()` of `tools/lcr_spec.py` on the demonstration data; the capped inflows are outflows minus net outflow |
  | Inflow cap | Recognised inflows rise with inflows up to 75 % of outflows | Art. 33(1) of `SRC-02`; the curve is a sketch, not data |
  | Profile | EU selected, Basel not implemented | [PROTOTYPE.md](../PROTOTYPE.md) |
  | Smoke test | LCR of EUR, USD and TOTAL, self-test 22/22 and 46 lines, each ticked | The LibreOffice run recorded in [PROTOTYPE.md](../PROTOTYPE.md): the VBA agreed with the Python model; it is not an Excel run and the model is not an independent oracle |

- **Fonts:** Barlow, Barlow Condensed and JetBrains Mono, under the SIL Open
  Font License 1.1, loaded from Google Fonts when the page is rendered; no
  font file is stored here. Rendering therefore needs the network.

Regenerate the PNG by opening the HTML in Chromium with a 1280 x 640 viewport
at device scale factor 1. Wait for the network to be idle and for
`document.fonts.ready`, check that the three families are loaded (a family
that fails to load falls back silently), and capture the viewport. The
current PNG was rendered on 2026-11-13 with Playwright 1.63.0 and its
Chromium build on Linux; its SHA-256 is
`004a9bd8850786436336e80fe6e8061514e746c23feea6a6391c849efe9e1df6`. A
different browser or font build gives a slightly different image. Then upload
the PNG in **Settings > General > Social preview**; GitHub has no API for this
setting.
