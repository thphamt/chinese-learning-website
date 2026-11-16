import re
import glob

def clean_svg_illustrations(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern matching the cartoon SVG box
    pattern = re.compile(r'<div class="p-2\.5 rounded-xl bg-slate-50 border border-slate-200 mt-2"><div class="flex items-center gap-2 mb-1"><svg viewBox="0 0 120 80".*?</div></div>', re.DOTALL)

    def repl(m):
        block = m.group(0)
        # Find the text in the last div
        last_div_match = re.search(r'>([^<]+)</div></div>$', block)
        if last_div_match:
            tip = last_div_match.group(1).strip()
        else:
            tip = "Cấu tạo từ các nét và bộ thủ thành phần."
        return f'<div class="cc-tip"><b>💡 Gợi nhớ chiết tự:</b> {tip}</div>'

    new_content, count = pattern.subn(repl, content)
    print(f"{filepath}: replaced {count} illustration blocks.")
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

files = ['step4.html', 'all-steps.html', 'lessons/step4-lesson-1.html', 'lessons/step4-all.html']
for f in files:
    clean_svg_illustrations(f)
