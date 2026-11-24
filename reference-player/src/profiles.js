// Device classes as profiles (ADR 0080): one Chromium plays every class, and
// the class is a configuration of the module. The reference chooses what a
// device of that class would choose; nothing here measures a real decoder.
//
// The first three axes are the rows of R3.1 of context/03, the only
// definition of the classes ("D1 — top tier: `2` or `3`" decoders; D1 is
// given 2, the value every vector writes). `sgai-custom-layout` and
// `sgai-ad-audio` are not part of a class: a vector sets them in its
// `player_capabilities` as its use case needs, and they default to 0.
(function (global) {
  const AXES = ['sgai-video-decoders', 'sgai-image-over-video', 'sgai-html-over-video'];
  const R3_1 = {
    D1: { 'sgai-video-decoders': 2, 'sgai-image-over-video': 1, 'sgai-html-over-video': 1 },
    D2: { 'sgai-video-decoders': 2, 'sgai-image-over-video': 0, 'sgai-html-over-video': 0 },
    D3: { 'sgai-video-decoders': 1, 'sgai-image-over-video': 1, 'sgai-html-over-video': 1 },
    D4: { 'sgai-video-decoders': 1, 'sgai-image-over-video': 1, 'sgai-html-over-video': 0 },
    D5: { 'sgai-video-decoders': 1, 'sgai-image-over-video': 0, 'sgai-html-over-video': 0 },
  };
  const D1_DECODERS = [2, 3];

  // The profile of class `klass`, with `capabilities` (a vector's
  // player_capabilities row) laid over it. Returns { klass, capabilities,
  // problems }: a problem is a capability that puts the device outside its
  // class by R3.1; the module still runs, and the harness reports it.
  function profileFor(klass, capabilities) {
    const row = R3_1[klass];
    if (!row) return { klass, capabilities: null, problems: [`unknown class ${klass}`] };
    const caps = Object.assign({}, row, { 'sgai-custom-layout': 0, 'sgai-ad-audio': 0 }, capabilities || {});
    const problems = [];
    for (const axis of AXES) {
      const ok = klass === 'D1' && axis === 'sgai-video-decoders'
        ? D1_DECODERS.includes(caps[axis]) : caps[axis] === row[axis];
      if (!ok) problems.push(`${axis}=${caps[axis]} is not class ${klass} by R3.1`);
    }
    return { klass, capabilities: caps, problems };
  }

  global.SGAI_PROFILES = { R3_1, AXES, profileFor };
})(window);
