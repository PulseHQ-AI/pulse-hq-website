#!/usr/bin/env python3
"""
Generate the static, Google-indexable Pulse HQ site from the in-app
showcase artifact (the source of truth / "test dummy").

Source : ~/workspace/ts-spaces/pulse-hq-ai-workspace/index.html
         (single-page app; content lives in 8 <div class="view" id="view-*">)
Output : this folder (~/workspace/pulse-hq-pages/) — 9 static .html pages,
         styles.css, assets/, sitemap.xml, robots.txt, README.md.

The artifact itself is never modified. Re-run this script whenever the
artifact's content changes, then re-check the sitemap base URL at publish
time (BASE_PLACEHOLDER below is deliberately not a real domain yet).
"""

import html as html_lib
import os
import re
import shutil
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser("~/workspace/ts-spaces/pulse-hq-ai-workspace/index.html")
SRC_ASSETS = os.path.join(os.path.dirname(SRC), "assets")
OUT = HERE

BASE_PLACEHOLDER = "https://pulsehq-ai.github.io/pulse-hq-website/"

# (view id suffix, output file, page name for <title>; None = home page title)
VIEWS = [
    ("front", "index.html", None),
    ("showcase", "showcase.html", "Showcase"),
    ("how-it-works", "how-it-works.html", "How it works"),
    ("devlog", "dev-log.html", "Dev Log"),
    ("case-study", "case-study.html", "Case Study"),
    ("start", "start.html", "Start"),
    ("faq", "faq.html", "FAQ"),
    ("terms", "terms.html", "Terms"),
    ("privacy", "privacy.html", "Privacy"),
]
HOME_TITLE = "Pulse HQ — Bring your online presence to life"
HASH_TO_FILE = {view: fname for view, fname, _ in VIEWS}
NAV = [
    ("index.html", "Front page"),
    ("showcase.html", "Showcase"),
    ("how-it-works.html", "How it works"),
    ("start.html", "Start"),
    ("__sep__", ""),
    ("dev-log.html", "Dev Log"),
    ("case-study.html", "Case Study"),
]
# Live-build CSS additions (appended to styles.css at generation time):
# nav separator + two-column hero with the Pulse HQ logo (Ben, 2026-10-18).
LIVE_CSS = """
/* ---- Live-build additions: nav separator + hero media ---- */
.nav-sep { width: 1px; height: 22px; background: var(--panel-edge); margin: 0 9px; flex: none; }
.hero-media { max-width: 400px; width: 100%; margin-inline: auto; }
.hero-media img { display: block; width: 100%; height: auto; border-radius: 20px; border: 1px solid var(--panel-edge); }
.hero-top { display: flex; flex-direction: column; gap: 26px; }
@media (min-width: 760px) {
  .hero-top { flex-direction: row; align-items: center; gap: 36px; }
  .hero-head { flex: 1.08 1 0; }
  .hero-media { flex: 0.92 1 0; margin-inline: 0; }
}
"""
FB_URL = "https://www.facebook.com/profile.php?id=61595370269409"
FONT_CSS = (
    "https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;"
    "8..60,650;8..60,800&family=Public+Sans:wght@400;500;600;700;800&display=swap"
)
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


# --------------------------------------------------------------------------
# Extraction helpers
# --------------------------------------------------------------------------

class SpanFinder(HTMLParser):
    """Find the inner-content span of the element identified by `want(tag, attrs)`."""

    def __init__(self, text, want):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.want = want
        self.line_offsets = [0]
        for m in re.finditer("\n", text):
            self.line_offsets.append(m.end())
        self.target_depth = None
        self.inner_start = None
        self.inner_end = None

    def _offset(self):
        line, col = self.getpos()
        return self.line_offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if self.inner_end is not None:
            return
        if self.target_depth is None:
            if self.want(tag, dict(attrs)):
                self.target_depth = 1
                self.inner_start = self._offset() + len(self.get_starttag_text())
        elif tag not in VOID_TAGS:
            self.target_depth += 1

    def handle_startendtag(self, tag, attrs):
        pass  # self-closing: no depth change

    def handle_endtag(self, tag):
        if self.target_depth is None or self.inner_end is not None:
            return
        if tag in VOID_TAGS:
            return
        self.target_depth -= 1
        if self.target_depth == 0:
            self.inner_end = self._offset()


def extract_span(text, want):
    """Return (inner_html, method) for the first element matching `want`."""
    finder = SpanFinder(text, want)
    finder.feed(text)
    finder.close()
    if finder.inner_start is not None and finder.inner_end is not None:
        return text[finder.inner_start:finder.inner_end], "parser"
    return None, "failed"


def extract_view(text, view_id):
    inner, method = extract_span(
        text,
        lambda tag, attrs: tag == "div" and attrs.get("id") == f"view-{view_id}",
    )
    if inner is not None:
        return inner, method
    # Fallback: slice from the end of the view's start tag to the next view's
    # start tag (or </main> for the last view).
    m = re.search(r'<div class="view" id="view-%s"[^>]*>' % re.escape(view_id), text)
    if not m:
        return None, "failed"
    start = m.end()
    nxt = re.search(r'<div class="view" id="view-', text[start:])
    end = start + nxt.start() if nxt else text.index("</main>", start)
    return text[start:end], "boundary-fallback"


def extract_style(text):
    inner, _ = extract_span(text, lambda tag, attrs: tag == "style")
    return inner


# --------------------------------------------------------------------------
# Content transforms
# --------------------------------------------------------------------------

def clean_text(fragment):
    txt = re.sub(r"<[^>]+>", " ", fragment)
    txt = html_lib.unescape(txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    # Stripped inline tags can leave "word ." — reattach punctuation.
    txt = re.sub(r"\s+([.,;:!?])", r"\1", txt)
    return txt


def trim_description(txt, limit=170):
    if len(txt) <= limit:
        return txt
    cut = txt[:limit]
    dot = cut.rfind(". ")
    if dot > 80:
        return cut[: dot + 1]
    space = cut.rfind(" ")
    return cut[:space] + "…"


def make_description(inner_html):
    """First heading if it is substantive, else the first real lead paragraph."""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", inner_html, re.S)
    if h1:
        t = clean_text(h1.group(1))
        if 50 <= len(t) <= 175:
            return trim_description(t)
    for m in re.finditer(r"<p([^>]*)>(.*?)</p>", inner_html, re.S):
        attrs, body = m.group(1), m.group(2)
        if re.search(r'class="[^"]*(tagline|kicker|eyebrow|bar-label)', attrs):
            continue
        t = clean_text(body)
        if len(t) >= 40:
            return trim_description(t)
    if h1:
        return trim_description(clean_text(h1.group(1)))
    return ""


def transform(inner_html):
    # 1. Drop the per-view footer; a shared footer is emitted by the template.
    inner_html, n_footers = re.subn(r"<footer>.*?</footer>", "", inner_html, flags=re.S)
    # 2. Rewrite SPA hash links to real pages; drop the now-inert data-navlink.
    for hash_name, fname in HASH_TO_FILE.items():
        inner_html = inner_html.replace(f'href="#{hash_name}"', f'href="{fname}"')
    inner_html = re.sub(r'\s+data-navlink="[^"]*"', "", inner_html)
    # 3. Open every <details> so no content sits hidden without JS.
    inner_html = re.sub(
        r"<details(?![^>]*\bopen\b)([^>]*)>", r"<details open\1>", inner_html
    )
    return inner_html.strip(), n_footers


# --------------------------------------------------------------------------
# Live-build overrides (generated pages only; the dummy source is untouched)
# --------------------------------------------------------------------------

STRIPE_LINKS = [
    ("Standard Pilot", "$650", "https://buy.stripe.com/6oU5kFd8V2St1Ap8uq6kg03"),
    ("Website design and deploy", "$450", "https://buy.stripe.com/28E8wRc4R8cN4MB11Y6kg01"),
    ("Facebook page setup", "$200", "https://buy.stripe.com/6oUdRb8SF2Sta6VdOK6kg04"),
    ("Logo & branding mini-kit", "$175", "https://buy.stripe.com/bJe00lecZ8cNcf3bGC6kg05"),
    ("Batch of 14 posts", "$300", "https://buy.stripe.com/5kQ4gB1qdakVa6V9yu6kg06"),
    ("Research Report", "$250", "https://buy.stripe.com/bJeaEZ9WJeBb2EtbGC6kg02"),
]


def _buy_block():
    rows = "\n".join(
        '            <p style="display: flex; justify-content: space-between; '
        'align-items: center; gap: 14px; margin: 0;"><span><strong>%s</strong> '
        '&mdash; %s, one-time</span><a class="cta-btn" href="%s" target="_blank" '
        'rel="noopener noreferrer">Buy</a></p>' % (name, price, url)
        for name, price, url in STRIPE_LINKS
    )
    return (
        '        <div style="margin-top: 30px;">\n'
        '          <h3>Pay for a single service</h3>\n'
        '          <p style="max-width: 62ch;">Secure checkout by Stripe. You get '
        'a receipt by email, and we reply within one business day to start '
        'the work.</p>\n'
        '          <div style="display: grid; gap: 10px; max-width: 640px; '
        'margin-top: 14px;">\n'
        + rows + '\n'
        '          </div>\n'
        '        </div>\n'
    )


def apply_overrides(fname, inner_html):
    """Live-only overrides. Every pattern must fire exactly once; warn loudly
    otherwise so a silent miss can never ship."""

    def swap(old, new):
        nonlocal inner_html
        n = inner_html.count(old)
        if n != 1:
            print(f"WARNING override on {fname}: pattern found {n}x "
                  f"(expected 1): {old[:70]!r}", file=sys.stderr)
        inner_html = inner_html.replace(old, new)

    if fname == "index.html":
        month_box = (
            '      <!-- ================= ONE MONTH (live-build addition) '
            '================= -->\n'
            '      <section class="offer" aria-labelledby="fp-month-h">\n'
            '        <div class="offer-box">\n'
            '          <div>\n'
            '            <span class="kicker">One month</span>\n'
            '            <h2 id="fp-month-h">One month of Pulse HQ</h2>\n'
            '            <p class="offer-intro">This is <b>Core</b> — the '
            'full service, running month after month, once your setup is '
            'done:</p>\n'
            '            <ul class="offer-list">\n'
            '              <li><span class="tick" aria-hidden="true">✓</span>'
            '<span><b>Your website kept live</b> — and your Facebook page '
            'and Instagram, handled.</span></li>\n'
            '              <li><span class="tick" aria-hidden="true">✓</span>'
            '<span><b>Weekly posts researched and written</b> in your '
            'business\'s own voice.</span></li>\n'
            '              <li><span class="tick" aria-hidden="true">✓</span>'
            '<span><b>Nothing publishes without your approval</b> — the '
            'same rule as everything else at Pulse HQ.</span></li>\n'
            '              <li><span class="tick" aria-hidden="true">✓</span>'
            '<span><b>Month-to-month</b> — cancel with 30 days\' notice, '
            'no lock-in.</span></li>\n'
            '            </ul>\n'
            '          </div>\n'
            '          <div class="offer-side">\n'
            '            <span class="offer-spots">Core retainer</span>\n'
            '            <p class="offer-price">$1,450</p>\n'
            '            <p><b>Per month</b>, billed monthly.</p>\n'
            '            <p><b>Starts after setup</b> — $1,250 one time, '
            'minus any Test Run or Pilot credit you\'ve already paid.</p>\n'
            '            <p>Full-service agencies typically charge more '
            'than this for social media alone.</p>\n'
            '          </div>\n'
            '        </div>\n'
            '      </section>\n\n'
        )
        swap(
            '<!-- ================= CHERRY-PICK SINGLES ================= -->',
            month_box
            + '<!-- ================= CHERRY-PICK SINGLES ================= -->',
        )
        # Hero restructure (Ben, 2026-10-18): headline + logo share ONE
        # div (.hero-top, flex, centered); paragraphs run below full width.
        swap(
            '<div class="hero-grid">\n'
            '          <div>\n'
            '            <h1 style="max-width: 21ch;">',
            '<div class="hero-grid">\n'
            '          <div class="hero-top">\n'
            '            <div class="hero-head">\n'
            '            <h1 style="max-width: 21ch;">',
        )
        swap(
            '</svg>\n'
            '            <p class="lede">',
            '</svg>\n'
            '            </div>\n'
            '            <div class="hero-media"><img '
            'src="assets/pulse-logo.jpg" alt="Pulse HQ logo — a neon pulse '
            'line on deep blue" /></div>\n'
            '          </div>\n'
            '          <div class="hero-body">\n'
            '            <p class="lede">',
        )
    elif fname == "start.html":
        swap(
            '<p class="start-note">A preview of the intake form — the button '
            'below opens the real one.</p>',
            '<p class="start-note">A preview of the intake form — for now, '
            'the button below starts your intake by email.</p>',
        )
        swap(
            '<a class="cta-btn" href="start.html">Open the intake form</a>',
            '<a class="cta-btn" href="mailto:getpulsehq@proton.me">'
            'Email us to start</a>',
        )
        swap(
            '<p style="margin-top: 22px; max-width: 62ch;">The Founding Test '
            'Run starts with the form above, not a buy button — there are '
            'only two spots, and Ben replies personally. Fixed-price singles '
            'and the Standard Pilot will carry checkout buttons on this '
            'page when they go live.</p>',
            _buy_block()
            + '        <p style="margin-top: 22px; max-width: 62ch;">The '
            'Founding Test Run starts with the form above, not a buy '
            'button — there are only two spots, and we reply '
            'personally.</p>',
        )
    elif fname == "faq.html":
        swap(
            '<p>By e-transfer or PayPal. The Test Run, Pilot, and Setup are '
            'paid before work begins; the Core retainer is billed monthly.</p>',
            '<p>By card through Stripe&rsquo;s secure checkout — the '
            'payment links are on the <a href="start.html">Start page</a> '
            '— or by PayPal or e-transfer. The Test Run, Pilot, and Setup '
            'are paid before work begins; the Core retainer is billed '
            'monthly.</p>',
        )
        new_entry = (
            '<details open>\n'
            '                <summary>How do you cost less than an '
            'agency?</summary>\n'
            '                <p>Structure. An agency&rsquo;s price carries '
            'account managers, a sales team, and an office lease between '
            'you and the people doing the work. Pulse HQ has none of that '
            'layer — you pay for finished, researched work and one '
            'accountable approval step, not overhead. Don&rsquo;t take '
            'our word for it: search social media management and compare '
            'the first fifteen results on Google with what&rsquo;s '
            'included here.</p>\n'
            '              </details>\n'
            '              '
        )
        swap(
            '<details open>\n'
            '                <summary>How much does done-for-you social '
            'media cost?</summary>',
            new_entry
            + '<details open>\n'
            '                <summary>How much does done-for-you social '
            'media cost?</summary>',
        )
        swap(
            'Our packages are built for Facebook pages — ask us about '
            'other platforms.',
            'Our Core service covers Facebook and Instagram — every post '
            'is written once and adapted for both. Ask us about other '
            'platforms.',
        )
        swap(
            'Our packages are built for Facebook pages. Ask us about '
            'other platforms.',
            'Facebook and Instagram, on the Core retainer — every post '
            'is written once and adapted for both. Ask us about other '
            'platforms.',
        )
    elif fname == "terms.html":
        swap(
            'Payment is by e-transfer or PayPal.',
            'Payment is by card through Stripe&rsquo;s secure checkout, '
            'or by PayPal or e-transfer.',
        )
        swap('Contact: Ben from Pulse HQ', 'Contact: Pulse HQ')
    elif fname == "privacy.html":
        swap('Contact: Ben from Pulse HQ', 'Contact: Pulse HQ')
    elif fname == "case-study.html":
        swap("Ben's own page", "Pulse HQ's own page")
    return inner_html


# --------------------------------------------------------------------------
# Page chrome (shared header / footer)
# --------------------------------------------------------------------------

def build_header(current_file):
    links = []
    for fname, label in NAV:
        if fname == "__sep__":
            links.append('        <span class="nav-sep" aria-hidden="true"></span>')
            continue
        current = ' aria-current="page"' if fname == current_file else ""
        links.append(f'        <a class="nav-link" href="{fname}"{current}>{label}</a>')
    nav_links = "\n".join(links)
    return f"""    <header class="site-nav">
      <nav class="wrap nav-in" aria-label="Site">
        <a class="nav-brand" href="index.html"><span class="brand-name">Pulse <span class="hq">HQ</span></span><span class="nav-tagline">Bring your online presence to life</span></a>
{nav_links}
        <a class="nav-fb" href="{FB_URL}" target="_blank" rel="noopener noreferrer">Facebook</a>
      </nav>
    </header>"""


def build_footer():
    return """    <footer>
      <div class="wrap">
        <span>Pulse HQ. Content, research &amp; design: drafted by AI, approved by a human.</span>
        <div class="footer-links">
          <span><a href="faq.html">FAQ</a> · <a href="how-it-works.html">How it works</a> · <a href="terms.html">Terms</a> · <a href="privacy.html">Privacy</a></span>
          <span>Pulse HQ · <a href="mailto:getpulsehq@proton.me">getpulsehq@proton.me</a> · We reply within one business day</span>
        </div>
      </div>
    </footer>"""


def build_page(view_id, fname, page_name, inner_html):
    title = HOME_TITLE if page_name is None else f"Pulse HQ — {page_name}"
    desc = make_description(inner_html)
    esc_title = html_lib.escape(title, quote=True)
    esc_desc = html_lib.escape(desc, quote=True)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="color-scheme" content="light dark" />
    <meta name="description" content="{esc_desc}" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{esc_title}" />
    <meta property="og:description" content="{esc_desc}" />
    <meta property="og:image" content="{BASE_PLACEHOLDER}assets/home-preview.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{esc_title}" />
    <meta name="twitter:description" content="{esc_desc}" />
    <meta name="twitter:image" content="{BASE_PLACEHOLDER}assets/home-preview.png" />
    <link rel="icon" href="data:," />
    <title>{html_lib.escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="{FONT_CSS}" rel="stylesheet" />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
{build_header(fname)}

    <main>
      <div class="view" id="view-{view_id}">
{inner_html}
      </div>
    </main>

{build_footer()}
  </body>
</html>
"""


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    with open(SRC, encoding="utf-8") as f:
        source = f.read()

    # --- clean previous build outputs (never this script) ---
    for fname, *_ in [(v[1],) for v in VIEWS]:
        p = os.path.join(OUT, fname)
        if os.path.exists(p):
            os.remove(p)
    for extra in ("styles.css", "sitemap.xml", "robots.txt", "README.md"):
        p = os.path.join(OUT, extra)
        if os.path.exists(p):
            os.remove(p)
    for d in ("assets", "img"):
        p = os.path.join(OUT, d)
        if os.path.isdir(p):
            shutil.rmtree(p)

    # --- styles.css: artifact CSS with the view-hiding rule neutralized ---
    css = extract_style(source)
    if css is None:
        print("ERROR: could not extract <style> from source", file=sys.stderr)
        return 1
    css, n = re.subn(
        r"\.view\[hidden\]\s*\{\s*display:\s*none;\s*\}",
        "/* Static build: the .view[hidden] rule is removed — every page "
        "shows its own view; nothing is hidden behind JS view switching. */",
        css,
    )
    print(f"styles.css: neutralized .view[hidden] rule ({n} replacement)")
    with open(os.path.join(OUT, "styles.css"), "w", encoding="utf-8") as f:
        f.write(css.strip() + "\n" + LIVE_CSS)

    # --- pages ---
    # og:image: a screenshot of the front page itself, kept in site-assets/
    referenced_assets = {"assets/home-preview.png", "assets/pulse-logo.jpg"}
    for view_id, fname, page_name in VIEWS:
        inner, method = extract_view(source, view_id)
        if inner is None:
            print(f"ERROR: could not extract view '{view_id}'", file=sys.stderr)
            return 1
        inner, n_footers = transform(inner)
        inner = apply_overrides(fname, inner)
        for ref in re.findall(r'(?:src|href)="(assets/[^"]+)"', inner):
            referenced_assets.add(ref)
        page = build_page(view_id, fname, page_name, inner)
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(page)
        print(f"{fname}: extracted via {method}, stripped {n_footers} footer(s), "
              f"{len(page)} bytes")

    # --- copy referenced assets ---
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    missing = []
    for ref in sorted(referenced_assets):
        src_path = os.path.join(os.path.dirname(SRC), ref)
        if not os.path.exists(src_path):
            alt = os.path.join(HERE, "site-assets", os.path.basename(ref))
            if os.path.exists(alt):
                src_path = alt
        dst_path = os.path.join(OUT, ref)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
        else:
            missing.append(ref)
    print(f"assets: copied {len(referenced_assets) - len(missing)} file(s)")
    if missing:
        print(f"WARNING missing assets: {missing}", file=sys.stderr)

    # --- sitemap.xml (placeholder base; regenerated with real base at publish) ---
    urls = []
    for _, fname, _ in VIEWS:
        loc = BASE_PLACEHOLDER if fname == "index.html" else BASE_PLACEHOLDER + fname
        urls.append(f"  <url><loc>{loc}</loc></url>")
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    # --- robots.txt (base URL is the live one; Sitemap line included) ---
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: "
                + BASE_PLACEHOLDER + "sitemap.xml\n")

    # --- README ---
    readme = """# Pulse HQ — static site (GitHub Pages mirror)

A plain static, Google-indexable version of the Pulse HQ website: 9 pages
(index, case-study, start, showcase, how-it-works, dev-log, faq, terms, privacy),
one shared styles.css, images under assets/. No JavaScript view switching —
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
"""
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    print("done: 9 pages + styles.css + assets/ + sitemap.xml + robots.txt + README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
