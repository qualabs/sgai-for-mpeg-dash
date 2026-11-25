// Adapter `sgai` (ADR 0081): dash.js, pinned and unmodified, plus the
// reference module (reference-player/src/). With `mode: 'legacy'` it is the
// same dash.js file without the module (ADR 0075): the legacy Player of the
// vectors' `legacy` outcomes.
//
// Besides what every adapter exposes (name, version, load, inspect), it
// records what is on screen, by reading the page and not by asking the module:
// a sample of every shown surface (`data-sgai-element`, see the contract at
// the top of reference-player/src/sgai-reference.js) with its rectangle in
// percent of the Player's viewport, taken every 25 ms and kept when anything
// but the primary's media time changed, at every event of the primary <video>
// that can start a new presentation segment, and every 500 ms regardless.
// Sample times are ms since load() was called. The session clock of the
// vectors starts later, at the first frame (spec-source/scenarios/README.md):
// `firstFrame()` is the sample time of the first sample that shows a `primary`
// or an `ad` surface (the primary content's first frame, or what the Player
// presents in its place, UC-01's linear ad), and the runner and the
// comparison move every time onto that origin. A requestVideoFrameCallback on
// the primary <video> takes a sample at each of its first frames, so the
// origin is not late by the sampling period.
//
// The session clock (adapters/sgai-clock.js, spec-source/scenarios/README.md)
// starts at that first frame and advances with what is presented: the
// primary's media time while it plays, a linear ad's while it has taken over
// the screen, wall time while the viewer has paused and for image or HTML
// takeovers, and not at all (up to a bound) in a transition with nothing on
// screen; `clock.holds` lists those transitions. It is ticked at every sample from the <video> elements of the
// viewport, never from the module; `sessionNow()` is what the runner schedules
// the viewer's actions on and ends the observation by, and `clock.points`
// ([ms since load(), session ms, what drove it]) is how the comparison maps
// every wall time it holds (samples, requests) onto the session clock.
// Configured `clock: 'wall'`, it is the wall clock since the first frame.
//
// Each surface carries `inst`, a serial of its DOM element, and an `ad`
// <video> its media `time` and `pass` (how many times it went back to its
// start): what tells a second pass of the same candidate from the first.
// A surface's `presentation` (its `data-sgai-presentation`) tells a new
// presentation on the same element, a still image shown again.
//
// A ClickThrough destination shown on screen (R28.1 lets the Player show its
// URL instead of opening it) is read from any shown node carrying
// `data-sgai-clickthrough="<the @uri>"`: `destinations` keeps the first time
// each URI was shown. A destination opened as a page is a request, recorded
// by the runner. Requests and beacons are recorded by the runner
// (bin/players/behaviour.mjs), on the network.
//
// This file measures; bin/conformance/behaviour_compare.py decides.
(function () {
  const VIEWPORT = { width: 960, height: 540 };
  const SAMPLE_MS = 25;
  const HEARTBEAT_MS = 500;
  let cfg = { mode: 'sgai', klass: 'D1', capabilities: null, sendsCapabilities: [], startTime: NaN,
    clock: 'presentation' };
  let t0 = null;
  let container = null;
  let primary = null;
  let player = null;
  let ref = null;
  const samples = [];
  const moduleLog = [];
  let seeks = 0;
  let pendingSeek = null;
  let lastTime = 0;
  let lastKey = null;
  let lastAt = -1e9;
  let timer = null;
  let firstFrame = null;
  const destinations = [];
  let clock = null;
  let viewerPaused = false;
  const serials = new WeakMap();
  let nextSerial = 1;
  const passes = new WeakMap();   // ad <video> -> { last (s), pass }
  let click = null;               // the armed `activate`: { at } once its click arrived
  const serial = (el) => {
    if (!serials.has(el)) serials.set(el, nextSerial++);
    return serials.get(el);
  };

  const now = () => Date.now() - t0;
  const r2 = (v) => Math.round(v * 100) / 100;
  const log = (type, data) => moduleLog.push({ t: t0 === null ? null : now(), type, data: data === undefined ? null : data });

  function setupViewport(video) {
    document.body.style.margin = '0';
    container = document.createElement('div');
    container.id = 'sgai-viewport';
    container.style.cssText = `position:fixed;left:0;top:0;width:${VIEWPORT.width}px;`
      + `height:${VIEWPORT.height}px;overflow:hidden;background:#000`;
    video.parentNode.insertBefore(container, video);
    container.appendChild(video);
    video.removeAttribute('width');
    video.removeAttribute('height');
    video.style.cssText = 'position:absolute;left:0;top:0;width:100%;height:100%;object-fit:contain';
    video.dataset.sgaiElement = 'primary';
    container.dataset.sgaiLayout = 'none';
  }

  // Shown: displayed, visible, opaque, with an area inside the viewport and,
  // for a <video>, a frame.
  function shownRect(el, box) {
    for (let e = el; e && e !== container.parentNode; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility !== 'visible' || Number(cs.opacity) === 0) return null;
    }
    if (el.tagName === 'VIDEO' && el.readyState < 2) return null;
    if (el.tagName === 'IMG' && !(el.complete && el.naturalWidth > 0)) return null;
    const r = el.getBoundingClientRect();
    const x0 = Math.max(r.left, box.left);
    const y0 = Math.max(r.top, box.top);
    const x1 = Math.min(r.right, box.right);
    const y1 = Math.min(r.bottom, box.bottom);
    if (x1 <= x0 || y1 <= y0) return null;
    return {
      x: r2(((r.left - box.left) / box.width) * 100),
      y: r2(((r.top - box.top) / box.height) * 100),
      width: r2((r.width / box.width) * 100),
      height: r2((r.height / box.height) * 100),
    };
  }

  function describe(el, rect) {
    const d = el.dataset;
    const e = { element: d.sgaiElement, rect, inst: serial(el) };
    for (const k of ['doc', 'candidateId', 'candidateIndex', 'optionId', 'optionIndex',
      'opportunityDoc', 'opportunityEvent', 'presentation']) {
      const v = d['sgai' + k[0].toUpperCase() + k.slice(1)];
      if (v !== undefined) e[k] = v;
    }
    if (el === primary) {
      e.time = Math.round(primary.currentTime * 1000);
      e.paused = primary.paused;
      e.rate = primary.playbackRate;
    } else if (el.tagName === 'VIDEO') {
      const p = passes.get(el) || { last: 0, pass: 0 };
      if (el.currentTime + 0.25 < p.last) p.pass += 1;
      p.last = el.currentTime;
      passes.set(el, p);
      e.time = Math.round(el.currentTime * 1000);
      e.pass = p.pass;
    }
    return e;
  }

  // The <video> elements of the viewport as the session clock reads them, and
  // how many `primary` or `ad` surfaces of any kind are shown (none: a
  // transition, sgai-clock.js case 4).
  function clockState(box) {
    const videos = [];
    for (const el of container.querySelectorAll('video')) {
      const role = el === primary ? 'primary' : (el.dataset.sgaiElement === 'ad' ? 'ad' : null);
      if (!role) continue;
      videos.push({ id: serial(el), role, shown: !!shownRect(el, box), paused: el.paused,
        time: el.currentTime, rate: el.playbackRate, seeks: el === primary ? seeks : 0 });
    }
    let surfaces = 0;
    for (const el of container.querySelectorAll('[data-sgai-element="primary"], [data-sgai-element="ad"]')) {
      if (shownRect(el, box)) surfaces += 1;
    }
    return { viewerPaused, videos, surfaces };
  }

  function tick(box) {
    if (!clock || clock.origin === null) return null;
    return clock.tick(now(), clockState(box || container.getBoundingClientRect()));
  }

  function sample(why) {
    if (t0 === null || !container) return;
    const box = container.getBoundingClientRect();
    const elements = [];
    for (const el of container.querySelectorAll('[data-sgai-element]')) {
      const rect = shownRect(el, box);
      if (rect) elements.push(describe(el, rect));
    }
    // the seek's origin (`pendingSeek.from`): not taken while the primary is
    // seeking, or a sample between the seek and its 'seeking' event would
    // record the target as the origin and the seek as no jump
    if (primary && !primary.seeking) lastTime = Math.round(primary.currentTime * 1000);
    const s = { t: now(), layout: container.dataset.sgaiLayout || 'none', elements, seeks };
    if (firstFrame === null && elements.some((e) => e.element === 'primary' || e.element === 'ad')) {
      firstFrame = s.t;
      why = why || 'first-frame';
      clock.start(s.t, clockState(box));
    }
    const st = tick(box);
    if (st !== null) s.st = Math.round(st);
    for (const el of container.querySelectorAll('[data-sgai-clickthrough]')) {
      const uri = el.dataset.sgaiClickthrough;
      if (shownRect(el, box) && !destinations.some((d) => d.uri === uri)) destinations.push({ t: s.t, uri });
    }
    if (pendingSeek) { s.seek = pendingSeek; pendingSeek = null; }
    const key = JSON.stringify([s.layout, seeks, elements.map((e) => Object.assign({}, e, { time: undefined }))]);
    if (key !== lastKey || s.seek || why || s.t - lastAt >= HEARTBEAT_MS) {
      if (why) s.why = why;
      samples.push(s);
      lastKey = key;
      lastAt = s.t;
    }
  }

  function watchPrimary(video) {
    video.addEventListener('seeking', () => {
      seeks += 1;
      pendingSeek = { from: lastTime, to: Math.round(video.currentTime * 1000) };
      sample('seeking');
    });
    for (const ev of ['playing', 'pause', 'seeked', 'ratechange', 'loadeddata', 'emptied', 'ended']) {
      video.addEventListener(ev, () => sample(ev));
    }
    if (video.requestVideoFrameCallback) {
      let frames = 0;
      const onFrame = () => {
        sample('frame');
        frames += 1;
        if (frames < 3) video.requestVideoFrameCallback(onFrame);
      };
      video.requestVideoFrameCallback(onFrame);
    }
  }

  window.SGAI_ADAPTER = {
    name: 'sgai',
    version() { return dashjs.Version || dashjs.MediaPlayer().create().getVersion(); },

    // {mode: 'sgai'|'legacy', klass, capabilities, startTime (s)}
    configure(c) { cfg = Object.assign({}, cfg, c); },

    async load(video, url, harnessLog) {
      t0 = Date.now();
      clock = new window.SGAI_CLOCK.SessionClock(cfg.clock);
      primary = video;
      setupViewport(video);
      watchPrimary(video);
      timer = setInterval(() => sample(null), SAMPLE_MS);
      const startTime = cfg.startTime === null || cfg.startTime === undefined ? NaN : cfg.startTime;
      if (cfg.mode === 'legacy') {
        player = dashjs.MediaPlayer().create();
        player.updateSettings({ debug: { logLevel: dashjs.Debug.LOG_LEVEL_NONE } });
        player.on(dashjs.MediaPlayer.events.ERROR, (e) => {
          log('dashjs:error', JSON.stringify((e && e.error) || e).slice(0, 300));
          harnessLog.error('dashjs', 'error', true);
        });
        player.initialize(video, url, true, startTime);
        log('legacy:initialize', { url, startTime });
        return;
      }
      const profile = window.SGAI_PROFILES.profileFor(cfg.klass, cfg.capabilities);
      // The capability parameters this session discloses on a resolution
      // request (the vector's `sends_capabilities`), read by the module from
      // its profile.
      profile.sendsCapabilities = (cfg.sendsCapabilities || []).slice();
      ref = new window.SgaiReference({ container, video, profile, log });
      ref.start(url, startTime);
      player = ref.player;
    },

    sessionStart() { return t0; },

    // The sample time (ms since load()) of the first frame shown, or null.
    firstFrame() { sample(null); return firstFrame; },

    // The session time now (ms since the first frame, on the session clock),
    // or null before the first frame.
    sessionNow() {
      if (t0 === null || !container) return null;
      if (firstFrame === null) { sample(null); return clock.now(); }
      return tick(null);
    },

    // A viewer action; `activate` is a click, made by the runner
    // (clickAtFrame). A `pause`
    // runs the session clock on wall time until the `resume`.
    act(action) {
      sample('action:' + action.do);
      if (action.do === 'pause') viewerPaused = true;
      if (action.do === 'resume') viewerPaused = false;
      if (cfg.mode === 'legacy') {
        switch (action.do) {
          case 'pause': player.pause(); return { done: 'primary paused' };
          case 'resume': player.play(); return { done: 'primary resumed' };
          case 'seek': player.seek(action.to); return { done: `primary sought to ${action.to} s` };
          case 'rate': player.setPlaybackRate(action.rate); return { done: `primary rate ${action.rate}` };
          default: return { done: null, reason: `a legacy Player has nothing that takes '${action.do}'` };
        }
      }
      return ref.act(action);
    },

    // A viewer action made inside a requestAnimationFrame callback: the first
    // frame whose session time is at or past `atMs` (R16.1's "within one
    // rendering frame" is measured from that frame). The page is sampled at
    // every frame while it waits and at the frame after the action, so a
    // change the action causes is seen at the frame it is shown in, not at
    // the next 25 ms sample. Resolves to { result, startedAt, doneAt,
    // nextFrameAt } (session ms), or to { notYet: true } when the session
    // clock has not reached `atMs` within `waitMs` of wall time (the runner
    // asks again).
    actAtFrame(action, atMs, waitMs) {
      return new Promise((resolve) => {
        const until = Date.now() + waitMs;
        const frame = () => {
          sample(null);
          const t = SGAI_ADAPTER.sessionNow();
          if (t === null || t < atMs) {
            if (Date.now() > until) { resolve({ notYet: true }); return; }
            requestAnimationFrame(frame);
            return;
          }
          const startedAt = Math.round(t);
          const result = SGAI_ADAPTER.act(action);
          const doneAt = Math.round(SGAI_ADAPTER.sessionNow());
          requestAnimationFrame(() => {
            sample('frame-after:' + action.do);
            resolve({ result, startedAt, doneAt, nextFrameAt: Math.round(SGAI_ADAPTER.sessionNow()) });
          });
        };
        requestAnimationFrame(frame);
      });
    },

    // The `activate` action, scheduled as the others are: at the first frame
    // whose session time is at or past `atMs`, the centre of the first shown
    // ad surface is taken (page coordinates; null: none) and a listener is
    // armed for the click the runner then makes there with the real mouse.
    // Resolves to { point, scheduledAt } (session ms), or { notYet: true } as
    // actAtFrame. `clickArrival()` is the session time the click reached the
    // page (null until it does): the time the viewer acted, which the
    // comparison measures from. A trusted click is listened for in the page
    // and in the same-origin document of an <iframe> under the point (an HTML
    // creative, which takes its clicks there).
    clickAtFrame(atMs, waitMs) {
      return new Promise((resolve) => {
        const until = Date.now() + waitMs;
        const frame = () => {
          sample(null);
          const t = SGAI_ADAPTER.sessionNow();
          if (t === null || t < atMs) {
            if (Date.now() > until) { resolve({ notYet: true }); return; }
            requestAnimationFrame(frame);
            return;
          }
          const point = SGAI_ADAPTER.adPoint();
          const armed = { at: null };
          click = armed;
          if (point) {
            const on = (ev) => {
              if (!ev.isTrusted || click !== armed || armed.at !== null) return;
              armed.at = Math.round(SGAI_ADAPTER.sessionNow());
              sample('action:activate');
            };
            document.addEventListener('click', on, true);
            const under = document.elementFromPoint(point.x, point.y);
            if (under && under.tagName === 'IFRAME') {
              try { under.contentWindow.addEventListener('click', on, true); } catch (e) { /* not same-origin */ }
            }
          }
          resolve({ point, scheduledAt: Math.round(t) });
        };
        requestAnimationFrame(frame);
      });
    },

    clickArrival() { return click ? click.at : null; },

    // The centre of the first shown ad surface, in page coordinates, or null.
    adPoint() {
      const box = container.getBoundingClientRect();
      for (const el of container.querySelectorAll('[data-sgai-element="ad"]')) {
        if (!shownRect(el, box)) continue;
        const r = el.getBoundingClientRect();
        return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
      }
      return null;
    },

    observation() {
      sample('end');
      if (timer) clearInterval(timer);
      timer = null;
      const clk = clock ? { mode: clock.mode, points: clock.points, holds: clock.holds } : null;
      return { t0, firstFrame, viewport: VIEWPORT, mode: cfg.mode, klass: cfg.klass, samples, destinations, moduleLog,
        clock: clk };
    },

    inspect() {
      if (!player) return null;
      let isDynamic = null;
      try { isDynamic = player.isDynamic(); } catch (e) { /* not initialised yet */ }
      return { isDynamic, samples: samples.length };
    },
  };
})();
