#!/usr/bin/env python3
import os
import glob
import re
import json
from datetime import datetime

def generate_whiteboard_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    html_files = sorted(glob.glob('*.html') + glob.glob('lessons/*.html'))
    file_set = set(html_files)
    print(f"Scanning {len(html_files)} HTML files...")

    nodes = {}
    
    # 1. First pass: extract file metadata and links
    for fpath in html_files:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        stat = os.stat(fpath)
        size_kb = round(stat.st_size / 1024, 1)
        mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Parse <title>
        m_title = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        raw_title = m_title.group(1).strip() if m_title else fpath
        clean_title = raw_title.replace(' · VNCHINESECLUB', '').strip()

        # Parse header / heading
        h2_match = re.search(r'<h2[^>]*class=[\"\'][^\"\']*l-h2[^\"\']*[\"\'][^>]*>(.*?)</h2>', content, re.IGNORECASE | re.DOTALL)
        if not h2_match:
            h2_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        heading = re.sub(r'<[^>]+>', ' ', h2_match.group(1)).strip() if h2_match else clean_title

        # Parse subtitle / tag
        sub_match = re.search(r'<div[^>]*class=[\"\'][^\"\']*l-sub[^\"\']*[\"\'][^>]*>(.*?)</div>', content, re.IGNORECASE | re.DOTALL)
        sub_tag = re.sub(r'<[^>]+>', ' ', sub_match.group(1)).strip() if sub_match else ''

        # Detect prev and next buttons
        cur_dir = os.path.dirname(fpath)
        prv_match = re.search(r'<a[^>]+href=[\"\']([^\"\']+)[\"\'][^>]*class=[\"\'][^\"\']*btn-prv[^\"\']*[\"\']', content)
        nxt_match = re.search(r'<a[^>]+href=[\"\']([^\"\']+)[\"\'][^>]*class=[\"\'][^\"\']*btn-nxt[^\"\']*[\"\']', content)
        
        seq_prev = None
        if prv_match:
            p_href = prv_match.group(1).split('#')[0].split('?')[0]
            p_target = os.path.normpath(os.path.join(cur_dir, p_href))
            if p_target in file_set and p_target != fpath:
                seq_prev = p_target

        seq_next = None
        if nxt_match:
            n_href = nxt_match.group(1).split('#')[0].split('?')[0]
            n_target = os.path.normpath(os.path.join(cur_dir, n_href))
            if n_target in file_set and n_target != fpath:
                seq_next = n_target

        # Extract internal links
        outgoing = set()
        for m in re.finditer(r'href=[\"\']([^\"\'#?]+)[\"\']', content):
            href = m.group(1).strip()
            if not href or href.startswith(('http:', 'https:', 'mailto:', 'tel:', 'javascript:')):
                continue
            target = os.path.normpath(os.path.join(cur_dir, href))
            if target in file_set and target != fpath:
                outgoing.add(target)

        # Categorization & cluster assignment
        cluster = 'other'
        cluster_name = 'Khác'
        step_num = None
        item_num = None
        parent_hub = None
        badge_color = '#64748b'

        if fpath in ['index.html', 'step1.html', 'Chinese-website.html']:
            cluster = 'core_steps'
            cluster_name = 'Bước 1: 60 Bộ Thủ'
            step_num = 1
            parent_hub = 'index.html'
            badge_color = '#10b981'
        elif fpath == 'step2.html':
            cluster = 'core_steps'
            cluster_name = 'Bước 2: Bút Thuận'
            step_num = 2
            parent_hub = 'index.html'
            badge_color = '#06b6d4'
        elif fpath == 'step3.html':
            cluster = 'core_steps'
            cluster_name = 'Bước 3: 93 Chữ HSK 1'
            step_num = 3
            parent_hub = 'index.html'
            badge_color = '#3b82f6'
        elif fpath == 'step4.html':
            cluster = 'core_steps'
            cluster_name = 'Bước 4: Look & Learn'
            step_num = 4
            parent_hub = 'index.html'
            badge_color = '#8b5cf6'
        elif fpath == 'step5.html':
            cluster = 'core_steps'
            cluster_name = 'Bước 5: Từ Ghép HSK'
            step_num = 5
            parent_hub = 'index.html'
            badge_color = '#ec4899'
        elif fpath == 'step6.html':
            cluster = 'core_steps'
            cluster_name = 'Bước 6: 150 Chủ Đề'
            step_num = 6
            parent_hub = 'index.html'
            badge_color = '#f59e0b'
        elif fpath == 'methods.html':
            cluster = 'methods_hub'
            cluster_name = 'Phương Pháp Đa Chiều (Hub)'
            parent_hub = 'index.html'
            badge_color = '#6366f1'
        elif fpath == 'rad214.html':
            cluster = 'reference'
            cluster_name = 'Tra Cứu 214 Bộ Thủ'
            parent_hub = 'index.html'
            badge_color = '#14b8a6'
        elif fpath == 'all-steps.html':
            cluster = 'overview'
            cluster_name = 'Tổng Hợp Lộ Trình 6 Bước'
            parent_hub = 'index.html'
            badge_color = '#475569'
        elif fpath.startswith('lessons/step3-lesson'):
            cluster = 'step3_lessons'
            cluster_name = 'Bước 3: 11 Bài Nhập Môn HSK 1'
            step_num = 3
            parent_hub = 'step3.html'
            m = re.search(r'step3-lesson-(\d+)', fpath)
            item_num = int(m.group(1)) if m else 0
            badge_color = '#2563eb'
        elif fpath == 'lessons/step4-all.html':
            cluster = 'step4_lessons'
            cluster_name = 'Bước 4: Look & Learn (Tất cả 52 bài)'
            step_num = 4
            parent_hub = 'step4.html'
            item_num = 0
            badge_color = '#7c3aed'
        elif fpath.startswith('lessons/step4-lesson'):
            cluster = 'step4_lessons'
            cluster_name = 'Bước 4: 52 Bài Look & Learn'
            step_num = 4
            parent_hub = 'step4.html'
            m = re.search(r'step4-lesson-(\d+)', fpath)
            item_num = int(m.group(1)) if m else 0
            badge_color = '#7c3aed'
        elif fpath == 'lessons/step5-all.html':
            cluster = 'step5_lessons'
            cluster_name = 'Bước 5: Từ ghép HSK (Tất cả 51 bài)'
            step_num = 5
            parent_hub = 'step5.html'
            item_num = 0
            badge_color = '#db2777'
        elif fpath.startswith('lessons/step5-lesson'):
            cluster = 'step5_lessons'
            cluster_name = 'Bước 5: 51 Bài Hán Tự & Từ Ghép'
            step_num = 5
            parent_hub = 'step5.html'
            m = re.search(r'step5-lesson-(\d+)', fpath)
            item_num = int(m.group(1)) if m else 0
            badge_color = '#db2777'
        elif fpath == 'lessons/step6-all.html':
            cluster = 'step6_topics'
            cluster_name = 'Bước 6: Hội thoại (Tất cả 150 chủ đề)'
            step_num = 6
            parent_hub = 'step6.html'
            item_num = 0
            badge_color = '#d97706'
        elif fpath.startswith('lessons/step6-topic'):
            cluster = 'step6_topics'
            cluster_name = 'Bước 6: 150 Chủ Đề Hội Thoại'
            step_num = 6
            parent_hub = 'step6.html'
            m = re.search(r'step6-topic-(\d+)', fpath)
            item_num = int(m.group(1)) if m else 0
            badge_color = '#d97706'
        elif fpath.startswith('lessons/method'):
            cluster = 'methods_lessons'
            cluster_name = 'Các Phân Hệ Học Đa Chiều'
            parent_hub = 'methods.html'
            badge_color = '#4f46e5'

        nodes[fpath] = {
            'id': fpath,
            'title': clean_title,
            'heading': heading,
            'subTag': sub_tag,
            'cluster': cluster,
            'clusterName': cluster_name,
            'step': step_num,
            'itemNum': item_num,
            'parentHub': parent_hub,
            'badgeColor': badge_color,
            'sizeKb': size_kb,
            'mtime': mtime,
            'outgoing': sorted(list(outgoing)),
            'incoming': [],
            'seqPrev': seq_prev,
            'seqNext': seq_next
        }

    # 2. Second pass: compute incoming links
    for source_id, node in nodes.items():
        for target_id in node['outgoing']:
            if target_id in nodes:
                nodes[target_id]['incoming'].append(source_id)

    for nid in nodes:
        nodes[nid]['incoming'].sort()

    # 3. Calculate spatial coordinates for the Whiteboard canvas
    # We organize the whiteboard into intuitive visual clusters/swimlanes:
    # Lane 1 (Top Center): Navigation Hubs & Overview (Index, Steps 1-6, Rad214, All-steps, Methods)
    # Lane 2: Step 3 Lessons (11 Cards)
    # Lane 3: Step 4 Lessons (52 Cards in grid)
    # Lane 4: Step 5 Lessons (51 Cards in grid)
    # Lane 5: Step 6 Topics (150 Cards in grid)
    # Lane 6: Multi-Dimensional Learning (26 Cards)

    cluster_configs = {
        'core_hubs': {
            'id': 'core_hubs',
            'title': '🌟 CỔNG ĐIỀU HƯỚNG & LỘ TRÌNH 6 BƯỚC CỐT LÕI',
            'desc': 'Trục xương sống của toàn bộ website, kết nối từ Nhập môn đến Hội thoại nâng cao',
            'color': '#059669',
            'x': 50,
            'y': 50,
            'width': 2100,
            'height': 520
        },
        'step3_lessons': {
            'id': 'step3_lessons',
            'title': '🔤 BƯỚC 3: 11 BÀI HÁN TỰ NHẬP MÔN HSK 1',
            'desc': '93 chữ Hán HSK 1 nền tảng nhất: số đếm, ngày tháng, gia đình, phương hướng',
            'color': '#2563eb',
            'x': 50,
            'y': 620,
            'width': 2100,
            'height': 380
        },
        'step4_lessons': {
            'id': 'step4_lessons',
            'title': '👁️ BƯỚC 4: HANZI LOOK & LEARN (52 BÀI MINH HỌA)',
            'desc': 'Học 512 chữ Hán qua hình ảnh minh họa tư duy thị giác (HSK 1, 2, 3)',
            'color': '#7c3aed',
            'x': 50,
            'y': 1050,
            'width': 2100,
            'height': 850
        },
        'step5_lessons': {
            'id': 'step5_lessons',
            'title': '🧩 BƯỚC 5: 51 BÀI HÁN TỰ & TỪ GHÉP HSK 1–6',
            'desc': 'Ghép từ lũy tiến theo gốc chữ và bộ thủ (1.000+ chữ và 3.000+ từ ghép)',
            'color': '#db2777',
            'x': 50,
            'y': 1950,
            'width': 2100,
            'height': 850
        },
        'step6_topics': {
            'id': 'step6_topics',
            'title': '💬 BƯỚC 6: 150 CHỦ ĐỀ TỪ VỰNG & HỘI THOẠI THỰC TẾ',
            'desc': '3.150 từ vựng và hội thoại phản xạ qua 16 nhóm chủ đề đời sống sinh hoạt & công việc',
            'color': '#d97706',
            'x': 50,
            'y': 2850,
            'width': 2100,
            'height': 1950
        },
        'methods_lessons': {
            'id': 'methods_lessons',
            'title': '🧠 PHƯƠNG PHÁP HỌC HÁN TỰ ĐA CHIỀU (26 MODULES)',
            'desc': 'Phân tích bộ thủ, cụm âm thanh biểu âm, sơ đồ tư duy, và gốc từ HSK 1–5',
            'color': '#4f46e5',
            'x': 50,
            'y': 4850,
            'width': 2100,
            'height': 580
        }
    }

    # Place Core Hubs
    core_items = [
        ('index.html', 'Trang Chủ / Bước 1: 60 Bộ Thủ', 'Hub chính'),
        ('step2.html', 'Bước 2: Quy Tắc Bút Thuận', '28 nét & thứ tự nét'),
        ('step3.html', 'Bước 3: 93 Chữ HSK 1', 'Nhập môn chữ đơn'),
        ('step4.html', 'Bước 4: Look & Learn', '52 bài tư duy ảnh'),
        ('step5.html', 'Bước 5: Từ Ghép HSK', '51 bài ghép từ'),
        ('step6.html', 'Bước 6: 150 Chủ Đề', 'Hội thoại thực tế'),
        ('methods.html', 'Học Chữ Đa Chiều', '6 phương pháp HSK 1-5'),
        ('rad214.html', '214 Bộ Thủ Khang Hy', 'Tra cứu đầy đủ'),
        ('all-steps.html', 'Tổng Hợp 6 Bước', 'Mục lục toàn diện'),
        ('Chinese-website.html', 'Chinese Website (Alias)', 'Bản sao trang chủ')
    ]

    card_w = 260
    card_h = 130
    gap_x = 25
    gap_y = 25

    # Core Hub row 1: The 6 steps pipeline
    for i, cid in enumerate(['index.html', 'step2.html', 'step3.html', 'step4.html', 'step5.html', 'step6.html']):
        if cid in nodes:
            nodes[cid]['x'] = 80 + i * (card_w + 70)
            nodes[cid]['y'] = 140
            nodes[cid]['width'] = card_w
            nodes[cid]['height'] = card_h
            nodes[cid]['isStepPipeline'] = True

    # Core Hub row 2: Supporting hubs (rad214, all-steps, methods, Chinese-website)
    sub_core = ['methods.html', 'rad214.html', 'all-steps.html', 'Chinese-website.html']
    for i, cid in enumerate(sub_core):
        if cid in nodes:
            nodes[cid]['x'] = 120 + i * (card_w + 100)
            nodes[cid]['y'] = 340
            nodes[cid]['width'] = card_w
            nodes[cid]['height'] = card_h

    # Step 3 Lessons: 11 cards
    s3_nodes = sorted([n for n in nodes.values() if n['cluster'] == 'step3_lessons'], key=lambda x: x['itemNum'] or 0)
    cols_s3 = 6
    for i, n in enumerate(s3_nodes):
        r = i // cols_s3
        c = i % cols_s3
        n['x'] = 80 + c * (card_w + 70)
        n['y'] = 710 + r * (card_h + gap_y)
        n['width'] = card_w
        n['height'] = card_h

    # Step 4 Lessons: step4-all + 52 lessons
    s4_nodes = sorted([n for n in nodes.values() if n['cluster'] == 'step4_lessons'], key=lambda x: x['itemNum'] or 0)
    cols_s4 = 7
    for i, n in enumerate(s4_nodes):
        r = i // cols_s4
        c = i % cols_s4
        n['x'] = 80 + c * (card_w + 30)
        n['y'] = 1140 + r * (card_h + gap_y)
        n['width'] = card_w
        n['height'] = card_h

    # Step 5 Lessons: step5-all + 51 lessons
    s5_nodes = sorted([n for n in nodes.values() if n['cluster'] == 'step5_lessons'], key=lambda x: x['itemNum'] or 0)
    cols_s5 = 7
    for i, n in enumerate(s5_nodes):
        r = i // cols_s5
        c = i % cols_s5
        n['x'] = 80 + c * (card_w + 30)
        n['y'] = 2040 + r * (card_h + gap_y)
        n['width'] = card_w
        n['height'] = card_h

    # Step 6 Topics: step6-all + 150 topics
    s6_nodes = sorted([n for n in nodes.values() if n['cluster'] == 'step6_topics'], key=lambda x: x['itemNum'] or 0)
    cols_s6 = 7
    for i, n in enumerate(s6_nodes):
        r = i // cols_s6
        c = i % cols_s6
        n['x'] = 80 + c * (card_w + 30)
        n['y'] = 2940 + r * (card_h + gap_y)
        n['width'] = card_w
        n['height'] = card_h

    # Methods modules: 26 files
    m_nodes = sorted([n for n in nodes.values() if n['cluster'] == 'methods_lessons'], key=lambda x: x['id'])
    cols_m = 7
    for i, n in enumerate(m_nodes):
        r = i // cols_m
        c = i % cols_m
        n['x'] = 80 + c * (card_w + 30)
        n['y'] = 4940 + r * (card_h + gap_y)
        n['width'] = card_w
        n['height'] = card_h

    # Build key connections list:
    # 1. Main Pipeline Connections (Step 1 -> Step 2 -> Step 3 -> Step 4 -> Step 5 -> Step 6)
    # 2. Hub-to-Child Connections (e.g. step3.html -> step3-lesson-1.html, etc.)
    # 3. Sequential Connections (Lesson N -> Lesson N+1)
    # 4. Cross connections
    connections = []

    # Pipeline
    pipeline_steps = ['index.html', 'step2.html', 'step3.html', 'step4.html', 'step5.html', 'step6.html']
    for i in range(len(pipeline_steps) - 1):
        connections.append({
            'source': pipeline_steps[i],
            'target': pipeline_steps[i+1],
            'type': 'pipeline',
            'label': f'Lộ trình Bước {i+1} ➔ {i+2}',
            'color': '#10b981',
            'width': 4
        })

    # Sequence connections
    for nid, node in nodes.items():
        if node['seqNext'] and node['seqNext'] in nodes:
            connections.append({
                'source': nid,
                'target': node['seqNext'],
                'type': 'sequence',
                'label': 'Bài tiếp',
                'color': '#64748b',
                'width': 1.5
            })

    # Hub to child connections
    for nid, node in nodes.items():
        ph = node.get('parentHub')
        if ph and ph in nodes and ph != nid and not node.get('isStepPipeline'):
            connections.append({
                'source': ph,
                'target': nid,
                'type': 'hierarchy',
                'label': 'Mục con',
                'color': node['badgeColor'],
                'width': 1.2
            })

    # Summary stats
    stats = {
        'totalPages': len(nodes),
        'totalClusters': len(cluster_configs),
        'totalExplicitConnections': len(connections),
        'totalAllLinks': sum(len(n['outgoing']) for n in nodes.values()),
        'orphans': [n['id'] for n in nodes.values() if len(n['incoming']) == 0],
        'lastGenerated': datetime.now().isoformat(),
        'clusterCounts': {}
    }
    for n in nodes.values():
        c = n['cluster']
        stats['clusterCounts'][c] = stats['clusterCounts'].get(c, 0) + 1

    result = {
        'meta': stats,
        'clusters': list(cluster_configs.values()),
        'nodes': list(nodes.values()),
        'connections': connections
    }

    # Save to JSON
    with open('whiteboard-data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Save to JS for zero-config file:// and http:// execution
    with open('whiteboard-data.js', 'w', encoding='utf-8') as f:
        f.write('/* Auto-generated by scripts/generate_whiteboard.py */\n')
        f.write('window.WHITEBOARD_DATA = ')
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write(';\n')

    print(f"✅ Generated whiteboard data successfully!")
    print(f"   Total Pages: {stats['totalPages']}")
    print(f"   Clusters: {len(stats['clusterCounts'])}")
    print(f"   Key Connections: {len(connections)}")
    print(f"   Output written to whiteboard-data.json and whiteboard-data.js")

if __name__ == '__main__':
    generate_whiteboard_data()
