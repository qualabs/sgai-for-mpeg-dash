// The linear family of the reference (phase 11, ADR 0083): ISO/IEC 23009-1
// 6th edition's alternative-MPD insertion and replacement events (§5.16), the
// execution queue by PRT (§5.16.2.2) with @executeOnce, @maxDuration, @clip,
// @returnOffset, @earliestResolutionTimeOffset and @startWithOffset, and the
// List MPD (§8.14) with its Linked Periods (§5.3.2.6), and the callback
// events (§5.10.4.5) of the alternative MPDs, and the click on a candidate:
// the <svta:ClickThrough> of a List MPD's Period (spec §4.7.5, the only
// place a linear candidate carries one), armed on its <video> (sgai-click.js;
// R28.1, R28.2). Out: SCTE-35, MPD chaining, xlink, @noJump, event updates
// (@status="update" is not re-dispatched by dash.js 5.3.0, T-01).
//
// Shape (ADR 0075, measured in T-01): the primary MediaPlayer dispatches the
// events on receive; this family keeps the table T and the queue QE
// (§5.16.2.2.2), runs the playhead-triggered processing (§5.16.2.2.5) on a
// 10 ms tick, and plays the alternative presentation in MediaPlayers of its
// own, one per Period of the alternative (a single-period MPD has one, a List
// MPD one per Linked Period), each on a <video> of its own inside the
// viewport. dash.js plays neither a List MPD nor an MPD it did not fetch
// itself without asking again, so the family fetches every alternative
// document once, makes its BaseURL absolute, and hands dash.js a blob: URL.
// The callback events are taken out of that copy and fired here, on start
// (Annex A's dispatch mode for the scheme), as the alternative's own playhead
// passes them: dash.js would fire a callback at 0 the moment a preloaded
// player initialises, before anything is shown.
//
// Readings this file takes where the base leaves room (each said where used):
// - after a termination the queue is not reset (A.14.5), so an insertion
//   with @executeOnce="false" does not re-execute at RT = PRTA;
// - before the alternative plays, only its first Linked Period is resolved;
//   the others from PeriodStart − @earliestResolutionTimeOffset of the
//   alternative's own playhead, which exists once it plays;
// - while a due event's document is still being fetched, the primary is
//   held at PRT (§5.16.2.2.6 NOTE 2 admits resolving at PRTA) for at most
//   HOLD_MS; past that the execution fails;
// - an alternative MPD of type "dynamic" (a live alternative) is a single
//   Period like a static one; with no MPD@mediaPresentationDuration its APD
//   is infinite (nothing in the MPD ends it), and its playhead is counted
//   from where it started, its live edge (§5.16.2.2.6).
//
// Observation contract (sgai-reference.js): the <video> of the alternative is
// `data-sgai-element="ad"` with `data-sgai-doc` (the alternative MPD, or the
// List MPD), `data-sgai-candidate-id` (its Period@id, the Linked Period's for
// a List), the opportunity (main MPD URL, Event@id) and
// `data-sgai-presentation`, stamped on the Part's first frame and kept across
// a suspension (R17.5: a pause and its resume are one presentation); the
// primary <video> is hidden while it shows, and the viewport's layout is `linear`.
//
// For the other families: `ref.linear` is this object. `active` says a linear
// alternative is on screen (or about to be), `onScreen` that its first frame
// is, `position` its playhead (s on its own timeline, null when none plays),
// `video` the <video> showing it;
// `suspend()` / `resumeAd()` pause
// and resume it (a pause ad over a linear ad, R17.5); `addSuppressor(fn)`
// keeps every event for which fn(E) is true from being resolved or executed
// until fn says otherwise (a window that supersedes linear events, R40.3), and
// returns the function that removes it. The viewport's layout is the
// compositor's (sgai-compositor.js): this family tells it when its
// alternative starts or ends. Each alternative's player is offered to the
// non-linear family before it is initialised (`ref.nonlinear.attachAlternative`),
// so that the windows its MPD declares are that presentation's own (R40.6).
(function (global) {
  const INSERT = 'urn:mpeg:dash:event:alternativeMPD:insert:2025';
  const REPLACE = 'urn:mpeg:dash:event:alternativeMPD:replace:2025';
  const SCHEMES = [INSERT, REPLACE];
  const CALLBACK = 'urn:mpeg:dash:event:callback:2015';
  const TICK_MS = 10;
  const EPS = 0.02;          // s: a Period or the alternative counts as ended this close to its end
  // s of wall time: how far currentTime and performance.now() may be read
  // apart in one tick. Media time is that times the rate: measured up to
  // 0.028 s x 2 at 2x under load (T-09 scheme-and-lag), against seconds for
  // a seek or a start at an offset.
  const CLOCK_SLACK = 0.1;
  const HOLD_MS = 3000;      // the longest the primary is held at PRT for a document in flight
  const START_MS = 8000;     // the longest an alternative may take to show its first frame

  const bool = (v, d) => (v === undefined || v === null || v === '' ? d : String(v) === 'true');
  const num = (v, d) => (v === undefined || v === null || v === '' ? d : Number(v));

  // xs:duration as used by MPDs (PnDTnHnMnS), in seconds; NaN when absent.
  function isoDuration(s) {
    if (!s) return NaN;
    const m = /^P(?:(\d+(?:\.\d+)?)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$/.exec(s.trim());
    if (!m) return NaN;
    return (Number(m[1] || 0) * 86400) + (Number(m[2] || 0) * 3600) + (Number(m[3] || 0) * 60) + Number(m[4] || 0);
  }

  // The InsertPresentation / ReplacePresentation of an Event, from the
  // manifest dash.js parsed: its Event object does not carry the child (T-01),
  // with its EventStream's @value (null when absent: dash.js's EventStream
  // object reports an absent @value as "").
  function findChild(manifest, scheme, id, periodIndex) {
    const periods = (manifest && manifest.Period) || [];
    const order = periodIndex !== undefined && periods[periodIndex] ? [periods[periodIndex]] : periods;
    const name = scheme === INSERT ? 'InsertPresentation' : 'ReplacePresentation';
    for (const p of order) {
      for (const es of (p && p.EventStream) || []) {
        if (es.schemeIdUri !== scheme) continue;
        for (const ev of es.Event || []) {
          if (String(ev.id) !== String(id)) continue;
          const el = Array.isArray(ev[name]) ? ev[name][0] : ev[name];
          return { el: el || null, value: es.value === undefined || es.value === null ? null : String(es.value) };
        }
      }
    }
    return { el: null, value: null };
  }

  const children = (el, name) => Array.from(el.children).filter((c) => c.localName === name);

  // An MPD's text with its MPD-level BaseURL made absolute against the URL it
  // was fetched from (§5.6), so it can be handed to dash.js as a blob: URL.
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

  // §5.10.4.5.3: a callback event in an MPD is an EventStream with
  // @schemeIdUri "urn:mpeg:dash:event:callback:2015" and @value 1 whose
  // Event value is the URL. Removed from the document; returned as
  // [{ key, at (s on the Period's timeline), url }].
  function takeCallbacks(doc) {
    const out = [];
    for (const period of children(doc.documentElement, 'Period')) {
      for (const es of children(period, 'EventStream')) {
        if (es.getAttribute('schemeIdUri') !== CALLBACK) continue;
        const value = es.getAttribute('value');
        const ts = num(es.getAttribute('timescale'), 1);
        const pto = num(es.getAttribute('presentationTimeOffset'), 0);
        if (value === '1') {
          for (const ev of children(es, 'Event')) {
            const url = (ev.textContent || ev.getAttribute('messageData') || '').trim();
            if (!url) continue;
            out.push({ key: `${CALLBACK}|${value}|${ev.getAttribute('id')}`,
              at: (num(ev.getAttribute('presentationTime'), 0) - pto) / ts, url });
          }
        }
        es.remove();
      }
    }
    return out.sort((a, b) => a.at - b.at);
  }

  // The longest segment of an MPD (s): MPD@maxSegmentDuration, else the
  // longest SegmentTemplate@duration of its first Period; NaN when it says
  // neither (a SegmentTimeline only).
  function segmentDuration(doc) {
    const max = isoDuration(doc.documentElement.getAttribute('maxSegmentDuration'));
    if (max > 0) return max;
    let out = NaN;
    for (const t of doc.getElementsByTagNameNS('*', 'SegmentTemplate')) {
      const d = num(t.getAttribute('duration'), NaN) / num(t.getAttribute('timescale'), 1);
      if (d > 0 && !(d <= out)) out = d;
    }
    return out;
  }

  // GET a document and parse it as an MPD: { ok, doc, reason }.
  async function fetchMpd(url) {
    let res;
    try { res = await fetch(url, { credentials: 'omit', cache: 'no-store' }); } catch (e) {
      return { ok: false, reason: `request failed: ${e && e.message}` };
    }
    if (!res.ok) return { ok: false, reason: `HTTP ${res.status}` };
    const text = await res.text();
    const doc = new DOMParser().parseFromString(text, 'application/xml');
    const root = doc.documentElement;
    if (!root || root.localName !== 'MPD' || doc.getElementsByTagName('parsererror').length) {
      return { ok: false, reason: 'not an MPD' };
    }
    return { ok: true, doc };
  }

  // One Period of the alternative presentation: a single-period MPD's only
  // Period, or a Linked Period of a List MPD. `start` and `duration` are on
  // the alternative's timeline, in seconds.
  class Part {
    constructor(family, { id, doc, importedUri, ert, duration, click, live = false }) {
      this.family = family;
      this.live = live;             // MPD@type "dynamic": played from its live edge
      this.origin = 0;              // s on its own timeline where it started playing
      this.click = click;           // its <svta:ClickThrough> (SgaiClick.parse), or null
      this.id = id;                 // data-sgai-candidate-id
      this.doc = doc;               // data-sgai-doc
      this.importedUri = importedUri;
      this.ert = ert;               // ImportedMPD@earliestResolutionTimeOffset (s)
      this.duration = duration;     // provisional until resolved (Linked Period@duration)
      this.start = 0;
      this.state = 'unresolved';    // unresolved | resolving | ready | failed | done
      this.blobUrl = null;
      this.video = null;
      this.player = null;
      this.loaded = null;
    }

    // §5.3.2.6.3: fetch the imported MPD; it must be a single-Period MPD
    // with content; the Linked Period's @id takes precedence, and its
    // @duration is the smaller of the two.
    async resolve() {
      if (this.state !== 'unresolved') return this.loaded;
      this.state = 'resolving';
      this.loaded = (async () => {
        const r = await fetchMpd(this.importedUri);
        if (!r.ok) return this.fail(r.reason);
        const periods = children(r.doc.documentElement, 'Period');
        if (periods.length !== 1 || !children(periods[0], 'AdaptationSet').length) {
          return this.fail('imported MPD is not a single Period with content');
        }
        const own = isoDuration(periods[0].getAttribute('duration'))
          || isoDuration(r.doc.documentElement.getAttribute('mediaPresentationDuration'));
        if (isFinite(own)) this.duration = isFinite(this.duration) ? Math.min(this.duration, own) : own;
        if (!(this.duration > 0)) return this.fail('no media');
        periods[0].setAttribute('id', this.id);
        return this.ready(r.doc, this.importedUri);
      })();
      return this.loaded;
    }

    fail(reason) {
      this.state = 'failed';
      this.family.log('linear:part-failed', { id: this.id, uri: this.importedUri, reason });
      return false;
    }

    // The document is in: take its callback events out, create the player
    // and preload (autoplay off).
    ready(doc, url) {
      this.callbacks = takeCallbacks(doc);
      const text = absolutised(doc, url);
      this.blobUrl = URL.createObjectURL(new Blob([text], { type: 'application/dash+xml' }));
      this.state = 'ready';
      const f = this.family;
      const v = document.createElement('video');
      v.playsInline = true;
      v.muted = f.main.muted;
      v.style.cssText = 'position:absolute;left:0;top:0;width:100%;height:100%;object-fit:contain;visibility:hidden';
      v.dataset.sgaiElement = 'ad';
      v.dataset.sgaiDoc = this.doc;
      v.dataset.sgaiCandidateId = this.id;
      f.ref.container.appendChild(v);
      this.video = v;
      SgaiClick.arm(v, this.click && (() => f.activate(this)));
      const p = dashjs.MediaPlayer().create();
      p.updateSettings({ debug: { logLevel: dashjs.Debug.LOG_LEVEL_NONE } });
      // A live Part starts at "the most recent available segment (i.e. the
      // live edge)" (§5.16.4, @returnOffset NOTE 1): one segment behind the
      // end of its availability window, not dash.js's default of four.
      // (liveDelayFragmentCount does not do it: dash.js has no segment
      // duration yet when it computes the delay, and falls back to 4 x
      // @minBufferTime — measured.)
      const seg = this.live ? segmentDuration(doc) : NaN;
      if (seg > 0) p.updateSettings({ streaming: { delay: { liveDelay: seg } } });
      p.clearDefaultUTCTimingSources();
      p.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, () => { this.initialized = true; });
      p.on(dashjs.MediaPlayer.events.ERROR, (e) => {
        this.error = JSON.stringify((e && e.error) || e).slice(0, 200);
        f.log('linear:part-error', { id: this.id, error: this.error });
      });
      if (f.ref.nonlinear && f.ref.nonlinear.attachAlternative) {
        f.ref.nonlinear.attachAlternative({ player: p, video: v, url, part: this });
      }
      p.initialize(v, this.blobUrl, false);
      this.player = p;
      this.seg = seg;
      if (seg > 0) this.trackLiveEdge(seg);
      return true;
    }

    // A preloaded live Part follows its live edge until it plays: each time a
    // new segment becomes available it is sought to again, so the segment it
    // will start from is already buffered when the execution comes (one
    // sought to only then is fetched then: 0.3-0.8 s of the paused primary
    // on screen, measured on E15/E17).
    trackLiveEdge(seg) {
      let at = null;
      this.tracker = setInterval(() => {
        if (!this.player || this.playing) { clearInterval(this.tracker); return; }
        if (!this.initialized) return;
        const w = this.player.getDvrWindow();
        const n = w && Math.floor(w.end / seg);
        if (!(n > 0) || n === at) return;
        at = n;
        this.player.seekToOriginalLive();
      }, 250);
    }

    destroy() {
      clearInterval(this.tracker);
      if (this.player) { try { this.player.reset(); } catch (e) { /* already gone */ } }
      if (this.video) this.video.remove();
      if (this.blobUrl) URL.revokeObjectURL(this.blobUrl);
      this.player = null;
      this.video = null;
      this.blobUrl = null;
    }
  }

  class SgaiLinear {
    constructor(ref) {
      this.ref = ref;
      this.main = ref.video;
      this.log = ref.log;
      this.table = new Map();      // T, keyed by scheme and Event@id
      this.queue = [];             // QE, ordered by PRT
      this.alt = null;             // alt_client: the execution in progress
      this.suppressors = new Set();
      this.seeking = false;
      this.streamReady = false;
      // The primary stays hidden until the first processing has run: an
      // event due where playback starts (a pre-roll, a join inside an active
      // interval) pauses the primary on its first frame, and that frame must
      // not be shown before the alternative's. Measured without it: UC-01,
      // E4, E5 show "primary (paused)" for 0.3-1.2 s first.
      this.gated = true;
      this.main.style.visibility = 'hidden';
      ref.linear = this;
    }

    get active() { return !!this.alt; }

    get onScreen() { return !!(this.alt && this.alt.parts.some((p) => p.shown && p.video)); }

    get position() { return this.alt && this.alt.started ? this.altPosition(this.alt) : null; }

    // The <video> of the alternative on screen, or null.
    get video() {
      const part = this.alt && this.alt.parts[this.alt.index];
      return part && part.shown && part.video ? part.video : null;
    }

    // The viewport's layout follows from what every family has on screen.
    layoutChanged(layout) {
      if (this.ref.compositor) this.ref.compositor.refresh();
      else this.ref.container.dataset.sgaiLayout = layout;
    }

    addSuppressor(fn) {
      this.suppressors.add(fn);
      return () => this.suppressors.delete(fn);
    }

    suppressed(E) {
      for (const fn of this.suppressors) if (fn(E)) return true;
      return false;
    }

    attach(player) {
      this.player = player;
      const ev = dashjs.MediaPlayer.events;
      // §5.16.3 / §5.16.4: the dispatch mode of both schemes is on-receive.
      for (const scheme of SCHEMES) {
        player.on(scheme, (e) => this.onReceive(e), null, { mode: ev.EVENT_MODE_ON_RECEIVE });
      }
      player.on(ev.STREAM_INITIALIZED, () => { this.streamReady = true; });
      // §5.16.2.2.7: a user seek empties QE and the return to playback
      // resets it. Only the viewer's seek is one (act() below): the seeks
      // dash.js makes itself (to the start time, to RT) are not, and it may
      // report more than one seeked for one seek.
      this.main.addEventListener('seeked', () => {
        if (!this.seeking) return;
        this.seeking = false;
        this.resetQueue('seeked');
      });
      this.timer = setInterval(() => this.tick(), TICK_MS);
    }

    // §5.16.2.2.4, with the variables of Table 57.
    onReceive(payload) {
      const e = payload.event;
      const es = e.eventStream;
      const scheme = es.schemeIdUri;
      const { el: child, value } = findChild(this.player.getManifest(), scheme, e.id, es.period && es.period.index);
      if (!child || !child.uri) {
        this.log('linear:ignored', { id: e.id, reason: 'no InsertPresentation/ReplacePresentation@uri' });
        return;
      }
      const ts = es.timescale || 1;
      const period = es.period;
      const periodEnd = period && isFinite(period.duration) ? period.start + period.duration : Infinity;
      const PRT = e.calculatedPresentationTime;
      const key = scheme + '#' + e.id;
      const old = this.table.get(key);
      // §5.16.2.2.4 1): an event already in T whose status is "repeat" or
      // absent gets no further processing. dash.js dispatches every event of
      // the MPD again after a seek (measured); it is not a new event, and it
      // must not reset QE behind the queue's own rules (an executed event
      // would be put back). dash.js 5.3.0 does not dispatch @status="update"
      // at all (T-01), so no update reaches this point either.
      if (old) { this.log('linear:receive-repeat', { key }); return; }
      const E = {
        key, scheme, id: String(e.id), uri: child.uri, PRT,
        // EventStream@value, null when absent: with the scheme and Event@id it
        // identifies the opportunity (data-sgai-opportunity-*).
        value,
        // EAP = PRT + Event@duration; with no @duration, the end of the Period.
        EAP: Math.min(e.duration === undefined || e.duration === null || isNaN(e.duration) ? Infinity : PRT + e.duration, periodEnd),
        // ERT: @earliestResolutionTimeOffset in EventStream@timescale units, default 60 s.
        ERT: PRT - num(child.earliestResolutionTimeOffset, 60 * ts) / ts,
        // APDmax: @maxDuration in EventStream@timescale units, infinity if absent.
        APDmax: num(child.maxDuration, Infinity) / ts,
        executeOnce: bool(child.executeOnce, false),
        clip: bool(child.clip, true),
        startWithOffset: bool(child.startWithOffset, false),
        returnOffset: child.returnOffset === undefined || child.returnOffset === null ? null : Number(child.returnOffset) / ts,
        c: 0,
        resolution: null,
      };
      this.table.set(key, E);
      this.log('linear:receive', { key, PRT, EAP: E.EAP, ERT: E.ERT, APDmax: E.APDmax, executeOnce: E.executeOnce });
      // While an alternative plays there is no processing (§5.16.2.2.5 NOTE);
      // the new event goes into QE alone (A.14.4.1: only it needs inserting).
      if (this.alt || this.holding) this.enqueue(E, this.main.currentTime);
      else this.resetQueue('receive');
    }

    eligible(E, php) {
      // §5.16.2.2.3 2): active or future, and not already executed when @executeOnce.
      return php <= E.EAP && (!E.executeOnce || E.c === 0);
    }

    enqueue(E, php) {
      this.queue = this.queue.filter((x) => x.key !== E.key);
      if (this.eligible(E, php)) this.queue.push(E);
      this.queue.sort((a, b) => a.PRT - b.PRT);
    }

    // §5.16.2.2.3: QE rebuilt from T; a priority queue by PRT.
    resetQueue(why) {
      const php = this.main.currentTime;
      this.queue = [...this.table.values()].filter((E) => this.eligible(E, php)).sort((a, b) => a.PRT - b.PRT);
      this.log('linear:queue', { why, php, queue: this.queue.map((E) => E.key) });
    }

    tick() {
      if (this.alt) { this.last = null; this.tickAlt(); return; }
      if (this.holding || this.seeking || !this.streamReady || this.main.readyState < 1) { this.last = null; return; }
      const php = this.main.currentTime;
      // The previous tick's playhead, kept only while playback runs on from
      // it: no more media time passed than wall time at the rate, with
      // CLOCK_SLACK for the two clocks being read apart (a seek, a start at
      // an offset, a return to RT jump further), so PRT was crossed by
      // playing up to it. The slack is wall time, so it scales with the rate
      // as the media time does.
      const now = performance.now();
      const last = this.last;
      this.last = { php, now };
      const crossed = (E) => !!last && last.php < E.PRT
        && php - last.php <= ((now - last.now) / 1000 + CLOCK_SLACK) * (this.main.playbackRate || 1);
      // §5.16.2.2.6: resolve when the playhead is between ERT and PRT.
      // @maxDuration zero: the event is not executed (§5.16.5), so it is never resolved.
      for (const E of this.queue) {
        if (!E.resolution && E.APDmax > 0 && php >= E.ERT && php < E.PRT && !this.suppressed(E)) {
          E.resolution = this.resolve(E);
        }
      }
      // §5.16.2.2.5 2): the events with PRT ≤ PHP, oldest PRT first.
      for (const E of this.queue.slice()) {
        if (E.PRT > php) break;
        if (this.suppressed(E)) continue;
        this.queue.splice(this.queue.indexOf(E), 1);
        if (E.EAP <= php) { this.log('linear:expired', { key: E.key, php }); continue; }
        if (E.executeOnce && E.c > 0) continue;
        if (!(E.APDmax > 0)) { this.log('linear:not-executed', { key: E.key, reason: '@maxDuration is zero' }); continue; }
        // The step the crossing was judged on, for diagnosis.
        this.log('linear:crossing', { key: E.key, php, crossed: crossed(E), lastPhp: last && last.php,
          dphp: last && php - last.php, dwall: last && (now - last.now) / 1000, rate: this.main.playbackRate });
        this.execute(E, php, crossed(E));
        return;
      }
      if (this.gated && this.main.readyState >= 2) {
        this.gated = false;
        this.main.style.visibility = 'visible';
      }
    }

    // A.14.5 resolve(E): fetch, parse, and for a List MPD resolve it
    // (§5.3.2.6.3). Returns { ok, parts, reason }.
    resolve(E) {
      this.log('linear:resolve', { key: E.key, uri: E.uri, php: this.main.currentTime });
      return (async () => {
        const r = await fetchMpd(E.uri);
        if (!r.ok) return { ok: false, reason: r.reason };
        const mpd = r.doc.documentElement;
        const type = mpd.getAttribute('type') || 'static';
        const periods = children(mpd, 'Period');
        if (type === 'list') {
          // §8.14 / §5.3.2.6: every Period is a Linked Period; a Period with
          // no ImportedMPD and no content, or of zero duration, has no media.
          const parts = [];
          for (const p of periods) {
            const imp = children(p, 'ImportedMPD')[0];
            const duration = isoDuration(p.getAttribute('duration'));
            if (!imp || duration === 0) continue;
            const base = children(mpd, 'BaseURL')[0];
            const listBase = base ? new URL(base.textContent.trim(), E.uri).href : E.uri;
            parts.push(new Part(this, {
              id: p.getAttribute('id'), doc: E.uri,
              importedUri: new URL(imp.textContent.trim(), listBase).href,
              ert: num(imp.getAttribute('earliestResolutionTimeOffset'), 60),
              duration, click: SgaiClick.parse(p, E.uri),
            }));
          }
          // Before the alternative plays, its first Linked Period with media
          // is resolved: "merge process resulted in no available media" is a
          // failure at PRTA (§5.16.2.2.6), so it has to be known by then.
          while (parts.length) {
            if (await parts[0].resolve()) break;
            parts.shift();
          }
          if (!parts.length) return { ok: false, reason: 'List MPD: no available media' };
          return { ok: true, parts };
        }
        if (type !== 'static' && type !== 'dynamic') return { ok: false, reason: `alternative MPD of type ${type} is not played by this reference` };
        if (periods.length !== 1 || !children(periods[0], 'AdaptationSet').length) {
          return { ok: false, reason: 'not a single Period with content' };
        }
        const live = type === 'dynamic';
        let duration = isoDuration(periods[0].getAttribute('duration'))
          || isoDuration(mpd.getAttribute('mediaPresentationDuration'));
        // Table 57: APD is the duration the alternative MPD defines; a live
        // one that defines none has no end the MPD knows of.
        if (live && !isFinite(duration)) duration = Infinity;
        const part = new Part(this, { id: periods[0].getAttribute('id'), doc: E.uri, importedUri: null, ert: 0, duration, live });
        part.ready(r.doc, E.uri);
        return { ok: true, parts: [part] };
      })().catch((e) => ({ ok: false, reason: String(e && e.message || e) }));
    }

    // §5.16.2.2.5 2b–2d and §5.16.2.2.6.
    async execute(E, php, crossed = false) {
      const wasPlaying = !this.main.paused;
      this.main.pause();
      const PRTA = php;
      this.holding = E;
      // "The alternative MPD is resolved at each execution of the Event"
      // (§5.16.2.2.6): a resolution is used by one execution only.
      const pending = E.resolution || this.resolve(E);
      E.resolution = null;
      const timeout = new Promise((r) => setTimeout(() => r({ ok: false, reason: `no document within ${HOLD_MS} ms` }), HOLD_MS));
      const res = await Promise.race([pending, timeout]);
      if (!res.ok) {
        // A document that arrives after the hold is dropped with its players.
        pending.then((late) => { if (late.ok && late !== res) for (const p of late.parts) p.destroy(); });
        return this.failed(E, wasPlaying, res.reason, res.parts);
      }
      const parts = res.parts;
      const isReplace = E.scheme === REPLACE;
      // Table 57: ASO = PRTA − PRT with @startWithOffset (replacement), else 0;
      // APDadj = max(APDmax − PRTA + PRT, 0) with @clip true or absent, else APDmax.
      // A live alternative "always starts at the live edge" (§5.16.2.2.6) and
      // @startWithOffset "does not apply to a live alternative presentation"
      // (§5.16.4): its ASO is 0.
      const live = parts[0].live;
      const ASO = isReplace && E.startWithOffset && !live ? PRTA - E.PRT : 0;
      const APDadj = isReplace && E.clip ? Math.max(E.APDmax - PRTA + E.PRT, 0) : E.APDmax;
      // An execution on time is still late by the time between PRT and the
      // tick that saw it; @clip's APDadj takes exactly that off the end.
      const lag = crossed ? PRTA - E.PRT : 0;
      const alt = { E, parts, PRTA, ASO, APDadj, lag, wasPlaying, index: -1, started: false, startWall: Date.now(),
        rate: this.main.playbackRate || 1, fired: new Set() };
      // "If at time PRTA the duration APDA is determined to be 0, the event is
      // not executed" (§5.16.2.2.1 step 3).
      this.layout(alt);
      if (!(this.apda(alt) > 0)) return this.failed(E, wasPlaying, 'APDA is 0', parts);
      this.holding = null;
      this.alt = alt;
      this.log('linear:execute', { key: E.key, PRT: E.PRT, PRTA, lag, ASO, APDadj, APD: this.apd(alt), APDA: this.apda(alt), parts: parts.map((p) => p.id) });
      // ASO falls in the Part whose span holds it.
      let i = parts.findIndex((p) => ASO < p.start + p.duration);
      if (i < 0) i = parts.length - 1;
      this.playPart(alt, i, ASO - parts[i].start);
    }

    failed(E, wasPlaying, reason, parts) {
      // A failed execution: E.c is not incremented (§5.16.2.2.6 NOTE 3); the
      // next due events of QE are tried at once (§5.16.2.2.5 2d).
      for (const p of parts || []) p.destroy();
      this.holding = null;
      this.log('linear:failed', { key: E.key, reason });
      if (wasPlaying) this.main.play();
      this.tick();
    }

    // APD: the alternative's duration (the sum of its Periods, a Linked
    // Period counted at its own @duration until resolved).
    apd(alt) { return alt.parts.reduce((s, p) => s + (p.state === 'failed' ? 0 : p.duration), 0); }

    // Table 57: replacement APDA = min(APD − ASO, APDadj); insertion min(APD, APDmax).
    apda(alt) {
      const APD = this.apd(alt);
      return alt.E.scheme === REPLACE ? Math.min(APD - alt.ASO, alt.APDadj) : Math.min(APD, alt.E.APDmax);
    }

    async playPart(alt, i, offset) {
      const part = alt.parts[i];
      alt.index = i;
      part.fromT = offset;
      if (part.state !== 'ready' && part.state !== 'done') {
        const ok = await part.resolve();
        if (this.alt !== alt) return;
        if (!ok) { this.nextPart(alt); return; }
      }
      const p = part.player;
      const go = () => {
        if (this.alt !== alt) return;
        // A live Part goes to its live edge as it is now: the one dash.js
        // took when the Part was preloaded is as old as the preload.
        if (part.live) {
          part.playing = true;
          clearInterval(part.tracker);
          // Already in the most recent available segment (the tracker put
          // it there): it plays from where it is, without a new seek.
          const w = p.getDvrWindow();
          const edge = w && w.end;
          const inLast = part.seg > 0 && edge > 0
            && part.video.currentTime >= (Math.floor(edge / part.seg) - 1) * part.seg - 0.001;
          if (!inLast) p.seekToOriginalLive();
          this.log('linear:live-seek', { id: part.id, edge, from: part.video.currentTime, sought: !inLast });
        } else if (offset > 0) p.seek(offset);
        p.setPlaybackRate(alt.rate);
        p.play();
      };
      part.video.addEventListener('playing', () => this.onPartPlaying(alt, part), { once: true });
      if (part.initialized) go();
      else p.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, go);
    }

    // The first frame of a Part: it replaces what was on screen.
    onPartPlaying(alt, part) {
      if (this.alt !== alt) return;
      part.video.dataset.sgaiOpportunityDoc = this.ref.url;
      part.video.dataset.sgaiOpportunityEvent = alt.E.id;
      part.video.dataset.sgaiOpportunityScheme = alt.E.scheme;
      if (alt.E.value !== null) part.video.dataset.sgaiOpportunityValue = alt.E.value;
      else delete part.video.dataset.sgaiOpportunityValue;
      // One serial per Part: the 'playing' of a resume after a suspension
      // (R17.5) is not a new presentation.
      if (!part.video.dataset.sgaiPresentation) {
        part.video.dataset.sgaiPresentation = this.ref.nextPresentation();
        // A live Part's playhead is counted from its live edge; its callbacks
        // before that point were not reached in course of playback.
        if (part.live) {
          part.fromT = part.origin = part.video.currentTime;
          this.log('linear:live-start', { id: part.id, origin: part.origin });
        }
      }
      part.video.style.visibility = 'visible';
      this.main.style.visibility = 'hidden';
      part.shown = true;
      this.layoutChanged('linear');
      for (const q of alt.parts) if (q !== part && q.video && q.state === 'done') q.destroy();
      if (!alt.started) {
        alt.started = true;
        // §5.16.2.2.6: E.c counts the times the alternative successfully started.
        alt.E.c += 1;
        this.log('linear:started', { key: alt.E.key, gapMs: Date.now() - alt.startWall });
      }
      this.log('linear:part', { key: alt.E.key, id: part.id, start: part.start, duration: part.duration });
    }

    // The alternative's playhead, on its own timeline (s).
    altPosition(alt) {
      const part = alt.parts[alt.index];
      if (!part || !part.video) return part ? part.start : 0;
      return part.start + part.video.currentTime - part.origin;
    }

    tickAlt() {
      const alt = this.alt;
      if (!alt.started) {
        const part = alt.parts[alt.index];
        if (Date.now() - alt.startWall > START_MS || (part && part.error)) {
          this.alt = null;
          this.layoutChanged('none');
          this.failed(alt.E, alt.wasPlaying, part && part.error ? `cannot start: ${part.error}` : 'no first frame', alt.parts);
        }
        return;
      }
      this.layout(alt);
      const pos = this.altPosition(alt);
      const cur = alt.parts[alt.index];
      if (cur && cur.shown && cur.video) this.fireCallbacks(alt, cur, cur.video.currentTime);
      // Linked Periods resolved from PeriodStart − @earliestResolutionTimeOffset
      // of the alternative's playhead (§5.3.2.6.1), and preloaded.
      for (const p of alt.parts) if (p.state === 'unresolved' && pos >= p.start - p.ert) p.resolve();
      // A.14.5: terminate when PRTA + APDA ≤ the alternative's playhead.
      const APDA = this.apda(alt);
      if (pos - alt.ASO >= APDA - EPS) { this.terminate(alt, APDA); return; }
      this.readyAhead(alt, APDA);
      const part = alt.parts[alt.index];
      if (part.state === 'ready' && part.video && (part.video.ended || part.video.currentTime >= part.duration - EPS)) {
        part.state = 'done';
        part.player.pause();
        this.fireCallbacks(alt, part, part.duration);
        this.nextPart(alt);
      }
    }

    // The Parts' starts on the alternative's timeline. A Linked Period that
    // failed to resolve is removed (§5.3.2.6.3 step 2: it has no content of
    // its own), and the ones after it move up.
    layout(alt) {
      let t = 0;
      for (const p of alt.parts) { p.start = t; if (p.state !== 'failed') t += p.duration; }
    }

    nextPart(alt) {
      this.layout(alt);
      const i = alt.parts.findIndex((p, k) => k > alt.index && p.state !== 'failed');
      if (i < 0) { this.terminate(alt, this.apda(alt)); return; }
      this.playPart(alt, i, 0);
    }

    // The callback events of a Part its playhead has reached (on start), from
    // where it started playing. §5.10.2.4: an event whose @schemeIdUri,
    // @value and @id were already processed "in course of normal playback"
    // is ignored; the scope is one execution of the alternative presentation
    // (a List MPD's Periods are one presentation), and a new execution plays
    // it anew.
    fireCallbacks(alt, part, upTo) {
      for (const cb of part.callbacks || []) {
        if (cb.done || cb.at > upTo + 0.001) continue;
        cb.done = true;
        if (cb.at < (part.fromT || 0) - EPS) continue;
        if (alt.fired.has(cb.key)) { this.log('linear:callback-ignored', { id: part.id, key: cb.key }); continue; }
        alt.fired.add(cb.key);
        this.log('linear:callback', { id: part.id, at: cb.at, url: cb.url });
        fetch(cb.url, { mode: 'no-cors', credentials: 'omit', cache: 'no-store', keepalive: true }).catch(() => {});
      }
    }

    // Table 57: RT, the time the primary resumes at.
    returnTime(alt, APDA) {
      const E = alt.E;
      if (E.scheme === INSERT) return alt.PRTA;
      if (E.returnOffset !== null) return E.PRT + E.returnOffset;
      if (!E.clip) return alt.PRTA + APDA;
      return E.PRT + APDA;
    }

    // While the alternative plays, the hidden, paused primary is moved to RT
    // as soon as RT is known and inside what the primary can seek to (a
    // dynamic MPD's window reaches it only as the live edge does), so that it
    // has a decoded frame when the alternative ends: a seek made at the end
    // leaves nothing on screen until the primary's first frame (0.6-2.0 s
    // measured under load, T-09). RT follows APDA, so a change of APDA (a
    // Linked Period that failed) moves the primary again. When and where the
    // primary resumes is unchanged: this only does the seek earlier.
    readyAhead(alt, APDA) {
      const RT = this.returnTime(alt, APDA);
      if (!isFinite(RT)) return;     // a live alternative with no end: RT is not known yet
      if (alt.readyAt !== undefined && Math.abs(alt.readyAt - RT) <= 0.001) return;
      if (this.player.isDynamic && this.player.isDynamic()) {
        const w = this.player.getDvrWindow && this.player.getDvrWindow();
        if (!w || !(w.end >= RT)) return;
      }
      alt.readyAt = RT;
      this.log('linear:ready-ahead', { key: alt.E.key, RT, from: this.main.currentTime, alt: this.altPosition(alt) });
      if (Math.abs(this.main.currentTime - RT) > 0.001) this.player.seekToPresentationTime(RT);
    }

    // §5.16.2.2.5 1a: terminate, compute RT (Table 57), move the playhead to it.
    terminate(alt, APDA) {
      const E = alt.E;
      // A live alternative with no APDA that ended on its own: its observed
      // duration (Table 57's APDE) is what played.
      if (!isFinite(APDA)) APDA = Math.max(this.altPosition(alt) - alt.ASO, 0);
      const RT = this.returnTime(alt, APDA);
      // The callbacks up to where the alternative stops. A stop within EPS of
      // the Part's end, or within the lag of an execution on time, counts as
      // its end, as when it plays to it: otherwise @clip would take an ad's
      // own end-of-ad callback for the time a Player needs to see PRT (an
      // event at the Period's end has no media sample of its own either).
      const cur = alt.parts[alt.index];
      if (cur && cur.shown) {
        const reached = cur.origin + APDA + alt.ASO - cur.start;
        this.fireCallbacks(alt, cur, reached >= cur.duration - Math.max(EPS, alt.lag) ? cur.duration : reached);
      }
      this.alt = null;
      for (const p of alt.parts) p.destroy();
      this.gated = false;
      this.main.style.visibility = 'visible';
      this.layoutChanged('none');
      const ready = alt.readyAt !== undefined && Math.abs(alt.readyAt - RT) <= 0.001;
      this.log('linear:terminate', { key: E.key, APDA, RT, readyAhead: ready, readyState: this.main.readyState,
        played: alt.parts.map((p) => [p.id, p.state]) });
      // The primary normally stands at RT already (readyAhead); otherwise the
      // seek is made now: insertion RT = PRTA, where the primary stands;
      // replacement a seek, which dash.js clips to the time-shift buffer of a
      // dynamic MPD.
      if (!ready && Math.abs(this.main.currentTime - RT) > 0.001) this.player.seekToPresentationTime(RT);
      // The queue is not reset here (A.14.5; §5.16.2.2.5 1a read literally
      // would put an insertion back, since RT = PRTA lies in its active
      // interval — the T-01 finding).
      this.main.play();
    }

    // The viewer's actions while a linear alternative is on screen: they
    // act on it, not on the primary (which is paused or listening).
    act(action) {
      const alt = this.alt;
      if (!alt) {
        if (action.do !== 'seek' || this.holding) return null;
        this.seeking = true;
        this.queue = [];
        this.player.seek(action.to);
        return { done: `primary sought to ${action.to} s` };
      }
      const part = alt.parts[alt.index];
      switch (action.do) {
        case 'pause': this.suspend(); return { done: 'linear ad paused' };
        case 'resume': this.resumeAd(); return { done: 'linear ad resumed' };
        case 'rate':
          alt.rate = action.rate;
          if (part && part.player) part.player.setPlaybackRate(action.rate);
          this.player.setPlaybackRate(action.rate);
          return { done: `linear ad and primary rate ${action.rate}` };
        default: return { done: null, reason: `a linear ad does not take '${action.do}'` };
      }
    }

    // R28.1, R28.2: the viewer activated the <video> of a Part on screen.
    activate(part) {
      this.log('linear:click', { id: part.id, uri: part.click.uri, tracking: part.click.tracking });
      SgaiClick.activate(this.ref, part.click);
    }

    suspend() {
      const part = this.alt && this.alt.parts[this.alt.index];
      if (part && part.player) part.player.pause();
    }

    resumeAd() {
      const part = this.alt && this.alt.parts[this.alt.index];
      if (part && part.player) part.player.play();
    }
  }

  (global.SGAI_FAMILIES = global.SGAI_FAMILIES || []).push(SgaiLinear);
})(window);
