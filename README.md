# Pulse HQ — static site (GitHub Pages mirror)

A plain static, Google-indexable version of the Pulse HQ website: 9 linked pages
(index, case-study, start, showcase, how-it-works, dev-log, faq, terms, privacy)
plus the founders' personal dev log at dev-log-personal.html (public but
unlinked and noindex by the founder's ruling), one shared styles.css, images under assets/. No JavaScript view switching —
every page is real HTML at its own URL.

## Regenerate

The source of truth is the in-app showcase artifact
(`~/workspace/ts-spaces/pulse-hq-ai-workspace/index.html`). After it changes,
re-run:

    python3 generate.py

## Publish notes

- `sitemap.xml` currently uses the placeholder base
  `https://pulsehq-ai.github.io/pulse-hq-website/` — regenerate/replace it with the real base
  URL when the site is published, and add the matching `Sitemap:` line to
  `robots.txt` at the same time.
- Push the contents of this folder to the hosting repo and enable Pages
  (Settings → Pages → Deploy from a branch, root folder).
