#!/usr/bin/env python3
"""
Canary vault builder — converts markdown vault to clean HTML site.
Usage: python3 build.py [--site-title "Title"] [--out _site]
"""
import os, re, sys, shutil, argparse, html as htmllib
from pathlib import Path

# ── pip install markdown pyyaml ───────────────────────────────────────────────
import markdown as md_lib
import yaml

# ─── CLI ─────────────────────────────────────────────────────────────────────
p = argparse.ArgumentParser()
p.add_argument("--site-title", default="Canary Retail Brain")
p.add_argument("--out", default="_site")
p.add_argument("--root", default=".")
args = p.parse_args()

ROOT   = Path(args.root).resolve()
OUT    = Path(args.out)
TITLE  = args.site_title

SKIP_DIRS  = {'.git','.github','.obsidian','quartz','node_modules','_site','static'}
SKIP_FILES = {'ACKNOWLEDGMENT.md','CONTRIBUTING.md','NOTICE.md','SECURITY.md','README.md'}

# ─── MARKDOWN CONVERTER ──────────────────────────────────────────────────────
MD = md_lib.Markdown(extensions=[
    'tables','fenced_code','attr_list','def_list','footnotes',
    'toc','md_in_html',
])

def parse_frontmatter(text):
    if not text.startswith('---'):
        return {}, text
    end = text.find('\n---', 3)
    if end == -1:
        return {}, text
    fm_raw = text[3:end].strip()
    body   = text[end+4:].lstrip('\n')
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except Exception:
        fm = {}
    return fm, body

def md_to_html(text):
    # Convert Obsidian [[wikilinks]] → plain text (link targets are ambiguous cross-vault)
    text = re.sub(r'\[\[([^\]|]+)\|?([^\]]*)\]\]',
                  lambda m: m.group(2) or m.group(1), text)
    # Convert bare > [!NOTE] callout syntax to blockquote
    text = re.sub(r'> \[!(NOTE|WARNING|INFO|TIP)\]', r'> **\1:**', text, flags=re.I)
    MD.reset()
    return MD.convert(text)

# ─── NAV TREE ────────────────────────────────────────────────────────────────
def collect_pages(root: Path):
    """Return list of (rel_path, fm, title) for all .md files."""
    pages = []
    for path in sorted(root.rglob('*.md')):
        rel = path.relative_to(root)
        if any(p in SKIP_DIRS for p in rel.parts):
            continue
        if rel.name in SKIP_FILES:
            continue
        fm, body = parse_frontmatter(path.read_text(encoding='utf-8'))
        title = fm.get('title') or path.stem.replace('-',' ').replace('_',' ').title()
        pages.append((rel, fm, title))
    return pages

def get_nav_order(pages):
    """Read nav_order list from Home.md frontmatter if present."""
    for rel, fm, title in pages:
        if rel.name in ('Home.md', 'index.md') and len(rel.parts) == 1:
            order = fm.get('nav_order', [])
            if isinstance(order, list):
                return order
    return []

def build_sidebar(pages, current_rel):
    """Build sidebar HTML grouped by top-level directory."""
    groups = {}
    for rel, fm, title in pages:
        parts = rel.parts
        group = parts[0] if len(parts) > 1 else '.'
        groups.setdefault(group, []).append((rel, fm, title))

    nav_order = get_nav_order(pages)

    def sort_key(g):
        if g == '.':
            return (-1, '')
        if nav_order and g in nav_order:
            return (nav_order.index(g), g.lower())
        return (len(nav_order) + 1, g.lower())

    def item_sort_key(item):
        rel, fm, title = item
        order = fm.get('nav_order')
        if isinstance(order, int):
            return (order, str(rel).lower())
        return (9999, str(rel).lower())

    html = ['<nav class="sb-nav">']

    # Home link
    home_active = ' on' if str(current_rel) in ('index.md','Home.md') else ''
    html.append(f'  <a href="/" class="sb-home{home_active}">Home</a>')

    for group in sorted(groups.keys(), key=sort_key):
        items = sorted(groups[group], key=item_sort_key)
        group_label = group.replace('-',' ').replace('_',' ').title() if group != '.' else 'Pages'
        if group == '.':
            # Root files — show inline without group header
            for rel, fm, title in items:
                if rel.name in ('Home.md', 'index.md'):
                    continue
                href = '/' + str(rel.with_suffix('.html'))
                active = ' on' if rel == current_rel else ''
                html.append(f'  <a href="{href}" class="sb-a{active}">{title}</a>')
        else:
            html.append(f'  <div class="sb-group">')
            html.append(f'    <span class="sb-lbl">{group_label}</span>')
            for rel, fm, title in items:
                href = '/' + str(rel.with_suffix('.html'))
                active = ' on' if rel == current_rel else ''
                # shorten title for sidebar
                short = title if len(title) < 40 else title[:38] + '…'
                html.append(f'    <a href="{href}" class="sb-a{active}">{short}</a>')
            html.append('  </div>')

    html.append('</nav>')
    return '\n'.join(html)

# ─── HTML TEMPLATE ───────────────────────────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:'Inter',system-ui,sans-serif;font-size:16px;line-height:1.75;
  color:#1C3A2B;background:#F5F0E8;-webkit-font-smoothing:antialiased}
a{color:#2A5240;text-decoration:none;border-bottom:1px solid rgba(28,58,43,.15);transition:color .15s,border-color .15s}
a:hover{color:#BF8700;border-bottom-color:#BF8700}
h1,h2,h3,h4,h5{font-family:'Source Serif 4',Georgia,serif;color:#1C3A2B;margin:0 0 .5em;line-height:1.2}
h1{font-size:clamp(26px,4vw,42px);font-weight:700;letter-spacing:-.02em;margin-bottom:.75em}
h2{font-size:clamp(20px,3vw,28px);font-weight:600;margin-top:2em;padding-top:1em;border-top:1px solid #D0C9BB}
h3{font-size:18px;font-weight:600;margin-top:1.5em}
h4{font-size:15px;font-weight:600;margin-top:1em;color:#3A3A3A}
p{margin:0 0 1em}
ul,ol{margin:0 0 1em 1.4em;padding:0}
li{margin-bottom:.25em}
code{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:.88em;
  padding:2px 5px;background:rgba(76,175,125,.12);border-radius:3px;color:#1C3A2B}
pre{background:#1C3A2B;color:#d4f1e4;border-radius:6px;padding:20px 22px;overflow-x:auto;
  margin:0 0 1.5em;font-size:.875em;line-height:1.6}
pre code{background:none;padding:0;color:inherit;font-size:inherit}
blockquote{margin:0 0 1em;padding:.75em 1.25em;border-left:3px solid #BF8700;
  background:rgba(191,135,0,.08);border-radius:0 4px 4px 0}
blockquote p{margin:0;color:#3A3A3A}
table{width:100%;border-collapse:collapse;margin-bottom:1.5em;font-size:14px}
thead tr{background:#1C3A2B;color:#F5F0E8}
thead th{padding:10px 14px;text-align:left;font-size:11px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase}
tbody tr{border-bottom:1px solid #E5E0D4}
tbody tr:nth-child(even){background:rgba(28,58,43,.03)}
td{padding:9px 14px;vertical-align:top;line-height:1.45}
td code{font-size:.82em}
hr{border:none;border-top:1px solid #D0C9BB;margin:2em 0}
/* NAV */
.top-nav{background:#1C3A2B;height:56px;position:sticky;top:0;z-index:50;
  border-bottom:1px solid rgba(0,0,0,.2);display:flex;align-items:center;padding:0 24px;gap:12px}
.top-nav .wordmark{font-family:'Source Serif 4',Georgia,serif;font-style:italic;
  font-size:19px;font-weight:600;color:#F5F0E8;border:none;white-space:nowrap}
.top-nav .slash{color:rgba(245,240,232,.3);font-size:14px}
.top-nav .site-name{font-size:13px;color:rgba(245,240,232,.6);letter-spacing:.04em;border:none}
.top-nav .nav-right{margin-left:auto;display:flex;gap:16px;align-items:center}
.top-nav .nav-right a{color:rgba(245,240,232,.6);font-size:13px;border:none}
.top-nav .nav-right a:hover{color:#E8A800}
.top-nav .cta{border:1px solid #BF8700;color:#E8A800;padding:6px 14px;border-radius:4px;
  font-size:12px;font-weight:600;background:transparent}
.top-nav .cta:hover{background:#BF8700;color:#1C3A2B;border:none}
/* LAYOUT */
.shell{display:grid;grid-template-columns:240px 1fr;min-height:calc(100vh - 56px)}
@media(max-width:900px){.shell{grid-template-columns:1fr}}
/* SIDEBAR */
.sidebar{background:#1C3A2B;padding:28px 16px;position:sticky;top:56px;
  height:calc(100vh - 56px);overflow-y:auto;border-right:1px solid rgba(0,0,0,.2)}
.sidebar::-webkit-scrollbar{width:4px}
.sidebar::-webkit-scrollbar-thumb{background:rgba(245,240,232,.15);border-radius:3px}
@media(max-width:900px){.sidebar{position:static;height:auto;border-right:none;
  border-bottom:1px solid rgba(0,0,0,.2)}}
.sb-nav{display:flex;flex-direction:column;gap:2px}
.sb-home{display:block;color:rgba(245,240,232,.9);font-size:13px;font-weight:600;
  border:none;padding:6px 8px;border-radius:4px;margin-bottom:12px}
.sb-home:hover,.sb-home.on{background:rgba(191,135,0,.2);color:#E8A800;border:none}
.sb-group{margin-bottom:14px}
.sb-lbl{display:block;font-size:10px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;
  color:rgba(245,240,232,.38);margin-bottom:5px;padding-left:8px}
.sb-a{display:block;padding:5px 8px;border-radius:4px;color:rgba(245,240,232,.7);
  font-size:13px;border:none;transition:background .1s,color .1s}
.sb-a:hover,.sb-a.on{background:rgba(191,135,0,.18);color:#E8A800;border:none}
/* MAIN */
.main{padding:44px 52px 80px;min-width:0;max-width:860px}
@media(max-width:900px){.main{padding:28px 20px 60px}}
.breadcrumb{font-size:12px;color:#6B6B6B;margin-bottom:24px;display:flex;gap:6px;
  align-items:center;flex-wrap:wrap}
.breadcrumb a{color:#6B6B6B;font-size:12px}
.breadcrumb a:hover{color:#BF8700}
.breadcrumb .sep{color:#C0BAB0}
.page-meta{font-size:12px;color:#9A958E;margin-bottom:28px;padding-bottom:20px;
  border-bottom:1px solid #E5E0D4}
/* FOOTER */
.page-footer{margin-top:56px;padding-top:20px;border-top:1px solid #D0C9BB;
  font-size:12px;color:#9A958E;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
"""

def build_top_nav_links(pages):
    """Return top-level directory links pointing to the first page in each dir."""
    dirs = {}
    for rel, fm, title in pages:
        if len(rel.parts) > 1:
            d = rel.parts[0]
            if d not in dirs:
                label = d.replace('-',' ').replace('_',' ').title()
                out = rel.with_suffix('.html')
                if rel.name in ('index.md', 'Home.md'):
                    out = rel.parent / 'index.html'
                dirs[d] = (f'/{out}', label)
    # Up to 3 links — pick shortest label names
    items = sorted(dirs.values(), key=lambda x: len(x[1]))[:3]
    return ''.join(f'<a href="{href}">{label}</a>' for href, label in items)

def page_html(title, body_html, sidebar_html, breadcrumb_html, site_title, fm, nav_links=''):
    date = fm.get('date','')
    meta = f'<div class="page-meta">{htmllib.escape(str(date))}</div>' if date else ''
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{htmllib.escape(title)} · {htmllib.escape(site_title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<nav class="top-nav">
  <a href="/" class="wordmark">Canary</a>
  <span class="slash">/</span>
  <span class="site-name">{htmllib.escape(site_title)}</span>
  <div class="nav-right">
    {nav_links}
    <a href="mailto:canary@growdirect.io" class="cta">Contact</a>
  </div>
</nav>
<div class="shell">
  <aside class="sidebar">{sidebar_html}</aside>
  <main class="main">
    {breadcrumb_html}
    {meta}
    {body_html}
    <div class="page-footer">
      <span>{htmllib.escape(site_title)} · GrowDirect LLC</span>
      <span>canary@growdirect.io</span>
    </div>
  </main>
</div>
</body>
</html>"""

def breadcrumb(rel: Path):
    parts = rel.parts
    if len(parts) <= 1:
        return ''
    crumbs = ['<div class="breadcrumb"><a href="/">Home</a>']
    for i, part in enumerate(parts[:-1]):
        label = part.replace('-',' ').replace('_',' ').title()
        href  = '/' + '/'.join(parts[:i+1]) + '/'
        crumbs.append(f'<span class="sep">›</span><a href="{href}">{htmllib.escape(label)}</a>')
    crumbs.append('</div>')
    return '\n'.join(crumbs)

# ─── BUILD ───────────────────────────────────────────────────────────────────
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

# Copy static assets
static_src = ROOT / 'static'
if static_src.is_dir():
    shutil.copytree(static_src, OUT / 'static')

pages = collect_pages(ROOT)
nav_links = build_top_nav_links(pages)
print(f"Building {len(pages)} pages → {OUT}/")

for rel, fm, page_title in pages:
    src_path = ROOT / rel
    body_text = src_path.read_text(encoding='utf-8')
    _, body_text = parse_frontmatter(body_text)

    body_html  = md_to_html(body_text)
    sb_html    = build_sidebar(pages, rel)
    bc_html    = breadcrumb(rel)

    # Determine output path
    if rel.name in ('index.md', 'Home.md'):
        out_rel = rel.parent / 'index.html'
    else:
        out_rel = rel.with_suffix('.html')

    out_path = OUT / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)

    html = page_html(page_title, body_html, sb_html, bc_html, TITLE, fm, nav_links)
    out_path.write_text(html, encoding='utf-8')
    print(f"  {rel} → {out_rel}")

# Write CNAME
cname_src = ROOT / 'CNAME'
if cname_src.exists():
    shutil.copy(cname_src, OUT / 'CNAME')

print(f"\nDone. {len(pages)} pages in {OUT}/")
