// The reference Player (phase 11, ADR 0075): the pinned dash.js 5.3.0 dist,
// unmodified, plus this module. Loaded after dash.all.min.js and profiles.js.
//
// This file is the skeleton: it plays the primary content, applies the
// device profile and the viewer's actions, and keeps the observation contract
// below. It has no ad logic; the families (linear, resolution and selection,
// non-linear presentation, tracking) plug in through `families` and each
// arrives with its tests already seen failing against this skeleton (ADR 0085).
//
// THE OBSERVATION CONTRACT. The harness does not ask the module what it
// shows: it reads the page (bin/players/adapters/sgai.js). What it reads:
//
// - `container` is the Player's viewport; every rectangle is measured in
//   percent of it. Its `data-sgai-layout` is the R12.2 token of what is on
//   screen, or `none` when only the primary content is.
// - Every surface that shows something carries `data-sgai-element`:
//   `primary`, `ad` or `background`. An `ad` or `background` surface also
//   carries `data-sgai-doc` (the URL of the resolution document its candidate
//   came from), `data-sgai-candidate-id` or `data-sgai-candidate-index`
//   (1-based document order), `data-sgai-option-id` or
//   `data-sgai-option-index` (neither: a linear candidate, option null), and
//   `data-sgai-opportunity-doc` + `data-sgai-opportunity-event` (the URL of
//   the MPD carrying the opportunity and its Event@id).
// - A surface counts as shown when it is displayed, visible, not transparent,
//   has an area inside the container and, for a <video>, has a frame. The
//   harness computes no occlusion: a surface that is covered must be hidden.
// - Resolution requests and beacons are read from the network by the
//   harness, never from here.
//
// `log(type, data)` is the module's own record, for diagnosis: no verdict
// reads it.
(function (global) {
  class SgaiReference {
    // container: the viewport element; video: the primary <video>, inside it;
    // profile: SGAI_PROFILES.profileFor(...); log: (type, data) => void.
    constructor({ container, video, profile, log }) {
      this.container = container;
      this.video = video;
      this.profile = profile;
      this.log = log || (() => {});
      this.player = null;
      container.dataset.sgaiLayout = 'none';
      video.dataset.sgaiElement = 'primary';
      this.families = (global.SGAI_FAMILIES || []).map((F) => new F(this));
      for (const p of profile.problems || []) this.log('profile:problem', p);
      this.log('profile', { klass: profile.klass, capabilities: profile.capabilities });
    }

    // Starts the primary presentation at `startTime` seconds of its timeline
    // (NaN: dash.js's default start).
    start(url, startTime) {
      const player = dashjs.MediaPlayer().create();
      this.player = player;
      player.updateSettings({ debug: { logLevel: dashjs.Debug.LOG_LEVEL_NONE } });
      // No request leaves for dash.js's default UTC source; the device clock
      // is the clock the test content is served on.
      player.clearDefaultUTCTimingSources();
      const E = dashjs.MediaPlayer.events;
      player.on(E.ERROR, (e) => this.log('dashjs:error', JSON.stringify((e && e.error) || e).slice(0, 300)));
      for (const f of this.families) if (f.attach) f.attach(player);
      player.initialize(this.video, url, true, startTime);
      this.log('primary:initialize', { url, startTime });
    }

    // A viewer action of a vector: {do, to (s), rate}. A family that owns the
    // action takes it first (a pause may bring a pause ad, a dismiss closes
    // one); otherwise the primary content gets it. Returns what was done.
    act(action) {
      for (const f of this.families) {
        const r = f.act ? f.act(action) : null;
        if (r) return r;
      }
      const p = this.player;
      switch (action.do) {
        case 'pause': p.pause(); return { done: 'primary paused' };
        case 'resume': p.play(); return { done: 'primary resumed' };
        case 'seek': p.seek(action.to); return { done: `primary sought to ${action.to} s` };
        case 'rate': p.setPlaybackRate(action.rate); return { done: `primary rate ${action.rate}` };
        default: return { done: null, reason: `nothing on screen takes '${action.do}'` };
      }
    }
  }

  global.SgaiReference = SgaiReference;
})(window);
