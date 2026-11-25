// Unit test of SgaiLinear.seekable / readyAhead / terminate's fallback against
// a stub of dash.js 5.3.0's seekToPresentationTime clip (end - target live
// delay, start). Usage: node test-seekable.mjs [path/to/sgai-linear.js]
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const src = process.argv[2] || path.resolve(here, '../../../../../../reference-player/src/sgai-linear.js');
const win = {};
win.window = win;
vm.runInNewContext(fs.readFileSync(src, 'utf8'), { window: win, console, setInterval, clearInterval, setTimeout, clearTimeout, URL, fetch: () => Promise.resolve() });
const Linear = win.SGAI_FAMILIES[0];

// dash.js 5.3.0 MediaPlayer.seekToPresentationTime for a dynamic MPD:
// min(t, end - originalLiveDelay), then max(that, start).
function stubPlayer({ dynamic = true, win: w0 = { start: 0, end: 0 }, delay = 8 } = {}) {
  const p = {
    seeks: [],
    isDynamic: () => dynamic,
    getDvrWindow: () => w0,
    getTargetLiveDelay: () => delay,
    seekToPresentationTime(t) {
      let s = t; const w = p.getDvrWindow();
      if (dynamic && w && isFinite(w.end)) { if (s > w.end - delay) s = w.end - delay; if (s < w.start) s = w.start; }
      p.seeks.push(t); main.currentTime = s;
    },
  };
  const main = { currentTime: 600.005, style: {}, readyState: 4, play() {} };
  return { p, main };
}
function family(opts) {
  const { p, main } = stubPlayer(opts);
  const f = Object.create(Linear.prototype);
  f.player = p; f.main = main; f.logs = [];
  f.log = (k, v) => f.logs.push([k, v]);
  f.layoutChanged = () => {}; f.fireCallbacks = () => {}; f.altPosition = () => 0;
  return f;
}
const alt = (RT) => ({ E: { key: 'k', scheme: 'replace', returnOffset: RT - 600, PRT: 600 }, PRTA: 600.005, parts: [], ASO: 0 });

let fails = 0, n = 0;
function check(name, got, want) {
  n++;
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) { fails++; console.log(`FAIL ${name}: expected ${JSON.stringify(want)}, observed ${JSON.stringify(got)}`); }
}

// seekable: the edges.
check('static MPD holds', family({ dynamic: false }).seekable(630).holds, true);
check('no time-shift buffer yet ({}) does not hold', family({ win: {} }).seekable(630).holds, false);
check('absent getDvrWindow result (null) does not hold', family({ win: null }).seekable(630).holds, false);
check('RT exactly end - delay holds', family({ win: { start: 500, end: 638 } }).seekable(630).holds, true);
check('RT 10 ms past end - delay does not hold', family({ win: { start: 500, end: 637.99 } }).seekable(630).holds, false);
check('its landing point is end - delay', family({ win: { start: 500, end: 637.99 } }).seekable(630).at, 629.99);
check('window end alone reaching RT does not hold (the T-09 case: edge 630.09)', family({ win: { start: 500, end: 630.09 } }).seekable(630).holds, false);
check('delay 0: RT exactly the end holds', family({ win: { start: 500, end: 630 }, delay: 0 }).seekable(630).holds, true);
check('RT behind the start does not hold', family({ win: { start: 631, end: 700 } }).seekable(630).holds, false);
check('RT exactly the start holds', family({ win: { start: 630, end: 700 } }).seekable(630).holds, true);

// readyAhead: no seek while dash.js would clip it; the seek once it holds.
{
  const f = family({ win: { start: 500, end: 630.09 } });
  const a = alt(630);
  f.readyAhead(a, 30);
  check('readyAhead waits while end - delay < RT (no seek)', f.player.seeks, []);
  check('readyAhead waits (readyAt unset)', a.readyAt, undefined);
  f.player.getDvrWindow = () => ({ start: 500, end: 638.1 });
  f.readyAhead(a, 30);
  check('readyAhead seeks once it holds', f.player.seeks, [630]);
  check('and the primary stands at RT', f.main.currentTime, 630);
}

// terminate's fallback: lands at RT, or says where it lands and why.
{
  const f = family({ win: { start: 500, end: 638.6 } });
  const a = alt(630);
  f.terminate(a, 30);
  check('terminate seeks to RT when it holds', [f.player.seeks, f.main.currentTime], [[630], 630]);
  check('and says nothing more', f.logs.filter(([k]) => k === 'linear:return-clipped').length, 0);
}
{
  const f = family({ win: { start: 500, end: 634 } });
  const a = alt(630);
  f.terminate(a, 30);
  const c = f.logs.find(([k]) => k === 'linear:return-clipped');
  check('terminate reports a clipped return', c && [c[1].RT, c[1].at], [630, 626]);
  check('with its reason', !!(c && /live delay 8/.test(c[1].reason)), true);
}
console.log(fails ? `${n - fails} PASS, ${fails} FAIL` : `${n} PASS`);
process.exit(fails ? 1 : 0);
