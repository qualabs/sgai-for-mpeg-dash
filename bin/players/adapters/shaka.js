// Adapter for Shaka Player (version pinned in ../package.json), compiled build
// with the ads module.
//
// Fatal: a Player 'error' event of severity CRITICAL, or load() rejecting.
//
// The observable for "an InsertPresentation of the 6th edition is recognised"
// is the AdManager's 'ad-cue-points-changed' event (shaka.ads.Utils
// .CUEPOINTS_CHANGED). In the pinned source the chain is:
//   lib/player.js            regionTimeline 'regionadd' -> adManager_.onDASHMetadata(region)
//   lib/ads/ad_manager.js    onDASHMetadata: DashInterstitialParser.isInterstitialRegion
//                            (scheme urn:mpeg:dash:event:alternativeMPD:insert:2025)
//                            -> parseRegion -> interstitialAdManager_.addInterstitials
//   lib/ads/dash_interstitial_parser.js  parseAlternativeMpd_ reads InsertPresentation@uri
//   lib/ads/interstitial_ad_manager.js   addInterstitials -> cuepointsChanged_()
//                            -> sendEvent_(CUEPOINTS_CHANGED, {cuepoints})
// The event fires only when the region was parsed into a linear interstitial
// with a URI, so it is not raised by a mere EventStream of that scheme.
(function () {
  let player = null;
  const cuepoints = [];
  const regions = [];
  const ads = {};
  window.SGAI_ADAPTER = {
    name: 'shaka',
    version() { return shaka.Player.version; },
    async load(video, url, log) {
      shaka.polyfill.installAll();
      player = new shaka.Player();
      await player.attach(video);
      player.addEventListener('error', (e) => {
        const d = e.detail || {};
        log.error('shaka:' + d.code, (d.data || []).map(String).join(' ').slice(0, 300),
          d.severity === shaka.util.Error.Severity.CRITICAL);
      });
      player.addEventListener('timelineregionadded', (e) => {
        const r = e.detail || {};
        regions.push({ schemeIdUri: r.schemeIdUri, id: r.id, startTime: r.startTime });
      });
      const am = player.getAdManager();
      if (am) {
        am.addEventListener('ad-cue-points-changed', (e) => {
          const cps = (e.cuepoints || []).map((c) => ({ start: c.start, end: c.end }));
          cuepoints.push(cps);
          log.event('shaka:ad-cue-points-changed', cps);
        });
        for (const t of ['ad-error', 'ad-break-started', 'ad-break-ended', 'ad-started', 'ad-stopped',
          'ad-interstitial-preload', 'ads-loaded']) {
          am.addEventListener(t, (e) => {
            ads[t] = (ads[t] || 0) + 1;
            if (ads[t] === 1) log.event('shaka:' + t, e && e.originalEvent ? String(e.originalEvent) : null);
          });
        }
      } else {
        log.event('shaka:no-ad-manager');
      }
      await player.load(url);
    },
    inspect() {
      return { regions, cuepoints, ads, isLive: player ? player.isLive() : null };
    },
  };
})();
