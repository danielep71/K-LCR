# 🌐 Project website

The K-LCR landing page lives in `docs/index.html`, with styles in
`docs/assets/site.css` and its planned-architecture illustration in
`docs/assets/architecture.svg`. The page structure and CSS are adapted from
K-SFTs at `e6bae6df272083ba596c9eb866b14e6f9152bc15` under MPL-2.0.
K-LCR copy and the SVG describe the current setup scope.

## 📦 Publishing

The intended public URL is <https://danielep71.github.io/K-LCR/>.
K-LCR is public. Use Settings → Pages → **Deploy from a branch**,
branch **main**, folder **/docs**, matching the sibling project sites.
The empty `.nojekyll` file makes this a plain static site: no package
installation, JavaScript, analytics or external fonts are required.

Changes follow the active release branch, review and owner-authorized main
integration process in [Governance](GOVERNANCE.md). The live page updates only
after the reviewed files reach main and GitHub's Pages deployment succeeds.
Verify that deployment and the live page before claiming publication or
setting About → Website to the URL. A README link alone is not deployment
evidence. Do not change repository visibility as part of site maintenance.

## 🔎 Maintenance

- Keep scope, separate profile choices, maturity and evidence claims aligned
  with README, architecture and installation guidance. Avoid transient counts.
- Keep canonical, Open Graph and sitemap URLs aligned with the actual host.
- Link to rendered repository documentation on GitHub; plain static hosting
  does not convert the Markdown files into a documentation site.
- Preserve source attribution and the MPL-2.0 record in [NOTICE](../NOTICE.md).
- Run repository integrity, check HTML anchors and assets, parse SVG/sitemap,
  inspect desktop and narrow layouts and keyboard navigation, and verify the
  deployed page. Record candidate, deployment and live URL in #63.
