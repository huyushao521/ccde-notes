// 用本机 Chrome/Edge 的 DevTools 协议把 HTML 打印成 PDF（支持自定义页眉页脚与页码）
// 用法: node print_pdf.mjs <input.html> <output.pdf>

import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, writeFileSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const CANDIDATES = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
];

const [input, output] = process.argv.slice(2);
if (!input || !output) {
  console.error("usage: node print_pdf.mjs <input.html> <output.pdf>");
  process.exit(2);
}

const browserPath = CANDIDATES.find((p) => existsSync(p));
if (!browserPath) {
  console.error("[ERR] 未找到 Chrome 或 Edge");
  process.exit(3);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const port = 9330 + Math.floor(Math.random() * 60);
const profile = mkdtempSync(join(tmpdir(), "ccde-pdf-"));

const child = spawn(
  browserPath,
  [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-extensions",
    "--disable-background-networking",
    "--run-all-compositor-stages-before-draw",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profile}`,
    "about:blank",
  ],
  { stdio: "ignore" },
);

async function fetchJson(path, init) {
  const res = await fetch(`http://127.0.0.1:${port}${path}`, init);
  return res.json();
}

async function waitForDevtools() {
  for (let i = 0; i < 120; i++) {
    try {
      return await fetchJson("/json/version");
    } catch {
      await sleep(250);
    }
  }
  throw new Error("无法连接到浏览器调试端口");
}

function client(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let seq = 0;
  const pending = new Map();
  const listeners = [];
  const ready = new Promise((res, rej) => {
    ws.addEventListener("open", () => res());
    ws.addEventListener("error", (e) => rej(e));
  });
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve: ok, reject: bad } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? bad(new Error(JSON.stringify(msg.error))) : ok(msg.result);
    } else if (msg.method) {
      listeners.forEach((fn) => fn(msg));
    }
  });
  return {
    ready,
    close: () => ws.close(),
    on: (fn) => listeners.push(fn),
    send(method, params = {}, sessionId) {
      const id = ++seq;
      ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
      return new Promise((ok, bad) => pending.set(id, { resolve: ok, reject: bad }));
    },
  };
}

const cleanup = () => {
  try { child.kill(); } catch {}
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
};

try {
  const version = await waitForDevtools();
  const browser = client(version.webSocketDebuggerUrl);
  await browser.ready;

  const { targetId } = await browser.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await browser.send("Target.attachToTarget", { targetId, flatten: true });

  await browser.send("Page.enable", {}, sessionId);

  const fileUrl = pathToFileURL(resolve(input)).href;
  const loaded = new Promise((res) => {
    browser.on((msg) => {
      if (msg.sessionId === sessionId && msg.method === "Page.loadEventFired") res();
    });
  });
  await browser.send("Page.navigate", { url: fileUrl }, sessionId);
  await Promise.race([loaded, sleep(180000)]);
  await sleep(1500); // 等字体与布局稳定

  const header = `<div style="width:100%;padding:0 12mm;font-size:7pt;color:#8a949e;font-family:'Microsoft YaHei',sans-serif;display:flex;justify-content:space-between;"><span>CCDE 400-007 学习笔记 · 中文精讲</span><span>https://huyushao521.github.io/ccde2023-notes/</span></div>`;
  const footer = `<div style="width:100%;padding:0 12mm;font-size:7.5pt;color:#8a949e;font-family:'Microsoft YaHei',sans-serif;text-align:center;">第 <span class="pageNumber"></span> 页 / 共 <span class="totalPages"></span> 页</div>`;

  console.log("[..] 正在打印 PDF，文档较大，请稍候…");
  const t0 = Date.now();
  const ticker = setInterval(() => {
    console.log(`[..] 打印中，已等待 ${Math.round((Date.now() - t0) / 1000)}s`);
  }, 15000);
  const { data } = await browser.send(
    "Page.printToPDF",
    {
      printBackground: true,
      preferCSSPageSize: true,
      marginTop: 0.55,
      marginBottom: 0.6,
      marginLeft: 0.5,
      marginRight: 0.5,
      displayHeaderFooter: true,
      headerTemplate: header,
      footerTemplate: footer,
      transferMode: "ReturnAsBase64",
    },
    sessionId,
  );

  clearInterval(ticker);
  writeFileSync(resolve(output), Buffer.from(data, "base64"));
  const kb = readFileSync(resolve(output)).length / 1024 / 1024;
  console.log(`[OK] ${resolve(output)} (${kb.toFixed(2)} MB, ${browserPath.split("\\").pop()})`);

  await browser.send("Browser.close").catch(() => {});
  cleanup();
  process.exit(0);
} catch (err) {
  console.error("[ERR]", err?.message || err);
  cleanup();
  process.exit(1);
}
