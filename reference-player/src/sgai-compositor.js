// The presentation layer of the reference (phase 11, T-07): how a non-linear
// ad is put on screen with the content it composes with, per layout token
// (spec §5.3.6, PLY-71..73; context/03 R12.5, R26.1, R27.1). The families
// decide WHAT is on screen and WHEN; this file decides WHERE and in front of
// what, and keeps the viewport's `data-sgai-layout` (the observation
// contract of sgai-reference.js).
//
// Interface. `ref.compositor.present(el, layout, opts)` takes an ad surface
// the caller built (its identity already in `el.dataset`), appends it to the
// viewport and returns a handle:
//   handle.suspend() / handle.resume()  off and back on screen; a suspended
//                                       form leaves its content untransformed
//   handle.remove()                     gone for good
//   handle.ready                        the surface has something to show
// opts: { kind: 'overlay' | 'pause', rect (custom: the option's @rect),
//   background (an <img> already loaded, double-box-background),
//   content: () => the <video> the form composes with (the presentation that
//   declares its window, or the alternative presentation it is on top of) }.
// `refresh()` recomputes the screen; the families call it when something
// they own changes (the linear family when its alternative starts or ends).
//
// Composition, by the form on top (a pause ad before an overlay, PLY-52;
// R22.1: only that one is visible):
//   overlay, overlay-corner, overlay-lower-third, custom: the ad over the
//     content, which is not transformed;
//   squeezeback-l-shape-upper-left / -upper-right: the creative over the whole
//     frame underneath, the content on top of it in the named corner;
//   squeezeback-double-box: the content in the centre-left box, the ad in the
//     centre-right box, the bands black;
//   squeezeback-double-box-background: the same, over the background image,
//     which fills the bands;
//   linear (a non-linear candidate's takeover), pause-fullscreen: the ad
//     alone over the whole viewport; every other surface is taken off screen
//     (the harness computes no occlusion, so a covered surface must not be
//     shown);
//   pause-partial: the ad over the paused frame, which is not transformed.
//
// Readings this file takes where the specification leaves room:
// - R12.5's "upper-left 60% of the frame" and "centre-left 25%" are read as
//   AREA with the aspect ratio kept: an L-shape's content box is
//   sqrt(0.60) = 77.46% of each side, a double box's boxes 50% x 50%, side by
//   side and vertically centred (T-04 part C reads the tests the same way);
// - the overlay tokens' own rectangles are not fixed by any criterion
//   (PLY-73: "the corner follows from the creative"); OVERLAY_RECT gives the
//   creative's box for each (lower-third: the bottom 30%; corner: the
//   lower-right quarter of each side; overlay and pause-partial: a centred
//   box);
// - a covered surface is taken off screen with `display:none`, which no
//   family uses for anything else (they use `visibility`), so restoring it
//   cannot undo a family's own decision.
(function (global) {
  const L_SIDE = Math.sqrt(0.60) * 100;          // 77.4597%
  const REGION = {
    'squeezeback-l-shape-upper-left': [0, 0, L_SIDE, L_SIDE],
    'squeezeback-l-shape-upper-right': [100 - L_SIDE, 0, L_SIDE, L_SIDE],
    'squeezeback-double-box': [0, 25, 50, 50],
    'squeezeback-double-box-background': [0, 25, 50, 50],
  };
  const AD_BOX = {
    'squeezeback-double-box': [50, 25, 50, 50],
    'squeezeback-double-box-background': [50, 25, 50, 50],
  };
  const OVERLAY_RECT = {
    overlay: [10, 70, 80, 20],
    'overlay-corner': [75, 75, 25, 25],
    'overlay-lower-third': [0, 70, 100, 30],
    'pause-partial': [25, 25, 50, 50],
  };
  const FULL = [0, 0, 100, 100];
  const COVERING = new Set(['linear', 'pause-fullscreen']);
  const L_SHAPE = new Set(['squeezeback-l-shape-upper-left', 'squeezeback-l-shape-upper-right']);
  const DOUBLE_BOX = new Set(['squeezeback-double-box', 'squeezeback-double-box-background']);
  // Stacking inside the viewport: the band fill, the full-frame creative,
  // the content, the boxes' ad, an overlay, a pause ad or takeover.
  const Z = { band: 1, creative: 2, content: 3, box: 4, overlay: 5, cover: 6 };
  const GEOMETRY = ['left', 'top', 'width', 'height', 'zIndex'];

  const place = (el, r, z) => {
    el.style.position = 'absolute';
    el.style.left = `${r[0]}%`;
    el.style.top = `${r[1]}%`;
    el.style.width = `${r[2]}%`;
    el.style.height = `${r[3]}%`;
    el.style.zIndex = String(z);
  };

  class Handle {
    constructor(c, el, layout, opts) {
      this.c = c;
      this.el = el;
      this.layout = layout;
      this.kind = opts.kind || 'overlay';
      this.rect = opts.rect || null;
      this.background = opts.background || null;
      this.content = opts.content || (() => c.ref.video);
      this.suspended = false;
      this.removed = false;
      this.seq = ++c.seq;
    }

    get ready() {
      const el = this.el;
      if (el.tagName === 'IMG') return el.complete && el.naturalWidth > 0;
      if (el.tagName === 'VIDEO') return el.readyState >= 2;
      return true;
    }

    suspend() { if (!this.suspended) { this.suspended = true; this.c.refresh(); } }
    resume() { if (this.suspended) { this.suspended = false; this.c.refresh(); } }

    remove() {
      if (this.removed) return;
      this.removed = true;
      const c = this.c;
      c.handles = c.handles.filter((h) => h !== this);
      c.refresh();
      for (const el of [this.el, this.background]) if (el) el.remove();
    }
  }

  class SgaiCompositor {
    constructor(ref) {
      this.ref = ref;
      this.container = ref.container;
      this.handles = [];
      this.seq = 0;
      this.saved = new Map();      // content <video> -> its geometry before a squeeze
      this.covered = new Map();    // element -> its display before it was covered
      this.band = null;            // the black fill of a double box with no background
      this.sig = null;
      ref.compositor = this;
    }

    present(el, layout, opts) {
      const h = new Handle(this, el, layout, opts || {});
      el.style.visibility = 'hidden';
      el.style.border = '0';
      el.style.margin = '0';
      el.style.padding = '0';
      if (el.tagName === 'IMG' || el.tagName === 'VIDEO') el.style.objectFit = 'fill';
      this.container.appendChild(el);
      if (h.background) {
        h.background.style.visibility = 'hidden';
        h.background.style.objectFit = 'fill';
        this.container.appendChild(h.background);
      }
      this.handles.push(h);
      // A video's first frame may come after this call: the screen is
      // recomputed when it does.
      if (el.tagName === 'VIDEO' && !h.ready) {
        const again = () => { if (!h.removed) this.refresh(); };
        el.addEventListener('loadeddata', again, { once: true });
        el.addEventListener('playing', again, { once: true });
      }
      this.refresh();
      return h;
    }

    // The form on top: a pause ad before an overlay, the later before the
    // earlier; suspended forms are not candidates.
    top() {
      let best = null;
      for (const h of this.handles) {
        if (h.suspended || h.removed) continue;
        const rank = (h.kind === 'pause' ? 1e9 : 0) + h.seq;
        if (!best || rank > best.rank) best = { h, rank };
      }
      return best ? best.h : null;
    }

    refresh() {
      const h = this.top();
      const linear = this.ref.linear;
      const linearOn = !!(linear && linear.onScreen);
      const content = h ? h.content() : null;
      const sig = [h && h.seq, h && h.layout, h && h.ready, content && (content.sgaiId || (content.sgaiId = ++this.seq)),
        linearOn, this.handles.map((x) => `${x.seq}${x.suspended ? 's' : ''}`).join(',')].join('|');
      if (sig === this.sig) return;
      this.sig = sig;
      this.restore();
      for (const x of this.handles) {
        if (x === h) continue;
        x.el.style.visibility = 'hidden';
        if (x.background) x.background.style.visibility = 'hidden';
      }
      if (h) this.compose(h, content);
      this.container.dataset.sgaiLayout = h ? h.layout : linearOn ? 'linear' : 'none';
    }

    // Everything this file changed outside its own surfaces, put back.
    restore() {
      for (const [v, g] of this.saved) for (const k of GEOMETRY) v.style[k] = g[k];
      this.saved.clear();
      for (const [el, d] of this.covered) el.style.display = d;
      this.covered.clear();
      if (this.band) { this.band.remove(); this.band = null; }
    }

    squeeze(v, r) {
      if (!v) return;
      if (!this.saved.has(v)) {
        const g = {};
        for (const k of GEOMETRY) g[k] = v.style[k];
        this.saved.set(v, g);
      }
      place(v, r, Z.content);
    }

    compose(h, content) {
      const el = h.el;
      const L = h.layout;
      if (L_SHAPE.has(L)) {
        place(el, FULL, Z.creative);
        this.squeeze(content, REGION[L]);
      } else if (DOUBLE_BOX.has(L)) {
        place(el, AD_BOX[L], Z.box);
        this.squeeze(content, REGION[L]);
        if (h.background) {
          place(h.background, FULL, Z.band);
          h.background.style.visibility = 'visible';
        } else {
          // R26.1, PLY-71: with no background the bands render black.
          const b = document.createElement('div');
          place(b, FULL, Z.band);
          b.style.background = '#000';
          this.container.appendChild(b);
          this.band = b;
        }
      } else if (COVERING.has(L)) {
        place(el, FULL, Z.cover);
        // Until the ad has a frame, what was on screen stays.
        if (h.ready) {
          for (const s of this.container.querySelectorAll('[data-sgai-element]')) {
            if (s === el || this.covered.has(s)) continue;
            this.covered.set(s, s.style.display);
            s.style.display = 'none';
          }
        }
      } else {
        const r = L === 'custom' && h.rect ? h.rect : OVERLAY_RECT[L] || OVERLAY_RECT.overlay;
        place(el, r, h.kind === 'pause' ? Z.cover : Z.overlay);
      }
      el.style.visibility = 'visible';
    }
  }

  SgaiCompositor.REGION = REGION;
  SgaiCompositor.AD_BOX = AD_BOX;
  global.SgaiCompositor = SgaiCompositor;
})(window);
