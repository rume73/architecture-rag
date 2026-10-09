import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
TERMS_FILE = os.path.join(BASE_DIR, "terms_map.json")

with open(TERMS_FILE, "r", encoding="utf-8") as f:
    forbidden = list(json.load(f).keys())

pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in forbidden) + r")\b", re.IGNORECASE)

issues = 0
for root, _, files in os.walk(KB_DIR):
    for filename in files:
        if not filename.endswith(".md"):
            continue
        path = os.path.join(root, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        matches = pattern.findall(text)
        if matches:
            issues += 1
            print(f"[LEAK] {path}: {set(matches)}")

print(f"\nФайлов с остатками: {issues}")
