#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { generateWhiteboardData } = require('./generate-whiteboard');

console.log('👀 Watching project for HTML changes to update whiteboard live...');
generateWhiteboardData();

let debounceTimer = null;
function triggerRegen(filename) {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    console.log(`\n🔄 Detected change in ${filename}. Regenerating whiteboard data...`);
    try {
      generateWhiteboardData();
    } catch (err) {
      console.error('❌ Error regenerating whiteboard data:', err.message);
    }
  }, 200);
}

const rootDir = path.resolve(__dirname, '..');
const lessonsDir = path.join(rootDir, 'lessons');

fs.watch(rootDir, (eventType, filename) => {
  if (filename && filename.endsWith('.html')) {
    triggerRegen(filename);
  }
});

if (fs.existsSync(lessonsDir)) {
  fs.watch(lessonsDir, (eventType, filename) => {
    if (filename && filename.endsWith('.html')) {
      triggerRegen(path.join('lessons', filename));
    }
  });
}

console.log('✨ Live watcher ready. Press Ctrl+C to exit.');
