import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("j:/홈페이지/bori-1/public/reading-data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for ch in data.get("chapters", []):
    print(f"Group ID={ch.get('id')}, Title={ch.get('title') or ch.get('chapterName')}")
    for idx, sub in enumerate(ch.get("subchapters", [])):
        print(f"  Subchapter {idx+1}: ID={sub.get('id')}, Title={sub.get('title')}, Paras={len(sub.get('paragraphs', []))}")
