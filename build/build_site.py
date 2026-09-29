"""Build the portfolio site from content.json.

Usage:  python build_site.py
Writes ../index.html (complete page for hosting) and ../artifact.html (body fragment).
To update the site, edit content.json and run this script again.

The site is a single file with a home menu and separate pages selected by the URL hash
(#publications, #abstracts, #news, ...). Light mode is the default; the theme toggle
in the header stores the visitor's choice in localStorage.

Set SITE_URL to the final public address (for example "https://najamgohar.com")
once the site is hosted; the build then emits absolute Open Graph and JSON-LD URLs.
"""
import json
import os
from collections import OrderedDict
from html import escape

SITE_URL = "https://nvmnjm.github.io"
FONT_CSS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

with open(os.path.join(HERE, "content.json"), encoding="utf-8") as f:
    C = json.load(f)

PMID = {}
ids_path = os.path.join(HERE, "pubmed_ids.json")
if os.path.exists(ids_path):
    with open(ids_path, encoding="utf-8") as f:
        for r in json.load(f):
            PMID[r["doi"].lower()] = (r.get("pmid"), r.get("pmcid"))


def e(s):
    return escape(str(s), quote=True)


def authors_html(s):
    return e(s).replace("Gohar N", "<strong>Gohar N</strong>")


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


WORDS = {0: "None", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve"}


def word(n):
    return WORDS.get(n, str(n))


# ---------------------------------------------------------------- icons
ICONS = {
    "email": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6.5A2.5 2.5 0 0 1 5.5 4h13A2.5 2.5 0 0 1 21 6.5v11a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z"/><path d="m3.5 7 8.5 6 8.5-6"/></svg>',
    "yale": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" aria-hidden="true" class="fill"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0z"/></svg>',
    "scholar": '<svg viewBox="0 0 24 24" aria-hidden="true" class="fill"><path d="M5.242 13.769 0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z"/></svg>',
    "orcid": '<svg viewBox="0 0 24 24" aria-hidden="true" class="fill"><path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z"/></svg>',
}
ICON_EXT = '<svg viewBox="0 0 24 24" aria-hidden="true" class="ext"><path d="M7 17 17 7M8 7h9v9"/></svg>'
ICON_ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true" class="arrow"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
ICON_SEARCH = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
ICON_SUN = '<svg viewBox="0 0 24 24" aria-hidden="true" class="sun"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
ICON_MOON = '<svg viewBox="0 0 24 24" aria-hidden="true" class="moon"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg>'

# ---------------------------------------------------------------- derived data
groups = {g["key"]: g for g in C["groups"]}
counts = {k: len(g["items"]) for k, g in groups.items()}
n_articles = counts["research"] + counts["reviews"] + counts["preprints"]
abstracts = groups["abstracts"]["items"]
n_first = sum(1 for a in abstracts if a.get("role", "").lower().startswith("first"))
years = OrderedDict()
for a in abstracts:
    years.setdefault(a["year"], []).append(a)
years = OrderedDict(sorted(years.items(), key=lambda kv: kv[0], reverse=True))
news_sorted = sorted(C.get("news", []), key=lambda n: n.get("sort", ""), reverse=True)
ABSTRACT_SCOPE = "Abstracts presented at national and international meetings in cardiology, hematology, oncology, gastroenterology, and other specialties."

PAGES = [
    # route, nav label, page title, tile description, tile meta
    ("profile", "Profile", "Profile", "Background and research interests.", plural(len(C["interests"]), "research interest")),
    ("experience", "Experience", "Experience", "Yale postdoctoral fellowship, research collaborations, clinical training, and education.", f"{plural(len(C['experience']), 'role')} · {plural(len(C['education']), 'degree')}"),
    ("publications", "Publications", "Publications", "Peer-reviewed articles, systematic reviews, accepted manuscripts, and preprints, with DOI and PubMed links where available.", plural(n_articles, "article")),
    ("abstracts", "Abstracts", "Conference Abstracts", ABSTRACT_SCOPE, f"{plural(counts['abstracts'], 'abstract')} · {n_first} as first author"),
    ("news", "News", "News", "Announcements and updates.", plural(len(news_sorted), "update")),
    ("skills", "Skills", "Skills and Software", "Analysis tools, data platforms, methods, and an open-source project.", f"{plural(len(C['skills']), 'area')} · {plural(len(C.get('software', [])), 'project')}"),
    ("service", "Service", "Service and Awards", "Peer review, mentorship, leadership, and distinctions.", f"{plural(len(C['service']), 'service role')} · {plural(len(C.get('awards', [])), 'award')}"),
    ("contact", "Contact", "Contact", "Email and professional profiles.", f"Email and {plural(len(C['socials']) - 1, 'profile')}"),
]
ROUTES = ["home"] + [p[0] for p in PAGES]
TITLES = {p[0]: p[2] for p in PAGES}


# ---------------------------------------------------------------- shared pieces
def nav_html():
    items = ['<li><a href="#home" data-route="home">Home</a></li>']
    for route, label, *_ in PAGES:
        items.append(f'<li><a href="#{route}" data-route="{route}">{e(label)}</a></li>')
    return (
        '<header class="nav"><div class="wrap nav-inner">'
        f'<a class="brand" href="#home">{e(C["name"])}</a>'
        '<nav aria-label="Pages"><ul>' + "".join(items) + "</ul></nav>"
        '<button class="theme" id="theme-toggle" type="button" aria-label="Dark mode" aria-pressed="false" title="Toggle dark mode">'
        + ICON_SUN + ICON_MOON + "</button>"
        "</div></header>"
    )


def social_links_html():
    out = []
    for s in C["socials"]:
        ext = "" if s["url"].startswith("mailto:") else ' target="_blank" rel="noopener"'
        out.append(f'<li><a class="social" href="{e(s["url"])}"{ext}>{ICONS[s["key"]]}<span>{e(s["label"])}</span></a></li>')
    return '<ul class="socials">' + "".join(out) + "</ul>"


def view_open(route, title, lead=""):
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    return (
        f'<section class="view page" id="{route}" data-view="{route}" aria-labelledby="h-{route}">'
        '<div class="wrap page-wrap">'
        f'<header class="page-head"><a class="crumb" href="#home">{ICON_ARROW}Home</a>'
        f'<h1 id="h-{route}" tabindex="-1">{e(title)}</h1>{lead_html}</header>'
        '<div class="page-body">'
    )


VIEW_CLOSE = "</div></div></section>"


def sub(title, first=False):
    return f'<h2 class="{"sub first" if first else "sub"}">{e(title)}</h2>'


# ---------------------------------------------------------------- home
def home_html():
    tiles = []
    for i, (route, label, title, desc, meta) in enumerate(PAGES):
        tiles.append(
            f'<li style="--i:{i}"><a class="tile" href="#{route}">'
            f'<span class="tile-top"><span class="tile-title">{e(title)}</span>{ICON_ARROW}</span>'
            f'<span class="tile-desc">{e(desc)}</span>'
            f'<span class="tile-meta">{e(meta)}</span></a></li>'
        )
    return (
        '<section class="view home" id="home" data-view="home" aria-labelledby="h-home">'
        '<div class="wrap">'
        '<div class="hero-grid"><div class="hero-text">'
        f'<h1 id="h-home" tabindex="-1" style="--i:0">{e(C["name"])}<span class="cred"><span class="comma">, </span>{e(C["credentials"])}</span></h1>'
        f'<p class="hero-role" style="--i:1">{e(C["role"])}<br>{e(C["institution"])} · {e(C["location"])}</p>'
        f'<p class="tagline" style="--i:2">{e(C["tagline"])}</p>'
        '<div style="--i:3">' + social_links_html() + "</div>"
        "</div>"
        '<figure class="portrait"><img src="assets/najam-gohar.jpg" alt="Portrait of Najam Gohar" width="762" height="974" loading="eager" decoding="async"></figure>'
        "</div>"
        '<ul class="tiles" aria-label="Sections">' + "".join(tiles) + "</ul>"
        "</div></section>"
    )


# ---------------------------------------------------------------- pages
def profile_html():
    chips = "".join(f"<li>{e(i)}</li>" for i in C["interests"])
    return view_open("profile", "Profile") + f'<p class="prose">{e(C["profile"])}</p>' + sub("Research interests") + f'<ul class="chips">{chips}</ul>' + VIEW_CLOSE


def entry_html(org, role, dates, location="", bullets=None, detail=""):
    parts = ['<article class="entry">', '<div class="entry-head">', f'<div><h3>{e(org)}</h3><p class="role">{e(role)}</p>']
    if location:
        parts.append(f'<p class="loc">{e(location)}</p>')
    parts.append("</div>")
    parts.append(f'<p class="dates">{e(dates)}</p></div>')
    if detail:
        parts.append(f'<p class="detail">{e(detail)}</p>')
    if bullets:
        parts.append('<ul class="bullets">' + "".join(f"<li>{e(b)}</li>" for b in bullets) + "</ul>")
    parts.append("</article>")
    return "".join(parts)


def experience_html():
    out = [view_open("experience", "Experience"), sub("Clinical and research experience", first=True)]
    for x in C["experience"]:
        out.append(entry_html(x["org"], x["role"], x["dates"], x.get("location", ""), x.get("bullets")))
    out.append(sub("Education"))
    for x in C["education"]:
        out.append(entry_html(x["org"], x["degree"], x["dates"], x.get("location", "")))
    out.append(VIEW_CLOSE)
    return "".join(out)


def links_html(item):
    doi = item.get("doi", "")
    links = []
    if doi:
        label = item.get("doi_label", "DOI")
        links.append(f'<a href="https://doi.org/{e(doi)}" target="_blank" rel="noopener"><span class="lbl">{e(label)}</span> {e(doi)}{ICON_EXT}</a>')
        pmid, pmcid = PMID.get(doi.lower(), (None, None))
        if pmid:
            links.append(f'<a href="https://pubmed.ncbi.nlm.nih.gov/{e(pmid)}/" target="_blank" rel="noopener"><span class="lbl">PubMed</span> {e(pmid)}{ICON_EXT}</a>')
        if pmcid:
            links.append(f'<a href="https://pmc.ncbi.nlm.nih.gov/articles/{e(pmcid)}/" target="_blank" rel="noopener"><span class="lbl">PMC</span> {e(pmcid[3:])}{ICON_EXT}</a>')
    if item.get("url"):
        links.append(f'<a href="{e(item["url"])}" target="_blank" rel="noopener"><span class="lbl">{e(item.get("url_label", "Abstract"))}</span>{ICON_EXT}</a>')
    return ('<p class="links">' + "".join(links) + "</p>") if links else ""


def is_accent_role(role):
    r = role.lower()
    return r.startswith("first") or "finalist" in r or "featured" in r


def pub_html(item):
    bits = [item.get(k, "") for k in ("title", "authors", "journal", "meeting", "year", "venue", "role", "doi", "cite")]
    data_text = e(" ".join(b for b in bits if b).lower())
    parts = [f'<li class="pub" data-text="{data_text}">', f'<h3 class="pub-title">{e(item["title"])}</h3>']
    if item.get("authors"):
        parts.append(f'<p class="authors">{authors_html(item["authors"])}</p>')
    meta = []
    for key in ("journal", "meeting"):
        if item.get(key):
            meta.append(f'<span class="journal">{e(item[key])}</span>')
    venue = item.get("venue", "")
    if item.get("year") and item["year"] not in venue:
        meta.append(f"<span>{e(item['year'])}</span>")
    for key in ("cite", "venue"):
        if item.get(key):
            meta.append(f"<span>{e(item[key])}</span>")
    status = item.get("status")
    if status and not item.get("cite", "").lower().startswith(status.lower()):
        meta.append(f'<span class="badge">{e(status)}</span>')
    if item.get("role"):
        if is_accent_role(item["role"]):
            meta.append(f'<span class="badge">{e(item["role"])}</span>')
        else:
            meta.append(f"<span>{e(item['role'])}</span>")
    if item.get("note"):
        meta.append(f"<span>{e(item['note'])}</span>")
    parts.append('<p class="meta">' + "".join(meta) + "</p>")
    parts.append(links_html(item))
    parts.append("</li>")
    return "".join(parts)


def pubset_html(pid, segments, panels, search_label, placeholder, nomatch):
    """segments: list of (key, label, count). panels: list of (key, title, items)."""
    seg = ['<div class="seg" role="tablist" aria-label="Filter">']
    for i, (key, label, n) in enumerate(segments):
        sel = "true" if i == 0 else "false"
        controls = f"{pid}-panel-{key}" if key != "all" else " ".join(f"{pid}-panel-{k}" for k, _, _ in panels)
        seg.append(
            f'<button type="button" role="tab" id="{pid}-tab-{key}" aria-selected="{sel}" aria-controls="{controls}" '
            f'aria-label="{e(label)}, {plural(n, "item")}" data-key="{key}" tabindex="{0 if i == 0 else -1}">'
            f'<span>{e(label)}</span> <span class="count">{n}</span></button>'
        )
    seg.append("</div>")
    search = (
        f'<div class="search"><label class="vh" for="{pid}-search">{e(search_label)}</label>' + ICON_SEARCH
        + f'<input id="{pid}-search" type="search" placeholder="{e(placeholder)}" autocomplete="off" spellcheck="false"></div>'
    )
    panel_html = []
    for key, title, items in panels:
        panel_html.append(
            f'<div class="panel" id="{pid}-panel-{key}" role="tabpanel" aria-labelledby="{pid}-tab-{key}" data-key="{key}">'
            f'<h2 class="panel-title">{e(title)}</h2><ol class="pubs">{"".join(pub_html(it) for it in items)}</ol></div>'
        )
    return (
        f'<div class="pubset" id="{pid}" data-nomatch="{e(nomatch)}">'
        '<div class="controls">' + "".join(seg) + search + "</div>"
        f'<p class="results" id="{pid}-results" role="status" aria-live="polite"></p>'
        + "".join(panel_html)
        + "</div>"
    )


def publications_html():
    segs = [("all", "All", n_articles)] + [(k, groups[k]["short"], counts[k]) for k in ("research", "reviews", "preprints")]
    panels = [(k, groups[k]["label"], groups[k]["items"]) for k in ("research", "reviews", "preprints")]
    lead = (
        e(C["pub_note"])
        .replace("Google Scholar", f'<a href="{e(C["socials"][3]["url"])}" target="_blank" rel="noopener">Google Scholar</a>')
        .replace("ORCID", f'<a href="{e(C["socials"][4]["url"])}" target="_blank" rel="noopener">ORCID</a>')
    )
    return view_open("publications", "Publications", lead) + pubset_html(
        "pubs", segs, panels, "Search publications", "Search titles, journals, years", "No matches. Try a shorter word, a journal name, or a year."
    ) + VIEW_CLOSE


def abstracts_html():
    segs = [("all", "All", counts["abstracts"])] + [(y, y, len(items)) for y, items in years.items()]
    panels = [(y, y, items) for y, items in years.items()]
    lead = f"{ABSTRACT_SCOPE} {word(n_first)} were presented as first author and are marked below."
    return view_open("abstracts", "Conference Abstracts", lead) + pubset_html(
        "abs", segs, panels, "Search abstracts", "Search titles, meetings, years", "No matches. Try a shorter word, a meeting name, or a year."
    ) + VIEW_CLOSE


def news_html():
    items = []
    for n in news_sorted:
        items.append(
            '<article class="news-item">'
            f'<p class="news-meta"><span class="news-source">{e(n["source"])}</span><span>{e(n["date"])}</span></p>'
            f'<h2 class="news-title"><a href="{e(n["url"])}" target="_blank" rel="noopener">{e(n["title"])}</a></h2>'
            f'<p class="detail">{e(n["summary"])}</p>'
            f'<p class="links"><a href="{e(n["url"])}" target="_blank" rel="noopener"><span class="lbl">{e(n.get("url_label", "Read more"))}</span>{ICON_EXT}</a></p>'
            "</article>"
        )
    return view_open("news", "News", "Announcements and coverage, newest first.") + '<div class="news">' + "".join(items) + "</div>" + VIEW_CLOSE


def skills_html():
    rows = "".join(f'<div class="skill"><dt>{e(s["label"])}</dt><dd>{e(s["value"])}</dd></div>' for s in C["skills"])
    out = [view_open("skills", "Skills and Software"), f'<dl class="skills">{rows}</dl>']
    if C.get("software"):
        out.append(sub("Open-source software"))
        for s in C["software"]:
            links = "".join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener"><span class="lbl">{e(l["label"])}</span>{ICON_EXT}</a>' for l in s["links"])
            out.append(
                '<article class="entry">'
                f'<div class="entry-head"><div><h3>{e(s["name"])}</h3><p class="role">{e(s["role"])}</p></div><p class="dates">{e(s["year"])}</p></div>'
                f'<p class="detail">{e(s["detail"])}</p><p class="links">{links}</p></article>'
            )
    out.append(VIEW_CLOSE)
    return "".join(out)


def service_html():
    out = [view_open("service", "Service and Awards"), sub("Professional service", first=True)]
    for s in C["service"]:
        out.append(entry_html(s["org"], s["role"], s["dates"], detail=s["detail"]))
    if C.get("mentees"):
        out.append(sub("Research mentorship"))
        out.append('<ul class="mentees">' + "".join(f'<li><span class="mentee">{e(m["name"])}</span><span class="inst">{e(m["institution"])}</span></li>' for m in C["mentees"]) + "</ul>")
    out.append(sub("Leadership and community"))
    for s in C["leadership"]:
        out.append(entry_html(s["org"], s["role"], s["dates"], detail=s["detail"]))
    out.append(f'<p class="detail volunteer">{e(C["volunteering"])}</p>')
    if C.get("awards"):
        out.append(sub("Awards and distinctions"))
        out.append('<ul class="awards">' + "".join(
            f'<li><div><span class="mentee">{e(a["title"])}</span><span class="inst">{e(a["org"])}</span></div><span class="dates">{e(a["date"])}</span></li>' for a in C["awards"]) + "</ul>")
    out.append(sub("Languages"))
    out.append('<ul class="langs">' + "".join(f'<li><span class="mentee">{e(l["lang"])}</span><span class="inst">{e(l["level"])}</span></li>' for l in C["languages"]) + "</ul>")
    out.append(VIEW_CLOSE)
    return "".join(out)


def contact_html():
    rows = []
    for s in C["socials"]:
        mail = s["url"].startswith("mailto:")
        ext = "" if mail else ' target="_blank" rel="noopener"'
        rows.append(f'<li><span class="clabel">{e(s["label"])}</span><a href="{e(s["url"])}"{ext}>{e(s["display"])}{"" if mail else ICON_EXT}</a></li>')
    return view_open("contact", "Contact", "Email is the best way to get in touch.") + '<ul class="contact">' + "".join(rows) + "</ul>" + VIEW_CLOSE


def footer_html():
    return (
        '<footer class="foot"><div class="wrap foot-inner">'
        f'<p>© 2026 {e(C["name"])}</p><p><a href="#home">Home</a></p><p>Last updated {e(C["updated"])}</p>'
        "</div></footer>"
    )


# ---------------------------------------------------------------- css
DARK_TOKENS = """
  --bg:#0B1119; --surface:#121A27; --tint:#182334;
  --line:#243247; --line-soft:#1B2637; --line-strong:#5A6A85;
  --ink:#EAF0F8; --ink-2:#A6B3C7; --ink-3:#8A98B0;
  --accent:#7DAEF4; --accent-hover:#A3C6F9;
  --focus:#7DAEF4; --nav-bg:rgba(11,17,25,.72);
  --shadow:0 1px 2px rgba(0,0,0,.35), 0 8px 24px rgba(0,0,0,.35);
  --seg-on:#2A3A52; --seg-shadow:0 1px 2px rgba(0,0,0,.45);
  color-scheme:dark;
"""

CSS = """
:root{
  --bg:#F5F8FC; --surface:#FFFFFF; --tint:#E9EFF7;
  --line:#D8E1EC; --line-soft:#E6ECF4; --line-strong:#8090A8;
  --ink:#0E1726; --ink-2:#4B5B72; --ink-3:#5C6B84;
  --accent:#1D5BBF; --accent-hover:#174A9D;
  --focus:#1D5BBF; --nav-bg:rgba(245,248,252,.78);
  --shadow:0 1px 2px rgba(14,23,38,.04), 0 8px 24px rgba(14,23,38,.06);
  --seg-on:#FFFFFF; --seg-shadow:0 1px 2px rgba(14,23,38,.08), 0 2px 6px rgba(14,23,38,.08);
  --display:"SF Pro Display",-apple-system,BlinkMacSystemFont,"Inter","Helvetica Neue","Segoe UI",Arial,sans-serif;
  --text:"SF Pro Text","SF Pro Display",-apple-system,BlinkMacSystemFont,"Inter","Helvetica Neue","Segoe UI",Arial,sans-serif;
  --ease:cubic-bezier(.2,.7,.2,1);
  --r-s:6px; --r-m:10px; --r-l:14px;
  color-scheme:light;
}
:root[data-mode="dark"]{ __DARK__ }

*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--text);font-size:1.0625rem;line-height:1.55;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;font-feature-settings:"kern"}
img{max-width:100%;display:block}
a{color:var(--accent);text-decoration:none}
a:hover{color:var(--accent-hover);text-decoration:underline;text-underline-offset:.18em;text-decoration-thickness:1px}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px;border-radius:4px}
h1,h2,h3{font-family:var(--display);margin:0;text-wrap:balance}
h1:focus,#main:focus{outline:none}
p{margin:0}
ul,ol,dl{margin:0;padding:0;list-style:none}
svg{width:1em;height:1em;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;flex:none}
svg.fill{fill:currentColor;stroke:none}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.wrap{max-width:1080px;margin:0 auto;padding-inline:clamp(16px,5vw,44px)}
.skip{position:absolute;left:16px;top:-48px;background:var(--surface);color:var(--ink);padding:8px 12px;border-radius:var(--r-s);z-index:20;box-shadow:var(--shadow)}
.skip:focus{top:10px}
main{min-height:60vh}

/* routing: with JS, only the current view is displayed */
.js .view{display:none}
.js[data-route="home"] #home,.js[data-route="profile"] #profile,.js[data-route="experience"] #experience,
.js[data-route="publications"] #publications,.js[data-route="abstracts"] #abstracts,.js[data-route="news"] #news,
.js[data-route="skills"] #skills,.js[data-route="service"] #service,.js[data-route="contact"] #contact{display:block}

/* motion */
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.js .view.page{animation:rise .42s var(--ease) both}
.js .home .hero-text > *{animation:rise .55s var(--ease) both;animation-delay:calc(var(--i) * 70ms)}
.js .home .portrait{animation:rise .6s var(--ease) both;animation-delay:120ms}
.js .home .tiles li{animation:rise .5s var(--ease) both;animation-delay:calc(260ms + var(--i) * 45ms)}
.js.visited .home .hero-text > *,.js.visited .home .portrait,.js.visited .home .tiles li{animation-duration:.3s;animation-delay:0s}

/* nav */
.nav{position:sticky;top:0;z-index:10;background:var(--nav-bg);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid var(--line-soft)}
.nav-inner{display:flex;align-items:center;gap:20px;min-height:54px}
.brand{font-family:var(--display);font-weight:600;color:var(--ink);letter-spacing:-.01em;white-space:nowrap;margin-right:auto}
.brand:hover{text-decoration:none;color:var(--ink)}
.nav nav{min-width:0}
.nav ul{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;padding:4px;margin:-4px}
.nav ul::-webkit-scrollbar{display:none}
.nav li a{position:relative;display:block;padding:6px 10px;border-radius:var(--r-s);font-size:.9375rem;color:var(--ink-2);white-space:nowrap;transition:background-color .2s,color .2s}
.nav li a:hover{color:var(--ink);text-decoration:none;background:var(--tint)}
.nav li a[aria-current="page"]{color:var(--ink);background:var(--tint)}
.nav li a[aria-current="page"]::after{content:"";position:absolute;left:10px;right:10px;bottom:2px;height:2px;border-radius:1px;background:var(--accent)}
.theme{appearance:none;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);width:36px;height:36px;border-radius:999px;display:inline-grid;place-items:center;cursor:pointer;position:relative;flex:none;transition:border-color .2s,color .2s}
.theme:hover{border-color:var(--accent);color:var(--accent)}
.theme svg{position:absolute;font-size:1.05rem;transition:opacity .35s var(--ease),transform .35s var(--ease)}
.theme .moon{opacity:0;transform:rotate(90deg) scale(.6)}
:root[data-mode="dark"] .theme .sun{opacity:0;transform:rotate(-90deg) scale(.6)}
:root[data-mode="dark"] .theme .moon{opacity:1;transform:none}

/* home */
.home{padding-block:clamp(48px,8vw,88px) clamp(56px,8vw,96px)}
.hero-grid{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:clamp(32px,5vw,72px);align-items:start}
.home h1{font-size:clamp(2.375rem,5.2vw,3.625rem);font-weight:600;letter-spacing:-.028em;line-height:1.08}
h1 .cred{font-weight:400;color:var(--ink-3);letter-spacing:-.02em}
.hero-role{margin-top:14px;font-size:1.125rem;color:var(--ink-2);line-height:1.45}
.tagline{margin-top:22px;font-size:1.25rem;line-height:1.45;max-width:38em;letter-spacing:-.008em}
.socials{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}
.social{display:inline-flex;align-items:center;gap:8px;padding:8px 14px 8px 12px;border:1px solid var(--line);background:var(--surface);border-radius:999px;font-size:.9375rem;font-weight:500;color:var(--ink);transition:border-color .2s,transform .2s var(--ease),box-shadow .2s}
.social svg{font-size:1rem;color:var(--ink-2);transition:color .2s}
.social:hover{text-decoration:none;color:var(--ink);border-color:var(--accent);transform:translateY(-1px);box-shadow:var(--shadow)}
.social:hover svg{color:var(--accent)}
.portrait{margin:0;width:184px}
.portrait img{width:100%;height:auto;border-radius:24px;box-shadow:var(--shadow)}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:clamp(40px,6vw,64px)}
.tile{display:flex;flex-direction:column;gap:10px;height:100%;padding:20px 20px 18px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-l);color:var(--ink);transition:border-color .2s,transform .25s var(--ease),box-shadow .25s var(--ease)}
.tile:hover{text-decoration:none;color:var(--ink);border-color:var(--accent);transform:translateY(-2px);box-shadow:var(--shadow)}
.tile-top{display:flex;justify-content:space-between;align-items:center;gap:12px}
.tile-title{font-family:var(--display);font-weight:600;font-size:1.0625rem;letter-spacing:-.012em}
.tile .arrow{color:var(--ink-3);font-size:1.05rem;transition:transform .25s var(--ease)}
.tile:hover .arrow{transform:translateX(4px)}
.tile-desc{font-size:.9375rem;color:var(--ink-2);line-height:1.45;flex:1}
.tile-meta{font-size:.8125rem;color:var(--ink-3);font-variant-numeric:tabular-nums;letter-spacing:.01em}

/* pages */
.page{padding-block:clamp(36px,5vw,56px) clamp(56px,8vw,96px)}
.page-wrap{max-width:900px}
.page-head{margin-bottom:clamp(28px,4vw,40px);padding-bottom:clamp(20px,3vw,28px);border-bottom:1px solid var(--line-soft)}
.crumb{display:inline-flex;align-items:center;gap:6px;font-size:.875rem;color:var(--ink-3);margin-bottom:18px}
.crumb .arrow{transform:rotate(180deg);transition:transform .25s var(--ease)}
.crumb:hover{color:var(--accent);text-decoration:none}
.crumb:hover .arrow{transform:rotate(180deg) translateX(3px)}
.page h1{font-size:clamp(1.875rem,3.4vw,2.375rem);font-weight:600;letter-spacing:-.025em;line-height:1.15}
.lead{margin-top:12px;color:var(--ink-2);font-size:1rem;line-height:1.55;max-width:64ch}
.prose{max-width:66ch;font-size:1.0625rem}
.sub,.panel-title{font-family:var(--text);font-size:.8125rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-top:44px;text-wrap:initial}
.sub.first{margin-top:0}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.chips li{padding:6px 12px;border-radius:var(--r-s);background:var(--tint);color:var(--ink-2);font-size:.875rem;font-weight:500}

/* entries */
.entry{padding-block:20px;border-top:1px solid var(--line-soft)}
.sub + .entry{border-top:0;padding-top:12px}
.entry-head{display:flex;justify-content:space-between;gap:24px;align-items:baseline}
.entry h3{font-size:1.0625rem;font-weight:600;letter-spacing:-.01em}
.role{color:var(--ink-2);margin-top:2px}
.loc{color:var(--ink-3);font-size:.875rem;margin-top:2px}
.dates{color:var(--ink-3);font-size:.9375rem;white-space:nowrap;font-variant-numeric:tabular-nums}
.detail{margin-top:8px;color:var(--ink-2);font-size:.9375rem;max-width:66ch}
.volunteer{margin-top:20px;padding-top:20px;border-top:1px solid var(--line-soft)}
.bullets{margin-top:10px;display:grid;gap:6px;padding-left:1.15em;list-style:disc;color:var(--ink-2);font-size:.9375rem;max-width:70ch}
.bullets li::marker{color:var(--ink-3)}

/* publication sets */
.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}
.controls > *{min-width:0;max-width:100%}
.seg{position:relative;display:inline-flex;flex-wrap:wrap;gap:2px;padding:3px;background:var(--tint);border-radius:var(--r-m)}
.seg-ind{position:absolute;left:0;top:0;width:0;height:0;background:var(--seg-on);border-radius:7px;box-shadow:var(--seg-shadow);pointer-events:none;opacity:0;transition:transform .28s var(--ease),width .28s var(--ease),height .28s var(--ease)}
.seg.has-ind .seg-ind{opacity:1}
.seg button{position:relative;z-index:1;appearance:none;border:0;background:transparent;font:inherit;font-size:.9375rem;font-weight:500;color:var(--ink-2);padding:7px 13px;border-radius:7px;cursor:pointer;display:inline-flex;align-items:center;gap:6px;white-space:nowrap;transition:color .2s}
.seg button::after{content:"";position:absolute;left:13px;right:13px;bottom:4px;height:2px;border-radius:1px;background:var(--accent);opacity:0;transition:opacity .2s}
.seg button:hover{color:var(--ink)}
.seg button[aria-selected="true"]{background:var(--seg-on);color:var(--ink);box-shadow:var(--seg-shadow)}
.seg button[aria-selected="true"]::after{opacity:1}
.seg.has-ind button[aria-selected="true"]{background:transparent;box-shadow:none}
.seg button:focus-visible{outline-offset:1px}
.seg .count{font-size:.8125rem;color:var(--ink-3);font-variant-numeric:tabular-nums}
.seg button[aria-selected="true"] .count{color:var(--ink-2)}
.search{position:relative;flex:1 1 220px;max-width:320px}
.search svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--ink-3);pointer-events:none}
.search input{width:100%;font:inherit;font-size:.9375rem;padding:9px 12px 9px 36px;border:1px solid var(--line-strong);border-radius:var(--r-m);background:var(--surface);color:var(--ink);transition:border-color .2s}
.search input::placeholder{color:var(--ink-3)}
.search input:focus{border-color:var(--accent)}
.search input::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none}
.results{margin-top:18px;font-size:.875rem;color:var(--ink-2);min-height:1.2em}
.results:empty{margin-top:0;min-height:0}
.panel-title{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;margin:0}
.show-titles .panel-title{position:static;width:auto;height:auto;overflow:visible;clip:auto;white-space:normal;margin-top:28px}
.pub{padding-block:20px}
.pubs .pub:not([hidden]) ~ .pub:not([hidden]){border-top:1px solid var(--line-soft)}
.pub-title{font-size:1.0625rem;font-weight:600;line-height:1.4;letter-spacing:-.008em;text-wrap:pretty}
.authors{margin-top:6px;color:var(--ink-2);font-size:.9375rem;line-height:1.5}
.authors strong{color:var(--ink);font-weight:600}
.meta{margin-top:6px;display:flex;flex-wrap:wrap;gap:4px 8px;font-size:.9375rem;color:var(--ink-2);align-items:center}
.meta > span:not(.badge):not(:first-child)::before{content:"·";margin-right:8px;color:var(--ink-3)}
.meta .journal{color:var(--ink);font-weight:500}
.badge{display:inline-flex;align-items:center;font-size:.75rem;font-weight:600;padding:3px 8px;border-radius:var(--r-s);background:var(--tint);color:var(--accent);letter-spacing:.01em;line-height:1.2}
.links{margin-top:10px;display:flex;flex-wrap:wrap;gap:8px}
.links a{display:inline-flex;align-items:center;gap:4px;font-size:.8125rem;color:var(--ink-2);background:var(--surface);border:1px solid var(--line);border-radius:var(--r-s);padding:4px 9px;font-variant-numeric:tabular-nums;transition:border-color .2s,color .2s,transform .2s var(--ease)}
.links a .lbl{font-weight:600;color:var(--ink)}
.links a .ext{color:var(--ink-3);font-size:.875em}
.links a:hover{text-decoration:none;border-color:var(--accent);color:var(--accent);transform:translateY(-1px)}
.links a:hover .lbl,.links a:hover .ext{color:var(--accent)}

/* news */
.news{display:grid;gap:12px}
.news-item{padding:22px 24px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-l)}
.news-meta{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:.8125rem;color:var(--ink-3);align-items:center}
.news-source{font-weight:600;color:var(--accent);letter-spacing:.01em}
.news-meta > span + span::before{content:"·";margin-right:10px;color:var(--ink-3)}
.news-title{margin-top:8px;font-size:1.125rem;font-weight:600;letter-spacing:-.012em;line-height:1.35;text-wrap:pretty}
.news-title a{color:var(--ink)}
.news-title a:hover{color:var(--accent);text-decoration:none}

/* skills, lists */
.skills{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px clamp(24px,4vw,48px)}
.skill dt{font-weight:600;font-size:.9375rem;letter-spacing:-.005em}
.skill dd{margin:6px 0 0;color:var(--ink-2);font-size:.9375rem;line-height:1.55}
.mentees,.langs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 clamp(24px,4vw,48px);margin-top:4px}
.mentees li,.langs li{display:flex;flex-direction:column;padding-block:12px;border-bottom:1px solid var(--line-soft)}
.awards{margin-top:4px}
.awards li{display:flex;justify-content:space-between;gap:24px;align-items:baseline;padding-block:12px;border-bottom:1px solid var(--line-soft)}
.awards li > div{display:flex;flex-direction:column}
.mentee{font-weight:500}
.inst{color:var(--ink-3);font-size:.875rem}

/* contact */
.contact li{display:grid;grid-template-columns:160px minmax(0,1fr);gap:16px;padding-block:14px;border-top:1px solid var(--line-soft);align-items:baseline}
.contact li:first-child{border-top:0;padding-top:0}
.clabel{color:var(--ink-2);font-size:.9375rem}
.contact a{display:inline-flex;align-items:center;gap:6px;font-weight:500;overflow-wrap:anywhere}
.contact .ext{color:var(--ink-3);font-size:.8em}

/* footer */
.foot{border-top:1px solid var(--line-soft);padding-block:28px 44px}
.foot-inner{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 24px;font-size:.875rem;color:var(--ink-3)}
.foot a{color:var(--ink-3)}
.foot a:hover{color:var(--accent)}

@media (max-width: 1000px){
  .tiles{grid-template-columns:repeat(2,minmax(0,1fr))}
  .nav-inner{flex-wrap:wrap;gap:0 16px;padding-block:8px 6px}
  .nav nav{flex-basis:100%;order:3}
  .nav ul{padding-right:40px;-webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 36px),transparent);mask-image:linear-gradient(90deg,#000 calc(100% - 36px),transparent)}
}
@media (max-width: 720px){
  .hero-grid{grid-template-columns:1fr}
  .home h1 .cred{display:block;font-size:.62em;margin-top:4px}
  h1 .comma{display:none}
  .portrait{order:-1;width:128px}
  .portrait img{border-radius:20px}
  .seg{display:grid;grid-template-columns:1fr 1fr;width:100%}
  .seg button{justify-content:center;white-space:normal;text-align:center}
  .search{max-width:none;flex-basis:100%}
  .skills,.mentees,.langs{grid-template-columns:1fr}
  .contact li{grid-template-columns:1fr;gap:2px}
  .entry-head,.awards li{flex-direction:column;gap:2px}
  .dates{white-space:normal}
}
@media (max-width: 560px){
  .tiles{grid-template-columns:1fr}
}
@media (prefers-reduced-motion: reduce){
  *{animation:none!important;transition:none!important}
}
@media print{
  *{animation:none!important;transition:none!important}
  .nav,.controls,.results,.skip,.crumb,.tiles{display:none}
  .js .view{display:block!important}
  .panel[hidden],.pub[hidden]{display:block!important}
  .panel-title{position:static;width:auto;height:auto;overflow:visible;clip:auto;white-space:normal;margin-top:28px}
  .page,.home{padding-block:24px}
  a{color:inherit}
}
""".replace("__DARK__", DARK_TOKENS)

# ---------------------------------------------------------------- js
EARLY_JS = (
    "(function(){var R={" + ",".join(f"{r}:1" for r in ROUTES) + "};"
    "var h=location.hash.replace(/^#\\/?/,'').replace(/\\/.*$/,'');var d=document.documentElement;"
    "d.classList.add('js');d.setAttribute('data-route',Object.prototype.hasOwnProperty.call(R,h)?h:'home');"
    "try{if(localStorage.getItem('ng-theme')==='dark')d.setAttribute('data-mode','dark')}catch(e){}"
    "var l=document.createElement('link');l.rel='stylesheet';l.href=" + json.dumps(FONT_CSS) + ";document.head.appendChild(l);"
    "})();"
)

JS = r"""
(function(){
  var ROUTES = __ROUTES__;
  var TITLES = __TITLES__;
  var SITE = __NAME__;
  var root = document.documentElement;
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav a[data-route]'));

  // ---- theme (light by default; the visitor's choice is remembered in this browser)
  var btn = document.getElementById('theme-toggle');
  function setMode(mode, persist){
    if (mode === 'dark') root.setAttribute('data-mode', 'dark'); else root.removeAttribute('data-mode');
    if (btn) btn.setAttribute('aria-pressed', mode === 'dark' ? 'true' : 'false');
    if (persist) { try { localStorage.setItem('ng-theme', mode); } catch (e) {} }
  }
  setMode(root.getAttribute('data-mode') === 'dark' ? 'dark' : 'light', false);
  if (btn) btn.addEventListener('click', function(){ setMode(root.getAttribute('data-mode') === 'dark' ? 'light' : 'dark', true); });

  // ---- publication sets (filter tabs + search)
  var sets = [];
  Array.prototype.forEach.call(document.querySelectorAll('.pubset'), function(box){
    var seg = box.querySelector('.seg');
    var tabs = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]'));
    var panels = Array.prototype.slice.call(box.querySelectorAll('.panel'));
    var search = box.querySelector('input[type="search"]');
    var results = box.querySelector('.results');
    if (!seg || !tabs.length || !panels.length || !search || !results) return;
    var NO_MATCH = box.getAttribute('data-nomatch') || 'No matches.';
    var ind = document.createElement('span');
    ind.className = 'seg-ind';
    seg.insertBefore(ind, seg.firstChild);
    var current = tabs[0].getAttribute('data-key');
    var beforeSearch = null;

    function layoutInd(){
      var t = tabs.filter(function(x){ return x.getAttribute('aria-selected') === 'true'; })[0];
      if (!t || seg.offsetParent === null) return;
      var sr = seg.getBoundingClientRect(), tr = t.getBoundingClientRect();
      if (!tr.width) return;
      var firstTime = !seg.classList.contains('has-ind');
      if (firstTime) ind.style.transition = 'none';
      ind.style.width = tr.width + 'px';
      ind.style.height = tr.height + 'px';
      ind.style.transform = 'translate(' + (tr.left - sr.left) + 'px,' + (tr.top - sr.top) + 'px)';
      seg.classList.add('has-ind');
      if (firstTime) { void ind.offsetWidth; ind.style.transition = ''; }
    }
    function showPanels(){
      var all = current === 'all';
      panels.forEach(function(p){ p.hidden = !all && p.getAttribute('data-key') !== current; });
      box.classList.toggle('show-titles', all);
    }
    function select(key, focus){
      current = key;
      tabs.forEach(function(t){
        var on = t.getAttribute('data-key') === key;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        if (on && focus) t.focus();
      });
      if (!search.value.trim()) showPanels();
      layoutInd();
    }
    function runSearch(){
      var terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      if (!terms.length) {
        panels.forEach(function(p){ Array.prototype.forEach.call(p.querySelectorAll('.pub'), function(li){ li.hidden = false; }); });
        results.textContent = '';
        if (beforeSearch !== null) { var k = beforeSearch; beforeSearch = null; select(k, false); } else { showPanels(); }
        return;
      }
      if (current !== 'all') { if (beforeSearch === null) beforeSearch = current; select('all', false); }
      var total = 0;
      panels.forEach(function(p){
        var hits = 0;
        Array.prototype.forEach.call(p.querySelectorAll('.pub'), function(li){
          var text = li.getAttribute('data-text') || '';
          var ok = terms.every(function(t){ return text.indexOf(t) !== -1; });
          li.hidden = !ok; if (ok) hits++;
        });
        p.hidden = hits === 0; total += hits;
      });
      box.classList.add('show-titles');
      results.textContent = total ? (total + (total === 1 ? ' result' : ' results')) : NO_MATCH;
    }
    function clearSearch(){ if (search.value.trim()) { search.value = ''; beforeSearch = null; runSearch(); } }
    tabs.forEach(function(t, i){
      t.addEventListener('click', function(){ clearSearch(); select(t.getAttribute('data-key'), false); });
      t.addEventListener('keydown', function(ev){
        var j = null;
        if (ev.key === 'ArrowRight') j = (i + 1) % tabs.length;
        else if (ev.key === 'ArrowLeft') j = (i - 1 + tabs.length) % tabs.length;
        else if (ev.key === 'Home') j = 0;
        else if (ev.key === 'End') j = tabs.length - 1;
        if (j !== null) { ev.preventDefault(); clearSearch(); select(tabs[j].getAttribute('data-key'), true); }
      });
    });
    search.addEventListener('input', runSearch);
    search.addEventListener('keydown', function(ev){ if (ev.key === 'Escape') { search.value = ''; runSearch(); } });
    showPanels();
    sets.push({ layout: layoutInd });
  });

  // ---- routing
  function parseRoute(){
    var h = location.hash.replace(/^#\/?/, '').replace(/\/.*$/, '');
    return ROUTES.indexOf(h) !== -1 ? h : 'home';
  }
  var first = true, homeSeen = false;
  function show(route){
    if (route === 'home') { if (homeSeen) root.classList.add('visited'); homeSeen = true; }
    root.setAttribute('data-route', route);
    document.title = route === 'home' ? SITE : TITLES[route] + ' · ' + SITE;
    var currentLink = null;
    navLinks.forEach(function(a){
      if (a.getAttribute('data-route') === route) { a.setAttribute('aria-current', 'page'); currentLink = a; }
      else a.removeAttribute('aria-current');
    });
    if (!first) {
      window.scrollTo(0, 0);
      var h = document.querySelector('#' + route + ' h1');
      if (h) { try { h.focus({ preventScroll: true }); } catch (e) { h.focus(); } }
    }
    if (currentLink && currentLink.scrollIntoView) {
      try { currentLink.scrollIntoView({ block: 'nearest', inline: 'center' }); } catch (e) {}
    }
    first = false;
    requestAnimationFrame(function(){ sets.forEach(function(s){ s.layout(); }); });
  }
  var skip = document.querySelector('.skip');
  if (skip) skip.addEventListener('click', function(ev){
    ev.preventDefault();
    var route = root.getAttribute('data-route') || 'home';
    var target = document.querySelector('#' + route + ' h1') || document.getElementById('main');
    if (!target) return;
    try { target.focus({ preventScroll: true }); } catch (e) { target.focus(); }
    try { target.scrollIntoView({ block: 'start' }); } catch (e2) {}
  });
  window.addEventListener('hashchange', function(){ show(parseRoute()); });
  window.addEventListener('resize', function(){ sets.forEach(function(s){ s.layout(); }); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function(){ sets.forEach(function(s){ s.layout(); }); });
  show(parseRoute());
})();
"""
JS = JS.replace("__ROUTES__", json.dumps(ROUTES)).replace("__TITLES__", json.dumps(TITLES)).replace("__NAME__", json.dumps(C["name"]))

# ---------------------------------------------------------------- assemble
description = f"{C['name']}, {C['credentials']}. {C['role']} at {C['institution']}. Publications, conference abstracts, news, and profiles."
same_as = [s["url"] for s in C["socials"] if not s["url"].startswith("mailto:")]
jsonld = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": C["name"],
    "honorificSuffix": C["credentials"],
    "jobTitle": "Postdoctoral Fellow",
    "email": f"mailto:{C['email']}",
    "affiliation": {"@type": "Organization", "name": C["institution"]},
    "sameAs": same_as,
}
og_extra = ""
if SITE_URL:
    base = SITE_URL.rstrip("/")
    jsonld["url"] = base + "/"
    jsonld["image"] = base + "/assets/najam-gohar.jpg"
    og_extra = (
        f'<meta property="og:url" content="{e(base)}/">\n'
        f'<meta property="og:image" content="{e(base)}/assets/najam-gohar.jpg">\n'
        f'<link rel="canonical" href="{e(base)}/">\n'
    )

head_common = (
    f"<title>{e(C['name'])}</title>\n"
    f"<script>{EARLY_JS}</script>\n"
    f'<meta name="description" content="{e(description)}">\n'
    f'<meta property="og:title" content="{e(C["name"])}">\n'
    f'<meta property="og:description" content="{e(description)}">\n'
    '<meta property="og:type" content="profile">\n'
    + og_extra
    + '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    f'<noscript><link rel="stylesheet" href="{e(FONT_CSS)}"></noscript>\n'
    f"<style>{CSS}</style>\n"
    "<noscript><style>.controls,.results,.theme,.tiles,.crumb{display:none}.panel-title{position:static;width:auto;height:auto;overflow:visible;clip:auto;white-space:normal;margin-top:28px}</style></noscript>\n"
    f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n'
)

body = (
    '<a class="skip" href="#main">Skip to content</a>\n'
    + nav_html() + "\n"
    + '<main id="main" tabindex="-1">\n'
    + home_html() + "\n"
    + profile_html() + "\n"
    + experience_html() + "\n"
    + publications_html() + "\n"
    + abstracts_html() + "\n"
    + news_html() + "\n"
    + skills_html() + "\n"
    + service_html() + "\n"
    + contact_html() + "\n"
    + "</main>\n"
    + footer_html() + "\n"
    + f"<script>{JS}</script>\n"
)

full = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="color-scheme" content="light">\n'
    + head_common
    + "</head>\n<body>\n" + body + "</body>\n</html>\n"
)
fragment = head_common + body

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(full)
with open(os.path.join(ROOT, "artifact.html"), "w", encoding="utf-8") as f:
    f.write(fragment)

print(f"Built index.html and artifact.html: {counts} | articles {n_articles} | abstracts by year {dict((y, len(v)) for y, v in years.items())} | news {len(news_sorted)} | {len(PMID)} DOIs with PubMed lookups")
