/* Shared navigation behavior; lesson content remains available without JavaScript. */
(() => {
  const toggle = document.querySelector('.index-toggle');
  const sidebar = document.querySelector('aside');
  const index = document.querySelector('#lesson-index');
  if (toggle && sidebar && index) {
    toggle.hidden = false;
    const setExpanded = expanded => {
      toggle.setAttribute('aria-expanded', String(expanded));
      sidebar.classList.toggle('index-open', expanded);
      toggle.querySelector('span').textContent = expanded ? '−' : '＋';
    };
    // Collapse only after enhancement so the complete index works without JS.
    sidebar.classList.add('index-enhanced');
    toggle.addEventListener('click', () => setExpanded(toggle.getAttribute('aria-expanded') !== 'true'));
    index.addEventListener('click', event => {
      const link = event.target.closest('a[href^="#"]');
      if (link && matchMedia('(max-width: 1023px)').matches) {
        const target = document.getElementById(link.hash.slice(1));
        if (target && !sidebar.contains(target)) setExpanded(false);
      }
    });
    document.addEventListener('click', event => {
      const link = event.target.closest('a[href^="#"]');
      const target = link && document.getElementById(link.hash.slice(1));
      if (target && sidebar.contains(target)) setExpanded(true);
    });
  }

  let availableSettings = 0;
  document.querySelectorAll('[data-setting]').forEach(input => {
    const original = document.getElementById(input.dataset.setting === 'pinyin' ? 'toggle-pinyin' : 'toggle-hide-meaning');
    if (!original) { input.closest('label').hidden = true; return; }
    availableSettings++;
    input.checked = original.checked;
    input.addEventListener('change', () => {
      original.checked = input.checked;
      original.dispatchEvent(new Event('change', { bubbles: true }));
    });
  });
  const settings = document.querySelector('.study-settings');
  if (settings && !availableSettings) settings.hidden = true;
  document.addEventListener('click', event => {
    if (settings && !settings.contains(event.target)) settings.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && settings?.open) {
      settings.open = false;
      settings.querySelector('summary').focus();
    }
  });

  const selector = document.querySelector('.s6-selector-box');
  if (selector) {
    const rows = [...selector.querySelectorAll('.s6-topic-row')];
    const groups = [...selector.querySelectorAll('details')];
    const initialState = groups.map(group => group.open);
    const search = document.createElement('div');
    search.className = 'topic-search';
    search.innerHTML = '<label for="topic-query">Tìm chủ đề</label><input id="topic-query" type="search" placeholder="Tên, chữ Hán hoặc số chủ đề…" autocomplete="off"><p class="search-status" role="status" aria-live="polite"></p>';
    selector.insertBefore(search, selector.children[1] || null);
    const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
    search.querySelector('input').addEventListener('input', event => {
      const query = normalize(event.target.value);
      let matches = 0;
      rows.forEach(row => {
        const number = row.querySelector('.s6-topic-num')?.textContent.replace('#', '');
        const match = !query || (/^#?\d+$/.test(query) ? number === query.replace('#', '') : normalize(row.textContent).includes(query));
        row.hidden = !match;
        if (match) matches++;
      });
      groups.forEach((group, i) => {
        group.hidden = ![...group.querySelectorAll('.s6-topic-row')].some(row => !row.hidden);
        group.open = query ? !group.hidden : initialState[i];
      });
      search.querySelector('.search-status').textContent = query ? (matches ? `${matches} chủ đề phù hợp` : 'Không tìm thấy. Thử tên tiếng Anh, chữ Hán hoặc số chủ đề.') : '';
    });
  }
})();
