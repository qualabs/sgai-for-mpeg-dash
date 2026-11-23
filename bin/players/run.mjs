// Runs legacy-Player jobs in headless Chromium and prints what it observed.
//
//   node run.mjs < jobs.json > results.json
//
// jobs.json: { origin, advance, timeoutMs, concurrency,
//              jobs: [{ id, player, mpd }] }   (mpd: absolute URL on origin)
// results.json: { browser, results: [{ id, player, version, ok, ... }] }
//
// This file decides nothing: it measures. PASS/FAIL is computed by
// bin/conformance/players.py from these numbers.
//
// Every request leaving `origin` is recorded and aborted: the test content is
// local, and a request elsewhere is either a Player acting on a construct of
// the MPD (which the caller judges) or a defect of the rewrite.
import { chromium } from 'playwright';

const input = JSON.parse(await new Promise((resolve) => {
  let s = '';
  process.stdin.on('data', (d) => { s += d; });
  process.stdin.on('end', () => resolve(s));
}));

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function runJob(browser, job) {
  const context = await browser.newContext();
  const page = await context.newPage();
  const external = [];
  const localErrors = [];
  const segments = { requested: 0 };
  await page.route('**/*', (route) => {
    const url = route.request().url();
    if (url.startsWith(input.origin)) return route.continue();
    external.push({ url, resourceType: route.request().resourceType() });
    return route.abort('connectionrefused');
  });
  page.on('response', (r) => {
    if (!r.url().startsWith(input.origin)) return;
    if (r.url().includes('/c/')) segments.requested += 1;
    if (r.status() >= 400) localErrors.push({ url: r.url().slice(input.origin.length), status: r.status() });
  });
  const consoleErrors = [];
  page.on('pageerror', (e) => consoleErrors.push(String(e).slice(0, 300)));

  const out = { id: job.id, player: job.player };
  const wall0 = Date.now();
  try {
    await page.goto(`${input.origin}/harness.html?player=${job.player}`);
    const meta = await page.evaluate(() => window.SGAI.ready);
    out.version = meta.version;
    await page.evaluate((u) => { window.SGAI.load(u); }, job.mpd);
    let st;
    for (;;) {
      st = await page.evaluate(() => window.SGAI.state());
      const advanced = st.playingAt !== null ? st.currentTime - st.startPos : 0;
      if (st.fatal) break;
      if (st.playingAt !== null && advanced >= input.advance) break;
      if (Date.now() - wall0 > input.timeoutMs) break;
      await sleep(200);
    }
    out.state = st;
    out.started = st.playingAt !== null;
    out.startMs = st.playingAt !== null ? st.playingAt - st.loadAt : null;
    out.advanced = st.playingAt !== null ? st.currentTime - st.startPos : 0;
    out.wallMs = Date.now() - wall0;
    out.ok = true;
  } catch (e) {
    out.ok = false;
    out.harnessError = String(e).slice(0, 500);
  }
  out.external = external;
  out.localErrors = localErrors.slice(0, 20);
  out.localErrorCount = localErrors.length;
  out.segmentResponses = segments.requested;
  out.pageErrors = consoleErrors.slice(0, 10);
  await context.close();
  return out;
}

const browser = await chromium.launch({
  args: ['--autoplay-policy=no-user-gesture-required'],
});
const results = [];
const queue = input.jobs.slice();
async function worker() {
  while (queue.length) {
    const job = queue.shift();
    results.push(await runJob(browser, job));
  }
}
await Promise.all(Array.from({ length: Math.max(1, input.concurrency || 1) }, worker));
const out = { browser: `chromium ${browser.version()}`, results };
await browser.close();
process.stdout.write(JSON.stringify(out));
