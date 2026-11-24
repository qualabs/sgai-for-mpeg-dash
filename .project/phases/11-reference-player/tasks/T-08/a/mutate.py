import sys
M = {
 'M1-R13.1-window-timebase': [("this.beacons(x.plan[k], x.slotT - x.plan[k].start, w.key);", "this.beacons(x.plan[k], x.slotT, w.key);")],
 'M2-R13.6-first-option-only': [("if (!bs || !bs.length) return;", "if (!bs || !bs.length || p.c.option.index !== 1) return;")],
 'M3-R13.3-trim-ignored': [("const limit = Math.min(upTo, p.shown) + 1e-6;", "const limit = upTo + 1e-6;"),
    ("if (x.plan[x.k]) this.beacons(x.plan[x.k], x.plan[x.k].shown, w.key);   // it completed\n          this.endExec", "if (x.plan[x.k]) this.beacons(x.plan[x.k], x.plan[x.k].c.duration, w.key);   // it completed\n          this.endExec")],
 'M4-R13.3-dismiss-flushes': [("this.endExec(x, 'dismissed by the viewer (R35.4)');", "for (const p of x.plan) this.beacons(p, Infinity, x.w.key); this.endExec(x, 'dismissed by the viewer (R35.4)');")],
 'M5-R13.3-resume-flushes': [("      const slot = this.pauseSlot;\n      this.pauseSlot = null;", "      const slot = this.pauseSlot;\n      if (slot && slot.plan) for (const p of slot.plan) this.beacons(p, Infinity, slot.w.key);\n      this.pauseSlot = null;")],
 'M6-R6.5-no-dedup': [("if (keys.some((k) => st.seen.has(k)))", "if (false)")],
 'M7-R6.5-document-scope': [("if (!p.beacons) p.beacons = { next: 0, seen: new Set() };", "if (!p.beacons) p.beacons = { next: 0, seen: (this.docSeen = this.docSeen || new Set()) };")],
 'M8-R6.4-drop-foreign-attr-events': [("        if (!url) continue;\n        out.push({ id: ev", "        if (!url || Array.from(ev.attributes).some((a) => a.namespaceURI && a.namespaceURI !== DASH)) continue;\n        out.push({ id: ev")],
 'M9-slot-not-anchored-at-PT': [("slotT: lateBy, lastT: php,", "slotT: 0, lastT: php,")],
}
name, path = sys.argv[1], sys.argv[2]
s = open(path).read()
for a, b in M[name]:
    assert s.count(a) == 1, (name, a, s.count(a))
    s = s.replace(a, b)
open(path, 'w').write(s)
print('applied', name)
