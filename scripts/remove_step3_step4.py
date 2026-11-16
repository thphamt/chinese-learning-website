import os
import re
import glob

# 1. New navigation templates
def get_root_nav(active_step):
    def act(s):
        return ' is-active' if s == active_step else ''

    return f'''      <nav aria-label="Lộ trình 3 bước Hán tự" class="grid grid-cols-2 md:grid-cols-4 gap-2">
        <a href="index.html" class="step-nav-card{act(1)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 1</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">60 bộ thủ</div></a>
        <a href="step3.html" class="step-nav-card{act(2)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 2</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">93 chữ HSK 1</div></a>
        <a href="step6.html" class="step-nav-card{act(3)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 3</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">150 Chủ đề</div></a>
        <a href="methods.html" class="step-nav-card{act(4)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Cách học khác</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">Học chữ đa chiều</div></a>
      </nav>'''

def get_lesson_nav(active_step):
    def act(s):
        return ' is-active' if s == active_step else ''

    return f'''      <nav aria-label="Lộ trình 3 bước Hán tự" class="grid grid-cols-2 md:grid-cols-4 gap-2">
        <a href="../index.html" class="step-nav-card{act(1)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 1</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">60 bộ thủ</div></a>
        <a href="../step3.html" class="step-nav-card{act(2)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 2</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">93 chữ HSK 1</div></a>
        <a href="../step6.html" class="step-nav-card{act(3)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Bước 3</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">150 Chủ đề</div></a>
        <a href="../methods.html" class="step-nav-card{act(4)}"><div class="step-sub text-[11px] text-slate-500 font-bold uppercase tracking-wider">Cách học khác</div><div class="step-title font-extrabold text-xs sm:text-sm mt-0.5 leading-snug text-slate-900">Học chữ đa chiều</div></a>
      </nav>'''

nav_pattern = re.compile(r'<nav aria-label="[^"]*" class="[^"]*grid-cols-[^"]*">.*?</nav>', re.DOTALL)

# 2. Redirect page template for step4 and step5
def get_redirect_page(target_url, title_text, reason_text):
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="0; url={target_url}">
  <title>{title_text} · VNCHINESECLUB</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
  <script>window.location.replace("{target_url}");</script>
</head>
<body class="min-h-screen flex items-center justify-center p-6 bg-[#F7F8FC]">
  <div class="max-w-md w-full bg-white p-8 rounded-3xl border border-slate-200 shadow-xl text-center space-y-4">
    <div class="w-14 h-14 mx-auto rounded-2xl bg-[#12131F] text-white flex items-center justify-center text-2xl font-bold">字</div>
    <h1 class="text-xl font-bold text-slate-900">{title_text}</h1>
    <p class="text-sm text-slate-600 leading-relaxed">
      {reason_text}
    </p>
    <div>
      <a href="{target_url}" class="btn-nxt inline-block px-6 py-2.5">Tiếp tục lộ trình Hán tự →</a>
    </div>
  </div>
</body>
</html>'''

# Write redirects for step4.html and step5.html
with open('step4.html', 'w', encoding='utf-8') as f:
    f.write(get_redirect_page('step6.html', 'Chuyển hướng sang Bước 3: 150 Chủ đề', 'Lộ trình đã được tinh gọn sang 3 bước trực tiếp (Bộ thủ → Hán tự sơ cấp → 150 Chủ đề thực tế).'))

with open('step5.html', 'w', encoding='utf-8') as f:
    f.write(get_redirect_page('step6.html', 'Chuyển hướng sang Bước 3: 150 Chủ đề', 'Lộ trình đã được tinh gọn sang 3 bước trực tiếp (Bộ thủ → Hán tự sơ cấp → 150 Chủ đề thực tế).'))

print("Updated redirects for step4.html and step5.html")

# 3. Update root files
root_map = {
    'index.html': 1,
    'step1.html': 1,
    'rad214.html': 1,
    'Chinese-website.html': 1,
    'all-steps.html': 0,
    'step3.html': 2,
    'step6.html': 3,
    'methods.html': 4
}

for fpath, active_num in root_map.items():
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = nav_pattern.sub(get_root_nav(active_num), content, count=1)
    
    if fpath == 'step3.html':
        content = content.replace('Sang Bước 4: Look & Learn →', 'Sang Bước 3: 150 Chủ đề →')
        content = content.replace('Sang Bước 4: Hanzi Look and Learn →', 'Sang Bước 3: 150 Chủ đề →')
        content = content.replace('Sang Bước 3: Chiết tự Hán tự →', 'Sang Bước 3: 150 Chủ đề →')
        content = content.replace('href="step4.html"', 'href="step6.html"')
        content = content.replace('← Bước 2: Cách viết Hán tự', '← Bước 1: 60 bộ thủ')
        content = content.replace('← Quay lại Bước 2: Cách viết Hán tự', '← Quay lại Bước 1: 60 bộ thủ')
    elif fpath == 'step6.html':
        content = content.replace('Bước 6: 150 Chủ Đề', 'Bước 3: 150 Chủ Đề')
        content = content.replace('BƯỚC 6: 150 CHỦ ĐỀ', 'BƯỚC 3: 150 CHỦ ĐỀ')
        content = content.replace('Bước 5: 150 Chủ Đề', 'Bước 3: 150 Chủ Đề')
        content = content.replace('BƯỚC 5: 150 CHỦ ĐỀ', 'BƯỚC 3: 150 CHỦ ĐỀ')
        content = content.replace('HÁN TỰ · BƯỚC 5 TRONG LỘ TRÌNH', 'HÁN TỰ · BƯỚC 3 TRONG LỘ TRÌNH')
        content = content.replace('HÁN TỰ · BƯỚC 6 TRONG LỘ TRÌNH', 'HÁN TỰ · BƯỚC 3 TRONG LỘ TRÌNH')
        content = content.replace('Bước 5: 150 Chủ đề & Hội thoại', 'Bước 3: 150 Chủ đề & Hội thoại')
        content = content.replace('Bước 6: 150 Chủ đề & Hội thoại', 'Bước 3: 150 Chủ đề & Hội thoại')
        content = content.replace('← Bước 5', '← Bước 2: 93 chữ HSK 1')
        content = content.replace('← Bước 4', '← Bước 2: 93 chữ HSK 1')
        content = content.replace('href="step5.html"', 'href="step3.html"')
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated root navigation {fpath}")

# 4. Update all-steps.html
with open('all-steps.html', 'r', encoding='utf-8') as f:
    as_content = f.read()

# Sidebar nav in all-steps.html
as_old_nav_pattern = re.compile(r'<div class="text-xs font-extrabold uppercase tracking-wider text-emerald-800">🧭 Điều hướng nhanh.*?</nav>\s*</div>', re.DOTALL)
as_new_nav = '''<div class="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2.5">
  <div class="text-xs font-extrabold uppercase tracking-wider text-emerald-800">🧭 Điều hướng nhanh 3 Bước</div>
  <nav class="flex flex-col gap-1.5 text-xs font-bold">
    <a href="#page-step1" class="sidebar-nav-link">Bước 1: 60 Bộ thủ Hán tự cơ bản</a>
    <a href="#page-step3" class="sidebar-nav-link">Bước 2: 93 chữ HSK 1</a>
    <a href="#page-step6" class="sidebar-nav-link">Bước 3: 150 Chủ đề</a>
    <a href="#page-rad214" class="sidebar-nav-link">Phụ lục: Bảng 214 Bộ thủ Khang Hy</a>
    <a href="methods.html" class="sidebar-nav-link">Cách học khác: Học chữ đa chiều (HSK 1–5)</a>
  </nav>
</div>'''

as_content = as_old_nav_pattern.sub(as_new_nav, as_content, count=1)

# Remove page-step4 and page-step5 articles from all-steps.html
as_content = re.sub(r'<article id="page-step4".*?</article>\s*', '', as_content, flags=re.DOTALL)
as_content = re.sub(r'<article id="page-step5".*?</article>\s*', '', as_content, flags=re.DOTALL)

# Re-title page-step6 in all-steps.html
as_content = as_content.replace('BƯỚC 5: 150 CHỦ ĐỀ TỪ VỰNG &amp; HỘI THOẠI HÀNG NGÀY', 'BƯỚC 3: 150 CHỦ ĐỀ TỪ VỰNG &amp; HỘI THOẠI HÀNG NGÀY')
as_content = as_content.replace('BƯỚC 6: 150 CHỦ ĐỀ TỪ VỰNG &amp; HỘI THOẠI HÀNG NGÀY', 'BƯỚC 3: 150 CHỦ ĐỀ TỪ VỰNG &amp; HỘI THOẠI HÀNG NGÀY')
as_content = as_content.replace('BƯỚC 5 TRONG LỘ TRÌNH', 'BƯỚC 3 TRONG LỘ TRÌNH')
as_content = as_content.replace('BƯỚC 6 TRONG LỘ TRÌNH', 'BƯỚC 3 TRONG LỘ TRÌNH')

with open('all-steps.html', 'w', encoding='utf-8') as f:
    f.write(as_content)
print("Updated all-steps.html")

# 5. Update lessons/*.html
lesson_files = glob.glob('lessons/*.html')
for lf in lesson_files:
    active_num = 0
    if 'step3' in lf:
        active_num = 2
    elif 'step6' in lf:
        active_num = 3
    elif 'method' in lf:
        active_num = 4
        
    with open(lf, 'r', encoding='utf-8') as f:
        l_content = f.read()
        
    new_nav = get_lesson_nav(active_num)
    l_content = nav_pattern.sub(new_nav, l_content, count=1)
    
    if 'step6-topic' in lf:
        l_content = l_content.replace('Bước 6: 150 Chủ đề', 'Bước 3: 150 Chủ đề')
        l_content = l_content.replace('Bước 5: 150 Chủ đề', 'Bước 3: 150 Chủ đề')
        l_content = l_content.replace('Bước 6', 'Bước 3')
    
    with open(lf, 'w', encoding='utf-8') as f:
        f.write(l_content)

print(f"Updated {len(lesson_files)} lesson files in lessons/")
