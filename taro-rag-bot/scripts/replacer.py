import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw_docs")
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
TERMS_FILE = os.path.join(BASE_DIR, "terms_map.json")


def load_terms():
    with open(TERMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_pattern(terms_map):
    sorted_terms = sorted(terms_map.keys(), key=len, reverse=True)
    pattern = r"\b(" + "|".join(re.escape(t) for t in sorted_terms) + r")\b"
    return re.compile(pattern, flags=re.IGNORECASE)


def replace_text(text, terms_map, pattern):
    def _sub(match):
        original = match.group(0)
        replacement = terms_map.get(original)
        if replacement is None:
            for k, v in terms_map.items():
                if k.lower() == original.lower():
                    replacement = v
                    break
            else:
                return original
        if original[0].isupper() and replacement[0].islower():
            replacement = replacement[0].upper() + replacement[1:]
        return replacement

    return pattern.sub(_sub, text)


def process_all():
    terms_map = load_terms()
    pattern = build_pattern(terms_map)

    total, changed = 0, 0

    for root, _, files in os.walk(RAW_DIR):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            src_path = os.path.join(root, filename)
            rel_path = os.path.relpath(src_path, RAW_DIR)
            dst_path = os.path.join(KB_DIR, rel_path)

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            with open(src_path, "r", encoding="utf-8") as f:
                original_text = f.read()

            new_text = replace_text(original_text, terms_map, pattern)

            with open(dst_path, "w", encoding="utf-8") as f:
                f.write(new_text)

            total += 1
            if new_text != original_text:
                changed += 1
                print(f"[OK] {rel_path}")
            else:
                print(f"[WARN] {rel_path} — замен не найдено")

    print(f"\nГотово: обработано {total} файлов, изменено {changed}")


if __name__ == "__main__":
    process_all()
