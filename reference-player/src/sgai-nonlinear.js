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
// With T-07, the presentation: each form is put on screen through the
// compositor (sgai-compositor.js), which draws every layout token; this file
// says what is on screen and when — the slot timeline, the suspension and
// resumption of a form across the families (§4.5.8, §4.5.9: a pause ad over
// an overlay, R17.1/R17.2; a pause ad over a linear ad, R17.5; a window and
// the inherited linear events, R40.4, R40.5, R40.9), the windows declared in
// an alternative presentation's MPD (R40.6), the takeover of a `linear`
// option (§5.3.6), and the viewer's dismissal (§4.5.14). The beacons and the
// click are T-08's.
//
// With T-08, the beacons (§5.5.2): each candidate's <svta:Tracking> callback
// events, fired on the candidate's own presentation (time 0 when it begins
// rendering, whichever option rendered, R13.1, R13.6), de-duplicated within
// one presentation of the candidate by @id and by URL at one time (R6.5), and
// never past the end of that presentation: its shown duration when the cap
// trims it, the dismissal, the resume from a pause ad (R13.3). Elements and
// attributes of other namespaces inside the carrier are not read (R6.4).
// The click (§4.5.16, §5.6): a candidate's <svta:ClickThrough> is armed on its
// ad surface; the viewer's activation of that surface fires each URL of
// @trackingUris once and makes @uri available (R28.1, R28.2; sgai-click.js,
// shared with the linear family).
//
// Readings this file takes where the specification leaves room (each said
// where used):
// - a resolution request with no answer is given up after RESOLVE_TIMEOUT_MS
//   (PLY-39 fixes no time); a document arriving later is dropped;
// - the slot timeline of an overlay accrues the media time the presentation
//   that declares its window advances (PLY-31: a pause does not accrue; at
//   rate r a form of d s is on screen d/r s, PLY-69), plus, for an `on-top`
//   window composited over an alternative presentation, the time that
//   presentation advances (R40.5); a `linear` takeover accrues its own
//   playback; a pause slot runs on the wall clock while the viewer is paused;
// - the default relation is context/03's R40.9 and R40.4, not the spec's
//   PLY-49: a form on screen when an alternative presentation begins is
//   suspended and resumed in the same execution if the presentation that
//   declares it comes back inside the window's range (the tests follow
//   context/03; T-04 part C finding 2 records the disagreement);
// - a `linear` takeover on a static presentation pauses the primary and
//   resumes it where it stood; on a dynamic one the primary runs on hidden
//   (§5.3.6);
// - `@dismissAfter` absent means not dismissible (APS-19); the delay runs on
//   the slot timeline from the first candidate on screen (PLY-74);
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
//   primary's decoder, PLY-56 is a permission);
//
// For the other families: `ref.nonlinear` is this object; `active` says an
// overlay or pause ad is on screen; `attachAlternative({player, video, url,
// part})` is called by the linear family for each alternative presentation's
// player before it is initialised.
(function (global) {
  const OVERLAY = 'urn:svta:dash:sgai-overlay:2026';
  const PAUSE = 'urn:svta:dash:sgai-pause-trigger:2026';
  const SVTA = 'urn:svta:dash:sgai:2026';
  const DASH = 'urn:mpeg:dash:schema:mpd:2011';
  const CALLBACK = 'urn:mpeg:dash:event:callback:2015';
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
  const MAX_STEP = 1.0;                // s: a larger advance in one tick is a jump, not playback

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

  // @dismissAfter (§5.2.4): seconds before the slot may be dismissed;
  // absent or "never", not dismissible (APS-19).
  function dismissDelay(v) {
    if (v === null || v === undefined || v === 'never') return Infinity;
    const d = isoDuration(v);
    return isFinite(d) ? d : Infinity;
  }

  function rectOf(v) {
    const r = String(v || '').trim().split(/\s+/).map(Number);
    return r.length === 4 && r.every((x) => isFinite(x)) ? r : null;
  }

  // §5.5.2: a candidate's <svta:Tracking>, an EventStreamType of the
  // callback scheme with @value 1 (Table 47), its DASH Events' values the
  // URLs; @presentationTimeOffset subtracted, as the base. Returned as
  // [{ id, at (s on the candidate's presentation), url }], in time order,
  // document order kept between equal times (the first of two events sharing
  // an @id is the one that fires, §5.10.2.4).
  function trackingOf(ad) {
    const out = [];
    for (const es of children(ad, 'Tracking', SVTA)) {
      if (es.getAttribute('schemeIdUri') !== CALLBACK || es.getAttribute('value') !== '1') continue;
      const ts = num(es.getAttribute('timescale'), 1);
      const pto = num(es.getAttribute('presentationTimeOffset'), 0);
      for (const ev of children(es, 'Event', DASH)) {
        const url = (ev.textContent || ev.getAttribute('messageData') || '').trim();
        if (!url) continue;
        out.push({ id: ev.getAttribute('id'), at: (num(ev.getAttribute('presentationTime'), 0) - pto) / ts, url });
      }
    }
    return out.map((b, i) => [b, i]).sort((a, b) => a[0].at - b[0].at || a[1] - b[1]).map((e) => e[0]);
  }

  // One overlay or pause window, from its Event and its child element.
  class Window {
    constructor(family, e, child, order, tl) {
      const es = e.eventStream;
      const ts = es.timescale || 1;
      const period = es.period;
      const periodEnd = period && isFinite(period.duration) ? period.start + period.duration : Infinity;
      this.family = family;                       // 'overlay' | 'pause'
      this.id = String(e.id);
      this.order = order;                         // position inside its EventStream
      this.tl = tl;                               // the presentation that declares it
      this.opportunityDoc = tl.doc;
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
    }
  }

  class SgaiNonLinear {
    constructor(ref) {
      this.ref = ref;
      this.main = ref.video;
      this.log = ref.log;
      this.windows = new Map();   // key -> Window
      this.timelines = [];        // the presentations whose windows are read: the main one, then alternatives
      this.execs = [];            // active overlay executions
      this.pauseSlot = null;      // the active pause slot
      ref.nonlinear = this;
    }

    get active() { return this.execs.some((x) => x.h && !x.h.suspended) || !!(this.pauseSlot && this.pauseSlot.shown); }

    get caps() { return this.ref.profile.capabilities || {}; }

    attach(player) {
      this.player = player;
      this.mainTl = this.timeline({ key: 'main', player, video: this.main, url: this.ref.url, part: null });
      this.mainTl.ready = () => this.streamReady;
      this.ref.video.addEventListener('ratechange', () => this.syncRates());
      this.timer = setInterval(() => this.tick(), TICK_MS);
    }

    // A presentation whose MPD may declare windows: the main one, or an
    // alternative presentation the linear family plays (R40.6, PLY-51).
    timeline({ key, player, video, url, part }) {
      const ev = dashjs.MediaPlayer.events;
      const tl = { key, player, video, doc: url, part, main: !part, seeks: 0, chains: { overlay: [], pause: [] }, init: false };
      tl.time = () => video.currentTime;
      tl.live = () => !part || part.video === video;
      tl.ready = () => tl.init;
      // §5.1.3: both window schemes are dispatched on receive.
      for (const scheme of [OVERLAY, PAUSE]) {
        player.on(scheme, (e) => this.onReceive(e, tl), null, { mode: ev.EVENT_MODE_ON_RECEIVE });
      }
      player.on(ev.STREAM_INITIALIZED, () => { tl.init = true; if (tl.main) this.streamReady = true; });
      // Any seek of this presentation is a jump of its timeline: no slot time
      // accrues across it. Only the viewer's seek starts a new entry of the
      // spans (act, R34.6); the seek back to RT after a replacement does not.
      video.addEventListener('seeking', () => { tl.seeks += 1; });
      this.timelines.push(tl);
      return tl;
    }

    attachAlternative({ player, video, url, part }) {
      const tl = this.timeline({ key: 'alt' + this.timelines.length, player, video, url, part });
      this.log('nonlinear:alternative', { key: tl.key, url });
    }

    onReceive(payload, tl) {
      const e = payload.event;
      const es = e.eventStream;
      const scheme = es.schemeIdUri;
      const key = tl.key + '#' + scheme + '#' + e.id + '#' + (es.period ? es.period.id : '');
      if (this.windows.has(key)) return;   // dash.js dispatches again after a seek
      const family = scheme === OVERLAY ? 'overlay' : 'pause';
      const { el, order } = findWindow(tl.player.getManifest(), scheme, e.id, es.period && es.period.index);
      const w = new Window(family, e, el, order, tl);
      w.key = key;
      this.windows.set(key, w);
      this.log('nonlinear:receive', { key, family, PT: w.PT, end: w.end, ERT: w.ERT, capUnits: w.capUnits, ts: w.ts,
        admitted: w.admitted, relation: w.linearRelation, executeOnce: w.executeOnce, fires: w.fires, why: w.why });
      // PLY-48: a superseding window keeps the inherited linear events inside
      // its span from being resolved or executed until it presents no ad.
      if (w.linearRelation === 'supersede' && this.ref.linear && tl.main) {
        if (!w.fires) w.released = true;
        else {
          const off = this.ref.linear.addSuppressor((E) => !w.released && E.PRT >= w.PT - 1e-6 && E.PRT < w.end);
          w.release = () => { if (!w.released) { w.released = true; off(); this.log('nonlinear:supersede-released', { key }); } };
        }
      }
      if (w.fires) this.rebuildChains(tl, family);
    }

    // §4.5.6, PLY-40: windows of one family whose spans overlap are a chain,
    // ordered by presentation time and, for equal ones, by document order.
    rebuildChains(tl, family) {
      const ws = [...this.windows.values()].filter((w) => w.tl === tl && w.family === family && w.fires)
        .sort((a, b) => (a.PT - b.PT) || (a.order - b.order));
      const chains = [];
      for (const w of ws) {
        const last = chains[chains.length - 1];
        if (last && w.PT < last.end) { last.windows.push(w); last.end = Math.max(last.end, w.end); } else chains.push({ windows: [w], end: w.end });
      }
      for (const c of chains) c.windows.forEach((w) => { w.chain = c; });
      tl.chains[family] = chains;
    }

    // The viewer's seek of the primary ends the executions of its windows and
    // starts a new entry of every span (R34.6: a seek back is a new execution).
    onSeek(to) {
      for (const x of this.execs.slice()) if (x.w.tl.main) this.endExec(x, 'seek');
      for (const w of this.windows.values()) if (w.tl.main) w.resetEntry();
      this.log('nonlinear:seek', { from: this.main.currentTime, to });
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
        dismissAfter: dismissDelay(root.getAttribute('dismissAfter')),
        ads: children(root, 'Ad', SVTA), plan: [],
      };
      for (let i = 0; i < out.ads.length; i++) {
        const sel = await this.select(w, out.ads[i], url);
        if (sel) out.plan.push(Object.assign({ index: i + 1, doc: url, beacons: trackingOf(out.ads[i]),
          click: SgaiClick.parse(out.ads[i], url) }, sel));
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
        let background = null;
        if (layout === 'squeezeback-double-box-background') {
          // §5.3.6: the background is always a still image; its first request
          // failing makes the option unsatisfiable, as the ad's would (R5.9).
          const b = o.getAttribute('background');
          const bsrc = b ? new URL(b, docUrl).href : null;
          const ok = bsrc && await new Promise((r) => { const i = new Image(); i.onload = () => r(true); i.onerror = () => r(false); i.src = bsrc; });
          if (!ok) { this.log('nonlinear:option-skipped', { key: w.key, option: k + 1, layout, why: bsrc ? `the background's first request failed (R5.9)` : 'no @background' }); continue; }
          background = bsrc;
        }
        return { option: { index: k + 1, id: o.getAttribute('id') }, layout, form: f, src, rect: rectOf(o.getAttribute('rect')),
          duration: loaded.duration, make: loaded.make, background };
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
      const linear = this.ref.linear;
      for (const tl of this.timelines.slice()) {
        if (!tl.live()) { this.dropTimeline(tl); continue; }
        // An alternative's windows run while it is on screen (PLY-51).
        if (!tl.main && !(tl.part && tl.part.shown)) continue;
        if (!tl.ready() || tl.video.readyState < 1) continue;
        const php = tl.time();
        const over = tl.main && !!(linear && linear.active);
        for (const chain of tl.chains.overlay) this.processChain(chain, tl, php, over);
      }
      for (const x of this.execs.slice()) this.advance(x);
      for (const tl of this.timelines) {
        if (!tl.main && !(tl.part && tl.part.shown)) continue;
        for (const chain of tl.chains.pause) this.preResolvePause(chain, tl.time());
      }
      if (this.pauseSlot) this.advancePause(this.pauseSlot);
      if (this.ref.compositor) this.ref.compositor.refresh();
    }

    // An alternative presentation that ended takes its windows with it: a
    // form on its content ends with it (R40.9: anchored to the presentation
    // that declares it).
    dropTimeline(tl) {
      this.timelines.splice(this.timelines.indexOf(tl), 1);
      for (const x of this.execs.slice()) if (x.w.tl === tl) this.endExec(x, 'the presentation that declares the window ended');
      for (const [k, w] of this.windows) if (w.tl === tl) this.windows.delete(k);
      this.log('nonlinear:alternative-gone', { key: tl.key });
    }

    // The current window of a chain is its first that has not failed in this
    // entry (PLY-38); only it is resolved, ahead from PT − offset (PLY-6), and
    // executed when the playhead is in its span.
    processChain(chain, tl, php, over) {
      if (chain.windows.some((w) => w.executed)) return;
      const w = chain.windows.find((x) => !x.failed);
      if (!w) return;
      const before = w.seen;
      w.seen = php;
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
      if (php < w.PT) return;
      // R40.9 default: nothing is presented while an alternative presentation
      // is output; `on-top` is composited over it (R40.5).
      if (over && w.linearRelation !== 'on-top') return;
      // Nothing is composited before the primary's first frame is shown (the
      // linear family keeps it hidden until its first processing has run).
      if (tl.main && this.ref.linear && this.ref.linear.gated) return;
      if (w.doc && (this.usable(w, php) || w.doc.fresh)) {
        // §3.1: an overlay's slot timeline is the timeline of the content it
        // is composited over, so a window fired on the tick that crossed its
        // start begins at PT, not at the tick (the beacon at the candidate's
        // end would otherwise fall past the span's end by the tick's lag).
        w.lateBy = before !== undefined && before < w.PT && php - w.PT <= MAX_STEP ? php - w.PT : 0;
        this.fire(w);
        return;
      }
      // PLY-9: not usable when the opportunity fires: a new request, whose
      // document serves this opportunity whatever its @validFor.
      this.resolve(w, w.doc ? 'expired at the opportunity' : 'at the opportunity').then((r) => {
        if (r.failed) this.fail(w, r.failed); else r.fresh = true;
      });
    }

    fail(w, reason) {
      if (w.failed) return;
      w.failed = true;
      this.log('nonlinear:failed', { key: w.key, reason, php: w.tl.time() });
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
      const php = w.tl.time();
      const lateBy = w.lateBy || 0;
      w.lateBy = 0;
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
      const x = { w, d, PRTA: php, plan, k: -1, h: null, el: null, slotT: lateBy, lastT: php, seeks: w.tl.seeks,
        lastAlt: null, lastAd: null, lastWall: null, overAlt: null, heldMain: false, stall: null, shownAt: null };
      this.execs.push(x);
      this.log('nonlinear:execute', { key: w.key, PRTA: php, capUnits: w.capUnits, ts: w.ts,
        plan: plan.map((p) => ({ candidate: p.c.index, option: p.c.option.index, layout: p.c.layout,
          start: p.start, shown: p.shown })), windowEnd: w.end });
      this.advance(x);
    }

    // The <video> a form of this execution composes with: the presentation
    // that declares the window or, for an `on-top` window over an alternative
    // presentation, that presentation (R40.5).
    contentOf(x) {
      const lin = this.ref.linear;
      if (x.w.tl.main && x.w.linearRelation === 'on-top' && lin && lin.video) return lin.video;
      return x.w.tl.video;
    }

    // The time the slot timeline advanced since the last tick (s).
    accrue(x) {
      const w = x.w;
      const tl = w.tl;
      const lin = this.ref.linear;
      const step = (d) => (d >= 0 && d <= MAX_STEP ? d : 0);
      let d = 0;
      const p = x.plan[x.k];
      if (p && p.c.layout === 'linear') {
        // A takeover runs on its own playback (a video), or on the wall clock
        // at the primary's rate (an image or HTML).
        const v = x.el;
        if (v && v.tagName === 'VIDEO') {
          if (x.lastAd !== null && v.readyState >= 2) d += step(v.currentTime - x.lastAd);
          x.lastAd = v.readyState >= 2 ? v.currentTime : x.lastAd;
        } else {
          const t = now();
          if (x.lastWall !== null && !this.pauseSlot) d += step((t - x.lastWall) / 1000 * (this.main.playbackRate || 1));
          x.lastWall = t;
        }
      } else {
        const t = tl.time();
        if (tl.seeks === x.seeks) d += step(t - x.lastT);
        x.seeks = tl.seeks;
        x.lastT = t;
      }
      // R40.5: while composited over an alternative presentation, the slot
      // accrues on that presentation's timeline.
      const a = tl.main && w.linearRelation === 'on-top' && lin ? lin.position : null;
      if (a !== null && x.lastAlt !== null) d += step(a - x.lastAlt);
      x.lastAlt = a;
      return d;
    }

    advance(x) {
      const w = x.w;
      const tl = w.tl;
      const lin = this.ref.linear;
      const over = tl.main && !!(lin && lin.active);
      x.slotT += this.accrue(x);
      const php = tl.time();
      // R40.5: a form composited over an alternative presentation ends when
      // that presentation ends.
      if (over && w.linearRelation === 'on-top' && lin.onScreen && x.h) x.overAlt = lin.alt;
      if (x.overAlt && (!lin || lin.alt !== x.overAlt)) { this.endExec(x, 'the alternative presentation it was composited over ended (R40.5)'); return; }
      if (php >= w.end - EPS) {
        // The candidate on screen is presented up to the span's end.
        const p = x.plan[x.k];
        if (p) this.beacons(p, x.slotT - p.start + Math.max(0, w.end - php), w.key);
        this.endExec(x, 'the span ended');
        return;
      }
      // R40.9 default: suspended while an alternative presentation is output,
      // resumed in the same execution when the content comes back inside the
      // range (R40.4).
      if (over && w.linearRelation !== 'on-top') {
        if (x.h && !x.h.suspended) { x.h.suspend(); this.syncAd(x, false); this.log('nonlinear:suspend', { key: w.key, slotT: x.slotT, why: 'an alternative presentation is output (R40.9)' }); }
        return;
      }
      if (x.h && x.h.suspended && !this.pauseShown()) { x.h.resume(); this.log('nonlinear:resume', { key: w.key, slotT: x.slotT }); }
      const k = x.plan.findIndex((p) => x.slotT >= p.start - 1e-6 && x.slotT < p.start + p.shown - 1e-6);
      if (k < 0) {
        const last = x.plan[x.plan.length - 1];
        if (x.slotT >= (last ? last.start + last.shown : 0) - 1e-6) {
          if (x.plan[x.k]) this.beacons(x.plan[x.k], x.plan[x.k].shown, w.key);   // it completed
          this.endExec(x, 'candidates exhausted or the cap reached');
        }
        return;
      }
      if (k !== x.k) {
        if (x.plan[x.k]) this.beacons(x.plan[x.k], x.plan[x.k].shown, w.key);   // it completed
        this.showCandidate(x, k);
      }
      this.beacons(x.plan[k], x.slotT - x.plan[k].start, w.key);
      // PLY-52: during a pause ad, the overlay is suspended (the compositor
      // keeps the pause ad the only form on screen).
      this.syncAd(x, this.contentPlaying(x) && !this.pauseShown());
      this.watchStall(x);
    }

    pauseShown() { return !!(this.pauseSlot && this.pauseSlot.shown); }

    // Whether the content under an execution's form is playing.
    contentPlaying(x) {
      const p = x.plan[x.k];
      if (p && p.c.layout === 'linear') return !this.pauseShown();
      const v = this.contentOf(x);
      return !!v && !v.paused;
    }

    // A video form plays while its slot timeline runs, at the content's rate
    // (R19.1), and stands still while it does not.
    syncAd(x, playing) {
      const v = x.el;
      if (!v || !v.sgaiPlayer || !x.started) return;
      const rate = (this.contentOf(x) || this.main).playbackRate || 1;
      if (v.playbackRate !== rate) v.sgaiPlayer.setPlaybackRate(rate);
      if (playing && v.paused && !v.ended) v.sgaiPlayer.play();
      else if (!playing && !v.paused) v.sgaiPlayer.pause();
    }

    syncRates() { for (const x of this.execs) if (x.el && x.el.sgaiPlayer && x.started) this.syncAd(x, !x.el.paused); }

    showCandidate(x, k) {
      this.removeSurface(x);
      x.k = k;
      const p = x.plan[k];
      const c = p.c;
      const el = c.make();
      this.identify(el, c, x.w, 'ad');
      this.armClick(el, c, x.w);
      let bg = null;
      if (c.background) {
        bg = new Image();
        bg.src = c.background;
        this.identify(bg, c, x.w, 'background');
      }
      x.el = el;
      x.stall = null;
      x.started = false;
      x.lastAd = null;
      x.lastWall = null;
      if (x.shownAt === null) x.shownAt = x.slotT;
      // §5.3.6: a takeover on a static presentation suspends the primary and
      // resumes it where it stood; on a dynamic one the primary runs on.
      if (c.layout === 'linear' && x.w.tl.main && !this.isDynamic() && !this.main.paused) {
        this.player.pause();
        x.heldMain = true;
      } else if (c.layout !== 'linear') this.releaseMain(x);
      x.h = this.ref.compositor.present(el, c.layout, { kind: 'overlay', rect: c.rect, background: bg, content: () => this.contentOf(x) });
      if (el.sgaiPlayer) {
        const v = el;
        const start = () => {
          if (x.el !== v) return;
          x.started = true;
          v.sgaiPlayer.setPlaybackRate((this.contentOf(x) || this.main).playbackRate || 1);
          v.sgaiPlayer.play();
        };
        v.addEventListener('playing', () => { x.stall = { t: now(), at: v.currentTime, php: this.main.currentTime }; }, { once: true });
        if (v.readyState >= 1) start(); else v.sgaiPlayer.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, start);
      }
      this.log('nonlinear:show', { key: x.w.key, candidate: c.index, option: c.option.index, layout: c.layout,
        php: x.w.tl.time(), slotT: x.slotT });
    }

    isDynamic() { try { return this.player.isDynamic(); } catch (e) { return false; } }

    releaseMain(x) {
      if (!x.heldMain) return;
      x.heldMain = false;
      if (!this.pauseSlot) this.player.play();
    }

    // The identity the harness reads (sgai-reference.js, the observation contract).
    identify(el, c, w, element) {
      const d = el.dataset;
      d.sgaiElement = element;
      d.sgaiDoc = c.doc;
      d.sgaiCandidateIndex = String(c.index);
      d.sgaiOptionIndex = String(c.option.index);
      d.sgaiOpportunityDoc = w.opportunityDoc;
      d.sgaiOpportunityEvent = w.id;
    }

    // PLY-84: the viewer's activation of the surface (SgaiClick.arm).
    armClick(el, c, w) {
      SgaiClick.arm(el, c.click && (() => this.activate(c, w)));
    }

    // R28.1, R28.2 (SgaiClick.activate).
    activate(c, w) {
      const ct = c.click;
      this.log('nonlinear:click', { key: w.key, candidate: c.index, option: c.option.index, uri: ct.uri, tracking: ct.tracking });
      SgaiClick.activate(this.ref, ct);
    }

    // PLY-86: a video option that stops advancing while its content plays,
    // or that dash.js reports in error, has failed at runtime and is aborted.
    watchStall(x) {
      const v = x.el;
      if (!v || !v.sgaiPlayer) return;
      if (v.sgaiError) { this.abort(x, `video error: ${v.sgaiError}`); return; }
      const s = x.stall;
      if (!s || v.ended) return;
      const content = this.contentOf(x) || this.main;
      if (v.currentTime > s.at + 0.001 || content.paused || v.paused) { x.stall = { t: now(), at: v.currentTime, php: content.currentTime }; return; }
      if (now() - s.t > STALL_MS && content.currentTime > s.php + 0.5) this.abort(x, `video stalled ${Math.round(now() - s.t)} ms at ${v.currentTime.toFixed(3)} s`);
    }

    abort(x, reason) {
      this.log('nonlinear:abort', { key: x.w.key, reason, php: x.w.tl.time() });
      this.endExec(x, 'aborted (PLY-86)');
    }

    removeSurface(x) {
      const el = x.el;
      if (!el) return;
      if (el.sgaiPlayer) { try { el.sgaiPlayer.reset(); } catch (e) { /* gone */ } el.sgaiPlayer = null; }
      if (x.h) x.h.remove();
      else el.remove();
      x.h = null;
      x.el = null;
    }

    // §5.5.2: the beacons of one presentation of a candidate (a plan entry)
    // whose time its presentation has reached (`upTo`, s from its start),
    // never past what it shows (R13.3: a time after the trim is not reached).
    // §5.5.2, R6.5: within the presentation, a second event with an @id
    // already processed, or the same URL at the same time, is the same beacon.
    beacons(p, upTo, key) {
      const bs = p.c.beacons;
      if (!bs || !bs.length) return;
      if (!p.beacons) p.beacons = { next: 0, seen: new Set() };
      const st = p.beacons;
      const limit = Math.min(upTo, p.shown) + 1e-6;
      while (st.next < bs.length && bs[st.next].at <= limit) {
        const b = bs[st.next++];
        const keys = [`url|${b.at.toFixed(6)}|${b.url}`];
        if (b.id !== null) keys.push(`id|${b.id}`);
        if (keys.some((k) => st.seen.has(k))) { this.log('nonlinear:beacon-ignored', { key, candidate: p.c.index, id: b.id, at: b.at, url: b.url }); continue; }
        for (const k of keys) st.seen.add(k);
        this.log('nonlinear:beacon', { key, candidate: p.c.index, option: p.c.option.index, id: b.id, at: b.at, url: b.url });
        fetch(b.url, { mode: 'no-cors', credentials: 'omit', cache: 'no-store', keepalive: true }).catch(() => {});
      }
    }

    endExec(x, why) {
      const i = this.execs.indexOf(x);
      if (i < 0) return;
      this.execs.splice(i, 1);
      this.removeSurface(x);
      this.releaseMain(x);
      this.log('nonlinear:end', { key: x.w.key, why, php: x.w.tl.time(), slotT: x.slotT });
    }

    // ------------------------------------------------------------------ the viewer's actions

    act(action) {
      const lin = this.ref.linear;
      const linearOn = !!(lin && lin.active);
      switch (action.do) {
        case 'pause': return this.pause(linearOn);
        case 'resume': {
          const slot = this.pauseSlot;
          if (!slot) return null;
          this.closePause('resume');
          // PLY-60: back to what the pause interrupted, at once.
          if (slot.overLinear && lin) { lin.resumeAd(); return { done: 'pause ad removed, linear ad resumed' }; }
          this.player.play();
          return { done: 'pause ad removed, primary resumed' };
        }
        case 'dismiss': return this.dismiss();
        case 'seek':
          // The viewer's seek: a new entry of every span (R34.6). The linear
          // family or the core moves the playhead.
          if (!linearOn) this.onSeek(action.to);
          return null;
        default: return null;
      }
    }

    // A pause inside a pause window opens a pause slot (PLY-11). Over a
    // linear ad, the windows applicable to it are those of its own MPD and
    // the main presentation's `on-top` ones (PLY-55, R17.5); the linear ad
    // is suspended, and resumed where it was on resume.
    pause(linearOn) {
      const ws = [];
      for (const tl of this.timelines) {
        if (linearOn ? (tl.part && !tl.part.shown) : !tl.main) continue;
        const php = tl.time();
        for (const chain of tl.chains.pause) {
          for (const w of chain.windows) {
            if (linearOn && tl.main && w.linearRelation !== 'on-top') continue;
            if (php >= w.PT && php < w.end) ws.push(w);
          }
        }
      }
      if (!ws.length) return null;
      if (linearOn) this.ref.linear.suspend();
      else this.player.pause();
      for (const x of this.execs) this.syncAd(x, false);
      const slot = { windows: ws, i: 0, plan: null, k: -1, el: null, h: null, shown: false, again: 0,
        php: ws[0].tl.time(), overLinear: linearOn };
      this.pauseSlot = slot;
      this.log('nonlinear:pause', { php: slot.php, overLinear: linearOn, windows: ws.map((w) => w.key) });
      this.tryPauseWindow(slot);
      return { done: linearOn ? 'linear ad suspended inside a pause window' : 'primary paused inside a pause window' };
    }

    // PLY-74, PLY-75: a dismissal ends the whole slot on screen once its
    // delay has elapsed on the slot timeline.
    dismiss() {
      const slot = this.pauseSlot;
      if (slot && slot.shown) {
        const t = (now() - slot.firstShown) / 1000;
        if (!(t >= slot.d.dismissAfter - 1e-6)) return { done: null, reason: `the pause slot is not dismissible (after ${slot.d.dismissAfter} s; ${t.toFixed(3)} s shown)` };
        this.clearPauseSurface(slot);
        slot.plan = null;
        slot.stopped = true;   // no repeat, no request-again (PLY-75)
        this.log('nonlinear:dismissed', { key: slot.w.key, after: t });
        return { done: 'pause slot dismissed; the paused frame stays until the resume' };
      }
      const x = this.execs.find((e) => e.h && !e.h.suspended);
      if (!x) return null;
      const t = x.slotT - (x.shownAt || 0);
      if (!(t >= x.d.dismissAfter - 1e-6)) return { done: null, reason: `the slot is not dismissible (after ${x.d.dismissAfter} s; ${t.toFixed(3)} s shown)` };
      this.endExec(x, 'dismissed by the viewer (R35.4)');
      return { done: 'slot dismissed' };
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
      this.advancePause(slot);
    }

    advancePause(slot) {
      if (!slot.plan) return;
      const t = (now() - slot.t0) / 1000;
      const k = slot.plan.findIndex((p) => t >= p.start && t < p.start + p.shown);
      const prev = slot.plan[slot.k];
      if (k >= 0) {
        if (k !== slot.k) {
          if (prev) this.beacons(prev, prev.shown, slot.w.key);   // it completed
          this.showPause(slot, k);
        }
        this.beacons(slot.plan[k], t - slot.plan[k].start, slot.w.key);
        return;
      }
      if (prev) this.beacons(prev, prev.shown, slot.w.key);   // the last one completed
      // §5.2.6, PLY-65: the candidates are exhausted while still paused.
      const how = slot.d.onExhausted;
      slot.plan = null;
      this.log('nonlinear:pause-exhausted', { key: slot.w.key, onExhausted: how });
      if (how === 'repeat') { this.startPausePlan(slot, slot.w, slot.d); return; }
      this.clearPauseSurface(slot);
      if (how === 'request-again' && !slot.stopped) {
        const w = slot.w;
        this.resolve(w, 'request-again').then((r) => {
          if (this.pauseSlot !== slot || slot.stopped) return;
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
      const el = c.make();
      this.identify(el, c, slot.w, 'ad');
      this.armClick(el, c, slot.w);
      const lin = this.ref.linear;
      slot.h = this.ref.compositor.present(el, c.layout, { kind: 'pause', rect: c.rect,
        content: () => (slot.overLinear && lin && lin.video) || this.main });
      if (el.sgaiPlayer) {
        const start = () => el.sgaiPlayer.play();
        if (el.readyState >= 1) start(); else el.sgaiPlayer.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, start);
      }
      slot.el = el;
      slot.shown = true;
      if (slot.firstShown === undefined) slot.firstShown = now();
      // PLY-64: consumed when a pause ad begins rendering.
      if (slot.w.executeOnce && !slot.w.consumed) { slot.w.consumed = true; this.log('nonlinear:consumed', { key: slot.w.key }); }
      this.log('nonlinear:pause-show', { key: slot.w.key, candidate: c.index, option: c.option.index, layout: c.layout });
    }

    clearPauseSurface(slot) {
      if (!slot.el) return;
      if (slot.el.sgaiPlayer) { try { slot.el.sgaiPlayer.reset(); } catch (e) { /* gone */ } slot.el.sgaiPlayer = null; }
      slot.shown = false;
      if (slot.h) slot.h.remove(); else slot.el.remove();
      slot.h = null;
      slot.el = null;
    }

    // PLY-57: the pause ad leaves the screen in this same task, so the next
    // frame the compositor produces no longer has it.
    closePause(why) {
      const slot = this.pauseSlot;
      this.pauseSlot = null;
      this.clearPauseSurface(slot);
      for (const x of this.execs) if (x.h && x.h.suspended && !(x.w.tl.main && this.ref.linear && this.ref.linear.active && x.w.linearRelation !== 'on-top')) x.h.resume();
      this.log('nonlinear:pause-close', { why });
    }
  }

  (global.SGAI_FAMILIES = global.SGAI_FAMILIES || []).push(SgaiNonLinear);
})(window);
