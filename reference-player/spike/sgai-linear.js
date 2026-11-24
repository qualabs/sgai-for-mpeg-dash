// Spike (T-01, phase 11): ISO/IEC 23009-1 6th edition §5.16 alternative-MPD
// InsertPresentation / ReplacePresentation on top of dash.js 5.3.0, using its
// public API only. Not the reference implementation: it answers whether the
// public API is enough, and records what it measured.
//
// Shape (ADR 0075): the main MediaPlayer receives the events (on-receive
// subscription to each scheme); this module keeps its own event table and
// execution queue (§5.16.2.2.2), runs the playhead-triggered processing
// (§5.16.2.2.5) itself, and plays the alternative presentation in a second
// MediaPlayer on a second <video>.
(function () {
  const INSERT = 'urn:mpeg:dash:event:alternativeMPD:insert:2025';
  const REPLACE = 'urn:mpeg:dash:event:alternativeMPD:replace:2025';
  const t0 = performance.now();
  const now = () => Math.round(performance.now() - t0);

  // Attributes of the Event's child element, read from the manifest object
  // dash.js parsed (MediaPlayer.getManifest()): dash.js's Event object keeps
  // presentationTime, duration and id, but not the child element.
  function findChild(manifest, scheme, id, periodIndex) {
    const periods = manifest && manifest.Period ? manifest.Period : [];
    const order = periodIndex !== undefined ? [periods[periodIndex]] : periods;
    for (const p of order) {
      for (const es of (p && p.EventStream) || []) {
        if (es.schemeIdUri !== scheme) continue;
        for (const ev of es.Event || []) {
          if (parseInt(ev.id) !== id) continue;
          const name = scheme === INSERT ? 'InsertPresentation' : 'ReplacePresentation';
          let el = ev[name];
          if (Array.isArray(el)) el = el[0];
          return el || null;
        }
      }
    }
    return null;
  }

  const bool = (v, d) => (v === undefined || v === null ? d : String(v) === 'true');
  const num = (v, d) => (v === undefined || v === null || v === '' ? d : Number(v));

  class SgaiLinear {
    constructor(mainPlayer, mainVideo, altVideo, log) {
      this.main = mainPlayer;
      this.mainVideo = mainVideo;
      this.altVideo = altVideo;
      this.log = log;
      this.table = new Map();   // key scheme#id -> E (§5.16.2.2.2 table T)
      this.alt = null;          // alt_client: { E, player, ... } while playing
      this.lastPHP = null;
      this.seeking = false;
      this.preloaded = new Map();
      this.timer = null;
    }

    attach() {
      const ev = dashjs.MediaPlayer.events;
      for (const scheme of [INSERT, REPLACE]) {
        // On-receive is the dispatch mode §5.16.3 / §5.16.4 give both schemes.
        this.main.on(scheme, (e) => this.onReceive(e), null, { mode: ev.EVENT_MODE_ON_RECEIVE });
        // Subscribed only to record when dash.js itself would start the event;
        // the module does not act on it.
        this.main.on(scheme, (e) => this.log('dashjs:onStart', {
          scheme, id: e.event.id, php: this.mainVideo.currentTime,
        }), null, { mode: ev.EVENT_MODE_ON_START });
      }
      // A user seek empties the queue and refills it on return to playback
      // (§5.16.2.2.7). The seek this module makes to RT is not a user seek.
      this.mainVideo.addEventListener('seeking', () => {
        if (this.returning) return;
        this.seeking = true; this.resetQueue('seek');
      });
      this.mainVideo.addEventListener('seeked', () => {
        if (this.returning) { this.returning = false; return; }
        this.seeking = false; this.resetQueue('seeked');
      });
      this.timer = setInterval(() => this.tick(), 10);
    }

    onReceive(payload) {
      const e = payload.event;
      const scheme = e.eventStream.schemeIdUri;
      const child = findChild(this.main.getManifest(), scheme, e.id, e.eventStream.period && e.eventStream.period.index);
      const ts = e.eventStream.timescale || 1;
      this.log('dashjs:onReceive', {
        scheme, id: e.id, calculatedPresentationTime: e.calculatedPresentationTime, duration: e.duration,
        eventKeys: Object.keys(e).sort(), messageData: e.messageData === undefined ? null : String(e.messageData),
        child,
      });
      if (!child || !child.uri) {
        this.log('module:ignored', { id: e.id, reason: 'no child element / @uri' });
        return;
      }
      const periodEnd = e.eventStream.period && isFinite(e.eventStream.period.duration)
        ? e.eventStream.period.start + e.eventStream.period.duration : Infinity;
      const PRT = e.calculatedPresentationTime;
      const E = {
        key: scheme + '#' + e.id, scheme, id: e.id, uri: child.uri, PRT,
        // Event@duration absent: active till the end of the Period.
        EAP: Math.min(isNaN(e.duration) ? Infinity : PRT + e.duration, periodEnd),
        ERT: PRT - num(child.earliestResolutionTimeOffset, 60 * ts) / ts,
        APDmax: num(child.maxDuration, Infinity) / ts,
        executeOnce: bool(child.executeOnce, false),
        clip: bool(child.clip, true),
        startWithOffset: bool(child.startWithOffset, false),
        returnOffset: child.returnOffset === undefined ? null : Number(child.returnOffset) / ts,
        c: 0,
      };
      const old = this.table.get(E.key);
      if (old) E.c = old.c;
      this.table.set(E.key, E);
      this.resetQueue('receive');
    }

    // §5.16.2.2.3 queue reset: events active or in the future, and not
    // already executed when @executeOnce is true.
    resetQueue(why) {
      // No processing while the alternative plays (listen mode, §5.16.2.2.5 NOTE).
      if (this.alt) return;
      const php = this.mainVideo.currentTime;
      this.queue = [...this.table.values()]
        .filter((E) => (php <= E.EAP) && (!E.executeOnce || E.c === 0))
        .sort((a, b) => a.PRT - b.PRT);
      if (why === 'seek') this.queue = []; // a seek empties the queue; seeked refills it
    }

    tick() {
      if (this.alt) return this.tickAlt();
      if (this.seeking || !this.queue || !this.queue.length) return;
      const v = this.mainVideo;
      const php = v.currentTime;
      // Resolve (preload) between ERT and PRT.
      for (const E of this.queue) {
        if (php >= E.ERT && php < E.PRT && !this.preloaded.has(E.key)) this.preload(E);
      }
      const top = this.queue[0];
      if (top.PRT > php) {
        // Close to PRT: a one-shot timer lands nearer to PRT than the 10 ms poll.
        const left = (top.PRT - php) / (v.playbackRate || 1);
        if (!v.paused && left < 0.05 && !this.armed) {
          this.armed = true;
          setTimeout(() => { this.armed = false; this.tick(); }, Math.max(0, left * 1000 - 2));
        }
        return;
      }
      this.queue.shift();
      if (top.EAP <= php) return this.log('module:expired', { id: top.id, php });
      this.execute(top, php);
    }

    preload(E) {
      const altVideo = this.altVideo;
      const player = dashjs.MediaPlayer().create();
      player.updateSettings({ debug: { logLevel: dashjs.Debug.LOG_LEVEL_NONE } });
      const p = { player, ready: false, APD: NaN };
      player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, () => {
        p.ready = true;
        p.APD = player.duration();
      });
      player.initialize(altVideo, E.uri, false);
      this.preloaded.set(E.key, p);
      this.log('module:resolve', { id: E.id, php: this.mainVideo.currentTime, uri: E.uri });
    }

    execute(E, php) {
      const PRTA = php;
      this.mainVideo.pause();
      const pauseAt = this.mainVideo.currentTime;
      let p = this.preloaded.get(E.key);
      this.preloaded.delete(E.key);
      if (!p) {
        p = { player: dashjs.MediaPlayer().create(), ready: false, APD: NaN };
        p.player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, () => { p.ready = true; p.APD = p.player.duration(); });
        p.player.initialize(this.altVideo, E.uri, false);
      }
      const ASO = E.scheme === REPLACE && E.startWithOffset ? PRTA - E.PRT : 0;
      const APDadj = E.scheme === REPLACE && E.clip ? Math.max(E.APDmax - PRTA + E.PRT, 0) : E.APDmax;
      this.alt = { E, p, PRTA, ASO, APDadj, pauseAt, startedAt: null, wall0: now() };
      this.log('module:execute', { id: E.id, scheme: E.scheme, PRT: E.PRT, PRTA, pauseAt, ASO, APDadj });
      this.mainVideo.style.visibility = 'hidden';
      this.altVideo.style.visibility = 'visible';
      const go = () => {
        if (ASO > 0) p.player.seek(ASO);
        p.player.play();
      };
      if (p.ready) go(); else p.player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, go);
      this.altVideo.addEventListener('playing', this._onAltPlaying = () => {
        if (this.alt && this.alt.startedAt === null) {
          this.alt.startedAt = now();
          E.c += 1; // §5.16.2.2.6: counted when the alternative successfully starts
          this.log('alt:playing', { id: E.id, altTime: this.altVideo.currentTime, gapMs: now() - this.alt.wall0 });
        }
      });
    }

    tickAlt() {
      const a = this.alt;
      if (a.startedAt === null) return;
      const APD = a.p.APD;
      // APDA: replacement min(APD - ASO, APDadj); insertion min(APD, APDmax).
      const APDA = a.E.scheme === REPLACE ? Math.min(APD - a.ASO, a.APDadj) : Math.min(APD, a.E.APDmax);
      const played = this.altVideo.currentTime - a.ASO;
      if (this.altVideo.ended || played >= APDA - 0.02) this.terminate(APDA, played);
    }

    terminate(APDA, played) {
      const a = this.alt;
      this.alt = null;
      this.altVideo.removeEventListener('playing', this._onAltPlaying);
      a.p.player.pause();
      const E = a.E;
      let RT;
      if (E.scheme === INSERT) RT = a.PRTA;
      else if (E.returnOffset !== null) RT = E.PRT + E.returnOffset;
      else if (!E.clip) RT = a.PRTA + APDA;
      else RT = E.PRT + APDA;
      this.log('module:terminate', { id: E.id, APD: a.p.APD, APDA, altPlayed: played, RT });
      a.p.player.reset();
      this.altVideo.style.visibility = 'hidden';
      this.mainVideo.style.visibility = 'visible';
      const resumeWall = now();
      const onPlaying = () => {
        this.mainVideo.removeEventListener('playing', onPlaying);
        this.log('main:resumed', { id: E.id, php: this.mainVideo.currentTime, RT, gapMs: now() - resumeWall });
        setTimeout(() => this.log('main:after1s', { id: E.id, php: this.mainVideo.currentTime }), 1000);
      };
      this.mainVideo.addEventListener('playing', onPlaying);
      // Insertion: RT = PRTA, the position the main stopped at; no seek.
      // Replacement: seek to RT (dash.js clips a dynamic RT to its live delay).
      // The queue is not reset on return: A.14.5 pops the executed event and
      // does not refill. A literal reset (§5.16.2.2.5 1a) would re-execute an
      // insertion at once, since RT = PRTA lies inside its active interval.
      if (Math.abs(this.mainVideo.currentTime - RT) > 0.001) {
        this.returning = true;
        this.main.seekToPresentationTime(RT);
      }
      this.main.play();
    }
  }

  window.SgaiLinear = SgaiLinear;
})();
