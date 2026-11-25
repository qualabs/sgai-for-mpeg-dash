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
//   the MPD carrying the opportunity and its Event@id), with
//   `data-sgai-opportunity-scheme` (the @schemeIdUri of the EventStream that
//   carries that Event) and `data-sgai-opportunity-value` (its @value; absent
//   when the EventStream has none).
// - An `ad` or `background` surface also carries `data-sgai-presentation`: a
//   serial (`ref.nextPresentation()`, unique in the session) stamped each
//   time the surface starts a new presentation of its candidate and option,
//   even on the same DOM element (a still image shown again by a repeat).
//   A suspension and its restore keep it: they are one presentation.
// - A surface counts as shown when it is displayed, visible, not transparent,
//   has an area inside the container and, for a <video>, has a frame. The
//   harness computes no occlusion: a surface that is covered must be hidden.
// - Resolution requests and beacons are read from the network by the
//   harness, never from here.
//
// `log(type, data)` is the module's own record, for diagnosis: no verdict
// reads it.
//
// FAMILIES. Each family is a file of this directory, named in FAMILY_FILES
// and loaded by this one (so the harness page lists only this file), in that
// order, that pushes a class onto `SGAI_FAMILIES`. A family is constructed with the
// SgaiReference once its scripts are in, and may have `attach(player)`
// (called before the primary is initialised) and `act(action)`. It reads
// `ref.url` (the main MPD's URL, the `data-sgai-opportunity-doc` of what it
// presents), `ref.container`, `ref.video`, `ref.profile`, `ref.log`, and
// may publish itself on `ref` for the others (the linear family is
// `ref.linear`). A viewer action goes to the families in the reverse of
// that order: a later family is layered over an earlier one, so a pause ad
// takes a pause before the linear ad under it does (R17.5).
//
// PRESENTATION. `ref.compositor` (sgai-compositor.js, loaded first and not a
// family) puts a non-linear form on screen with the content it composes with,
// per layout token, and keeps the viewport's `data-sgai-layout`.
// `SgaiClick` (sgai-click.js, not a family either) is the click on a
// candidate, which both families arm on the surfaces they show.
(function (global) {
  const FAMILY_FILES = ['sgai-compositor.js', 'sgai-click.js', 'sgai-linear.js', 'sgai-nonlinear.js'];
  const base = (document.currentScript && document.currentScript.src) || location.href;
  const loading = FAMILY_FILES.map((f) => new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = new URL(f, base).href;
    s.async = false;   // executed in list order: the order of SGAI_FAMILIES
    s.onload = resolve;
    s.onerror = () => reject(new Error('cannot load family ' + f));
    document.head.appendChild(s);
  }));
  const familiesReady = Promise.all(loading);
  class SgaiReference {
    // container: the viewport element; video: the primary <video>, inside it;
    // profile: SGAI_PROFILES.profileFor(...), plus `sendsCapabilities` (the
    // capability parameters this session discloses on a resolution request,
    // §5.8.2; none when absent); log: (type, data) => void.
    constructor({ container, video, profile, log }) {
      this.container = container;
      this.video = video;
      this.profile = profile;
      this.log = log || (() => {});
      this.player = null;
      this.url = null;
      container.dataset.sgaiLayout = 'none';
      video.dataset.sgaiElement = 'primary';
      this.families = [];
      this.presentationSerial = 0;
      for (const p of profile.problems || []) this.log('profile:problem', p);
      this.log('profile', { klass: profile.klass, capabilities: profile.capabilities,
        sendsCapabilities: profile.sendsCapabilities || [] });
    }

    // Starts the primary presentation at `startTime` seconds of its timeline
    // (NaN: dash.js's default start). The player exists on return; it is
    // initialised once the families are in (they are loaded long before a
    // run starts, so this waits for nothing in practice).
    start(url, startTime) {
      const player = dashjs.MediaPlayer().create();
      this.player = player;
      this.url = url;
      return familiesReady.then(() => this._start(player, url, startTime), (e) => {
        this.log('families:error', String(e && e.message || e));
        this._start(player, url, startTime);
      });
    }

    _start(player, url, startTime) {
      this.compositor = global.SgaiCompositor ? new global.SgaiCompositor(this) : null;
      this.families = (global.SGAI_FAMILIES || []).map((F) => new F(this));
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

    // The `data-sgai-presentation` of a new presentation (the contract above).
    nextPresentation() { return String(++this.presentationSerial); }

    // A viewer action of a vector: {do, to (s), rate}. A family that owns the
    // action takes it first (a pause may bring a pause ad, a dismiss closes
    // one); otherwise the primary content gets it. Returns what was done.
    act(action) {
      for (const f of this.families.slice().reverse()) {
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
