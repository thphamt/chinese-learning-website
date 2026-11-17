"""Apply the shared learner navigation without rewriting lesson content."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


def header(prefix, active):
    steps = [('index.html', '60 bộ thủ'), ('step3.html', '93 chữ HSK 1'), ('lessons/step4-all.html', 'Look & Learn'), ('lessons/step5-all.html', 'Chữ & từ ghép'), ('step6.html', '150 chủ đề'), ('methods.html', 'Cách ghi nhớ')]
    links = ''.join(
        f'<a href="{prefix}{url}" class="learning-step{" is-current" if active == i else ""}"'
        f'{chr(32) + "aria-current=\"page\"" if active == i else ""}>'
        f'<span>{label}</span></a>'
        for i, (url, label) in enumerate(steps, 1)
    )
    return f'''<header class="site-header">
  <div class="site-topbar">
    <a href="{prefix}index.html" class="site-brand"><span class="brand-mark" aria-hidden="true">字</span><span>VNCHINESECLUB</span></a>
    <div class="site-actions">
      <a href="{prefix}resources.html" class="resources-link"{' aria-current="page"' if active == 0 else ''}>Tra cứu</a>
      <details class="study-settings"><summary>Hiển thị <span aria-hidden="true">⌄</span></summary>
        <div class="settings-panel"><span class="settings-title">Tự kiểm tra</span>
          <label><input type="checkbox" data-setting="pinyin"> Ẩn Pinyin</label>
          <label><input type="checkbox" data-setting="meaning"> Ẩn nghĩa</label>
          <p>Bấm vào phần đã ẩn để xem đáp án.</p>
        </div>
      </details>
    </div>
  </div>
  <nav class="learning-path" aria-label="Các bộ bài học">{links}</nav>
</header>'''


def update(path):
    source = path.read_text()
    if '<header' not in source or path.name == 'whiteboard.html':
        return
    source = re.sub(r'(<input\b[^>]*class="toggle-check")(?! aria-hidden)', r'\1 aria-hidden="true" tabindex="-1"', source)
    name = path.name
    prefix = '../' if path.parent.name == 'lessons' else ''
    active = 0
    if name in ('index.html', 'step1.html', 'Chinese-website.html'): active = 1
    elif name == 'step3.html' or name.startswith('step3-lesson-'): active = 2
    elif name.startswith(('step4-lesson-', 'step4-all')): active = 3
    elif name.startswith(('step5-lesson-', 'step5-all')): active = 4
    elif name == 'step6.html' or name.startswith(('step6-topic-', 'step6-all')): active = 5
    elif name == 'methods.html' or name.startswith('method'): active = 6
    source = re.sub(r'<header\b[\s\S]*?</header>', header(prefix, active), source, count=1)
    if 'href="learner-ui.css"' not in source and 'href="../learner-ui.css"' not in source:
        source = source.replace('</head>', f'  <link rel="stylesheet" href="{prefix}learner-ui.css">\n  <script src="{prefix}learner-ui.js" defer></script>\n</head>')
    if 'class="skip-link"' not in source:
        source = re.sub(r'(<body[^>]*>)', r'\1\n<a class="skip-link" href="#lesson-content">Đến nội dung bài học</a>', source, count=1)
    source = re.sub(r'<main\b(?![^>]*\bid=)', '<main id="lesson-content" tabindex="-1"', source, count=1)
    if 'id="lesson-index"' not in source:
        source = re.sub(r'(<aside\b[^>]*>)([\s\S]*?)(</aside>)',
            r'\1<button class="index-toggle" type="button" aria-expanded="false" aria-controls="lesson-index">Mục lục bài học <span aria-hidden="true">＋</span></button><div id="lesson-index" class="lesson-index-content">\2</div>\3', source, count=1)
    # Shorten page headings, retaining detailed learning material below them.
    titles = {
        'index.html': 'Bước 1 · 60 bộ thủ cơ bản',
        'step1.html': 'Bước 1 · 60 bộ thủ cơ bản',
        'Chinese-website.html': 'Bước 1 · 60 bộ thủ cơ bản',
        'step3.html': 'Bước 2 · 93 chữ HSK 1',
        'step6.html': 'Bước 3 · 150 chủ đề hội thoại',
        'methods.html': '5 cách ghi nhớ chữ Hán',
    }
    if name in titles:
        source = re.sub(r'(<h1\b[^>]*>)[\s\S]*?(</h1>)', lambda m: m[1] + titles[name] + m[2], source, count=1)
    if name in ('index.html', 'step1.html', 'Chinese-website.html'):
        start = source.find('<div class="p-5 sm:p-6 rounded-2xl bg-white border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-12')
        if start != -1:
            depth = 0
            for match in re.finditer(r'<div\b[^>]*>|</div>', source[start:]):
                depth += -1 if match[0] == '</div>' else 1
                if depth == 0:
                    end = start + match.end()
                    source = source[:start] + '<div class="lesson-intro"><p>Bộ thủ là mảnh ghép giúp nhận diện và hiểu nghĩa chữ Hán. Học 60 bộ thông dụng qua 6 chặng, kèm cách đọc, cách viết và 201 chữ ví dụ.</p><a href="#stage-block-1">Bắt đầu chặng 1 →</a></div>' + source[end:]
                    break
    path.write_text(source)


if __name__ == '__main__':
    for path in [*ROOT.glob('*.html'), *ROOT.glob('lessons/*.html')]:
        update(path)
