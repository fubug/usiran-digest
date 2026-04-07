(function () {
  'use strict';

  const DATA_DIR = 'data/digest/';
  const PAGE_SIZE = 10;

  let currentLang = localStorage.getItem('lang') || 'zh';
  let activeTag = 'all';
  let allDigests = [];
  let allTags = [];
  let displayed = 0;
  let filtered = [];

  // --- Init ---
  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    setLang(currentLang);
    bindLangToggle();
    bindLoadMore();
    await loadIndex();
  }

  // --- Language ---
  function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.lang = lang;
    document.querySelectorAll('.lang-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
  }

  function bindLangToggle() {
    document.getElementById('langToggle').addEventListener('click', e => {
      const btn = e.target.closest('.lang-btn');
      if (!btn) return;
      setLang(btn.dataset.lang);
      displayed = 0;
      renderTimeline();
    });
  }

  // --- Load Data ---
  async function loadIndex() {
    try {
      const resp = await fetch(DATA_DIR + 'index.json?_=' + Date.now());
      if (!resp.ok) throw new Error('index.json not found');
      const index = await resp.json();
      // Sort by date descending
      allDigests = (index.files || []).sort(
        (a, b) => new Date(b.date) - new Date(a.date)
      );
      collectTags();
      renderFilterTags();
      applyFilter();
    } catch (err) {
      console.error('Failed to load index:', err);
      showEmpty();
    }
  }

  function collectTags() {
    const set = new Set();
    allDigests.forEach(d => (d.tags || []).forEach(t => set.add(t)));
    allTags = Array.from(set).sort();
  }

  // --- Filter ---
  function renderFilterTags() {
    const container = document.getElementById('filterTags');
    const allBtn = `<button class="filter-tag active" data-tag="all">
      <span class="lang-zh">全部</span><span class="lang-en">All</span></button>`;
    const tagBtns = allTags.map(t =>
      `<button class="filter-tag" data-tag="${t}">${t}</button>`
    ).join('');
    container.innerHTML = allBtn + tagBtns;

    container.addEventListener('click', e => {
      const btn = e.target.closest('.filter-tag');
      if (!btn) return;
      activeTag = btn.dataset.tag;
      container.querySelectorAll('.filter-tag').forEach(b =>
        b.classList.toggle('active', b.dataset.tag === activeTag)
      );
      applyFilter();
    });
  }

  function applyFilter() {
    filtered = activeTag === 'all'
      ? [...allDigests]
      : allDigests.filter(d => (d.tags || []).includes(activeTag));
    displayed = 0;
    updateCount();
    renderTimeline();
  }

  function updateCount() {
    const count = filtered.length;
    const elZh = document.getElementById('digestCount');
    const elEn = document.getElementById('digestCountEn');
    if (elZh) elZh.textContent = count;
    if (elEn) elEn.textContent = count;
  }

  // --- Render ---
  function renderTimeline() {
    const container = document.getElementById('timeline');
    const loadMoreWrap = document.getElementById('loadMoreWrap');
    const emptyState = document.getElementById('emptyState');

    if (filtered.length === 0) {
      container.innerHTML = '';
      loadMoreWrap.style.display = 'none';
      emptyState.style.display = '';
      return;
    }

    emptyState.style.display = 'none';
    const end = Math.min(displayed + PAGE_SIZE, filtered.length);
    const slice = filtered.slice(displayed, end);

    if (displayed === 0) container.innerHTML = '';

    slice.forEach(entry => {
      const card = createCard(entry);
      container.appendChild(card);
    });

    displayed = end;
    loadMoreWrap.style.display = displayed < filtered.length ? '' : 'none';
  }

  function createCard(entry) {
    const card = document.createElement('article');
    card.className = 'digest-card';
    card.dataset.id = entry.id;

    const dateStr = formatDate(entry.date);
    const title = entry.title[currentLang] || entry.title.zh || entry.title.en || '';
    const tags = (entry.tags || []).map(t =>
      `<span class="digest-tag ${getTagClass(t)}">${t}</span>`
    ).join('');

    // Placeholder content, will be filled by fetch
    card.innerHTML = `
      <div class="digest-date">${dateStr}</div>
      <h2 class="digest-title">${escHtml(title)}</h2>
      <div class="digest-tags">${tags}</div>
      <div class="digest-content digest-loading">
        <div class="spinner" style="width:18px;height:18px;border-width:2px;"></div>
      </div>
    `;

    // Async load full content
    loadDigestContent(entry, card);

    return card;
  }

  async function loadDigestContent(entry, card) {
    try {
      const resp = await fetch(DATA_DIR + entry.file + '?_=' + Date.now());
      if (!resp.ok) throw new Error('file not found');
      const raw = await resp.text();
      const { frontmatter, body } = parseFrontmatter(raw);

      // Extract the section for current language
      const section = extractLangSection(body, currentLang);
      const html = marked.parse(section);

      const contentEl = card.querySelector('.digest-content');
      contentEl.innerHTML = html;
      contentEl.classList.remove('digest-loading');

      // Sources
      if (frontmatter.sources && frontmatter.sources.length) {
        const srcHtml = frontmatter.sources.map(s =>
          `<a href="${escHtml(s.url)}" target="_blank" rel="noopener">${escHtml(s.name)}</a>`
        ).join('');
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'digest-sources';
        sourcesDiv.innerHTML = `
          <div class="digest-sources-title">
            <span class="lang-zh">信源</span><span class="lang-en">Sources</span>
          </div>${srcHtml}`;
        card.appendChild(sourcesDiv);
      }
    } catch (err) {
      const contentEl = card.querySelector('.digest-content');
      contentEl.innerHTML = `<em style="color:var(--text-dim)">Failed to load content</em>`;
      contentEl.classList.remove('digest-loading');
    }
  }

  // --- Markdown Parsing ---
  function parseFrontmatter(text) {
    const match = text.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    if (!match) return { frontmatter: {}, body: text };
    return { frontmatter: parseYaml(match[1]), body: match[2] };
  }

  function parseYaml(str) {
    // Minimal YAML parser for frontmatter
    const result = {};
    let currentKey = null;
    let inArray = false;
    let arrayKey = null;

    str.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) return;

      // Array item
      if (trimmed.startsWith('- ') && arrayKey) {
        if (!Array.isArray(result[arrayKey])) result[arrayKey] = [];
        const val = trimmed.slice(2).trim();
        // Try parse inline object
        const objMatch = val.match(/^(\w+):\s*["']?(.+?)["']?$/);
        if (objMatch) {
          let last = result[arrayKey][result[arrayKey].length - 1];
          if (!last || typeof last === 'string') {
            last = {};
            result[arrayKey].push(last);
          }
          last[objMatch[1]] = objMatch[2];
        } else if (val.startsWith('{')) {
          try { result[arrayKey].push(JSON.parse(val)); } catch { result[arrayKey].push(val); }
        } else if (val.startsWith('"') || val.startsWith("'")) {
          result[arrayKey].push(val.slice(1, -1));
        } else {
          result[arrayKey].push(val);
        }
        return;
      }

      // Key: value
      const kvMatch = line.match(/^(\w+):\s*(.*)$/);
      if (kvMatch) {
        const key = kvMatch[1];
        const val = kvMatch[2].trim();

        if (val === '' || val === '|' || val === '>') {
          // Nested block or empty — treat as array start
          arrayKey = key;
          inArray = true;
          return;
        }

        // Parse value
        if (val.match(/^\d{4}-\d{2}-\d{2}T/)) {
          result[key] = val;
        } else if (val === 'true' || val === 'false') {
          result[key] = val === 'true';
        } else if (/^\d+$/.test(val)) {
          result[key] = parseInt(val, 10);
        } else if (val.startsWith('"') || val.startsWith("'")) {
          result[key] = val.slice(1, -1);
        } else if (val.startsWith('{')) {
          try { result[key] = JSON.parse(val); } catch { result[key] = val; }
        } else {
          result[key] = val;
        }
        arrayKey = null;
        inArray = false;
      }
    });

    return result;
  }

  // --- i18n content extraction ---
  function extractLangSection(body, lang) {
    const zhMatch = body.match(/##\s*中文[\s\S]*?(?=##\s*English|$)/i);
    const enMatch = body.match(/##\s*English[\s\S]*?(?=##\s*中文|$)/i);

    if (lang === 'zh' && zhMatch) return zhMatch[0].replace(/^##\s*中文[^\n]*\n?/i, '').trim();
    if (lang === 'en' && enMatch) return enMatch[0].replace(/^##\s*English[^\n]*\n?/i, '').trim();

    // Fallback: return full body
    return body;
  }

  // --- Helpers ---
  function formatDate(dateStr) {
    const d = new Date(dateStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function getTagClass(tag) {
    const map = { military: 'military', diplomacy: 'diplomacy', economy: 'economy', politics: 'politics' };
    return map[tag] || 'default';
  }

  function escHtml(s) {
    const el = document.createElement('span');
    el.textContent = s;
    return el.innerHTML;
  }

  function showEmpty() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('emptyState').style.display = '';
  }

  // --- Load More ---
  function bindLoadMore() {
    document.getElementById('loadMoreBtn').addEventListener('click', () => {
      renderTimeline();
    });
  }
})();
