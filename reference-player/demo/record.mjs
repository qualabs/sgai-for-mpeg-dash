// Plays one job of the behaviour battery's format on the `sgai` adapter and
// records the page with Playwright's video recording. Started only by
// reference-player/demo/demo.py.
//
//   node record.mjs < input.json > raw.json
//
// input.json: { origin, job, videoDir, headed } — `job` as
// bin/conformance/behaviour.py builds it (see bin/players/behaviour.mjs).
// raw.json: the same record behaviour.mjs gives for a job, plus `video` (the
// path of the recording Playwright wrote).
//
// This is behaviour.mjs's runJob without what the demo session does not use
// (an `activate` action, CPU throttling, a live entry's timing source), and
// with the recording and a caption under the Player. The caption sits outside
// the Player's viewport, so the observation does not see it. Requests are
// answered as behaviour.mjs answers them; this file decides nothing.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(path.join(here, '..', '..', 'bin', 'players', 'package.json'));
const { chromium } = require('playwright');

const input = JSON.parse(await new Promise((resolve) => {
  let s = '';
  process.stdin.on('data', (d) => { s += d; });
  process.stdin.on('end', () => resolve(s));
}));
const job = input.job;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=', 'base64');
const CORS = { 'access-control-allow-origin': '*', 'cache-control': 'no-store' };
const STARTUP_LIMIT_MS = 30000;
const POLL_MS = 10;
const FRAME_LEAD_MS = 100;
// The adapter's viewport is 960x540 at the top left; the caption is below it.
const PAGE = { width: 960, height: 576 };
const VIDEO = { width: 640, height: 384 };

function covers(declared, requested) {
  let d; let r;
  try { d = new URL(declared); r = new URL(requested); } catch (e) { return false; }
  if (d.origin !== r.origin || d.pathname !== r.pathname) return false;
  for (const [k, v] of d.searchParams) if (!r.searchParams.getAll(k).includes(v)) return false;
  return true;
}

// The caption: session time and the layout token on screen, read from the
// adapter and the viewport's data-sgai-layout.
function caption() {
  const el = document.createElement('div');
  el.style.cssText = 'position:fixed;left:0;top:540px;width:960px;height:36px;background:#111;color:#eee;'
    + 'font:18px/36px sans-serif;padding-left:12px;box-sizing:border-box';
  document.body.appendChild(el);
  const names = { none: 'programme', linear: 'linear ad', 'overlay-lower-third': 'linear ad + overlay (lower third)',
    'pause-fullscreen': 'pause ad (viewer paused)', 'pause-partial': 'pause ad (viewer paused)' };
  setInterval(() => {
    const v = document.getElementById('sgai-viewport');
    const st = window.SGAI_ADAPTER && window.SGAI_ADAPTER.sessionNow();
    const layout = v ? v.dataset.sgaiLayout : 'none';
    el.textContent = `SGAI reference Player (dash.js 5.3.0)  |  t = ${st === null || st === undefined ? '-' : (st / 1000).toFixed(1)} s`
      + `  |  ${names[layout] || layout}`;
  }, 100);
}

const browser = await chromium.launch({ headless: !input.headed,
  args: ['--autoplay-policy=no-user-gesture-required'] });
const context = await browser.newContext({ viewport: PAGE, recordVideo: { dir: input.videoDir, size: VIDEO } });
const page = await context.newPage();
const requests = [];
const counts = new Map();
let mediaResponses = 0;
const mediaErrors = [];
const media = job.media.slice().sort((a, b) => b.prefix.length - a.prefix.length)
  .map((m) => Object.assign({}, m, { rx: (m.segments || []).map((x) => new RegExp(x)) }));
await context.route('**/*', async (route) => {
  const req = route.request();
  const url = req.url();
  if (url.startsWith(input.origin)) return route.continue();
  const rec = { wall: Date.now(), url, method: req.method(), resourceType: req.resourceType() };
  try {
    const aps = job.aps.filter((a) => covers(a.url, url));
    if (aps.length) {
      const key = aps[0].url;
      const n = (counts.get(key) || 0) + 1;
      counts.set(key, n);
      const rule = aps.find((a) => a.nth === n) || aps.find((a) => !a.nth);
      if (rule) {
        Object.assign(rec, { kind: rule.media ? 'aps-media' : 'aps', nth: n, fixture: rule.path || null,
          status: rule.noResponse ? null : rule.status });
        requests.push(rec);
        if (rule.noResponse) return undefined;
        if (rule.delayMs) await sleep(rule.delayMs);
        return await route.fulfill({ status: rule.status, headers: CORS,
          contentType: rule.contentType || 'text/plain', body: rule.body || '' });
      }
    }
    const doc = job.documents.find((d) => covers(d.url, url));
    if (doc) {
      Object.assign(rec, { kind: 'document', fixture: doc.path, status: 200 });
      requests.push(rec);
      return await route.fulfill({ status: 200, headers: CORS, contentType: doc.contentType, body: doc.body });
    }
    const m = media.find((x) => url.startsWith(x.prefix)
      && x.rx.some((r) => r.test(new URL(x.local + url.slice(x.prefix.length).split('?')[0]).pathname)));
    if (m) {
      const resp = await route.fetch({ url: m.local + url.slice(m.prefix.length).split('?')[0] });
      mediaResponses += 1;
      if (resp.status() >= 400) mediaErrors.push({ url, status: resp.status() });
      return await route.fulfill({ response: resp, headers: { ...resp.headers(), ...CORS } });
    }
    const image = req.resourceType() === 'image';
    Object.assign(rec, { kind: 'other', status: image ? 200 : 204 });
    requests.push(rec);
    return await route.fulfill(image
      ? { status: 200, headers: CORS, contentType: 'image/png', body: PNG }
      : { status: 204, headers: CORS, body: '' });
  } catch (e) {
    rec.routeError = String(e).slice(0, 200);
    if (!requests.includes(rec)) requests.push(rec);
    return undefined;
  }
});
const pageErrors = [];
page.on('pageerror', (e) => pageErrors.push(String(e).slice(0, 300)));

const out = { id: job.id, clock: job.clock };
const actions = [];
try {
  await page.goto(`${input.origin}/harness.html?player=sgai`);
  out.version = (await page.evaluate(() => window.SGAI.ready)).version;
  await page.evaluate((c) => window.SGAI_ADAPTER.configure(c),
    { mode: job.mode, klass: job.klass, capabilities: job.capabilities,
      sendsCapabilities: job.sendsCapabilities || [], startTime: job.startTime, clock: job.clock });
  await page.evaluate(caption);
  const loaded = await page.evaluate((u) => { window.SGAI.load(u); return window.SGAI_ADAPTER.sessionStart(); },
    job.entryUrl);
  out.t0 = loaded;
  let first = null;
  while (first === null && Date.now() - loaded < Math.min(STARTUP_LIMIT_MS, job.wallLimitMs)) {
    first = await page.evaluate(() => window.SGAI_ADAPTER.firstFrame());
    if (first === null) await sleep(5);
  }
  out.startupMs = first;
  out.origin = first === null ? null : loaded + first;
  const session = async () => {
    const s = await page.evaluate(() => window.SGAI_ADAPTER.sessionNow());
    return s === null ? Date.now() - loaded : s;
  };
  const pending = job.actions.slice().sort((a, b) => a.atMs - b.atMs);
  for (;;) {
    const t = await session();
    if (t >= job.observeMs) break;
    if (Date.now() - loaded > job.wallLimitMs) { out.timedOut = true; break; }
    if (pending.length && pending[0].atMs <= t + FRAME_LEAD_MS) {
      const a = pending[0];
      const r = await page.evaluate(([x, at, wait]) => window.SGAI_ADAPTER.actAtFrame(x, at, wait),
        [{ do: a.do, to: a.to, rate: a.rate }, a.atMs, FRAME_LEAD_MS * 4]);
      if (r.notYet) continue;
      pending.shift();
      actions.push({ at: a.atMs, do: a.do, startedAt: r.startedAt, result: r.result, doneAt: r.doneAt,
        nextFrameAt: r.nextFrameAt, timing: 'frame' });
      continue;
    }
    await sleep(POLL_MS);
  }
  out.observation = await page.evaluate(() => window.SGAI_ADAPTER.observation());
  out.ok = true;
} catch (e) {
  out.ok = false;
  out.harnessError = String(e).slice(0, 500);
}
out.actions = actions;
out.requests = requests;
out.mediaResponses = mediaResponses;
out.mediaErrors = mediaErrors.slice(0, 20);
out.pageErrors = pageErrors.slice(0, 20);
const video = page.video();
await context.close();          // the recording is complete once the context is closed
out.video = video ? await video.path() : null;
out.browser = `chromium ${browser.version()}`;
await browser.close();
process.stdout.write(JSON.stringify(out));
