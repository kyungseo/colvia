"""Check the two user guides embedded in the fixed installed documentation inventory."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs/README.md"
START = "<!-- First Work guides: edit manual/en or manual/ko, then run scripts/sync-first-work-guides.py --write. -->"
END = "<!-- End first Work guides -->"
SECTIONS = {
    "en": {"Before you begin": "setup", "Yesterday · agree on the change": "plan",
           "Today · make the decision": "review", "Update, Recovery And Removal": "recovery"},
    "ko": {"시작하기 전에": "setup", "어제 · 어디까지 맡길지 정하기": "plan",
           "오늘 · 새 대화에서 결정하기": "review", "다시 쓰거나 잠시 쉴 때": "recovery"},
}
NAV = {
    "en": "[한국어](#guide-ko) · English · [About Colvia](../README.md)",
    "ko": "한국어 · [English](#guide-en) · [제품 소개](#colvia는-무엇을-기억하나요)",
}
CONCEPT = {"en": "CONCEPTS.md#what-colvia-remembers", "ko": "#colvia는-무엇을-기억하나요"}


def anchor(target):
    return f'<a id="{target}" name="{target}"></a>'


def chapter(language):
    source = ROOT / "manual" / language / "getting-started.md"
    title, navigation, body = source.read_text(encoding="utf-8").strip().split("\n\n", 2)
    if not title.startswith("# ") or not navigation.startswith("["):
        raise ValueError(f"Missing title or language navigation in {source.name}")
    body = re.sub(r"\n+<!-- en_content_sha256: [0-9a-f]{64} -->\Z", "", body)
    body = body.replace("](README.md)", "](../README.md#한국어)" if language == "ko" else "](../README.md#english)")
    body = body.replace("](understand.md)", f"]({CONCEPT[language]})")
    body = body.replace("](project-setup.md)", f"](#setup-{language})")
    body = body.replace(f"](project-setup.md#maintenance-{language})", f"](#maintenance-{language})")
    body = body.replace("](resume.md)", f"](#resume-{language})")
    headings = re.findall(r"^## (.+)$", body, re.MULTILINE)
    if headings != list(SECTIONS[language]):
        raise ValueError(f"Update the installed navigation for the headings in {source}")
    for heading, slug in SECTIONS[language].items():
        target = anchor(f"guide-{language}-{slug}")
        body = body.replace(f"\n## {heading}\n", f"\n{target}\n\n### {heading}\n")
    return f"{anchor('guide-' + language)}\n\n#{title}\n\n{NAV[language]}\n\n{body}"


def setup_chapter(language):
    source = ROOT / "manual" / language / "project-setup.md"
    title, _, body = source.read_text(encoding="utf-8").strip().split("\n\n", 2)
    body = re.sub(r"\n+<!-- en_content_sha256: [0-9a-f]{64} -->\Z", "", body)
    body = body.replace("](README.md)", "](../README.md#한국어)" if language == "ko" else "](../README.md#english)")
    nav = "[한국어](#setup-ko) · English" if language == "en" else "한국어 · [English](#setup-en)"
    return f"{anchor('setup-' + language)}\n\n#{title}\n\n{nav}\n\n{body}"


def feature_chapter(language):
    source = ROOT / "manual" / language / "work-guide.md"
    title, _, body = source.read_text(encoding="utf-8").strip().split("\n\n", 2)
    body = re.sub(r"\n+<!-- en_content_sha256: [0-9a-f]{64} -->\Z", "", body)
    if language == "en":
        nav = "[한국어](#features-ko) · English · [First Work](#guide-en) · [How Colvia works](CONCEPTS.md#how-colvia-works-with-an-agent)"
    else:
        nav = "한국어 · [English](#features-en) · [첫 작업](#guide-ko) · [Colvia의 구조](#에이전트와-colvia가-함께-일하는-방식)"
    body = body.replace("](README.md)", "](../README.md#한국어)" if language == "ko" else "](../README.md#english)")
    body = re.sub(r"^(#{2,3}) ", r"#\1 ", body, flags=re.MULTILINE)
    body = re.sub(r"^#### 4\.", anchor("resume-" + language) + "\n\n#### 4.", body, count=1, flags=re.MULTILINE)
    return f"{anchor('features-' + language)}\n\n#{title}\n\n{nav}\n\n{body}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="refresh both installed chapters")
    args = parser.parse_args()
    current = INDEX.read_text(encoding="utf-8")
    if current.count(START) != 1 or current.count(END) != 1:
        raise SystemExit("Expected one pair of guide markers in docs/README.md")
    before, rest = current.split(START)
    _, after = rest.split(END)
    korean_entry = "## 한국어\n\n[첫 작업 따라 하기](#guide-ko) · [쉬운 설명](#colvia는-무엇을-기억하나요) · [엔지니어를 위한 구조 안내](#에이전트와-colvia가-함께-일하는-방식)"
    expected = before + "\n\n".join((START, chapter("en"), setup_chapter("en"), feature_chapter("en"), korean_entry, chapter("ko"), setup_chapter("ko"), feature_chapter("ko"), END)) + after
    if current != expected:
        if not args.write:
            raise SystemExit("Installed guides differ from the source manuals. Run with --write.")
        INDEX.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
