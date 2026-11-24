// Drives the T-01 spike cases in headless Chromium and prints what the page
// logged. Same browser, launch flags and request policy as bin/players/run.mjs
// (requests leaving the local origin are recorded and aborted).
//
//   node run-spike.mjs < cases.json > raw.json
//
// cases.json: { origin, cases: [{ id, mpd, opts, untilMainTime, timeoutMs }] }
import { chromium } from '../../bin/players/node_modules/playwright/index.mjs';

const input = JSON.parse(await new Promise((resolve) => {
  let s = '';
  process.stdin.on('data', (d) => { s += d; });
  process.stdin.on('end', () => resolve(s));
}));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function runCase(browser, c) {
  const context = await browser.newContext();
  const page = await context.newPage();
  const external = [];
  const pageErrors = [];
  await page.route('**/*', (route) => {
    const url = route.request().url();
    if (url.startsWith(input.origin)) return route.continue();
    external.push(url);
    return route.abort('connectionrefused');
  });
  page.on('pageerror', (e) => pageErrors.push(String(e).slice(0, 300)));
  const out = { id: c.id };
  const wall0 = Date.now();
  try {
    await page.goto(`${input.origin}/harness.html?player=dashjs`);
    out.dashjs = (await page.evaluate(() => window.SGAI.ready)).version;
    await page.addScriptTag({ url: '/spike/sgai-linear.js' });
    await page.addScriptTag({ url: '/spike/spike-page.js' });
    await page.evaluate(([u, o]) => window.SPIKE.start(u, o), [c.mpd, c.opts || {}]);
    let st;
    for (;;) {
      st = await page.evaluate(() => window.SPIKE.state());
      if (!st.altActive && st.mainTime >= c.untilMainTime) break;
      if (Date.now() - wall0 > c.timeoutMs) { out.timedOut = true; break; }
      await sleep(200);
    }
    out.state = st;
  } catch (e) {
    out.harnessError = String(e).slice(0, 500);
  }
  out.wallMs = Date.now() - wall0;
  out.external = external;
  out.pageErrors = pageErrors;
  await context.close();
  return out;
}

const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
const results = [];
for (const c of input.cases) results.push(await runCase(browser, c));
process.stdout.write(JSON.stringify({ browser: `chromium ${browser.version()}`, results }));
await browser.close();
