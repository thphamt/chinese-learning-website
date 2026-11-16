#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function generateWhiteboardData() {
  const baseDir = path.resolve(__dirname, '..');
  process.chdir(baseDir);

  function findHtmlFiles(dir) {
    let results = [];
    const list = fs.readdirSync(dir);
    for (const file of list) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        if (file === 'lessons') {
          results = results.concat(findHtmlFiles(fullPath));
        }
      } else if (file.endsWith('.html')) {
        results.push(path.relative(baseDir, fullPath));
      }
    }
    return results;
  }

  const htmlFiles = findHtmlFiles(baseDir).sort();
  const fileSet = new Set(htmlFiles);
  console.log(`Scanning ${htmlFiles.length} HTML files...`);

  const nodes = {};

  for (const fpath of htmlFiles) {
    const fullPath = path.join(baseDir, fpath);
    const content = fs.readFileSync(fullPath, 'utf8');
    const stat = fs.statSync(fullPath);
    const sizeKb = Math.round((stat.size / 1024) * 10) / 10;
    const mtime = stat.mtime.toISOString();

    // Parse title
    const titleMatch = content.match(/<title>(.*?)<\/title>/i);
    const rawTitle = titleMatch ? titleMatch[1].trim() : fpath;
    const cleanTitle = rawTitle.replace(/\s*·\s*VNCHINESECLUB/gi, '').trim();

    // Parse heading
    let heading = cleanTitle;
    const h2Match = content.match(/<h2[^>]*class=["'][^"']*l-h2[^"']*["'][^>]*>([\s\S]*?)<\/h2>/i) ||
                    content.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
    if (h2Match) {
      heading = h2Match[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    }

    // Parse subTag
    let subTag = '';
    const subMatch = content.match(/<div[^>]*class=["'][^"']*l-sub[^"']*["'][^>]*>([\s\S]*?)<\/div>/i);
    if (subMatch) {
      subTag = subMatch[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    }

    // Sequence links
    const curDir = path.dirname(fpath);
    const prvMatch = content.match(/<a[^>]+href=["']([^"']+)["'][^>]*class=["'][^"']*btn-prv[^"']*["']/i);
    const nxtMatch = content.match(/<a[^>]+href=["']([^"']+)["'][^>]*class=["'][^"']*btn-nxt[^"']*["']/i);

    let seqPrev = null;
    if (prvMatch) {
      const pHref = prvMatch[1].split('#')[0].split('?')[0];
      const pTarget = path.normalize(path.join(curDir, pHref));
      if (fileSet.has(pTarget) && pTarget !== fpath) {
        seqPrev = pTarget;
      }
    }

    let seqNext = null;
    if (nxtMatch) {
      const nHref = nxtMatch[1].split('#')[0].split('?')[0];
      const nTarget = path.normalize(path.join(curDir, nHref));
      if (fileSet.has(nTarget) && nTarget !== fpath) {
        seqNext = nTarget;
      }
    }

    // Outgoing internal links
    const outgoing = new Set();
    const hrefRegex = /href=["']([^"'#?]+)["']/gi;
    let match;
    while ((match = hrefRegex.exec(content)) !== null) {
      const href = match[1].trim();
      if (!href || /^(https?:|mailto:|tel:|javascript:)/i.test(href)) continue;
      const target = path.normalize(path.join(curDir, href));
      if (fileSet.has(target) && target !== fpath) {
        outgoing.add(target);
      }
    }

    // Clusters and categories
    let cluster = 'other';
    let clusterName = 'Khác';
    let stepNum = null;
    let itemNum = null;
    let parentHub = null;
    let badgeColor = '#64748b';

    if (['index.html', 'step1.html', 'Chinese-website.html'].includes(fpath)) {
      cluster = 'core_steps';
      clusterName = 'Bước 1: 60 Bộ Thủ';
      stepNum = 1;
      parentHub = 'index.html';
      badgeColor = '#10b981';
    } else if (fpath === 'step3.html') {
      cluster = 'core_steps';
      clusterName = 'Bước 2: 93 Chữ HSK 1';
      stepNum = 2;
      parentHub = 'index.html';
      badgeColor = '#3b82f6';
    } else if (fpath === 'step4.html' || fpath === 'step5.html') {
      cluster = 'other';
      clusterName = 'Lưu trữ (Đã chuyển hướng)';
      stepNum = null;
      parentHub = 'index.html';
      badgeColor = '#94a3b8';
    } else if (fpath === 'step6.html') {
      cluster = 'core_steps';
      clusterName = 'Bước 3: 150 Chủ Đề';
      stepNum = 3;
      parentHub = 'index.html';
      badgeColor = '#f59e0b';
    } else if (fpath === 'step2.html') {
      cluster = 'other';
      clusterName = 'Lưu trữ (Đã chuyển hướng)';
      stepNum = null;
      parentHub = 'index.html';
      badgeColor = '#94a3b8';
    } else if (fpath === 'methods.html') {
      cluster = 'methods_hub';
      clusterName = 'Phương Pháp Đa Chiều (Hub)';
      parentHub = 'index.html';
      badgeColor = '#6366f1';
    } else if (fpath === 'rad214.html') {
      cluster = 'reference';
      clusterName = 'Tra Cứu 214 Bộ Thủ';
      parentHub = 'index.html';
      badgeColor = '#14b8a6';
    } else if (fpath === 'all-steps.html') {
      cluster = 'overview';
      clusterName = 'Tổng Hợp Lộ Trình 6 Bước';
      parentHub = 'index.html';
      badgeColor = '#475569';
    } else if (fpath.startsWith('lessons/step3-lesson')) {
      cluster = 'step3_lessons';
      clusterName = 'Bước 3: 11 Bài Nhập Môn HSK 1';
      stepNum = 3;
      parentHub = 'step3.html';
      const m = fpath.match(/step3-lesson-(\d+)/);
      itemNum = m ? parseInt(m[1], 10) : 0;
      badgeColor = '#2563eb';
    } else if (fpath === 'lessons/step4-all.html') {
      cluster = 'step4_lessons';
      clusterName = 'Bước 4: Look & Learn (Tất cả 52 bài)';
      stepNum = 4;
      parentHub = 'step4.html';
      itemNum = 0;
      badgeColor = '#7c3aed';
    } else if (fpath.startsWith('lessons/step4-lesson')) {
      cluster = 'step4_lessons';
      clusterName = 'Bước 4: 52 Bài Look & Learn';
      stepNum = 4;
      parentHub = 'step4.html';
      const m = fpath.match(/step4-lesson-(\d+)/);
      itemNum = m ? parseInt(m[1], 10) : 0;
      badgeColor = '#7c3aed';
    } else if (fpath === 'lessons/step5-all.html') {
      cluster = 'step5_lessons';
      clusterName = 'Bước 5: Từ ghép HSK (Tất cả 51 bài)';
      stepNum = 3;
      parentHub = 'step5.html';
      itemNum = 0;
      badgeColor = '#db2777';
    } else if (fpath.startsWith('lessons/step5-lesson')) {
      cluster = 'step5_lessons';
      clusterName = 'Bước 5: 51 Bài Hán Tự & Từ Ghép';
      stepNum = 3;
      parentHub = 'step5.html';
      const m = fpath.match(/step5-lesson-(\d+)/);
      itemNum = m ? parseInt(m[1], 10) : 0;
      badgeColor = '#db2777';
    } else if (fpath === 'lessons/step6-all.html') {
      cluster = 'step6_topics';
      clusterName = 'Bước 6: Hội thoại (Tất cả 150 chủ đề)';
      stepNum = 6;
      parentHub = 'step6.html';
      itemNum = 0;
      badgeColor = '#d97706';
    } else if (fpath.startsWith('lessons/step6-topic')) {
      cluster = 'step6_topics';
      clusterName = 'Bước 6: 150 Chủ Đề Hội Thoại';
      stepNum = 6;
      parentHub = 'step6.html';
      const m = fpath.match(/step6-topic-(\d+)/);
      itemNum = m ? parseInt(m[1], 10) : 0;
      badgeColor = '#d97706';
    } else if (fpath.startsWith('lessons/method')) {
      cluster = 'methods_lessons';
      clusterName = 'Các Phân Hệ Học Đa Chiều';
      parentHub = 'methods.html';
      badgeColor = '#4f46e5';
    }

    nodes[fpath] = {
      id: fpath,
      title: cleanTitle,
      heading: heading,
      subTag: subTag,
      cluster: cluster,
      clusterName: clusterName,
      step: stepNum,
      itemNum: itemNum,
      parentHub: parentHub,
      badgeColor: badgeColor,
      sizeKb: sizeKb,
      mtime: mtime,
      outgoing: Array.from(outgoing).sort(),
      incoming: [],
      seqPrev: seqPrev,
      seqNext: seqNext
    };
  }

  // Pass 2: Incoming
  for (const [sourceId, node] of Object.entries(nodes)) {
    for (const targetId of node.outgoing) {
      if (nodes[targetId]) {
        nodes[targetId].incoming.push(sourceId);
      }
    }
  }

  for (const nid in nodes) {
    nodes[nid].incoming.sort();
  }

  // Clusters layout
  const clusterConfigs = [
    {
      id: 'core_hubs',
      title: '🌟 CỔNG ĐIỀU HƯỚNG & LỘ TRÌNH 6 BƯỚC CỐT LÕI',
      desc: 'Trục xương sống của website, kết nối từ Nhập môn đến Hội thoại nâng cao',
      color: '#059669',
      x: 50,
      y: 50,
      width: 2100,
      height: 520
    },
    {
      id: 'step3_lessons',
      title: '🔤 BƯỚC 3: 11 BÀI HÁN TỰ NHẬP MÔN HSK 1',
      desc: '93 chữ Hán HSK 1 nền tảng: số đếm, ngày tháng, gia đình, phương hướng',
      color: '#2563eb',
      x: 50,
      y: 620,
      width: 2100,
      height: 380
    },
    {
      id: 'step4_lessons',
      title: '👁️ BƯỚC 4: HANZI LOOK & LEARN (52 BÀI MINH HỌA)',
      desc: 'Học 512 chữ Hán qua hình ảnh minh họa tư duy thị giác (HSK 1, 2, 3)',
      color: '#7c3aed',
      x: 50,
      y: 1050,
      width: 2100,
      height: 850
    },
    {
      id: 'step5_lessons',
      title: '🧩 BƯỚC 5: 51 BÀI HÁN TỰ & TỪ GHÉP HSK 1–6',
      desc: 'Ghép từ lũy tiến theo gốc chữ và bộ thủ (1.000+ chữ và 3.000+ từ ghép)',
      color: '#db2777',
      x: 50,
      y: 1950,
      width: 2100,
      height: 850
    },
    {
      id: 'step6_topics',
      title: '💬 BƯỚC 6: 150 CHỦ ĐỀ TỪ VỰNG & HỘI THOẠI THỰC TẾ',
      desc: '3.150 từ vựng và hội thoại phản xạ qua 16 nhóm chủ đề đời sống sinh hoạt & công việc',
      color: '#d97706',
      x: 50,
      y: 2850,
      width: 2100,
      height: 1950
    },
    {
      id: 'methods_lessons',
      title: '🧠 PHƯƠNG PHÁP HỌC HÁN TỰ ĐA CHIỀU (26 MODULES)',
      desc: 'Phân tích bộ thủ, cụm âm thanh biểu âm, sơ đồ tư duy, và gốc từ HSK 1–5',
      color: '#4f46e5',
      x: 50,
      y: 4850,
      width: 2100,
      height: 580
    }
  ];

  const cardW = 260;
  const cardH = 130;
  const gapY = 25;

  // Pipeline positions (5 core Hanzi steps)
  const pipeline = ['index.html', 'step3.html', 'step6.html'];
  pipeline.forEach((cid, i) => {
    if (nodes[cid]) {
      nodes[cid].x = 80 + i * (cardW + 70);
      nodes[cid].y = 140;
      nodes[cid].width = cardW;
      nodes[cid].height = cardH;
      nodes[cid].isStepPipeline = true;
    }
  });

  const subCore = ['methods.html', 'rad214.html', 'all-steps.html', 'Chinese-website.html'];
  subCore.forEach((cid, i) => {
    if (nodes[cid]) {
      nodes[cid].x = 120 + i * (cardW + 100);
      nodes[cid].y = 340;
      nodes[cid].width = cardW;
      nodes[cid].height = cardH;
    }
  });

  // Step 3
  const s3Nodes = Object.values(nodes).filter(n => n.cluster === 'step3_lessons').sort((a,b) => (a.itemNum || 0) - (b.itemNum || 0));
  s3Nodes.forEach((n, i) => {
    const r = Math.floor(i / 6);
    const c = i % 6;
    n.x = 80 + c * (cardW + 70);
    n.y = 710 + r * (cardH + gapY);
    n.width = cardW;
    n.height = cardH;
  });

  // Step 4
  const s4Nodes = Object.values(nodes).filter(n => n.cluster === 'step4_lessons').sort((a,b) => (a.itemNum || 0) - (b.itemNum || 0));
  s4Nodes.forEach((n, i) => {
    const r = Math.floor(i / 7);
    const c = i % 7;
    n.x = 80 + c * (cardW + 30);
    n.y = 1140 + r * (cardH + gapY);
    n.width = cardW;
    n.height = cardH;
  });

  // Step 5
  const s5Nodes = Object.values(nodes).filter(n => n.cluster === 'step5_lessons').sort((a,b) => (a.itemNum || 0) - (b.itemNum || 0));
  s5Nodes.forEach((n, i) => {
    const r = Math.floor(i / 7);
    const c = i % 7;
    n.x = 80 + c * (cardW + 30);
    n.y = 2040 + r * (cardH + gapY);
    n.width = cardW;
    n.height = cardH;
  });

  // Step 6
  const s6Nodes = Object.values(nodes).filter(n => n.cluster === 'step6_topics').sort((a,b) => (a.itemNum || 0) - (b.itemNum || 0));
  s6Nodes.forEach((n, i) => {
    const r = Math.floor(i / 7);
    const c = i % 7;
    n.x = 80 + c * (cardW + 30);
    n.y = 2940 + r * (cardH + gapY);
    n.width = cardW;
    n.height = cardH;
  });

  // Methods
  const mNodes = Object.values(nodes).filter(n => n.cluster === 'methods_lessons').sort((a,b) => a.id.localeCompare(b.id));
  mNodes.forEach((n, i) => {
    const r = Math.floor(i / 7);
    const c = i % 7;
    n.x = 80 + c * (cardW + 30);
    n.y = 4940 + r * (cardH + gapY);
    n.width = cardW;
    n.height = cardH;
  });

  // Key architectural connections
  const connections = [];

  for (let i = 0; i < pipeline.length - 1; i++) {
    connections.push({
      source: pipeline[i],
      target: pipeline[i + 1],
      type: 'pipeline',
      label: `Lộ trình Bước ${i+1} ➔ ${i+2}`,
      color: '#10b981',
      width: 4
    });
  }

  for (const [nid, node] of Object.entries(nodes)) {
    if (node.seqNext && nodes[node.seqNext]) {
      connections.push({
        source: nid,
        target: node.seqNext,
        type: 'sequence',
        label: 'Bài tiếp',
        color: '#64748b',
        width: 1.5
      });
    }
  }

  for (const [nid, node] of Object.entries(nodes)) {
    const ph = node.parentHub;
    if (ph && nodes[ph] && ph !== nid && !node.isStepPipeline) {
      connections.push({
        source: ph,
        target: nid,
        type: 'hierarchy',
        label: 'Mục con',
        color: node.badgeColor,
        width: 1.2
      });
    }
  }

  const clusterCounts = {};
  for (const n of Object.values(nodes)) {
    clusterCounts[n.cluster] = (clusterCounts[n.cluster] || 0) + 1;
  }

  const meta = {
    totalPages: Object.keys(nodes).length,
    totalClusters: clusterConfigs.length,
    totalExplicitConnections: connections.length,
    totalAllLinks: Object.values(nodes).reduce((acc, n) => acc + n.outgoing.length, 0),
    orphans: Object.values(nodes).filter(n => n.incoming.length === 0).map(n => n.id),
    lastGenerated: new Date().toISOString(),
    clusterCounts: clusterCounts
  };

  const result = {
    meta,
    clusters: clusterConfigs,
    nodes: Object.values(nodes),
    connections
  };

  fs.writeFileSync('whiteboard-data.json', JSON.stringify(result, null, 2), 'utf8');
  fs.writeFileSync('whiteboard-data.js', `/* Auto-generated by scripts/generate-whiteboard.js */\nwindow.WHITEBOARD_DATA = ${JSON.stringify(result, null, 2)};\n`, 'utf8');

  console.log(`✅ Generated whiteboard data successfully via Node.js!`);
  console.log(`   Total Pages: ${meta.totalPages}`);
  console.log(`   Clusters: ${clusterConfigs.length}`);
  console.log(`   Key Connections: ${connections.length}`);
}

if (require.main === module) {
  generateWhiteboardData();
}

module.exports = { generateWhiteboardData };
