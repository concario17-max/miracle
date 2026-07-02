import re
import json
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import sys

# Reconfigure stdout to prevent encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def extract_odt_text(odt_path, txt_path):
    with zipfile.ZipFile(odt_path, 'r') as z:
        content_xml = z.read('content.xml')
        
    root = ET.fromstring(content_xml)
    
    lines = []
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local in ('p', 'h'):
            text = "".join(elem.itertext()).strip()
            if text:
                lines.append(text)
            else:
                lines.append("")
            
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Extracted ODT text to {txt_path}")

def get_chapter_num(lesson):
    if 221 <= lesson <= 230:
        return 7
    elif 231 <= lesson <= 240:
        return 8
    elif 241 <= lesson <= 250:
        return 9
    elif 251 <= lesson <= 260:
        return 10
    elif 261 <= lesson <= 270:
        return 11
    elif 271 <= lesson <= 280:
        return 12
    elif 281 <= lesson <= 290:
        return 13
    elif 291 <= lesson <= 300:
        return 14
    return None

def parse_commentary(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    commentaries = {}
    
    current_lessons = []
    current_title = ""
    current_keywords = ""
    current_blocks = []
    
    state = "normal"
    emoji_heading_pat = re.compile(r'^([^\x00-\x7F\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f])\s*(.*)')
    
    def save_current_section():
        if not current_lessons:
            return
        
        md_parts = []
        md_parts.append(f"# {current_title}")
        
        if current_keywords:
            md_parts.append(f"🔑 {current_keywords}")
            
        for block_type, heading, text_lines in current_blocks:
            if block_type == "block":
                md_parts.append(f"### {heading}")
                md_parts.append("\n".join(text_lines).strip())
            elif block_type == "summary":
                md_parts.append(f"### {heading}")
                bullet_lines = [f"- {line.strip()}" for line in text_lines if line.strip()]
                md_parts.append("\n".join(bullet_lines))
        
        full_markdown = "\n\n".join(md_parts).strip()
        
        for L in current_lessons:
            ch = get_chapter_num(L)
            if ch:
                key = f"miracle.{ch}.{L}"
                # If duplicate, we just overwrite (like lesson 298)
                commentaries[key] = full_markdown
                
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        if stripped.startswith('[🟢') or stripped.startswith('[🔴'):
            continue
            
        lesson_match = re.match(r'^(\d+)(?:-(\d+))?\.\s*(.*)', stripped)
        if lesson_match:
            save_current_section()
            
            start_num = int(lesson_match.group(1))
            end_num = lesson_match.group(2)
            end_num = int(end_num) if end_num else start_num
            
            current_lessons = list(range(start_num, end_num + 1))
            current_title = stripped
            current_keywords = ""
            current_blocks = []
            state = "normal"
            continue
            
        if current_lessons:
            if stripped.startswith('🔑'):
                kw_match = re.match(r'^🔑\s*(?:핵심\s*키워드:)?\s*(.*)', stripped)
                if kw_match:
                    current_keywords = "핵심 키워드: " + kw_match.group(1).strip()
                continue
                
            if '핵심 요약' in stripped:
                current_blocks.append(("summary", stripped, []))
                state = "summary"
                continue
                
            heading_match = emoji_heading_pat.match(stripped)
            if heading_match and len(stripped) < 80:
                current_blocks.append(("block", stripped, []))
                state = "block"
                continue
                
            if current_blocks:
                current_blocks[-1][2].append(stripped)
            else:
                current_blocks.append(("block", "", [stripped]))
                state = "block"
                
    save_current_section()
    return commentaries

def get_missing_lesson_title(lesson_num):
    # Lookup in reading-data.json
    try:
        with open("public/reading-data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        target_id = f"miracle.14.{lesson_num}"
        for ch in data.get("chapters", []):
            for sub in ch.get("subchapters", []):
                for p in sub.get("paragraphs", []):
                    if p.get("id") == target_id:
                        title_ko = p.get("text", {}).get("korean", "")
                        return title_ko if title_ko else p.get("title", "")
    except Exception as e:
        print(f"Error looking up title for lesson {lesson_num}: {e}")
    return ""

def main():
    odt_path = "기적수업-3.odt"
    txt_path = "scratch/기적수업-3.txt"
    comm_json_path = "public/bodhi-commentary.json"
    raw_comic_dir = "학습만화"
    dest_comic_dir = "src/assets/learning-comic"
    
    # 1. Extract text from ODT
    if os.path.exists(odt_path):
        extract_odt_text(odt_path, txt_path)
    else:
        print(f"Error: {odt_path} not found!")
        return
        
    # 2. Parse commentaries
    new_comms = parse_commentary(txt_path)
    print(f"Parsed {len(new_comms)} keys from {txt_path}")
    
    # 3. Handle missing lesson 299
    missing_lesson = 299
    missing_ch = get_chapter_num(missing_lesson)
    missing_key = f"miracle.{missing_ch}.{missing_lesson}"
    if missing_key not in new_comms:
        title = get_missing_lesson_title(missing_lesson)
        if title:
            placeholder_md = f"# {missing_lesson}. {title}"
        else:
            placeholder_md = f"# {missing_lesson}."
        new_comms[missing_key] = placeholder_md
        print(f"Added placeholder for missing lesson {missing_lesson}: {missing_key} -> '{placeholder_md}'")
        
    # 4. Merge with existing commentary JSON
    if os.path.exists(comm_json_path):
        with open(comm_json_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}
        
    existing_data.update(new_comms)
    
    with open(comm_json_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    print(f"Merged and saved commentaries to {comm_json_path}. Total keys: {len(existing_data)}")
    
    # 5. Copy comic images
    copied_count = 0
    pattern = re.compile(r'^(\d+)')
    
    for f in os.listdir(raw_comic_dir):
        if not f.endswith(".png"):
            continue
            
        match = pattern.match(f)
        if not match:
            continue
            
        num = int(match.group(1))
        
        # We only care about lessons 221 to 300
        if 221 <= num <= 300:
            dest_ch = get_chapter_num(num)
            if dest_ch:
                dest_ch_dir = os.path.join(dest_comic_dir, f"chapter-{dest_ch}")
                os.makedirs(dest_ch_dir, exist_ok=True)
                
                src_file = os.path.join(raw_comic_dir, f)
                dest_webp_name = f[:-4] + ".webp"
                dest_file = os.path.join(dest_ch_dir, dest_webp_name)
                
                if os.path.exists(dest_file):
                    os.remove(dest_file)
                try:
                    from PIL import Image
                    with Image.open(src_file) as img:
                        img.save(dest_file, "WEBP", quality=80)
                    copied_count += 1
                except Exception as e:
                    print(f"Error converting {src_file} to WebP: {e}")
                
    print(f"Copied {copied_count} comic images to {dest_comic_dir}/chapter-7..14/")

if __name__ == "__main__":
    main()
