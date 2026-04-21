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

md = mistune.create_markdown(
    plugins=["table", "fenced_code", "footnotes", "strikethrough"]
)


def git_file_times(filepath):
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%cI", "--", filepath],
        capture_output=True,
        text=True,
    )
    dates = result.stdout.strip().split("\n")
    if not dates or dates[0] == "":
        return None, None
    updated = datetime.fromisoformat(dates[0])
    created = datetime.fromisoformat(dates[-1])
    return created, updated


def collect_tils():
    tils = []
    for filepath in sorted(ROOT.glob("*/*.md")):
        path = str(filepath.relative_to(ROOT))
        topic = path.split("/")[0]
        slug = filepath.stem
        lines = filepath.read_text().split("\n")
        title = lines[0].lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()
        created, updated = git_file_times(path)
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
body {
    font-family: "Helvetica Neue", helvetica, sans-serif;
    line-height: 1.5;
    margin: 0;
    padding: 0;
    color: #333;
}
h1, h2, h3 { font-family: Georgia, 'Times New Roman', Times, serif; }
nav {
    background: linear-gradient(to bottom, #2c3e50, #34495e);
    color: white;
}
nav p {
    display: flex;
    justify-content: space-between;
    margin: 0;
    padding: 8px 2em;
}
nav a { color: white; text-decoration: none; }
nav a:hover { text-decoration: underline; }
section.body {
    padding: 1em 2em;
    max-width: 800px;
}
@media (max-width: 600px) {
    section.body { padding: 0.5em 1em; }
    nav p { padding: 8px 1em; }
}
.topic {
    background-color: #e0e0e0;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.75em;
}
.topic a { text-decoration: none; color: #555; }
.date { color: #999; font-size: 0.85em; }
.created {
    border-top: 1px solid #ddd;
    padding-top: 0.5em;
    font-size: 0.8em;
    color: #666;
}
pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    background: #f5f5f5;
    padding: 1em;
    border-radius: 4px;
    overflow-x: auto;
}
code {
    background: #f0f0f0;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 0.9em;
}
pre code { background: none; padding: 0; }
a { color: #2c3e50; }
table { border-collapse: collapse; }
th, td { padding: 0.3em 0.6em; border: 1px solid #ddd; }
th { background: #f5f5f5; }
blockquote {
    margin: 1em 0;
    border-left: 4px solid #2c3e50;
    padding-left: 1em;
    color: #555;
}
img { max-width: 100%; }
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
