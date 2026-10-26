/* ===== 留言板：本地存储版（无后端，数据存在当前浏览器） ===== */
(function () {
  'use strict';

  var board = document.getElementById('board');
  if (!board) return;

  var KEY = 'ccde_board_v1';
  var PAGE = board.dataset.page || '未命名页面';
  var PAGE_KEY = board.dataset.key || '';

  var form = document.getElementById('boardForm');
  var input = document.getElementById('boardInput');
  var listEl = document.getElementById('boardList');
  var emptyEl = document.getElementById('boardEmpty');
  var countEl = document.getElementById('boardCount');
  var hintEl = document.getElementById('boardHint');
  var anchorEl = document.getElementById('boardAnchor');
  var filterEl = document.getElementById('boardFilter');
  var scope = 'page';
  var hintTimer = null;

  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      var data = raw ? JSON.parse(raw) : [];
      return Array.isArray(data) ? data : [];
    } catch (e) {
      return [];
    }
  }

  function save(items) {
    try {
      localStorage.setItem(KEY, JSON.stringify(items));
      return true;
    } catch (e) {
      hint('保存失败：浏览器禁用了本地存储', 'err');
      return false;
    }
  }

  function hint(text, kind) {
    if (!hintEl) return;
    hintEl.textContent = text || '';
    hintEl.className = 'board-hint' + (kind ? ' ' + kind : '');
    clearTimeout(hintTimer);
    if (text) {
      hintTimer = setTimeout(function () {
        hintEl.textContent = '';
        hintEl.className = 'board-hint';
      }, 2600);
    }
  }

  function pad(n) { return n < 10 ? '0' + n : '' + n; }

  function fmtTime(ts) {
    var d = new Date(ts);
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
      ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }

  /* ---------- 当前阅读位置 ---------- */

  function currentSection() {
    var heads = document.querySelectorAll(
      '.article h2, .article h3, .layout-home h2, .layout-home h3'
    );
    var cur = '';
    for (var i = 0; i < heads.length; i++) {
      if (heads[i].getBoundingClientRect().top <= 140) {
        cur = heads[i].textContent.trim();
      } else {
        break;
      }
    }
    return cur;
  }

  function refreshAnchor() {
    if (!anchorEl) return;
    var sec = currentSection();
    anchorEl.textContent = sec ? '定位：' + sec : '未定位到小节';
  }

  if (anchorEl) {
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        refreshAnchor();
        ticking = false;
      });
    }, { passive: true });
    refreshAnchor();
  }

  /* ---------- 渲染 ---------- */

  function makeItem(item) {
    var li = document.createElement('li');

    var head = document.createElement('div');
    head.className = 'board-item-head';

    var page = document.createElement('span');
    page.className = 'board-item-page';
    page.textContent = item.page || '未知页面';
    head.appendChild(page);

    if (item.sec) {
      var sec = document.createElement('span');
      sec.className = 'board-item-sec';
      sec.textContent = '· ' + item.sec;
      head.appendChild(sec);
    }

    var time = document.createElement('span');
    time.className = 'board-item-time';
    time.textContent = fmtTime(item.t || Date.now());
    head.appendChild(time);

    li.appendChild(head);

    var text = document.createElement('p');
    text.className = 'board-item-text';
    text.textContent = item.x || '';
    li.appendChild(text);

    var actions = document.createElement('div');
    actions.className = 'board-item-actions';

    var copyBtn = document.createElement('button');
    copyBtn.type = 'button';
    copyBtn.className = 'board-btn mini';
    copyBtn.textContent = '复制';
    copyBtn.addEventListener('click', function () {
      copyText(toMarkdown(item), '已复制这条留言');
    });
    actions.appendChild(copyBtn);

    var delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.className = 'board-btn mini danger';
    delBtn.textContent = '删除';
    delBtn.addEventListener('click', function () {
      if (!confirm('删除这条留言？')) return;
      var items = load().filter(function (x) { return x.id !== item.id; });
      save(items);
      render();
    });
    actions.appendChild(delBtn);

    li.appendChild(actions);
    return li;
  }

  function render() {
    var all = load();
    var items = scope === 'page'
      ? all.filter(function (x) { return x.key === PAGE_KEY; })
      : all;

    items.sort(function (a, b) { return (b.t || 0) - (a.t || 0); });

    listEl.innerHTML = '';
    items.forEach(function (item) { listEl.appendChild(makeItem(item)); });

    var pageCount = all.filter(function (x) { return x.key === PAGE_KEY; }).length;
    if (countEl) {
      countEl.textContent = '本页 ' + pageCount + ' 条 · 全部 ' + all.length + ' 条';
    }
    if (emptyEl) {
      emptyEl.style.display = items.length ? 'none' : 'block';
      emptyEl.textContent = scope === 'page'
        ? '本页还没有留言，随手记一条吧。'
        : '整站还没有留言。';
    }
  }

  /* ---------- 导出 ---------- */

  function toMarkdown(item) {
    var head = '- **' + (item.page || '') + '**';
    if (item.sec) head += ' › ' + item.sec;
    head += '　`' + fmtTime(item.t || Date.now()) + '`';
    return head + '\n  ' + (item.x || '').replace(/\n/g, '\n  ');
  }

  function copyText(text, okMsg) {
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); hint(okMsg || '已复制', 'ok'); }
      catch (e) { hint('复制失败，请手动选中', 'err'); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { hint(okMsg || '已复制', 'ok'); },
        fallback
      );
    } else {
      fallback();
    }
  }

  function exportMarkdown() {
    var all = load().sort(function (a, b) { return (a.t || 0) - (b.t || 0); });
    if (!all.length) { hint('还没有留言可导出', 'err'); return; }

    var lines = ['# CCDE 笔记 · 留言与勘误', '', '导出时间：' + fmtTime(Date.now()), ''];
    var groups = {};
    all.forEach(function (item) {
      var k = item.page || '未分组';
      (groups[k] = groups[k] || []).push(item);
    });
    Object.keys(groups).forEach(function (k) {
      lines.push('## ' + k, '');
      groups[k].forEach(function (item) {
        lines.push(toMarkdown(item), '');
      });
    });

    var blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    var d = new Date();
    a.href = url;
    a.download = 'CCDE留言_ ' + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + '.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    hint('已导出 Markdown 文件', 'ok');
  }

  /* ---------- 事件绑定 ---------- */

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var text = (input.value || '').trim();
    if (!text) { hint('先写点什么再提交', 'err'); input.focus(); return; }

    var items = load();
    items.push({
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
      t: Date.now(),
      key: PAGE_KEY,
      page: PAGE,
      sec: currentSection(),
      x: text
    });
    if (!save(items)) return;

    input.value = '';
    hint('已保存到本机浏览器', 'ok');
    render();
  });

  input.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      form.requestSubmit ? form.requestSubmit() : form.submit();
    }
  });

  filterEl.addEventListener('click', function (e) {
    var btn = e.target.closest('.board-tab');
    if (!btn) return;
    scope = btn.dataset.scope === 'all' ? 'all' : 'page';
    Array.prototype.forEach.call(filterEl.querySelectorAll('.board-tab'), function (b) {
      b.classList.toggle('active', b === btn);
    });
    render();
  });

  document.getElementById('boardCopy').addEventListener('click', function () {
    var items = load().sort(function (a, b) { return (a.t || 0) - (b.t || 0); });
    if (!items.length) { hint('还没有留言可复制', 'err'); return; }
    copyText(items.map(toMarkdown).join('\n'), '已复制全部留言（Markdown）');
  });

  document.getElementById('boardExport').addEventListener('click', exportMarkdown);

  document.getElementById('boardClear').addEventListener('click', function () {
    var all = load();
    if (!all.length) { hint('本来就没有留言', 'err'); return; }
    if (!confirm('确定清空全部 ' + all.length + ' 条留言？此操作不可撤销（建议先导出备份）。')) return;
    if (!confirm('再确认一次：清空后无法恢复。')) return;
    save([]);
    render();
    hint('已清空', 'ok');
  });

  render();
})();
