// The session clock of the behaviour battery (spec-source/scenarios/README.md,
// "Times"): how far the session has got, advanced by what is presented and
// not by how fast this machine plays the page. Loaded by harness.html before
// adapters/sgai.js; pure (no DOM), so bin/test_behaviour_harness.py runs it
// under node.
//
// From the session's first frame on, at every tick, the clock advances by:
//
//   1. the wall time that passed, while the viewer has paused (a vector's
//      `pause` action, until its `resume`): a pause has no media time;
//   2. else the media time the linear ad <video> advanced, divided by its
//      rate, while it has taken over the screen (the primary is not shown and
//      an `ad` <video> is shown and not paused; the first such one);
//   3. else the media time the primary <video> advanced, divided by its rate,
//      while it is shown and not paused;
//   4. else the wall time that passed: an image or HTML takeover, the primary
//      held paused by the Player, nothing on screen.
//
// A media advance that is negative, or larger than the wall time that passed
// would allow (a seek, a reload), advances the clock by nothing: a jump is not
// presentation. A <video> that is shown, not paused, and not advancing (a
// stall) stands the clock still. The videos are read from the page by the
// adapter (their currentTime, paused, playbackRate, whether shown), never from
// what the module reports.
//
// `mode: 'wall'` keeps the clock of earlier runs: wall time since the first
// frame, whatever is presented. It is there to compare the two.
(function (global) {
  const JUMP_SLACK_MS = 200;   // a media advance this much above the wall time is a jump
  const JUMP_FACTOR = 1.5;

  // Which source drives the clock now. `state`: { viewerPaused, videos: [{ id,
  // role: 'primary' | 'ad', shown, paused, time (s), rate }] }. Returns
  // { kind: 'wall', why } or { kind: 'media', id, why }.
  function driverOf(state) {
    if (state.viewerPaused) return { kind: 'wall', why: 'viewer-paused' };
    const videos = state.videos || [];
    const primary = videos.find((v) => v.role === 'primary');
    if (!primary || !primary.shown) {
      const ad = videos.find((v) => v.role === 'ad' && v.shown && !v.paused);
      if (ad) return { kind: 'media', id: ad.id, why: 'linear-ad' };
    }
    if (primary && primary.shown && !primary.paused) return { kind: 'media', id: primary.id, why: 'primary' };
    return { kind: 'wall', why: 'no-playing-video' };
  }

  class SessionClock {
    constructor(mode) {
      this.mode = mode === 'wall' ? 'wall' : 'presentation';
      this.origin = null;     // wall ms of the first frame
      this.last = null;       // wall ms of the last tick
      this.session = null;    // session ms at the last tick
      this.times = new Map(); // video id -> { time (s), seeks } at the last tick
      this.points = [];       // [wall ms, session ms, why] at each tick
      this.why = null;
    }

    // Starts the clock at the first frame (`wall`), with the videos as they
    // are then.
    start(wall, state) {
      if (this.origin !== null) return;
      this.origin = wall;
      this.last = wall;
      this.session = 0;
      this._remember(state);
      this.why = this.mode === 'wall' ? 'wall' : driverOf(state).why;
      this.points.push([wall, 0, this.why]);
    }

    // Advances the clock to `wall` with the videos as they are now; returns
    // the session time (ms), or null before start().
    tick(wall, state) {
      if (this.origin === null) return null;
      const dt = Math.max(0, wall - this.last);
      let step = dt;
      let why = 'wall';
      if (this.mode !== 'wall') {
        const d = driverOf(state);
        why = d.why;
        if (d.kind === 'media') {
          const v = state.videos.find((x) => x.id === d.id);
          const prev = this.times.get(d.id);
          step = 0;
          if (prev && v && prev.seeks === (v.seeks || 0)) {
            const dm = ((v.time - prev.time) * 1000) / (v.rate || 1);
            if (dm >= 0 && dm <= dt * JUMP_FACTOR + JUMP_SLACK_MS) step = dm;
            else why += ':jump';
          }
        }
      }
      this.last = wall;
      this.session += step;
      this._remember(state);
      if (dt > 0 || why !== this.why) this.points.push([wall, Math.round(this.session * 10) / 10, why]);
      this.why = why;
      return this.session;
    }

    now() { return this.session; }

    _remember(state) {
      for (const v of (state && state.videos) || []) this.times.set(v.id, { time: v.time, seeks: v.seeks || 0 });
    }
  }

  const api = { SessionClock, driverOf };
  global.SGAI_CLOCK = api;
})(typeof window !== 'undefined' ? window : globalThis);
