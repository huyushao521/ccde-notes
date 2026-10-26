/* CCDE 学习笔记 · 交互脚本 */
(function () {
  'use strict';

  /* ---------- 主题切换 ---------- */
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem('ccde-theme'); } catch (e) {}
  if (!saved && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    saved = 'dark';
  }
  if (saved) root.setAttribute('data-theme', saved);

  var themeBtn = document.getElementById('themeBtn');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('ccde-theme', next); } catch (e) {}
    });
  }

  /* ---------- 移动端侧边栏 ---------- */
  var menuBtn = document.getElementById('menuBtn');
  var sidebar = document.getElementById('sidebar');
  var scrim = document.getElementById('scrim');

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (scrim) scrim.classList.remove('show');
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      scrim.classList.toggle('show');
    });
  }
  if (scrim) scrim.addEventListener('click', closeSidebar);

  /* ---------- 滚动进度 + 回到顶部 ---------- */
  var bar = document.getElementById('progressBar');
  var toTop = document.getElementById('toTop');

  function onScroll() {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? (window.scrollY / h) * 100 : 0;
    if (bar) bar.style.width = p + '%';
    if (toTop) toTop.classList.toggle('show', window.scrollY > 420);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- 右侧目录高亮 ---------- */
  var tocLinks = Array.prototype.slice.call(
    document.querySelectorAll('.toc-rail a[href^="#"]')
  );
  if (tocLinks.length) {
    var headings = tocLinks.map(function (a) {
      return document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
    }).filter(Boolean);

    var spy = function () {
      var pos = window.scrollY + 100;
      var idx = -1;
      for (var i = 0; i < headings.length; i++) {
        if (headings[i].offsetTop <= pos) idx = i;
      }
      tocLinks.forEach(function (a, i) {
        a.classList.toggle('active', i === idx);
      });
    };
    window.addEventListener('scroll', spy, { passive: true });
    spy();
  }

  /* ---------- 搜索 ---------- */
  var input = document.getElementById('searchInput');
  var results = document.getElementById('searchResults');
  var index = null;
  var loading = false;

  function loadIndex(cb) {
    if (index) return cb(index);
    if (loading) return;
    loading = true;
    fetch('assets/search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; loading = false; cb(data); })
      .catch(function () { loading = false; });
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function snippet(text, kw) {
    var i = text.toLowerCase().indexOf(kw);
    if (i < 0) return '';
    var s = Math.max(0, i - 26);
    return (s > 0 ? '…' : '') + text.slice(s, i + 60) + '…';
  }

  var current = [];
  var selIdx = -1;

  function render(list, kw) {
    current = list;
    selIdx = -1;
    if (!list.length) {
      results.innerHTML = '<div class="sr-empty">没有找到匹配内容</div>';
      results.classList.add('open');
      return;
    }
    results.innerHTML = list.map(function (it, i) {
      var label = it.n + ' · ' + it.t + (it.s ? ' › ' + it.s : '');
      return '<a class="sr-item" data-i="' + i + '" href="' + it.u + '">' +
        '<strong>' + esc(label) + '</strong>' +
        '<span>' + esc(snippet(it.x, kw) || it.t) + '</span></a>';
    }).join('');
    results.classList.add('open');
  }

  function doSearch(q) {
    q = q.trim().toLowerCase();
    if (q.length < 1) { results.classList.remove('open'); return; }
    loadIndex(function (data) {
      var hits = [];
      data.forEach(function (ch) {
        var titleHit = (ch.t + ' ' + ch.n).toLowerCase().indexOf(q) >= 0;
        var secHit = (ch.s || '').toLowerCase().indexOf(q) >= 0;
        var bodyHit = ch.x.toLowerCase().indexOf(q) >= 0;
        if (titleHit || secHit || bodyHit) {
          hits.push({
            u: ch.u, n: ch.n, t: ch.t, s: ch.s, x: ch.x,
            score: titleHit ? 0 : (secHit ? 1 : 2)
          });
        }
      });
      hits.sort(function (a, b) { return a.score - b.score || a.n - b.n; });
      var seen = {};
      var uniq = [];
      hits.forEach(function (h) {
        var key = h.u.split('#')[0] + '|' + (h.s || '');
        if (seen[key]) return;
        seen[key] = 1;
        uniq.push(h);
      });
      render(uniq.slice(0, 10), q);
    });
  }

  if (input) {
    var timer = null;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      var v = input.value;
      timer = setTimeout(function () { doSearch(v); }, 120);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { input.value = ''; results.classList.remove('open'); input.blur(); return; }
      if (!results.classList.contains('open')) return;
      var items = results.querySelectorAll('.sr-item');
      if (!items.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        selIdx += e.key === 'ArrowDown' ? 1 : -1;
        if (selIdx < 0) selIdx = items.length - 1;
        if (selIdx >= items.length) selIdx = 0;
        items.forEach(function (el, i) { el.classList.toggle('sel', i === selIdx); });
      } else if (e.key === 'Enter' && selIdx >= 0) {
        e.preventDefault();
        items[selIdx].click();
      }
    });

    document.addEventListener('click', function (e) {
      if (!results.contains(e.target) && e.target !== input) {
        results.classList.remove('open');
      }
    });

    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        input.focus();
      }
    });
  }

  /* ---------- 表格横向滚动提示 ---------- */
  document.querySelectorAll('.markdown-body table').forEach(function (t) {
    t.addEventListener('scroll', function () { t.classList.add('scrolled'); }, { passive: true, once: true });
  });
})();
