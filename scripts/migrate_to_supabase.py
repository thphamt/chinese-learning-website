import os
import glob
import re
import json
import ssl
import urllib.request
import time

SUPABASE_URL = "https://mzxbospldzbbndqkfalt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16eGJvc3BsZHpiYm5kcWtmYWx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ3MzcyNjcsImV4cCI6MjExMDMxMzI2N30.DWvUkoPg4exdSaC1s-CbRYuex3BRJtk0hc3OL3rPr98"
SSL_CTX = ssl._create_unverified_context()

STANDARD_CHAR_KEYS = [
    "hanzi", "pinyin", "sino_vietnamese", "meaning", "strokes",
    "radical", "level", "mnemonic", "source_step", "lesson_number",
    "lesson_slug", "card_id", "data"
]

def standardize_char(d):
    return {k: d.get(k, None) for k in STANDARD_CHAR_KEYS}

def post_batch(table_name, items, batch_size=100, on_conflict=None):
    if not items:
        return 0
    total_posted = 0
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    if on_conflict:
        headers["Prefer"] = f"resolution=merge-duplicates,return=minimal"

    for i in range(0, len(items), batch_size):
        chunk = items[i:i+batch_size]
        url = f"{SUPABASE_URL}/rest/v1/{table_name}"
        if on_conflict:
            url += f"?on_conflict={on_conflict}"
            
        data_bytes = json.dumps(chunk, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, context=SSL_CTX) as resp:
                total_posted += len(chunk)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"Error posting batch to {table_name} [{i}:{i+len(chunk)}]: {e.code} - {err_body}")
            raise e
        time.sleep(0.05)
    return total_posted

# ----------------- PARSERS -----------------

def parse_radicals():
    print("Parsing 214 radicals from rad214.html...")
    with open("rad214.html", "r", encoding="utf-8") as f:
        r214_html = f.read()

    stroke_sections = re.split(r'<div id=\"r214-stroke-(\d+)\"', r214_html)
    rad_dict = {}
    if len(stroke_sections) > 1:
        for i in range(1, len(stroke_sections), 2):
            strokes = int(stroke_sections[i])
            sec_content = stroke_sections[i+1]
            cards = re.split(r'<div id=\"r214-card-(\d+)\"', sec_content)
            for j in range(1, len(cards), 2):
                num = int(cards[j])
                c_body = cards[j+1][:1000]
                hz = re.search(r'class=\"hanzi-font text-3xl[^\"]*\"[^>]*>([^<]+)</div>', c_body)
                py = re.search(r'class=\"pinyin-text[^\"]*\"[^>]*>([^<]+)</div>', c_body)
                var = re.search(r'class=\"hanzi-font text-sm[^\"]*\"[^>]*>([^<]+)</div>', c_body)
                name = re.search(r'class=\"hanzi-font text-\[10px\][^\"]*\"[^>]*>([^<]+)</div>', c_body)
                mean = re.search(r'class=\"[^\"]*col-meaning-val\"[^>]*>([^<]+)</div>', c_body)
                is_60 = 'title="Có trong 60 bộ cơ bản"' in c_body
                rad_dict[num] = {
                    "number": num,
                    "radical": hz.group(1).strip() if hz else "",
                    "pinyin": py.group(1).strip() if py else "",
                    "sino_vietnamese": name.group(1).strip() if name else None,
                    "meaning": mean.group(1).strip() if mean else "",
                    "strokes": strokes,
                    "variants": var.group(1).strip() if var else None,
                    "is_in_60": is_60,
                    "stage": None,
                    "position": None,
                    "mnemonic": None,
                    "examples": None
                }

    # Enrich from step1.html
    if os.path.exists("step1.html"):
        print("Enriching with 60 core radicals from step1.html...")
        with open("step1.html", "r", encoding="utf-8") as f:
            s1_html = f.read()
        cards = re.split(r'<div id=\"rad-card-(\d+)\"', s1_html)
        for i in range(1, len(cards), 2):
            num = int(cards[i])
            body = cards[i+1][:3500]
            name = re.search(r'class=\"hanzi-font text-base font-semibold[^\"]*\"[^>]*>\(([^)]+)\)</span>', body)
            stage = (num - 1) // 10 + 1
            mean_match = re.search(r'<p class=\"text-xs sm:text-sm text-slate-700 mt-2[^\"]*\">([\s\S]*?)</p>', body)
            meaning = re.sub(r'<[^>]+>', ' ', mean_match.group(1)).strip() if mean_match else ""
            pos_match = re.search(r'VỊ TRÍ:</span>\s*<span[^>]*>([^<]+)</span>', body)
            pos = pos_match.group(1).strip() if pos_match else None

            if num in rad_dict:
                rad_dict[num]["stage"] = stage
                rad_dict[num]["is_in_60"] = True
                if pos:
                    rad_dict[num]["position"] = pos
                if meaning and len(meaning) > len(rad_dict[num]["meaning"]):
                    rad_dict[num]["mnemonic"] = meaning
                if name and not rad_dict[num]["sino_vietnamese"]:
                    rad_dict[num]["sino_vietnamese"] = name.group(1).strip()

    return list(rad_dict.values())

def parse_writing_rules():
    print("Parsing writing rules from step2.html...")
    with open("step2.html", "r", encoding="utf-8") as f:
        s2_html = f.read()

    rules = []
    cards = re.split(r'<div id=\"s2-rule-(\d+)\"', s2_html)
    for i in range(1, len(cards), 2):
        num = int(cards[i])
        body = cards[i+1][:2500]
        title_m = re.search(r'<h3 class=\"[^\"]*\">([^<]+)<span class=\"hanzi-font[^\"]*\"[^>]*>([^<]+)</span></h3>', body)
        py_m = re.search(r'class=\"pinyin-text text-xs[^\"]*\">\(?([^)<]+)\)?</span>', body)
        desc_m = re.search(r'<p class=\"text-xs sm:text-sm text-slate-600 mb-4\">([\s\S]*?)</p>', body)
        examples = re.findall(r'<div class=\"hanzi-font font-bold text-xl[^\"]*\">([^<]+)</div>', body)
        name = ""
        if title_m:
            name = f"{title_m.group(1).strip()} ({title_m.group(2).strip()})"
        desc = re.sub(r'<[^>]+>', ' ', desc_m.group(1)).strip() if desc_m else ""
        rules.append({
            "rule_number": num,
            "name": name,
            "pinyin": py_m.group(1).strip() if py_m else "",
            "description": desc,
            "examples": examples
        })
    return rules

def parse_step3_characters():
    print("Parsing 93 HSK 1 characters from step3.html...")
    with open("step3.html", "r", encoding="utf-8") as f:
        s3_html = f.read()

    chars = []
    blocks = re.split(r'<div id=\"s3-char-(\d+)\"', s3_html)
    for i in range(1, len(blocks), 2):
        num = int(blocks[i])
        body = blocks[i+1][:2500]
        hz_m = re.search(r'class=\"hanzi-font text-2xl font-bold\"[^\"]*\"[^>]*>([^<]+)</span>', body)
        py_m = re.search(r'class=\"pinyin-text text-lg font-extrabold[^\"]*\">([^<]+)</span>', body)
        mean_m = re.search(r'class=\"text-sm font-bold text-slate-800 col-meaning-val\">([^<]+)</span>', body)
        rad_m = re.search(r'Bộ thủ:\s*<strong>([^<]+)</strong>\s*·\s*(\d+)\s*nét', body)
        mnem_m = re.search(r'💡\s*([^<]+)</div>', body)

        chars.append(standardize_char({
            "hanzi": hz_m.group(1).strip() if hz_m else "",
            "pinyin": py_m.group(1).strip() if py_m else "",
            "meaning": mean_m.group(1).strip().lstrip("· ") if mean_m else "",
            "strokes": int(rad_m.group(2)) if rad_m else None,
            "radical": rad_m.group(1).strip() if rad_m else None,
            "mnemonic": mnem_m.group(1).strip() if mnem_m else None,
            "level": "HSK 1",
            "source_step": 3,
            "lesson_number": (num - 1) // 8 + 1,
            "lesson_slug": f"step3-lesson-{(num - 1) // 8 + 1}",
            "card_id": f"s3-char-{num}",
            "data": None
        }))
    return chars

def parse_step4_characters():
    print("Parsing Step 4 Look & Learn characters...")
    files = sorted(glob.glob("lessons/step4-lesson-*.html"))
    all_chars = []
    for fp in files:
        m_fn = re.search(r'step4-lesson-(\d+)\.html', fp)
        les_num = int(m_fn.group(1)) if m_fn else 0
        slug = f"step4-lesson-{les_num}"
        with open(fp, "r", encoding="utf-8") as f:
            html = f.read()

        cards = re.findall(r'<div (?:id=\"([^\"]+)\" class=\"cc\"|class=\"cc\" id=\"([^\"]+)\")>([\s\S]*?)(?=<div (?:id=\"[^\"]+\" class=\"cc\"|class=\"cc\" id=\"[^\"]+\")|</body>)', html)
        for c_match in cards:
            cid = c_match[0] or c_match[1]
            body = c_match[2]
            hz = re.search(r'class=\"[^\"]*hanzi-font[^\"]*\"[^>]*>([^<]+)<', body)
            py = re.search(r'class=\"pinyin-text font-extrabold[^\"]*\"[^>]*>([^<]+)</span>', body)
            mean = re.search(r'class=\"[^\"]*col-meaning-val\"[^>]*>([^<]+)</div>', body)
            st_match = re.search(r'class=\"st-bd\">.*?(\d+)\s*nét</span>', body)
            
            # Words
            words = []
            w_matches = re.findall(r'<div class=\"pinyin-text[^\"]*\">([^<]+)</div>\s*<div>\s*<span class=\"hanzi-font font-bold[^\"]*\">([^<]+)</span>\s*<span class=\"text-xs text-slate-600 col-meaning-val\">\s*:\s*([^<]+)</span>', body)
            for wp, wh, wm in w_matches:
                words.append({"hanzi": wh.strip(), "pinyin": wp.strip(), "meaning": wm.strip()})

            all_chars.append(standardize_char({
                "hanzi": hz.group(1).strip() if hz else "",
                "pinyin": py.group(1).strip() if py else "",
                "meaning": mean.group(1).strip() if mean else "",
                "strokes": int(st_match.group(1)) if st_match else None,
                "source_step": 4,
                "lesson_number": les_num,
                "lesson_slug": slug,
                "card_id": cid,
                "mnemonic": None,
                "data": {"words": words} if words else None
            }))
    return all_chars

def parse_step5_characters():
    print("Parsing Step 5 Từ ghép HSK characters...")
    files = sorted(glob.glob("lessons/step5-lesson-*.html"))
    all_chars = []
    for fp in files:
        m_fn = re.search(r'step5-lesson-(\d+)\.html', fp)
        les_num = int(m_fn.group(1)) if m_fn else 0
        slug = f"step5-lesson-{les_num}"
        with open(fp, "r", encoding="utf-8") as f:
            html = f.read()

        cards = re.findall(r'<div (?:id=\"([^\"]+)\" class=\"cc\"|class=\"cc\" id=\"([^\"]+)\")>([\s\S]*?)(?=<div (?:id=\"[^\"]+\" class=\"cc\"|class=\"cc\" id=\"[^\"]+\")|</body>)', html)
        for c_match in cards:
            cid = c_match[0] or c_match[1]
            body = c_match[2]
            hz = re.search(r'class=\"[^\"]*hanzi-font[^\"]*\"[^>]*>([^<]+)<', body)
            py = re.search(r'class=\"pinyin-text font-extrabold[^\"]*\"[^>]*>([^<]+)</span>', body)
            mean = re.search(r'class=\"[^\"]*col-meaning-val\"[^>]*>([^<]+)</div>', body)
            st_match = re.search(r'class=\"st-bd\">.*?(\d+)\s*nét</span>', body)
            tip_match = re.search(r'<div class=\"cc-tip\">([\s\S]*?)</div>', body)
            words_match = re.search(r'<div class=\"cc-wd\">([\s\S]*?)</div>', body)
            tip = re.sub(r'<[^>]+>', ' ', tip_match.group(1)).strip() if tip_match else None
            words_text = re.sub(r'<[^>]+>', ' ', words_match.group(1)).strip() if words_match else None

            all_chars.append(standardize_char({
                "hanzi": hz.group(1).strip() if hz else "",
                "pinyin": py.group(1).strip() if py else "",
                "meaning": mean.group(1).strip() if mean else "",
                "strokes": int(st_match.group(1)) if st_match else None,
                "source_step": 5,
                "lesson_number": les_num,
                "lesson_slug": slug,
                "card_id": cid,
                "mnemonic": tip,
                "data": {"compound_words": words_text} if words_text else None
            }))
    return all_chars

def parse_step6_characters_and_topics():
    print("Parsing Step 6 150 topics and characters...")
    files = sorted(glob.glob("lessons/step6-topic-*.html"))
    all_chars = []
    all_topics = []
    for fp in files:
        m_fn = re.search(r'step6-topic-(\d+)\.html', fp)
        top_num = int(m_fn.group(1)) if m_fn else 0
        with open(fp, "r", encoding="utf-8") as f:
            html = f.read()

        t_match = re.search(r'<title>([^<]+)</title>', html)
        title = t_match.group(1) if t_match else f"Topic #{top_num}"

        # characters
        cards = re.findall(r'<div (?:id=\"([^\"]+)\" class=\"cc\"|class=\"cc\" id=\"([^\"]+)\")>([\s\S]*?)(?=<div (?:id=\"[^\"]+\" class=\"cc\"|class=\"cc\" id=\"[^\"]+\")|id=\"s6-sec-vocab\"|</body>)', html)
        for c_match in cards:
            cid = c_match[0] or c_match[1]
            body = c_match[2]
            hz = re.search(r'class=\"[^\"]*hanzi-font[^\"]*\"[^>]*>([^<]+)<', body)
            py = re.search(r'class=\"pinyin-text font-extrabold[^\"]*\"[^>]*>([^<]+)</span>', body)
            mean = re.search(r'class=\"[^\"]*col-meaning-val\"[^>]*>([^<]+)</div>', body)
            w_match = re.search(r'<div class=\"cc-wd\">([\s\S]*?)</div>', body)
            w_text = re.sub(r'<[^>]+>', ' ', w_match.group(1)).strip() if w_match else None

            all_chars.append(standardize_char({
                "hanzi": hz.group(1).strip() if hz else "",
                "pinyin": py.group(1).strip() if py else "",
                "meaning": mean.group(1).strip() if mean else "",
                "source_step": 6,
                "lesson_number": top_num,
                "lesson_slug": f"step6-topic-{top_num}",
                "card_id": cid,
                "data": {"topic_word": w_text} if w_text else None
            }))

        # vocab list
        v_raw = re.findall(r'<span class=\"pinyin-text[^\"]*\">([^<]+)</span>[\s\S]*?<span class=\"hanzi-font[^\"]*\">([^<]+)</span>[\s\S]*?<div class=\"[^\"]*col-meaning-val\"[^>]*>([^<]+)</div>', html)
        vocab_items = []
        for vp, vh, vm in v_raw:
            vocab_items.append({"hanzi": vh.strip(), "pinyin": vp.strip(), "meaning": vm.strip()})

        all_topics.append({
            "topic_number": top_num,
            "title": title,
            "vocabulary": vocab_items
        })
    return all_chars, all_topics

def main():
    start_time = time.time()
    print("=== STARTING FULL DATABASE MIGRATION TO SUPABASE ===")

    # 1. Radicals
    radicals = parse_radicals()
    print(f"Loaded {len(radicals)} radicals. Posting to Supabase...")
    post_batch("radicals", radicals)
    print(f"✓ Successfully stored {len(radicals)} radicals!")

    # 2. Writing Rules
    rules = parse_writing_rules()
    print(f"Loaded {len(rules)} writing rules. Posting to Supabase...")
    post_batch("writing_rules", rules, on_conflict="rule_number")
    print(f"✓ Successfully stored {len(rules)} writing rules!")

    # 3. Characters
    s3_chars = parse_step3_characters()
    s4_chars = parse_step4_characters()
    s5_chars = parse_step5_characters()
    s6_chars, s6_topics = parse_step6_characters_and_topics()

    all_characters = s3_chars + s4_chars + s5_chars + s6_chars
    all_characters = [c for c in all_characters if c["hanzi"]]
    print(f"Total characters to insert: {len(all_characters)} (Step 3: {len(s3_chars)}, Step 4: {len(s4_chars)}, Step 5: {len(s5_chars)}, Step 6: {len(s6_chars)})")

    # Clear characters first if any existed
    post_batch("characters", all_characters, batch_size=100)
    print(f"✓ Successfully stored {len(all_characters)} characters!")

    # 4. Topics
    print(f"Loaded {len(s6_topics)} topics. Posting to Supabase...")
    post_batch("topics", s6_topics, batch_size=50, on_conflict="topic_number")
    print(f"✓ Successfully stored {len(s6_topics)} topics!")

    elapsed = time.time() - start_time
    print(f"=== MIGRATION COMPLETED IN {elapsed:.1f}s ===")

if __name__ == "__main__":
    main()
