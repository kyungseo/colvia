"""Refresh the repository index links to the frozen earlier-profile instructions."""
import argparse
import html
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs/README.md"
EARLIER = ROOT / "docs/earlier-profile.md"
START = "<!-- Earlier-profile anchor links: maintained by scripts/sync-first-work-guides.py. -->"
END = "<!-- End earlier-profile anchor links -->"
FENCES = re.compile(r"^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1[ \t]*$", re.M | re.S)


def earlier_anchors(text):
    text = FENCES.sub("", text)
    counts = {}
    anchors = dict.fromkeys(re.findall(r'<a[^>]+\b(?:id|name)="([^"]+)"', text), None)
    for title in re.findall(r"^#{1,6} +(.+?) *$", text, re.M):
        title = re.sub(r"<[^>]+>", "", title)
        title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
        slug = "".join(c for c in title.strip().lower()
                       if c in " -_" or unicodedata.category(c)[0] in "LNM").replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors[slug if count == 0 else f"{slug}-{count}"] = title
    return anchors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="refresh the repository index links")
    args = parser.parse_args()
    current = INDEX.read_text(encoding="utf-8")
    if current.count(START) != 1 or current.count(END) != 1:
        raise SystemExit("Expected one pair of earlier-profile markers in docs/README.md")
    before, rest = current.split(START)
    _, after = rest.split(END)
    active = earlier_anchors(before + after)
    aliases = []
    for anchor, title in earlier_anchors(EARLIER.read_text(encoding="utf-8")).items():
        if anchor not in active:
            fragment = quote(anchor, safe="-_")
            identifier = html.escape(anchor, quote=True)
            aliases.append(f'- <a id="{identifier}" name="{identifier}"></a>[{title or anchor}](earlier-profile.md#{fragment})')
    panel = ["<details>", "<summary>Earlier section links · 이전 문서 바로가기</summary>", "",
             *aliases, "", "</details>"]
    expected = before + "\n\n".join((START, "\n".join(panel), END)) + after
    if current != expected:
        if not args.write:
            raise SystemExit("Earlier-profile links differ. Run scripts/sync-first-work-guides.py --write.")
        INDEX.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
