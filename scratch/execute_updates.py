import os
import shutil
import re
import json

def get_chapter_num(lesson):
    if 61 <= lesson <= 80:
        return 2
    elif 91 <= lesson <= 110:
        return 3
    elif 121 <= lesson <= 140:
        return 4
    elif 151 <= lesson <= 170:
        return 5
    elif 181 <= lesson <= 200:
        return 6
    return None

def clear_dir(path):
    if os.path.exists(path):
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        os.makedirs(path, exist_ok=True)

def copy_comics():
    raw_root = "학습만화"
    comic_root = "src/assets/learning-comic"
    
    # 1. Clear chapter-2
    chapter_2_path = os.path.join(comic_root, "chapter-2")
    clear_dir(chapter_2_path)
    print("Cleared chapter-2 legacy images.")
    
    # Ensure chapter dirs exist
    for ch in range(1, 7):
        os.makedirs(os.path.join(comic_root, f"chapter-{ch}"), exist_ok=True)
        
    # Copy images
    copied_count = 0
    pattern = re.compile(r'^(\d+)')
    
    for f in os.listdir(raw_root):
        if not f.endswith(".png"):
            continue
            
        match = pattern.match(f)
        if not match:
            continue
            
        num = int(match.group(1))
        
        # Determine destination chapter
        dest_ch = None
        if 1 <= num <= 50:
            dest_ch = 1
        elif 61 <= num <= 80:
            dest_ch = 2
        elif 91 <= num <= 110:
            dest_ch = 3
        elif 121 <= num <= 140:
            dest_ch = 4
        elif 151 <= num <= 170:
            dest_ch = 5
        elif 181 <= num <= 200:
            dest_ch = 6
            
        if dest_ch:
            src_file = os.path.join(raw_root, f)
            dest_webp_name = f[:-4] + ".webp"
            dest_file = os.path.join(comic_root, f"chapter-{dest_ch}", dest_webp_name)
            
            try:
                from PIL import Image
                with Image.open(src_file) as img:
                    img.save(dest_file, "WEBP", quality=80)
                copied_count += 1
            except Exception as e:
                print(f"Error converting {src_file} to WebP: {e}")
            
    print(f"Copied {copied_count} comic images to src/assets/learning-comic/.")

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

def merge_and_save_commentary(new_comms):
    comm_json_path = "public/bodhi-commentary.json"
    
    if os.path.exists(comm_json_path):
        with open(comm_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}
        
    data.update(new_comms)
    
    with open(comm_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved merged commentaries to {comm_json_path}. Total keys: {len(data)}")

def main():
    # 1. Copy comic images
    copy_comics()
    
    # 2. Parse commentaries from scratch/기적수업-2.txt
    new_comms = parse_commentary("scratch/기적수업-2.txt")
    print(f"Parsed {len(new_comms)} commentary keys from scratch/기적수업-2.txt")
    
    # 3. Merge and save commentaries
    merge_and_save_commentary(new_comms)

if __name__ == "__main__":
    main()
