// Adapter for dash.js (upstream, unmodified; version pinned in ../package.json).
//
// dash.js has no severity on its errors: every MediaPlayer ERROR or
// PLAYBACK_ERROR event is counted as fatal. That is the strict reading; a
// non-fatal one would show up as a FAIL with its code, to be looked at,
// rather than as a PASS nobody questions.
//
// No handler is registered for any event scheme of the MPD: dash.js hands an
// application only the schemes it subscribed to, and a legacy deployment
// subscribes to none of ours. Whether dash.js acted on our constructs is read
// from the network (the runner records every request) and from its errors.
(function () {
  let player = null;
  const seen = {};
  window.SGAI_ADAPTER = {
    name: 'dashjs',
    version() { return dashjs.Version || (dashjs.MediaPlayer().create().getVersion()); },
    async load(video, url, log) {
      player = dashjs.MediaPlayer().create();
      player.updateSettings({ debug: { logLevel: dashjs.Debug.LOG_LEVEL_NONE } });
      const E = dashjs.MediaPlayer.events;
      player.on(E.ERROR, (e) => {
        const err = e && e.error ? e.error : e;
        log.error('dashjs:' + (err && err.code !== undefined ? err.code : '?'),
          err && err.message ? err.message : JSON.stringify(err).slice(0, 300), true);
      });
      player.on(E.PLAYBACK_ERROR, (e) => log.error('dashjs:playback', e && e.error ? String(e.error) : '', true));
      for (const name of ['MANIFEST_LOADED', 'STREAM_INITIALIZED', 'PLAYBACK_STARTED']) {
        player.on(E[name], () => {
          if (!seen[name]) log.event('dashjs:' + name);
          seen[name] = true;
        });
      }
      player.initialize(video, url, true);
    },
    inspect() {
      if (!player) return null;
      let isDynamic = null;
      try { isDynamic = player.isDynamic(); } catch (e) { /* not initialised yet */ }
      return { seen: Object.keys(seen), isDynamic };
    },
  };
})();
