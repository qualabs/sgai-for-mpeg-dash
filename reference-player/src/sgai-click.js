// The click on a candidate, shared by the families (§4.5.16, §5.6; R28.1,
// R28.2): a <svta:ClickThrough> read from the element that carries it (a
// non-linear Ad, a List MPD's Period, an alternative MPD's Period), armed on
// the surface that shows the candidate, and the viewer's activation of that
// surface. Nothing fires from the timeline or without an activation (PLY-84).
//
// Reading taken where the specification leaves room: the destination is made
// available by showing its URL on screen (one of the means R28.1 admits; a
// page opened from a test page would take the focus) for DESTINATION_MS, a
// node carrying `data-sgai-clickthrough`; each activation fires the
// click-tracking again (PLY-84 binds per activation). One destination is on
// screen at a time, whichever family's surface was activated.
//
// Not a family: loaded before them (sgai-reference.js), as `SgaiClick`.
(function (global) {
  const SVTA = 'urn:svta:dash:sgai:2026';
  const DESTINATION_MS = 5000;   // how long an activated ClickThrough's URL stays on screen

  // §5.6: the <svta:ClickThrough> child of `carrier`, { uri, tracking: [url] },
  // both resolved against the document's URL; null when there is none.
  function parse(carrier, docUrl) {
    const ct = carrier && Array.from(carrier.children).find((c) => c.localName === 'ClickThrough' && c.namespaceURI === SVTA);
    const uri = ct && (ct.getAttribute('uri') || '').trim();
    if (!uri) return null;
    const abs = (u) => { try { return new URL(u, docUrl).href; } catch (e) { return u; } };
    const list = (ct.getAttribute('trackingUris') || '').trim();
    return { uri: abs(uri), tracking: list ? list.split(/\s+/).map(abs) : [] };
  }

  // The viewer's activation of `el` (a click or a tap on it; a hidden surface
  // takes none) calls `on`; null disarms it. An HTML creative is its own
  // document, so its clicks are taken there. Assigned, not added: a surface
  // armed again is armed once.
  function arm(el, on) {
    el.onclick = on || null;
    if (el.tagName === 'IFRAME') {
      el.onload = () => { try { el.contentDocument.onclick = on || null; } catch (e) { /* not ours */ } };
    }
  }

  // R28.1, R28.2: each click-tracking URL fired once, ignoring the answer as
  // for a callback, and the destination made available (DESTINATION_MS).
  function activate(ref, ct) {
    for (const u of ct.tracking) fetch(u, { mode: 'no-cors', credentials: 'omit', cache: 'no-store', keepalive: true }).catch(() => {});
    const prev = ref.clickDestination;
    if (prev) { clearTimeout(prev.timer); prev.el.remove(); }
    const d = document.createElement('div');
    d.dataset.sgaiClickthrough = ct.uri;
    d.textContent = ct.uri;
    d.style.cssText = 'position:absolute;left:0;top:0;max-width:100%;padding:4px 8px;font:14px sans-serif;' +
      'color:#fff;background:rgba(0,0,0,0.7);z-index:100;pointer-events:none;overflow:hidden;white-space:nowrap';
    ref.container.appendChild(d);
    const dest = { el: d, timer: setTimeout(() => { d.remove(); if (ref.clickDestination === dest) ref.clickDestination = null; }, DESTINATION_MS) };
    ref.clickDestination = dest;
  }

  global.SgaiClick = { parse, arm, activate, DESTINATION_MS };
})(window);
