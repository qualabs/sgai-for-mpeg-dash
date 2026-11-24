// Page glue for the T-01 spike. Loaded into bin/players/harness.html (which
// has already loaded the pinned dash.js) after sgai-linear.js. Uses the
// harness's <video id="video"> as the main element and adds a second one.
(function () {
  const t0 = performance.now();
  const now = () => Math.round(performance.now() - t0);
  const main = document.getElementById('video');
  const alt = document.createElement('video');
  alt.id = 'alt';
  alt.muted = true;
  alt.playsInline = true;
  alt.width = main.width;
  alt.height = main.height;
  alt.style.cssText = 'position:absolute;left:8px;top:8px;visibility:hidden';
  document.body.appendChild(alt);

  const log = [];
  const errors = [];
  let resumes = 0;
  let opts = {};
  let player = null;
  let module = null;
  const record = (type, data) => {
    log.push({ t: now(), type, mainTime: main.currentTime, altTime: alt.currentTime, data });
    if (type === 'main:resumed') {
      resumes += 1;
      const a = (opts.seekAfterResume || {})[resumes];
      if (a !== undefined) setTimeout(() => { record('user:seek', { to: a }); player.seek(a); }, 1500);
    }
  };

  window.SPIKE = {
    start(url, o) {
      opts = o || {};
      player = dashjs.MediaPlayer().create();
      player.updateSettings({ debug: { logLevel: dashjs.Debug.LOG_LEVEL_NONE } });
      player.clearDefaultUTCTimingSources(); // no request leaves the local origin; device clock
      player.on(dashjs.MediaPlayer.events.ERROR, (e) => errors.push(JSON.stringify(e.error || e).slice(0, 300)));
      module = new SgaiLinear(player, main, alt, record);
      module.attach();
      player.initialize(main, url, true, opts.startTime === undefined ? NaN : opts.startTime);
      record('main:initialize', { url, startTime: opts.startTime });
    },
    state() {
      let isDynamic = null;
      try { isDynamic = player.isDynamic(); } catch (e) { /* not yet */ }
      return { t: now(), mainTime: main.currentTime, mainPaused: main.paused, isDynamic,
               altActive: !!(module && module.alt), log, errors };
    },
  };
})();
