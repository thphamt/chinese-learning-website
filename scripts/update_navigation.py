import os
import re
import glob

def get_root_nav(active_step):
    def act(s):
        return ' is-active' if s == active_step else ''

    return f'''      <nav aria-label="Lộ trình 5 bước Hán tự" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
        <a href="index.html" class="step-nav-card{act(1)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 1</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">60 bộ thủ</div></a>
        <a href="step3.html" class="step-nav-card{act(2)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 2</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">93 chữ HSK 1</div></a>
        <a href="step4.html" class="step-nav-card{act(3)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 3</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">Chiết tự Hán tự</div></a>
        <a href="step5.html" class="step-nav-card{act(4)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 4</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">Từ ghép HSK</div></a>
        <a href="step6.html" class="step-nav-card{act(5)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 5</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">150 Chủ đề</div></a>
        <a href="methods.html" class="step-nav-card{act(6)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Cách học khác</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">Học chữ đa chiều</div></a>
      </nav>'''

def get_lesson_nav(active_step):
    def act(s):
        return ' is-active' if s == active_step else ''

    return f'''      <nav aria-label="Lộ trình 5 bước Hán tự" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
        <a href="../index.html" class="step-nav-card{act(1)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 1</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">60 bộ thủ</div></a>
        <a href="../step3.html" class="step-nav-card{act(2)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 2</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">93 chữ HSK 1</div></a>
        <a href="../step4.html" class="step-nav-card{act(3)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 3</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">Chiết tự Hán tự</div></a>
        <a href="../step5.html" class="step-nav-card{act(4)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 4</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">Từ ghép HSK</div></a>
        <a href="../step6.html" class="step-nav-card{act(5)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 5</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">150 Chủ đề</div></a>
        <a href="../methods.html" class="step-nav-card{act(6)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Cách học khác</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">Học chữ đa chiều</div></a>
      </nav>'''

nav_pattern = re.compile(r'<nav aria-label="[^"]*" class="[^"]*grid-cols-[^"]*">.*?</nav>', re.DOTALL)

# Root files
root_map = {
    'index.html': 1,
    'step1.html': 1,
    'rad214.html': 1,
    'Chinese-website.html': 1,
    'all-steps.html': 0,
    'step3.html': 2,
    'step4.html': 3,
    'step5.html': 4,
    'step6.html': 5,
    'methods.html': 6
}

for fpath, active_num in root_map.items():
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_nav = get_root_nav(active_num)
    content = nav_pattern.sub(new_nav, content, count=1)
    
    # Specific link fixes in index.html and others
    if fpath in ['index.html', 'step1.html']:
        content = content.replace('href="step2.html"', 'href="step3.html"')
        content = content.replace('Sang Bước 2: Cách viết Hán tự →', 'Sang Bước 2: 93 chữ HSK 1 →')
    elif fpath == 'step3.html':
        content = content.replace('href="step2.html"', 'href="index.html"')
        content = content.replace('← Quay lại Bước 2: Cách viết Hán tự', '← Quay lại Bước 1: 60 bộ thủ')
        content = content.replace('Sang Bước 4: Look & Learn →', 'Sang Bước 3: Chiết tự Hán tự →')
        content = content.replace('Bước 3: Hán Tự Nhập Môn (93 Chữ HSK 1)', 'Bước 2: Hán Tự Nhập Môn (93 Chữ HSK 1)')
        content = content.replace('BƯỚC 3: HÁN TỰ NHẬP MÔN', 'BƯỚC 2: HÁN TỰ NHẬP MÔN')
    elif fpath == 'step4.html':
        content = content.replace('← Bước 3', '← Bước 2: 93 chữ')
        content = content.replace('Bước 4: Hanzi Look and Learn', 'Bước 3: Chiết tự Hán tự (Building Blocks)')
        content = content.replace('BƯỚC 4: HANZI LOOK AND LEARN', 'BƯỚC 3: CHIẾT TỰ HÁN TỰ (BUILDING BLOCKS)')
    elif fpath == 'step5.html':
        content = content.replace('← Bước 4', '← Bước 3: Chiết tự')
        content = content.replace('Bước 5: Hán tự & từ ghép', 'Bước 4: Hán tự & từ ghép')
        content = content.replace('BƯỚC 5: HÁN TỰ & TỪ GHÉP', 'BƯỚC 4: HÁN TỰ & TỪ GHÉP')
    elif fpath == 'step6.html':
        content = content.replace('← Bước 5', '← Bước 4: Từ ghép')
        content = content.replace('Bước 6: 150 Chủ đề', 'Bước 5: 150 Chủ đề')
        content = content.replace('BƯỚC 6: 150 CHỦ ĐỀ', 'BƯỚC 5: 150 CHỦ ĐỀ')

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated root {fpath}")

# Lessons files
lesson_files = glob.glob('lessons/*.html')
for lf in lesson_files:
    active_num = 0
    if 'step3' in lf:
        active_num = 2
    elif 'step4' in lf:
        active_num = 3
    elif 'step5' in lf:
        active_num = 4
    elif 'step6' in lf:
        active_num = 5
    elif 'method' in lf:
        active_num = 6
        
    with open(lf, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_nav = get_lesson_nav(active_num)
    content = nav_pattern.sub(new_nav, content, count=1)
    
    with open(lf, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Updated {len(lesson_files)} lesson files.")
