/* ===== 跨设备留言：giscus（后端为 GitHub Discussions，多浏览器/手机自动同步） =====
   前提（仓库管理员在网页上做一次）：
     1. 仓库 Settings -> General -> Features 勾选 Discussions
     2. github.com/apps/giscus 安装到本仓库
     3. 把 giscus.app 生成器给出的 data-category-id 填到下面的 categoryId
*/
(function () {
  'use strict';

  var CFG = {
    repo: 'huyushao521/ccde2023-notes',
    repoId: 'R_kgDOVXWldQ',
    category: 'Announcements', /* 必须与 categoryId 对应的分类名一致；改名/换分类时两者一起改 */
    categoryId: 'DIC_kwDOVXWldc4DJoTI',
    mapping: 'pathname',       /* 每页一个独立讨论帖 */
    strict: '1',
    reactionsEnabled: '1',
    inputPosition: 'top',
    lang: 'zh-CN'
  };

  var host = document.getElementById('giscusThread');
  if (!host) return;

  function theme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  if (!CFG.categoryId) {
    host.innerHTML =
      '<p class="giscus-pending">跨设备留言通道待配置：需先在仓库开启 Discussions 并安装 giscus App，' +
      '再把分类 ID 填入 <code>assets/giscus.js</code> 的 <code>categoryId</code>。' +
      '在此之前请使用下方「本机速记」。</p>';
    return;
  }

  var s = document.createElement('script');
  s.src = 'https://giscus.app/client.js';
  s.async = true;
  s.crossOrigin = 'anonymous';
  var attrs = {
    'data-repo': CFG.repo,
    'data-repo-id': CFG.repoId,
    'data-category': CFG.category,
    'data-category-id': CFG.categoryId,
    'data-mapping': CFG.mapping,
    'data-strict': CFG.strict,
    'data-reactions-enabled': CFG.reactionsEnabled,
    'data-emit-metadata': '0',
    'data-input-position': CFG.inputPosition,
    'data-theme': theme(),
    'data-lang': CFG.lang,
    'data-loading': 'lazy'
  };
  Object.keys(attrs).forEach(function (k) { s.setAttribute(k, attrs[k]); });
  s.addEventListener('error', function () {
    host.innerHTML = '<p class="giscus-pending">giscus.app 加载失败（网络被拦或 App 未安装）。' +
      '可刷新重试，或先用下方「本机速记」。</p>';
  });
  host.appendChild(s);

  /* 跟随站点深浅色切换 */
  var btn = document.getElementById('themeBtn');
  if (btn) {
    btn.addEventListener('click', function () {
      setTimeout(function () {
        var frame = document.querySelector('iframe.giscus-frame');
        if (!frame || !frame.contentWindow) return;
        frame.contentWindow.postMessage({ giscus: { setConfig: { theme: theme() } } }, 'https://giscus.app');
      }, 60);
    });
  }
})();
