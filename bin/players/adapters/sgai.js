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
// Times are session times: ms since load() was called, the instant the Player
// is told to start playback. Requests and beacons are recorded by the runner
// (bin/players/behaviour.mjs), on the network.
//
// This file measures; bin/conformance/behaviour_compare.py decides.
(function () {
  const VIEWPORT = { width: 960, height: 540 };
  const SAMPLE_MS = 25;
  const HEARTBEAT_MS = 500;
  let cfg = { mode: 'sgai', klass: 'D1', capabilities: null, startTime: NaN };
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
    const e = { element: d.sgaiElement, rect };
    for (const k of ['doc', 'candidateId', 'candidateIndex', 'optionId', 'optionIndex',
      'opportunityDoc', 'opportunityEvent']) {
      const v = d['sgai' + k[0].toUpperCase() + k.slice(1)];
      if (v !== undefined) e[k] = v;
    }
    if (el === primary) {
      e.time = Math.round(primary.currentTime * 1000);
      e.paused = primary.paused;
      e.rate = primary.playbackRate;
    }
    return e;
  }

  function sample(why) {
    if (t0 === null || !container) return;
    const box = container.getBoundingClientRect();
    const elements = [];
    for (const el of container.querySelectorAll('[data-sgai-element]')) {
      const rect = shownRect(el, box);
      if (rect) elements.push(describe(el, rect));
    }
    if (primary) lastTime = Math.round(primary.currentTime * 1000);
    const s = { t: now(), layout: container.dataset.sgaiLayout || 'none', elements, seeks };
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
  }

  window.SGAI_ADAPTER = {
    name: 'sgai',
    version() { return dashjs.Version || dashjs.MediaPlayer().create().getVersion(); },

    // {mode: 'sgai'|'legacy', klass, capabilities, startTime (s)}
    configure(c) { cfg = Object.assign({}, cfg, c); },

    async load(video, url, harnessLog) {
      t0 = Date.now();
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
      ref = new window.SgaiReference({ container, video, profile, log });
      ref.start(url, startTime);
      player = ref.player;
    },

    sessionStart() { return t0; },

    // A viewer action; `activate` is a click, made by the runner.
    act(action) {
      sample('action:' + action.do);
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
      return { t0, viewport: VIEWPORT, mode: cfg.mode, klass: cfg.klass, samples, moduleLog };
    },

    inspect() {
      if (!player) return null;
      let isDynamic = null;
      try { isDynamic = player.isDynamic(); } catch (e) { /* not initialised yet */ }
      return { isDynamic, samples: samples.length };
    },
  };
})();
