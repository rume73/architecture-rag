import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS_FILE = os.path.join(BASE_DIR, "data", "urls.json")
RAW_DIR = os.path.join(BASE_DIR, "raw_docs")

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": os.getenv("RAG_USER_AGENT", DEFAULT_USER_AGENT)
}

WIKI_CONTENT_ID = "mw-content-text"
WIKI_PARSER_CLASS = "mw-parser-output"

UNWANTED_SECTIONS = [
    "See also", "References", "External links", "Further reading",
    "Notes", "Bibliography", "Sources", "Citations",
    "См. также", "Примечания", "Ссылки", "Литература",
]


def clean_text(text: str) -> str:
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_paragraphs(soup: BeautifulSoup) -> str:
    content = soup.find(id=WIKI_CONTENT_ID)
    if not content:
        return ""

    body = content.find(class_=WIKI_PARSER_CLASS) or content
    paragraphs = []

    for element in body.find_all(["p", "h2", "h3"]):
        if element.name in ("h2", "h3"):
            heading_text = element.get_text(separator=" ", strip=True)
            if any(skip.lower() in heading_text.lower() for skip in UNWANTED_SECTIONS):
                break
            paragraphs.append(f"\n## {heading_text}\n")
        else:
            text = element.get_text(separator=" ", strip=True)
            text = re.sub(r"\s+", " ", text)
            if text:
                paragraphs.append(text)

    return "\n\n".join(paragraphs)


def fetch_page(url: str) -> str | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERROR] Не удалось скачать {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "lxml")
    text = extract_paragraphs(soup)
    return clean_text(text) if text else None


def parse_all():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    total = 0
    success = 0

    for category, items in urls.items():
        category_dir = os.path.join(RAW_DIR, category)
        os.makedirs(category_dir, exist_ok=True)

        for slug, url in items.items():
            total += 1
            print(f"[{total}] {category}/{slug}")

            text = fetch_page(url)
            if not text:
                print(f"  [SKIP] Пустой текст для {slug}")
                continue

            header = f"# {slug.replace('_', ' ').title()}\n\n"
            filepath = os.path.join(category_dir, f"{slug}.md")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header + text)

            success += 1
            print(f"  [OK] Сохранено: {filepath} ({len(text)} символов)")

            time.sleep(1)

    print(f"\nГотово: {success}/{total} страниц сохранено в {RAW_DIR}")


if __name__ == "__main__":
    parse_all()
