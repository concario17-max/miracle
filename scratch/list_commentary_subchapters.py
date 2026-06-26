import json

with open("j:/홈페이지/bori-1/public/reading-data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for g in data.get("chapters", []):
    if g.get("id") == "commentary":
        print(f"Group: {g.get('title')}")
        for idx, sub in enumerate(g.get("subchapters", [])):
            print(f"  {idx+1}: ID={sub.get('id')}, Title={sub.get('title')}, Paras={len(sub.get('paragraphs', []))}")
