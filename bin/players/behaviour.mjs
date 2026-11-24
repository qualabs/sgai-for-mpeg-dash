// Runs behaviour jobs (a vector, a class, a variant) on the `sgai` adapter in
// headless Chromium and prints what it observed. Started only by
// bin/conformance/behaviour.py, which `check-dash-conformance.py --behaviour`
// calls (ADR 0087): nothing else runs it.
//
//   node behaviour.mjs < jobs.json > raw.json
//
// jobs.json: { origin, concurrency, jobs: [{
//   id, mode ('sgai' | 'legacy'), klass, capabilities, startTime (s),
//   entryUrl, observeMs, wallLimitMs,
//   actions:   [{ atMs, do, to (s), rate }],
//   documents: [{ url, path, body, contentType }],      the vector's fixtures
//   aps:       [{ url, nth, status, path, body, contentType, delayMs, noResponse }],
//   media:     [{ prefix, local }] }] }               external prefix -> local
// raw.json: { browser, results: [{ id, ok, harnessError, t0, origin, startupMs,
//   requests, actions, observation, pageErrors, mediaResponses, mediaErrors }] }
//
// The session clock (spec-source/scenarios/README.md) starts at the first
// frame, not at load(): `t0` is the wall time of load(), `origin` the wall
// time of the first frame the adapter saw (`startupMs` after `t0`; null when
// none came within STARTUP_LIMIT_MS, and then the clock starts at `t0`).
// Actions are made, and observation ends, on the session clock.
//
// Every request leaving the local origin, from the page or from a page it
// opens (a ClickThrough destination opened as a popup), is answered here
// (ADR 0079), and each is recorded with its wall time (ms since the epoch,
// the clock of `t0` and `origin`):
//   1. an `aps` entry for its URL (and request number): its status, document,
//      delay, or no answer at all — kind 'aps';
//   2. a fixture whose URL it is (the fixture's query a subset of the
//      request's) — kind 'document', 200 with the fixture;
//   3. under a media prefix: fetched from the local content server, not
//      recorded beyond a count (media requests are not compared);
//   4. anything else — kind 'other', 204 (an image: a 1x1 PNG). Beacons are
//      among these; which are beacons is decided in Python.
// This file decides nothing.
import { chromium } from 'playwright';

const input = JSON.parse(await new Promise((resolve) => {
  let s = '';
  process.stdin.on('data', (d) => { s += d; });
  process.stdin.on('end', () => resolve(s));
}));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=', 'base64');
const STARTUP_LIMIT_MS = 30000;
const CORS = { 'access-control-allow-origin': '*', 'cache-control': 'no-store' };

// The declared URL covers the requested one: same origin and path, and every
// query parameter of the declared one present with the same value.
function covers(declared, requested) {
  let d; let r;
  try { d = new URL(declared); r = new URL(requested); } catch (e) { return false; }
  if (d.origin !== r.origin || d.pathname !== r.pathname) return false;
  for (const [k, v] of d.searchParams) if (!r.searchParams.getAll(k).includes(v)) return false;
  return true;
}

async function runJob(browser, job) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();
  const requests = [];
  const counts = new Map();
  let mediaResponses = 0;
  const mediaErrors = [];
  const media = job.media.slice().sort((a, b) => b.prefix.length - a.prefix.length);
  await context.route('**/*', async (route) => {
    const req = route.request();
    const url = req.url();
    if (url.startsWith(input.origin)) return route.continue();
    const wall = Date.now();
    const rec = { wall, url, method: req.method(), resourceType: req.resourceType() };
    try {
      const aps = job.aps.filter((a) => covers(a.url, url));
      if (aps.length) {
        const key = aps[0].url;
        const n = (counts.get(key) || 0) + 1;
        counts.set(key, n);
        const rule = aps.find((a) => a.nth === n) || aps.find((a) => !a.nth);
        if (rule) {
          Object.assign(rec, { kind: 'aps', nth: n, fixture: rule.path || null,
            status: rule.noResponse ? null : rule.status });
          requests.push(rec);
          if (rule.noResponse) return; // left open until the context closes
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
      const m = media.find((x) => url.startsWith(x.prefix));
      if (m) {
        const local = m.local + url.slice(m.prefix.length).split('?')[0];
        const resp = await route.fetch({ url: local });
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

  const out = { id: job.id };
  const actions = [];
  try {
    await page.goto(`${input.origin}/harness.html?player=sgai`);
    out.version = (await page.evaluate(() => window.SGAI.ready)).version;
    await page.evaluate((c) => window.SGAI_ADAPTER.configure(c),
      { mode: job.mode, klass: job.klass, capabilities: job.capabilities, startTime: job.startTime });
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
    const t0 = first === null ? loaded : loaded + first;
    const pending = job.actions.slice().sort((a, b) => a.atMs - b.atMs);
    for (;;) {
      const t = Date.now() - t0;
      if (t >= job.observeMs) break;
      if (Date.now() - loaded > job.wallLimitMs) { out.timedOut = true; break; }
      while (pending.length && pending[0].atMs <= t) {
        const a = pending.shift();
        const rec = { at: a.atMs, do: a.do, startedAt: Date.now() - t0 };
        if (a.do === 'activate') {
          const p = await page.evaluate(() => window.SGAI_ADAPTER.adPoint());
          if (p) {
            await page.mouse.click(p.x, p.y);
            rec.result = { done: `clicked the ad at ${Math.round(p.x)},${Math.round(p.y)}` };
          } else {
            rec.result = { done: null, reason: 'no ad surface on screen to click' };
          }
        } else {
          rec.result = await page.evaluate((x) => window.SGAI_ADAPTER.act(x),
            { do: a.do, to: a.to, rate: a.rate });
        }
        rec.doneAt = Date.now() - t0;
        actions.push(rec);
      }
      const next = pending.length ? pending[0].atMs - (Date.now() - t0) : 50;
      await sleep(Math.max(1, Math.min(50, next, job.observeMs - (Date.now() - t0))));
    }
    out.observation = await page.evaluate(() => window.SGAI_ADAPTER.observation());
    out.state = await page.evaluate(() => window.SGAI.state());
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
  await context.close();
  return out;
}

const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
const results = [];
const queue = input.jobs.slice();
async function worker() {
  while (queue.length) results.push(await runJob(browser, queue.shift()));
}
await Promise.all(Array.from({ length: Math.max(1, input.concurrency || 1) }, worker));
const out = { browser: `chromium ${browser.version()}`, results };
await browser.close();
process.stdout.write(JSON.stringify(out));
