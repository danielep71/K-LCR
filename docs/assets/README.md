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
limit. Its palette and `K` mark are those of the website.

- **Content:** the project name, the method, the two profiles and the current
  status, "v0.2.0 · Prototype setup", with "EU prototype, not validated" and
  "Synthetic data only" (#185). Update the status with each release, or when
  the prototype is validated or a host run is recorded.
- **Figures:** the card states four requirements, not results:

  | Statement | EU, Delegated Regulation (EU) 2015/61 | Basel Framework, LCR, in force from 15 Dec 2019 |
  | --- | --- | --- |
  | Liquidity buffer over net liquidity outflows over 30 calendar days, at least 100 % | Art. 4(1) and (2) | LCR20.5 |
  | Inflows recognised up to 75 % of outflows | Art. 33(1) | LCR40.1 |
  | Level 2 at most 40 % and Level 2B at most 15 % of the buffer | Art. 17(1)(a) and (c) | LCR30.31 and LCR30.33 |

  The EU text sets a minimum of 60 % Level 1 assets, the complement of the
  40 % Level 2 maximum. I checked the EU figures against the stored copy of
  `SRC-02` and the Basel figures against the LCR20, LCR30 and LCR40 chapters
  on bis.org on 2026-11-04. Both apply after the adjustments each text
  describes, which the image does not show.
- **Fonts:** Inter and JetBrains Mono, both under the SIL Open Font License
  1.1, installed on the rendering machine. The HTML loads no external file;
  without these fonts the browser substitutes others and the layout shifts.

Regenerate the PNG by opening the HTML in Chromium with a 1280 x 640 viewport
at device scale factor 1, waiting for `document.fonts.ready`, and capturing
the viewport. The current PNG was rendered on 2026-11-13 with Playwright
1.63.0 and its Chromium build on Linux; its SHA-256 is
`e0884b6599660dc946a8b1bb19f2567a6c3cc292f56ea057c3f4142d379d6864`. The same
setup rendered the previous HTML to exactly the previous PNG. A different
browser or font build gives a slightly different image. Then upload
the PNG in **Settings > General > Social preview**; GitHub has no API for this
setting.
