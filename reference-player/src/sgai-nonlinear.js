// The non-linear family of the reference (phase 11, T-06): the overlay and
// pause windows of the extension (spec §5.1.3, §5.1.4), their resolution
// (§4.5.2, §5.8), the validation of candidates and the selection of one
// option each (§4.5.3, §5.3.4, §5.3.5, §5.3.7), the cap (§4.5.4), the order
// of candidates (§4.5.5), the fallback chain across overlapping windows of one
// family (§4.5.6), the relation to the inherited linear events (§4.5.8:
// supersede through the linear family's suppressor; the default relation ends
// a form when an alternative presentation begins), the pause slot with its
// exhaustion behaviour (§4.5.10, §4.5.11, §5.2.6) and the usable lifetime of a
// document (§5.2.5).
//
// What this file does NOT do: draw. Every ad surface is a minimal element at a
// placeholder rectangle per layout token (a `custom` option at its @rect,
// which is the token's own geometry), so that the harness can read which
// candidate and option are on screen and when; the drawing of each layout
// (squeezeback scaling, backgrounds, partial pause composition, IAB bounds)
// is T-07's, and so are the beacons and the click (T-08).
//
// Readings this file takes where the specification leaves room (each said
// where used):
// - a resolution request with no answer is given up after RESOLVE_TIMEOUT_MS
//   (PLY-39 fixes no time); a document arriving later is dropped;
// - the slot timeline of an overlay is the primary's media time from the
//   execution's start (PLY-31: a pause does not accrue); a pause slot runs on
//   the wall clock while the viewer is paused;
// - options are validated and their resources fetched when the document
//   arrives (an image's or HTML's first request, a video's sub-MPD), so that a
//   first-request failure moves to the next option before the window starts
//   (R5.9);
// - a video option that stalls for STALL_MS while the primary plays, or that
//   dash.js reports in error, is aborted and ends the execution (PLY-86; the
//   candidate began rendering, so the chain is not walked further);
// - a held document serves any execution of its window while it is usable
//   (§5.2.5); an expired one is replaced by a request when the opportunity
//   fires (PLY-9), never earlier;
// - a pause video option needs two decoders (the Player does not release the
//   primary's decoder, PLY-56 is a permission).
//
// For the other families: `ref.nonlinear` is this object; `active` says an
// overlay or pause ad is on screen.
(function (global) {
  const OVERLAY = 'urn:svta:dash:sgai-overlay:2026';
  const PAUSE = 'urn:svta:dash:sgai-pause-trigger:2026';
  const SVTA = 'urn:svta:dash:sgai:2026';
  const TICK_MS = 10;
  const EPS = 0.02;                   // s
  const RESOLVE_TIMEOUT_MS = 10000;   // the longest a resolution request is waited for
  const STALL_MS = 1000;              // a video option that does not advance this long has failed
  const CAPABILITY_PARAMS = ['sgai-video-decoders', 'sgai-image-over-video', 'sgai-html-over-video', 'sgai-custom-layout'];

  // §3.4.3: the tokens each family's window may list, and its default.
  const LISTABLE = {
    overlay: ['overlay', 'overlay-corner', 'overlay-lower-third', 'squeezeback-l-shape-upper-left',
      'squeezeback-l-shape-upper-right', 'squeezeback-double-box', 'squeezeback-double-box-background',
      'linear', 'custom'],
    pause: ['pause-fullscreen', 'pause-partial'],
  };
  const DEFAULT = {
    overlay: ['overlay', 'overlay-corner', 'overlay-lower-third', 'squeezeback-l-shape-upper-left',
      'squeezeback-l-shape-upper-right', 'squeezeback-double-box', 'squeezeback-double-box-background'],
    pause: ['pause-fullscreen', 'pause-partial'],
  };
  // Placeholder rectangles (x, y, w, h in % of the viewport) until T-07 draws
  // each layout; `custom` uses the option's @rect.
  const PLACE = {
    overlay: [10, 70, 80, 20],
    'overlay-corner': [75, 75, 25, 25],
    'overlay-lower-third': [0, 70, 100, 30],
    'squeezeback-l-shape-upper-left': [0, 60, 100, 40],
    'squeezeback-l-shape-upper-right': [0, 60, 100, 40],
    'squeezeback-double-box': [50, 25, 50, 50],
    'squeezeback-double-box-background': [50, 25, 50, 50],
    linear: [0, 0, 100, 100],
    'pause-fullscreen': [0, 0, 100, 100],
    'pause-partial': [25, 25, 50, 50],
  };
  const COVERS_PRIMARY = new Set(['linear', 'pause-fullscreen']);

  const num = (v, d) => (v === undefined || v === null || v === '' ? d : Number(v));
  const str = (v) => (v === undefined || v === null ? null : String(v));
  const now = () => performance.now();

  function isoDuration(s) {
    if (!s) return NaN;
    const m = /^P(?:(\d+(?:\.\d+)?)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$/.exec(String(s).trim());
    if (!m) return NaN;
    return (Number(m[1] || 0) * 86400) + (Number(m[2] || 0) * 3600) + (Number(m[3] || 0) * 60) + Number(m[4] || 0);
  }

  const children = (el, name, ns) => Array.from(el.children).filter((c) => c.localName === name && (!ns || c.namespaceURI === ns));

  // The window element of an Event in the manifest dash.js parsed (its Event
  // object does not carry the child; dash.js strips the prefix).
  function findWindow(manifest, scheme, id, periodIndex) {
    const periods = (manifest && manifest.Period) || [];
    const order = periodIndex !== undefined && periods[periodIndex] ? [periods[periodIndex]] : periods;
    const name = scheme === OVERLAY ? 'OverlayPresentation' : 'PauseAdPresentation';
    for (const p of order) {
      for (const es of (p && p.EventStream) || []) {
        if (es.schemeIdUri !== scheme) continue;
        const events = es.Event || [];
        for (let k = 0; k < events.length; k++) {
          const ev = events[k];
          if (String(ev.id) !== String(id)) continue;
          const el = Array.isArray(ev[name]) ? ev[name][0] : ev[name];
          return { el: el || null, order: k };
        }
      }
    }
    return { el: null, order: 0 };
  }

  // §5.8.4: each parameter appended as name=value, `?` first when the URI has
  // no query, names and values percent-encoded (a space as %20).
  function withParams(uri, params) {
    if (!params.length) return uri;
    const hash = uri.indexOf('#');
    const base = hash < 0 ? uri : uri.slice(0, hash);
    const frag = hash < 0 ? '' : uri.slice(hash);
    const q = params.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&');
    return base + (base.includes('?') ? (base.endsWith('?') || base.endsWith('&') ? '' : '&') : '?') + q + frag;
  }

  function absolutised(doc, url) {
    const mpd = doc.documentElement;
    const bases = children(mpd, 'BaseURL');
    if (!bases.length) {
      const b = doc.createElementNS(mpd.namespaceURI, 'BaseURL');
      b.textContent = new URL('.', url).href;
      mpd.insertBefore(b, mpd.firstElementChild);
    } else {
      for (const b of bases) b.textContent = new URL(b.textContent.trim(), url).href;
    }
    return new XMLSerializer().serializeToString(doc);
  }

  function form(mime) {
    const m = String(mime || '').split(';')[0].trim().toLowerCase();
    if (m === 'application/dash+xml') return 'video';
    if (m.startsWith('image/')) return 'image';
    if (m === 'text/html') return 'html';
    return null;
  }

  function rectOf(v) {
    const r = String(v || '').trim().split(/\s+/).map(Number);
    return r.length === 4 && r.every((x) => isFinite(x)) ? r : null;
  }

  // One overlay or pause window, from its Event and its child element.
  class Window {
    constructor(family, e, child, order, mpdUrl) {
      const es = e.eventStream;
      const ts = es.timescale || 1;
      const period = es.period;
      const periodEnd = period && isFinite(period.duration) ? period.start + period.duration : Infinity;
      this.family = family;                       // 'overlay' | 'pause'
      this.id = String(e.id);
      this.order = order;                         // position inside its EventStream
      this.opportunityDoc = mpdUrl;
      this.ts = ts;
      this.PT = e.calculatedPresentationTime;     // s
      const dur = e.duration;
      this.hasDuration = dur !== undefined && dur !== null && !isNaN(dur);
      // The span ends at the end of its Period whatever Event@duration says (§5.1.3).
      this.end = Math.min(this.hasDuration ? this.PT + dur : Infinity, periodEnd);
      const a = (n) => (child ? child[n] : undefined);
      this.uri = str(a('uri'));
      this.capUnits = a('durationCap') === undefined || a('durationCap') === null ? null : Number(a('durationCap'));
      this.ERT = num(a('earliestResolutionTimeOffset'), 60 * ts) / ts;
      this.allowedRaw = str(a('allowedLayouts'));
      this.customRegionRaw = str(a('customRegion'));
      this.linearRelation = str(a('linearRelation'));
      this.executeOnce = family === 'pause' && String(a('executeOnce')) === 'true';
      // §3.4.3: the declared tokens the family can present, or the family default.
      this.admitted = this.allowedRaw !== null
        ? this.allowedRaw.split(/\s+/).filter((t) => t && LISTABLE[family].includes(t))
        : DEFAULT[family].slice();
      this.region = rectOf(this.customRegionRaw) || [0, 0, 100, 100];
      // PLY-29: no cap, or no span, is not a window of this specification;
      // PLY-30: a cap of zero does not fire.
      this.why = !child || !this.uri ? 'no window element'
        : this.capUnits === null || isNaN(this.capUnits) ? 'no @durationCap (PLY-29)'
          : !this.hasDuration ? 'no Event@duration (PLY-29)'
            : this.capUnits === 0 ? '@durationCap is zero (PLY-30)' : null;
      this.fires = this.why === null;
      this.doc = null;          // the held resolution: { url, receivedAt, validFor, ... }
      this.inflight = null;     // a promise while a request is out
      this.resetEntry();
      this.consumed = false;    // once-per-session (pause, PLY-63/64)
      this.released = false;    // supersede released (PLY-48)
    }

    resetEntry() {
      this.failed = false;      // this execution attempt produced no ad
      this.executed = false;    // an execution started in this entry of the span
      this.cut = false;         // an alternative presentation began in the span (PLY-49)
    }
  }

  class SgaiNonLinear {
    constructor(ref) {
      this.ref = ref;
      this.main = ref.video;
      this.log = ref.log;
      this.windows = new Map();   // key -> Window
      this.chains = { overlay: [], pause: [] };
      this.execs = [];            // active overlay executions
      this.pauseSlot = null;      // the active pause slot
      ref.nonlinear = this;
    }

    get active() { return this.execs.some((x) => x.shown) || !!(this.pauseSlot && this.pauseSlot.shown); }

    get caps() { return this.ref.profile.capabilities || {}; }

    attach(player) {
      this.player = player;
      const ev = dashjs.MediaPlayer.events;
      // §5.1.3: both window schemes are dispatched on receive.
      for (const scheme of [OVERLAY, PAUSE]) {
        player.on(scheme, (e) => this.onReceive(e), null, { mode: ev.EVENT_MODE_ON_RECEIVE });
      }
      player.on(ev.STREAM_INITIALIZED, () => { this.streamReady = true; });
      // Any seek of the primary ends the executions on screen and starts a
      // new entry of every span (R34.6: a seek back is a new execution).
      this.main.addEventListener('seeking', () => this.onSeek());
      this.timer = setInterval(() => this.tick(), TICK_MS);
    }

    onReceive(payload) {
      const e = payload.event;
      const es = e.eventStream;
      const scheme = es.schemeIdUri;
      const key = scheme + '#' + e.id + '#' + (es.period ? es.period.id : '');
      if (this.windows.has(key)) return;   // dash.js dispatches again after a seek
      const family = scheme === OVERLAY ? 'overlay' : 'pause';
      const { el, order } = findWindow(this.player.getManifest(), scheme, e.id, es.period && es.period.index);
      const w = new Window(family, e, el, order, this.ref.url);
      w.key = key;
      this.windows.set(key, w);
      this.log('nonlinear:receive', { key, family, PT: w.PT, end: w.end, ERT: w.ERT, capUnits: w.capUnits, ts: w.ts,
        admitted: w.admitted, relation: w.linearRelation, executeOnce: w.executeOnce, fires: w.fires, why: w.why });
      // PLY-48: a superseding window keeps the inherited linear events inside
      // its span from being resolved or executed until it presents no ad.
      if (w.linearRelation === 'supersede' && this.ref.linear) {
        if (!w.fires) w.released = true;
        else {
          const off = this.ref.linear.addSuppressor((E) => !w.released && E.PRT >= w.PT - 1e-6 && E.PRT < w.end);
          w.release = () => { if (!w.released) { w.released = true; off(); this.log('nonlinear:supersede-released', { key }); } };
        }
      }
      if (w.fires) this.rebuildChains(family);
    }

    // §4.5.6, PLY-40: windows of one family whose spans overlap are a chain,
    // ordered by presentation time and, for equal ones, by document order.
    rebuildChains(family) {
      const ws = [...this.windows.values()].filter((w) => w.family === family && w.fires)
        .sort((a, b) => (a.PT - b.PT) || (a.order - b.order));
      const chains = [];
      for (const w of ws) {
        const last = chains[chains.length - 1];
        if (last && w.PT < last.end) { last.windows.push(w); last.end = Math.max(last.end, w.end); } else chains.push({ windows: [w], end: w.end });
      }
      for (const c of chains) c.windows.forEach((w) => { w.chain = c; });
      this.chains[family] = chains;
    }

    onSeek() {
      for (const x of this.execs.slice()) this.endExec(x, 'seek');
      for (const w of this.windows.values()) w.resetEntry();
      this.log('nonlinear:seek', { to: this.main.currentTime });
    }

    // ------------------------------------------------------------------ resolution

    // §5.8: the window's @uri with the slot parameters it declares (§5.8.3)
    // and the capability parameters the Player chooses to send (§5.8.2, a
    // permission: none unless the profile lists them).
    requestUrl(w) {
      const params = [];
      if (w.allowedRaw !== null) params.push(['sgai-allowed-layouts', w.allowedRaw]);
      if (w.customRegionRaw !== null) params.push(['sgai-custom-region', w.customRegionRaw]);
      const sends = this.ref.profile.sendsCapabilities || [];
      for (const p of CAPABILITY_PARAMS) {
        const v = this.caps[p];
        if (sends.includes(p) && v !== undefined && v !== null && v !== '') params.push([p, String(v)]);
      }
      return withParams(w.uri, params);
    }

    // Requests the window's document and validates it, selecting an option per
    // candidate. Resolves to the held doc (also when it has no renderable
    // candidate: `plan` is then empty), or to { failed: reason }.
    resolve(w, why) {
      if (w.inflight) return w.inflight;
      const url = this.requestUrl(w);
      this.log('nonlinear:request', { key: w.key, url, why, php: this.main.currentTime });
      const p = (async () => {
        let res;
        const ctl = new AbortController();
        const timer = setTimeout(() => ctl.abort(), RESOLVE_TIMEOUT_MS);
        try {
          res = await fetch(url, { credentials: 'omit', cache: 'no-store', signal: ctl.signal });
        } catch (e) {
          clearTimeout(timer);
          return { failed: ctl.signal.aborted ? `no response within ${RESOLVE_TIMEOUT_MS} ms` : `request failed: ${e && e.message}` };
        }
        let text;
        try { text = await res.text(); } catch (e) { clearTimeout(timer); return { failed: `body: ${e && e.message}` }; }
        clearTimeout(timer);
        if (res.status !== 200) return { failed: `HTTP ${res.status}` };
        return this.validate(w, url, text);
      })().catch((e) => ({ failed: String(e && e.message || e) }));
      w.inflight = p.then((r) => {
        w.inflight = null;
        if (!r.failed) { w.doc = r; this.log('nonlinear:resolved', { key: w.key, candidates: r.ads.length, plan: r.plan.map((c) => [c.index, c.option && c.option.index, c.layout, c.duration]), validFor: r.validFor }); } else this.log('nonlinear:resolve-failed', { key: w.key, reason: r.failed });
        return r;
      });
      return w.inflight;
    }

    // PLY-39, PLY-42: a 200 whose body is not an <svta:OverlayList> of the
    // window's family is a failed execution. PLY-1, PLY-17..23: each
    // candidate's first satisfiable option.
    async validate(w, url, text) {
      const doc = new DOMParser().parseFromString(text, 'application/xml');
      const root = doc.documentElement;
      if (!root || doc.getElementsByTagName('parsererror').length || root.localName !== 'OverlayList' || root.namespaceURI !== SVTA) {
        return { failed: 'not a resolution document' };
      }
      const family = root.getAttribute('family');
      if (family !== w.family) return { failed: `document of family ${family} for a ${w.family} window (PLY-42)` };
      const validFor = isoDuration(root.getAttribute('validFor'));
      const out = {
        url, receivedAt: now(), validFor: isFinite(validFor) ? validFor : null,
        onExhausted: root.getAttribute('onExhausted') || 'stop',
        ads: children(root, 'Ad', SVTA), plan: [],
      };
      for (let i = 0; i < out.ads.length; i++) {
        const sel = await this.select(w, out.ads[i], url);
        if (sel) out.plan.push(Object.assign({ index: i + 1, doc: url }, sel));
        else this.log('nonlinear:candidate-skipped', { key: w.key, index: i + 1, reason: 'no option satisfiable (PLY-20)' });
      }
      return out;
    }

    // The first option, in document order, whose layout the window admits and
    // whose form the device renders; its resource is requested now, and a
    // failed first request makes it not satisfiable (R5.9).
    async select(w, ad, docUrl) {
      const options = children(ad, 'RenderableAsset', SVTA);
      for (let k = 0; k < options.length; k++) {
        const o = options[k];
        const layout = o.getAttribute('layout');
        const f = form(o.getAttribute('mimeType'));
        const why = this.unsatisfiable(w, o, layout, f);
        if (why) { this.log('nonlinear:option-skipped', { key: w.key, option: k + 1, layout, why }); continue; }
        const src = new URL(o.getAttribute('src'), docUrl).href;
        const loaded = await this.load(f, src, o);
        if (!loaded.ok) { this.log('nonlinear:option-skipped', { key: w.key, option: k + 1, layout, why: loaded.reason }); continue; }
        return { option: { index: k + 1, id: o.getAttribute('id') }, layout, form: f, src, rect: rectOf(o.getAttribute('rect')),
          duration: loaded.duration, make: loaded.make };
      }
      return null;
    }

    unsatisfiable(w, o, layout, f) {
      const c = this.caps;
      if (!w.admitted.includes(layout)) return `layout ${layout} not admitted by the window (PLY-18, PLY-19)`;
      if (!f) return `media type ${o.getAttribute('mimeType')} outside §3.5 (PLY-5)`;
      const decoders = Number(c['sgai-video-decoders'] || 0);
      const image = Number(c['sgai-image-over-video'] || 0) === 1;
      const html = Number(c['sgai-html-over-video'] || 0) === 1;
      if (f === 'video' && layout !== 'linear' && decoders < 2) return 'a video over video needs two decoders (§5.3.7)';
      if (f === 'image' && !image) return 'the device cannot composite an image over video (PLY-4)';
      if (f === 'html' && !html) return 'the device cannot composite HTML over video (PLY-4)';
      if (layout === 'squeezeback-double-box-background' && !image) return 'the background needs an image surface (PLY-22)';
      if (f !== 'video' && !isFinite(isoDuration(o.getAttribute('duration')))) return 'an image or HTML option without @duration';
      if (layout === 'custom') {
        if (Number(c['sgai-custom-layout'] || 0) !== 1) return 'the Player does not support custom (PLY-21)';
        const r = rectOf(o.getAttribute('rect'));
        const [rx, ry, rw, rh] = w.region;
        const e = 1e-9;
        if (!r) return 'custom option without @rect';
        if (!(r[0] >= rx - e && r[1] >= ry - e && r[0] + r[2] <= rx + rw + e && r[1] + r[3] <= ry + rh + e)) {
          return `rect ${r.join(' ')} outside the region ${w.region.join(' ')} (PLY-21)`;
        }
      }
      return null;
    }

    // Fetch an option's resource once; returns { ok, duration (s), make() }
    // where make() gives the surface element, ready to be shown.
    async load(f, src, o) {
      if (f === 'image') {
        const img = new Image();
        const ok = await new Promise((r) => { img.onload = () => r(true); img.onerror = () => r(false); img.src = src; });
        if (!ok) return { ok: false, reason: `the image's first request failed (R5.9)` };
        return { ok: true, duration: isoDuration(o.getAttribute('duration')), make: () => img };
      }
      if (f === 'html') {
        let res;
        try { res = await fetch(src, { credentials: 'omit', cache: 'no-store' }); } catch (e) { return { ok: false, reason: `the HTML's first request failed: ${e && e.message}` }; }
        if (!res.ok) return { ok: false, reason: `the HTML's first request answered ${res.status} (R5.9)` };
        const text = await res.text();
        return { ok: true, duration: isoDuration(o.getAttribute('duration')), make: () => {
          const fr = document.createElement('iframe');
          fr.srcdoc = text || '<!doctype html><title>ad</title>';
          fr.style.border = '0';
          fr.style.background = '#fff';
          return fr;
        } };
      }
      // Video: the sub-MPD (§5.4), handed to dash.js as a blob so it is
      // requested once; its duration is its Period@duration (PLY-28).
      let res;
      try { res = await fetch(src, { credentials: 'omit', cache: 'no-store' }); } catch (e) { return { ok: false, reason: `the sub-MPD's first request failed: ${e && e.message}` }; }
      if (!res.ok) return { ok: false, reason: `the sub-MPD answered ${res.status} (R5.9)` };
      const doc = new DOMParser().parseFromString(await res.text(), 'application/xml');
      const root = doc.documentElement;
      if (!root || root.localName !== 'MPD' || doc.getElementsByTagName('parsererror').length) return { ok: false, reason: 'the sub-MPD is not an MPD' };
      const periods = children(root, 'Period');
      const duration = periods.length ? (isoDuration(periods[0].getAttribute('duration')) || isoDuration(root.getAttribute('mediaPresentationDuration'))) : NaN;
      if (!(duration > 0)) return { ok: false, reason: 'the sub-MPD has no duration' };
      const blobUrl = URL.createObjectURL(new Blob([absolutised(doc, src)], { type: 'application/dash+xml' }));
      // The first surface is preloaded now (autoplay off), so its first frame
      // is there when the candidate starts; a reuse (a repeat, a later
      // execution) gets a new one.
      const create = () => {
        const v = document.createElement('video');
        v.playsInline = true;
        v.muted = true;
        const p = dashjs.MediaPlayer().create();
        p.updateSettings({ debug: { logLevel: dashjs.Debug.LOG_LEVEL_NONE } });
        p.clearDefaultUTCTimingSources();
        p.on(dashjs.MediaPlayer.events.ERROR, (e) => { v.sgaiError = JSON.stringify((e && e.error) || e).slice(0, 200); });
        p.initialize(v, blobUrl, false);
        v.sgaiPlayer = p;
        return v;
      };
      let pre = create();
      pre.style.cssText = 'position:absolute;left:0;top:0;width:1px;height:1px;visibility:hidden';
      this.ref.container.appendChild(pre);
      return { ok: true, duration, make: () => { const v = pre || create(); pre = null; return v; } };
    }

    // §5.2.5: usable for @validFor from receipt, else until the span ends.
    usable(w, php) {
      const d = w.doc;
      if (!d) return false;
      if (d.validFor !== null) return now() < d.receivedAt + d.validFor * 1000;
      return php < w.end;
    }

    // ------------------------------------------------------------------ the overlay chain

    tick() {
      if (!this.streamReady || this.main.readyState < 1) return;
      const php = this.main.currentTime;
      const linear = this.ref.linear && this.ref.linear.active;
      for (const chain of this.chains.overlay) this.processChain(chain, php, linear);
      for (const x of this.execs.slice()) this.advance(x, php, linear);
      for (const chain of this.chains.pause) this.preResolvePause(chain, php);
      if (this.pauseSlot) this.advancePause(this.pauseSlot);
    }

    // The current window of a chain is its first that has not failed in this
    // entry (PLY-38); only it is resolved, ahead from PT − offset (PLY-6), and
    // executed when the playhead is in its span.
    processChain(chain, php, linear) {
      if (chain.windows.some((w) => w.executed)) return;
      const w = chain.windows.find((x) => !x.failed);
      if (!w) return;
      if (linear && php >= w.PT && php < w.end && w.linearRelation !== 'on-top') w.cut = true;
      if (php >= w.end - EPS) {
        // The span passed without an execution: nothing was presented.
        if (!w.inflight) this.fail(w, 'the span ended without a presentation');
        return;
      }
      if (w.inflight) return;
      // A held document with nothing renderable is known to produce no ad:
      // the chain moves on now rather than at the window's start.
      if (w.doc && !w.doc.plan.length) { this.fire(w); return; }
      if (!w.doc && php >= w.PT - w.ERT - 1e-6) {
        this.resolve(w, 'early').then((r) => { if (r.failed) this.fail(w, r.failed); });
        return;
      }
      if (php < w.PT || w.cut || linear) return;
      // Nothing is composited before the primary's first frame is shown (the
      // linear family keeps it hidden until its first processing has run).
      if (this.ref.linear && this.ref.linear.gated) return;
      if (w.doc && (this.usable(w, php) || w.doc.fresh)) { this.fire(w); return; }
      // PLY-9: not usable when the opportunity fires: a new request, whose
      // document serves this opportunity whatever its @validFor.
      this.resolve(w, w.doc ? 'expired at the opportunity' : 'at the opportunity').then((r) => {
        if (r.failed) this.fail(w, r.failed); else r.fresh = true;
      });
    }

    fail(w, reason) {
      if (w.failed) return;
      w.failed = true;
      this.log('nonlinear:failed', { key: w.key, reason, php: this.main.currentTime });
      if (w.release) w.release();
    }

    // The window's held document presents, or the attempt failed.
    fire(w) {
      const d = w.doc;
      d.fresh = false;
      if (!d.plan.length) {
        // PLY-39 (no candidates), PLY-41 (none renderable): a failed execution.
        this.fail(w, d.ads.length ? 'no candidate renderable (PLY-41)' : 'empty resolution (PLY-39, PLY-44)');
        return;
      }
      this.execute(w, d);
    }

    // PLY-46, PLY-24, PLY-28: the candidates in sequence on the slot
    // timeline, the cap applied to the cumulative duration with each declared
    // duration converted to the cap's timescale and rounded up.
    execute(w, d) {
      const php = this.main.currentTime;
      w.executed = true;
      const plan = [];
      let cumUnits = 0;
      let t = 0;
      for (const c of d.plan) {
        if (cumUnits >= w.capUnits) break;
        const units = Math.ceil(c.duration * w.ts - 1e-9);
        let shown = c.duration;
        if (cumUnits + units > w.capUnits) shown = (w.capUnits - cumUnits) / w.ts;   // stopped at the cap
        cumUnits += units;
        if (!(shown > 0)) continue;
        plan.push({ c, start: t, shown });
        t += shown;
      }
      const x = { w, d, PRTA: php, plan, k: -1, el: null, shown: false, stall: null };
      this.execs.push(x);
      this.log('nonlinear:execute', { key: w.key, PRTA: php, capUnits: w.capUnits, ts: w.ts,
        plan: plan.map((p) => ({ candidate: p.c.index, option: p.c.option.index, layout: p.c.layout,
          start: p.start, shown: p.shown, until: php + p.start + p.shown })), windowEnd: w.end });
      this.advance(x, php, false);
    }

    advance(x, php, linear) {
      const w = x.w;
      const slotT = php - x.PRTA;
      // PLY-49: a form on screen when an alternative presentation begins ends there.
      if (linear && w.linearRelation !== 'on-top') { w.cut = true; this.endExec(x, 'an alternative presentation began'); return; }
      if (php >= w.end - EPS) { this.endExec(x, 'the span ended'); return; }
      const k = x.plan.findIndex((p) => slotT >= p.start - 1e-6 && slotT < p.start + p.shown - 1e-6);
      if (k < 0) {
        if (slotT >= (x.plan.length ? x.plan[x.plan.length - 1].start + x.plan[x.plan.length - 1].shown : 0) - 1e-6) this.endExec(x, 'candidates exhausted or the cap reached');
        return;
      }
      if (k !== x.k) this.showCandidate(x, k);
      this.watchStall(x);
      // PLY-52: during a pause ad, the overlay is not visible.
      if (x.el) x.el.style.visibility = this.pauseSlot && this.pauseSlot.shown ? 'hidden' : 'visible';
    }

    showCandidate(x, k) {
      this.removeSurface(x);
      x.k = k;
      const p = x.plan[k];
      const el = this.surface(p.c, x.w);
      x.el = el;
      x.stall = null;
      if (el.sgaiPlayer) {
        const v = el;
        const start = () => { v.sgaiPlayer.setPlaybackRate(this.main.playbackRate || 1); v.sgaiPlayer.play(); };
        v.addEventListener('playing', () => { x.stall = { t: now(), at: v.currentTime, php: this.main.currentTime }; }, { once: true });
        if (v.readyState >= 1) start(); else v.sgaiPlayer.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, start);
      }
      x.shown = true;
      this.ref.container.dataset.sgaiLayout = p.c.layout;
      this.log('nonlinear:show', { key: x.w.key, candidate: p.c.index, option: p.c.option.index, layout: p.c.layout,
        php: this.main.currentTime, slotT: this.main.currentTime - x.PRTA });
    }

    // PLY-86: a video option that stops advancing while the primary plays, or
    // that dash.js reports in error, has failed at runtime and is aborted.
    watchStall(x) {
      const v = x.el;
      if (!v || !v.sgaiPlayer) return;
      if (v.sgaiError) { this.abort(x, `video error: ${v.sgaiError}`); return; }
      const s = x.stall;
      if (!s || v.ended) return;
      if (v.currentTime > s.at + 0.001 || this.main.paused) { x.stall = { t: now(), at: v.currentTime, php: this.main.currentTime }; return; }
      if (now() - s.t > STALL_MS && this.main.currentTime > s.php + 0.5) this.abort(x, `video stalled ${Math.round(now() - s.t)} ms at ${v.currentTime.toFixed(3)} s`);
    }

    abort(x, reason) {
      this.log('nonlinear:abort', { key: x.w.key, reason, php: this.main.currentTime });
      this.endExec(x, 'aborted (PLY-86)');
    }

    // The ad surface of a candidate's selected option, with the identity the
    // harness reads (sgai-reference.js, the observation contract).
    surface(c, w) {
      const el = c.make();
      const r = c.layout === 'custom' && c.rect ? c.rect : PLACE[c.layout] || PLACE.overlay;
      el.style.cssText = `position:absolute;left:${r[0]}%;top:${r[1]}%;width:${r[2]}%;height:${r[3]}%;`
        + 'object-fit:fill;z-index:2;visibility:visible;border:0;margin:0;padding:0' + (el.tagName === 'IFRAME' ? ';background:#fff' : '');
      const d = el.dataset;
      d.sgaiElement = 'ad';
      d.sgaiDoc = c.doc;
      d.sgaiCandidateIndex = String(c.index);
      d.sgaiOptionIndex = String(c.option.index);
      d.sgaiOpportunityDoc = w.opportunityDoc;
      d.sgaiOpportunityEvent = w.id;
      this.ref.container.appendChild(el);
      if (COVERS_PRIMARY.has(c.layout)) this.main.style.visibility = 'hidden';
      return el;
    }

    removeSurface(x) {
      const el = x.el;
      if (!el) return;
      if (el.sgaiPlayer) { try { el.sgaiPlayer.reset(); } catch (e) { /* gone */ } el.sgaiPlayer = null; }
      el.remove();
      x.el = null;
      if (!(this.ref.linear && this.ref.linear.active)) this.main.style.visibility = 'visible';
    }

    endExec(x, why) {
      const i = this.execs.indexOf(x);
      if (i < 0) return;
      this.execs.splice(i, 1);
      this.removeSurface(x);
      if (x.shown && !this.active && !(this.ref.linear && this.ref.linear.active)) this.ref.container.dataset.sgaiLayout = 'none';
      this.log('nonlinear:end', { key: x.w.key, why, php: this.main.currentTime, slotT: this.main.currentTime - x.PRTA });
    }

    // ------------------------------------------------------------------ the pause family

    // PLY-7: a pause window may be resolved from PT − offset; once, ahead of
    // its first pause (later documents are requested when a pause finds the
    // held one expired, PLY-9).
    preResolvePause(chain, php) {
      if (this.pauseSlot) return;
      const w = chain.windows.find((x) => !x.consumed);
      if (!w || w.doc || w.inflight || w.preResolved) return;
      if (php >= w.PT - w.ERT - 1e-6 && php < w.end) { w.preResolved = true; this.resolve(w, 'early'); }
    }

    // A viewer action. A pause inside a pause window opens a pause slot
    // (PLY-11); a resume closes it (PLY-57, PLY-60).
    act(action) {
      if (this.ref.linear && this.ref.linear.active) return null;   // R17.5 is the linear family's and T-07's
      if (action.do === 'pause') {
        const php = this.main.currentTime;
        const ws = [];
        for (const chain of this.chains.pause) for (const w of chain.windows) if (php >= w.PT && php < w.end) ws.push(w);
        if (!ws.length) return null;
        this.player.pause();
        const slot = { windows: ws, i: 0, plan: null, k: -1, el: null, shown: false, startedAt: null, again: 0, php };
        this.pauseSlot = slot;
        this.log('nonlinear:pause', { php, windows: ws.map((w) => w.key) });
        this.tryPauseWindow(slot);
        return { done: 'primary paused inside a pause window' };
      }
      if (action.do === 'resume' && this.pauseSlot) {
        this.closePause('resume');
        this.player.play();
        return { done: 'pause ad dismissed, primary resumed' };
      }
      return null;
    }

    tryPauseWindow(slot) {
      if (this.pauseSlot !== slot) return;
      const w = slot.windows[slot.i];
      if (!w) { this.log('nonlinear:pause-no-ad', { php: slot.php }); return; }
      // PLY-63: a consumed once-per-session window leaves the pause alone.
      if (w.consumed) { this.log('nonlinear:pause-consumed', { key: w.key }); return; }
      const go = (d) => {
        if (this.pauseSlot !== slot) return;
        if (!d.plan.length) {
          this.log('nonlinear:failed', { key: w.key, reason: d.ads.length ? 'no candidate renderable (PLY-41)' : 'empty resolution (PLY-39, PLY-64)' });
          slot.i += 1; this.tryPauseWindow(slot); return;
        }
        this.startPausePlan(slot, w, d);
      };
      if (w.doc && this.usable(w, slot.php) && !w.inflight) { go(w.doc); return; }
      this.resolve(w, w.doc ? 'expired at the pause' : 'at the pause').then((r) => {
        if (this.pauseSlot !== slot) return;
        if (r.failed) { slot.i += 1; this.tryPauseWindow(slot); return; }
        go(r);
      });
    }

    startPausePlan(slot, w, d) {
      slot.w = w;
      slot.d = d;
      slot.k = -1;
      slot.t0 = now();
      slot.plan = [];
      let t = 0;
      // PLY-32: the cap bounds nothing on a pause slot.
      for (const c of d.plan) { slot.plan.push({ c, start: t, shown: c.duration }); t += c.duration; }
      this.log('nonlinear:pause-plan', { key: w.key, onExhausted: d.onExhausted, plan: slot.plan.map((p) => [p.c.index, p.c.option.index, p.c.layout, p.shown]) });
    }

    advancePause(slot) {
      if (!slot.plan) return;
      const t = (now() - slot.t0) / 1000;
      const k = slot.plan.findIndex((p) => t >= p.start && t < p.start + p.shown);
      if (k >= 0) {
        if (k !== slot.k) this.showPause(slot, k);
        return;
      }
      // §5.2.6, PLY-65: the candidates are exhausted while still paused.
      const how = slot.d.onExhausted;
      slot.plan = null;
      this.log('nonlinear:pause-exhausted', { key: slot.w.key, onExhausted: how });
      if (how === 'repeat') { this.startPausePlan(slot, slot.w, slot.d); return; }
      this.clearPauseSurface(slot);
      if (how === 'request-again' && !slot.stopped) {
        const w = slot.w;
        this.resolve(w, 'request-again').then((r) => {
          if (this.pauseSlot !== slot) return;
          // PLY-66: a document carrying no candidates ends the pause's ads.
          if (r.failed || !r.plan.length) { slot.stopped = true; this.log('nonlinear:pause-stop', { key: w.key, reason: r.failed || 'no candidates (PLY-66)' }); return; }
          this.startPausePlan(slot, w, r);
        });
      }
      // stop: the paused frame.
    }

    showPause(slot, k) {
      this.clearPauseSurface(slot);
      slot.k = k;
      const c = slot.plan[k].c;
      const el = this.surface(c, slot.w);
      if (el.sgaiPlayer) {
        const start = () => el.sgaiPlayer.play();
        if (el.readyState >= 1) start(); else el.sgaiPlayer.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, start);
      }
      slot.el = el;
      slot.shown = true;
      this.ref.container.dataset.sgaiLayout = c.layout;
      // PLY-64: consumed when a pause ad begins rendering.
      if (slot.w.executeOnce && !slot.w.consumed) { slot.w.consumed = true; this.log('nonlinear:consumed', { key: slot.w.key }); }
      this.log('nonlinear:pause-show', { key: slot.w.key, candidate: c.index, option: c.option.index, layout: c.layout });
    }

    clearPauseSurface(slot) {
      if (!slot.el) return;
      if (slot.el.sgaiPlayer) { try { slot.el.sgaiPlayer.reset(); } catch (e) { /* gone */ } slot.el.sgaiPlayer = null; }
      slot.el.remove();
      slot.el = null;
      slot.shown = false;
      this.main.style.visibility = 'visible';
      const on = this.execs.find((x) => x.el);
      this.ref.container.dataset.sgaiLayout = on ? on.plan[on.k].c.layout : 'none';
    }

    closePause(why) {
      const slot = this.pauseSlot;
      this.clearPauseSurface(slot);
      this.pauseSlot = null;
      this.log('nonlinear:pause-close', { why });
    }
  }

  (global.SGAI_FAMILIES = global.SGAI_FAMILIES || []).push(SgaiNonLinear);
})(window);
