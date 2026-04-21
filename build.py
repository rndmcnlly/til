# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mistune>=3.0",
# ]
# ///

import html
import pathlib
import re
import shutil
import subprocess
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring

import mistune

ROOT = pathlib.Path(__file__).parent.resolve()
SITE_DIR = ROOT / "_site"
BASE_URL = "https://til.adamsmith.as"
AUTHOR = "Adam Smith"
REPO = "rndmcnlly/til"

from mistune.plugins.table import table as table_plugin
from mistune.plugins.footnotes import footnotes as footnotes_plugin

md = mistune.create_markdown(plugins=[table_plugin, footnotes_plugin])


def git_all_file_times():
    result = subprocess.run(
        ["git", "log", "--name-only", "--format=%cI"],
        capture_output=True,
        text=True,
    )
    file_dates = {}
    current_date = None
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            current_date = datetime.fromisoformat(line)
        except ValueError:
            if current_date and line.endswith(".md"):
                existing = file_dates.get(line)
                if existing is None:
                    file_dates[line] = (current_date, current_date)
                else:
                    file_dates[line] = (existing[0], current_date)
    return file_dates


def collect_tils():
    file_times = git_all_file_times()
    tils = []
    for filepath in sorted(ROOT.glob("*/*.md")):
        path = str(filepath.relative_to(ROOT))
        topic = path.split("/")[0]
        slug = filepath.stem
        lines = filepath.read_text().split("\n")
        title = lines[0].lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()
        created, updated = file_times.get(path, (None, None))
        tils.append(
            {
                "path": path,
                "topic": topic,
                "slug": slug,
                "title": title,
                "body": body,
                "html": md(body),
                "created": created or datetime.now(timezone.utc),
                "updated": updated or datetime.now(timezone.utc),
            }
        )
    return tils


NAV = """<nav>
<p><a href="/">Adam Smith: TIL</a> <a href="https://adamsmith.as/">adamsmith.as</a></p>
</nav>"""


def render_page(title, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{html.escape(title)}</title>
<link rel="alternate" type="application/atom+xml" title="Atom" href="/feed.atom">
<link rel="stylesheet" href="/style.css">
{extra_head}
</head>
<body>
{NAV}
<section class="body">
{body}
</section>
</body>
</html>"""


def write_index(tils):
    by_topic = {}
    for t in tils:
        by_topic.setdefault(t["topic"], []).append(t)
    topic_links = " · ".join(
        f'<a href="/{topic}">{topic}</a> ({len(rows)})'
        for topic, rows in sorted(by_topic.items())
    )
    recent = sorted(tils, key=lambda t: t["created"], reverse=True)[:20]
    recent_html = "\n".join(
        f"""<h3><span class="topic"><a href="/{t['topic']}">{t['topic']}</a></span> <a href="/{t['topic']}/{t['slug']}">{html.escape(t['title'])}</a> <span class="date">{t['created'].strftime('%Y-%m-%d')}</span></h3>"""
        for t in recent
    )
    body = f"""<h1>Adam Smith: TIL</h1>
<p>Things I've learned, collected in <a href="https://github.com/{REPO}">{REPO}</a>.</p>
<p><a href="/feed.atom">Atom feed</a></p>
<p><strong>Browse by topic:</strong> {topic_links}</p>
<h2>Recent</h2>
{recent_html}"""
    (SITE_DIR / "index.html").write_text(render_page("Adam Smith: TIL", body))


def write_topic_page(topic, tils):
    topic_dir = SITE_DIR / topic
    topic_dir.mkdir(exist_ok=True)
    items = "\n".join(
        f"""<h3><a href="/{topic}/{t['slug']}">{html.escape(t['title'])}</a> <span class="date">{t['created'].strftime('%Y-%m-%d')}</span></h3>"""
        for t in sorted(tils, key=lambda x: x["created"], reverse=True)
    )
    body = f"""<h1>{html.escape(topic)}</h1>
{items}"""
    (topic_dir / "index.html").write_text(
        render_page(f"{topic} - TIL", body)
    )


def write_til_page(t):
    topic_dir = SITE_DIR / t["topic"]
    topic_dir.mkdir(exist_ok=True)
    date_line = f'Created {t["created"].strftime("%Y-%m-%d")}'
    if t["created"].date() != t["updated"].date():
        date_line += f', updated {t["updated"].strftime("%Y-%m-%d")}'
    body = f"""<h1>{html.escape(t['title'])}</h1>
{t['html']}
<p class="created">{date_line} · <a href="https://github.com/{REPO}/blob/main/{t['path']}">Edit</a></p>"""
    extra_head = f"""<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{html.escape(t['title'])}">
<meta property="og:title" content="{html.escape(t['title'])}">
<meta property="og:url" content="{BASE_URL}/{t['topic']}/{t['slug']}">"""
    (topic_dir / f"{t['slug']}.html").write_text(
        render_page(f"{t['title']} - TIL", body, extra_head)
    )


def write_feed(tils):
    recent = sorted(tils, key=lambda t: t["created"], reverse=True)[:15]
    feed = Element("feed", xmlns="http://www.w3.org/2005/Atom")
    SubElement(feed, "title").text = f"{AUTHOR} TIL"
    SubElement(feed, "link", href=f"{BASE_URL}/feed.atom", rel="self")
    SubElement(feed, "link", href=BASE_URL)
    SubElement(feed, "id").text = f"{BASE_URL}/"
    SubElement(feed, "updated").text = datetime.now(timezone.utc).isoformat()
    for t in recent:
        entry = SubElement(feed, "entry")
        SubElement(entry, "title").text = t["title"]
        SubElement(entry, "link", href=f"{BASE_URL}/{t['topic']}/{t['slug']}")
        SubElement(entry, "id").text = f"{BASE_URL}/{t['topic']}/{t['slug']}"
        SubElement(entry, "updated").text = t["updated"].isoformat()
        SubElement(entry, "content", type="html").text = t["html"]
        author = SubElement(entry, "author")
        SubElement(author, "name").text = AUTHOR
    xml = tostring(feed, encoding="unicode", xml_declaration=True)
    (SITE_DIR / "feed.atom").write_text(xml)


def write_css():
    (SITE_DIR / "style.css").write_text("""\
:root {
    color-scheme: light dark;
    --bg: #fff;
    --bg-nav: #1a1a2e;
    --bg-nav-end: #16213e;
    --bg-code: #f4f4f8;
    --bg-inline-code: #eeeef2;
    --bg-topic: #e2e2e8;
    --bg-th: #f4f4f8;
    --text: #2a2a2a;
    --text-muted: #6a6a7a;
    --text-topic: #555;
    --text-nav: #e0e0e8;
    --link: #3b5998;
    --link-nav: #c8c8e0;
    --border: #d8d8e0;
    --border-blockquote: #3b5998;
}
@media (prefers-color-scheme: dark) {
    :root {
        --bg: #0f0f14;
        --bg-nav: #0a0a12;
        --bg-nav-end: #12121e;
        --bg-code: #1a1a24;
        --bg-inline-code: #1e1e2a;
        --bg-topic: #1e1e2a;
        --bg-th: #1a1a24;
        --text: #d4d4dc;
        --text-muted: #7a7a8e;
        --text-topic: #9a9ab0;
        --text-nav: #b8b8d0;
        --link: #7b9fe0;
        --link-nav: #9898c0;
        --border: #2a2a3a;
        --border-blockquote: #7b9fe0;
    }
}
* { box-sizing: border-box; }
body {
    font-family: "Helvetica Neue", helvetica, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background: var(--bg);
    color: var(--text);
    transition: background 0.2s, color 0.2s;
}
h1, h2, h3 {
    font-family: Georgia, 'Times New Roman', Times, serif;
    line-height: 1.3;
}
h1 { margin-top: 0; }
nav {
    background: linear-gradient(to bottom, var(--bg-nav), var(--bg-nav-end));
    color: var(--text-nav);
    border-bottom: 1px solid var(--border);
}
nav p {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0;
    padding: 10px 2em;
    max-width: 800px;
}
nav a {
    color: var(--link-nav);
    text-decoration: none;
    font-weight: 500;
}
nav a:hover { text-decoration: underline; }
section.body {
    padding: 1.5em 2em;
    max-width: 800px;
    margin: 0 auto;
}
@media (max-width: 600px) {
    section.body { padding: 1em; }
    nav p { padding: 10px 1em; }
}
a {
    color: var(--link);
    text-decoration: none;
}
a:hover { text-decoration: underline; }
.topic {
    display: inline-block;
    background-color: var(--bg-topic);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75em;
    font-weight: 500;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}
.topic a {
    text-decoration: none;
    color: var(--text-topic);
}
.date {
    color: var(--text-muted);
    font-size: 0.85em;
    margin-left: 0.3em;
}
.created {
    border-top: 1px solid var(--border);
    padding-top: 0.75em;
    margin-top: 2em;
    font-size: 0.8em;
    color: var(--text-muted);
}
pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    background: var(--bg-code);
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid var(--border);
    font-size: 0.9em;
    line-height: 1.5;
}
code {
    background: var(--bg-inline-code);
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 0.88em;
}
pre code {
    background: none;
    padding: 0;
    border-radius: 0;
    font-size: inherit;
}
table {
    border-collapse: collapse;
    margin: 1em 0;
}
th, td {
    padding: 0.4em 0.8em;
    border: 1px solid var(--border);
}
th { background: var(--bg-th); }
blockquote {
    margin: 1em 0;
    border-left: 4px solid var(--border-blockquote);
    padding: 0.5em 1em;
    color: var(--text-muted);
    background: var(--bg-code);
    border-radius: 0 6px 6px 0;
}
img { max-width: 100%; border-radius: 4px; }
hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5em 0;
}
""")


def update_readme(tils):
    by_topic = {}
    for t in tils:
        by_topic.setdefault(t["topic"], []).append(t)
    index_lines = []
    for topic in sorted(by_topic):
        index_lines.append(f"## {topic}\n")
        for t in sorted(by_topic[topic], key=lambda x: x["created"]):
            index_lines.append(
                f"- [{t['title']}](https://github.com/{REPO}/blob/main/{t['path']}) - {t['created'].strftime('%Y-%m-%d')}"
            )
        index_lines.append("")
    index_text = "\n".join(index_lines)
    count = len(tils)
    readme_path = ROOT / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        content = re.sub(
            r"<!-- count starts -->.*?<!-- count ends -->",
            f"<!-- count starts -->{count}<!-- count ends -->",
            content,
            flags=re.DOTALL,
        )
        content = re.sub(
            r"<!-- index starts -->.*?<!-- index ends -->",
            f"<!-- index starts -->\n{index_text}\n<!-- index ends -->",
            content,
            flags=re.DOTALL,
        )
        readme_path.write_text(content)
    else:
        readme_path.write_text(
            f"""# Today I Learned

Search at <https://til.adamsmith.as/>

<!-- count starts -->{count}<!-- count ends --> TILs so far. [Atom feed](https://til.adamsmith.as/feed.atom).

<!-- index starts -->
{index_text}
<!-- index ends -->
"""
        )


if __name__ == "__main__":
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir()
    (SITE_DIR / ".nojekyll").write_text("")
    (SITE_DIR / "CNAME").write_text("til.adamsmith.as")

    tils = collect_tils()
    write_index(tils)
    write_feed(tils)
    write_css()

    by_topic = {}
    for t in tils:
        by_topic.setdefault(t["topic"], []).append(t)
    for topic, topic_tils in by_topic.items():
        write_topic_page(topic, topic_tils)
        for t in topic_tils:
            write_til_page(t)

    update_readme(tils)
    print(f"Built {len(tils)} TILs into {SITE_DIR}")
