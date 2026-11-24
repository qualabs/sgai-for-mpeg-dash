"""T-05's scoped mutation campaign: one deliberate break per rule of
reference-player/src/sgai-linear.js, each run only against the tests that
cover it. A break is CAUGHT when some field that PASSes on the unmutated
module (the baseline, run first in the same campaign on the same tests)
FAILs with the break. The module is restored after every break and its
sha256 checked. Usage (from the project root):
    python3 .project/phases/11-reference-player/tasks/T-05/mutate.py [--wide MS] OUTDIR [NAME ...]
--wide MS runs every vector with tolerance max(own, MS): for a break whose
effect is seconds, so that the page's own lateness under load (hundreds of
ms) cannot mask it in the baseline or fake it in the mutant.
"""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "reference-player/src/sgai-linear.js"
sys.path.insert(0, str(Path(__file__).resolve().parent / "vectors"))
import importlib.util
_spec = importlib.util.spec_from_file_location("run_edges", Path(__file__).resolve().parent / "vectors" / "run-edges.py")
run_edges = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(run_edges)
SOURCE = None   # set by main(): the composed source of the edge vectors

def vec(*names): return ("EDGE", [n.split("-")[0] for n in names])
def only(*ids): return ["--only", ",".join(ids)]

# name: ([(find, replace), ...], selection args, rule)
MUTATIONS = {
    "M01-executeOnce-ignored": ([("return php <= E.EAP && (!E.executeOnce || E.c === 0);", "return php <= E.EAP;"),
                                 ("if (E.executeOnce && E.c > 0) continue;", "")], vec("E1-execute-once-after-success"),
                                "§5.16.5 @executeOnce / §5.16.2.2.3 2b"),
    "M02-failure-counts": ([("      this.holding = null;\n      this.log('linear:failed'", "      E.c += 1;\n      this.holding = null;\n      this.log('linear:failed'")],
                           only("R30.2"), "§5.16.2.2.6 NOTE 3 (E.c not incremented on failure)"),
    "M03-maxDuration-zero-executed": ([("if (!(E.APDmax > 0)) {", "if (false) {"),
                                       ("!E.resolution && E.APDmax > 0 &&", "!E.resolution &&")], only("R4.7"),
                                      "§5.16.5 @maxDuration zero: not executed"),
    "M04-document-order": ([(".filter((E) => this.eligible(E, php)).sort((a, b) => a.PRT - b.PRT);", ".filter((E) => this.eligible(E, php));")],
                           only("R20.3"), "§5.16.2.2.2 QE ordered by PRT"),
    "M05-no-next-after-failure": ([("      if (wasPlaying) this.main.play();\n      this.tick();",
                                    "      this.queue = this.queue.filter((x) => x.PRT > this.main.currentTime);\n      if (wasPlaying) this.main.play();\n      this.tick();")],
                                  only("R20.1"), "§5.16.2.2.5 2d (next events of QE after a failed execution)"),
    "M06-insert-cap-ignored": ([(": Math.min(APD, alt.E.APDmax);", ": APD;")], only("R4.2"),
                               "Table 57 APDA = min(APD, APDmax) for insertion (cumulative over a List)"),
    "M07-maxDuration-default-finite": ([("num(child.maxDuration, Infinity) / ts", "num(child.maxDuration, 5 * ts) / ts")], only("R4.8"),
                                       "§5.16.5 @maxDuration absent = infinity"),
    "M08-ERT-ignored": ([("php >= E.ERT && php < E.PRT", "php < E.PRT")], only("R30.2"),
                        "§5.16.5 @earliestResolutionTimeOffset (not requested before ERT)"),
    "M09-clip-ignored": ([("isReplace && E.clip ? Math.max(E.APDmax - PRTA + E.PRT, 0) : E.APDmax", "E.APDmax")],
                         vec("E3-replace-late-clip"), "Table 57 APDadj with @clip"),
    "M10-noclip-RT": ([("else if (!E.clip) RT = alt.PRTA + APDA;", "")], vec("E4-replace-late-noclip"),
                      "Table 57 RT = PRTA + APDA with @clip=false"),
    "M11-startWithOffset-ignored": ([("isReplace && E.startWithOffset ? PRTA - E.PRT : 0", "0")],
                                    vec("E5-replace-start-with-offset"), "Table 57 ASO with @startWithOffset"),
    "M12-returnOffset-ignored": ([("if (E.returnOffset !== null) RT = E.PRT + E.returnOffset;", "if (false) RT = 0;")],
                                 vec("E6-replace-return-offset"), "Table 57 RT = PRT + RO"),
    "M13-APDA-zero-executed": ([("if (!(this.apda(alt) > 0)) return this.failed(E, wasPlaying, 'APDA is 0', parts);", "")],
                               vec("E7-replace-apda-zero"), "§5.16.2.2.1 step 3, APDA 0 not executed"),
    "M14-failed-linked-period-ends-break": ([("if (!ok) { this.nextPart(alt); return; }", "if (!ok) { this.terminate(alt, this.apda(alt)); return; }"),
                                             ("if (p.state === 'unresolved' && pos >= p.start - p.ert) p.resolve();",
                                              "if (p.state === 'unresolved' && pos >= p.start - p.ert) p.resolve().then((ok) => { if (!ok && this.alt === alt) this.terminate(alt, this.apda(alt)); });")],
                                            vec("E8-list-linked-period-fails"), "§5.3.2.6.3 step 2 (a Linked Period that fails is removed)"),
    "M15-all-linked-resolved-upfront": ([("          while (parts.length) {", "          for (const q of parts.slice(1)) q.resolve();\n          while (parts.length) {")],
                                        only("R4.2", "UC-01"), "§5.3.2.6.1 not resolved earlier than PeriodStart - @earliestResolutionTimeOffset"),
    "M16-callback-dedup-removed": ([("if (alt.fired.has(cb.key)) {", "if (false) {")], only("R6.5"),
                                   "§5.10.2.4 a processed (@schemeIdUri, @value, @id) is ignored"),
    "M17-callbacks-left-to-dashjs": ([("this.callbacks = takeCallbacks(doc);", "this.callbacks = [];")], only("R4.8"),
                                     "callbacks on start, as the alternative is played (not at preload)"),
    "M18-insert-RT-is-PRT": ([("if (E.scheme === INSERT) RT = alt.PRTA;", "if (E.scheme === INSERT) RT = E.PRT;")],
                             vec("E9-insert-late-join"), "Table 57 RT of an insertion is PRTA"),
    "M19-seek-no-reset": ([("        this.seeking = false;\n        this.resetQueue('seeked');", "        this.seeking = false;"),
                           ("        this.queue = [];\n        this.player.seek(action.to);", "        this.player.seek(action.to);")],
                          only("R30.2"), "§5.16.2.2.7 return from a seek resets QE"),
    "M20-pause-not-taken": ([("case 'pause': this.suspend(); return { done: 'linear ad paused' };", "case 'pause': return null;")],
                            vec("E11-pause-during-linear-ad"), "R17.5 linear part: the linear ad is suspended and resumed"),
    "M21-reset-after-termination": ([("      // The queue is not reset here", "      this.resetQueue('terminate');\n      // The queue is not reset here")],
                                    vec("E2-insert-reexecuted-after-seek"), "A.14.5: no reset at termination (the T-01 reading)"),
    "M22-expired-executed": ([("return php <= E.EAP && (!E.executeOnce || E.c === 0);", "return (!E.executeOnce || E.c === 0);"),
                              ("if (E.EAP <= php) {", "if (false) {")], vec("E10-join-after-eap"),
                             "§5.16.2.2.5 2a: an event no longer active is not executed"),
    "M23-no-preroll-gate": ([("      this.gated = true;\n      this.main.style.visibility = 'hidden';\n", "      this.gated = true;\n")],
                            vec("E4-replace-late-noclip", "E5-replace-start-with-offset"), "a join inside an active interval: the alternative is the first frame"),
}


def sha(): return hashlib.sha256(SRC.read_bytes()).hexdigest()


WIDE = None   # --wide MS: every vector of a run gets tolerance max(its own, MS)


def widened(files):
    """Copies of the vector files with tolerance max(own, WIDE), in the
    campaign's temporary directory (their fixture paths are unchanged)."""
    import yaml, tempfile
    out = []
    d = Path(tempfile.mkdtemp(dir=SOURCE, prefix="t05-wide-"))
    for f in files:
        v = yaml.safe_load(Path(f).read_text())
        v["tolerance"] = max(v.get("tolerance", 0), WIDE)
        g = d / Path(f).name
        g.write_text(yaml.safe_dump(v, sort_keys=False))
        out.append(str(g))
    return out


def only_files(ids):
    import re
    src = ROOT / "spec-source"
    fs = []
    for tok in ids:
        if tok.startswith("UC-"):
            fs.append(src / "scenarios" / f"{tok}.yaml")
        else:
            fs += [f for f in sorted((src / "behaviour").glob("R*.yaml")) if re.fullmatch(re.escape(tok) + r"(-\d+)?", f.stem)]
    return [str(f) for f in fs]


def run(args, out):
    if isinstance(args, tuple):
        args = run_edges.edge_args(SOURCE, args[1])
    if WIDE:
        if args[0] == "--only":
            files, src = only_files(args[1].split(",")), []
        else:
            src, files = args[:2], [a for a in args[2:] if a != "--vector"]
        args = src + [a for f in widened(files) for a in ("--vector", f)]
    cmd = ["python3", "bin/check-dash-conformance.py", "--behaviour", "--class", "D1", "--concurrency", "1",
           "--out-json", str(out)] + args
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    try:
        res = json.loads(out.read_text())["results"]
    except Exception:
        return p.returncode, None, p.stdout + p.stderr
    return p.returncode, {(r["subject"], r["rule"]): (r["outcome"], r["detail"]) for r in res}, p.stdout


def main():
    global WIDE
    argv = sys.argv[1:]
    if argv and argv[0] == "--wide":
        WIDE = int(argv[1]); argv = argv[2:]
    outdir = Path(argv[0]); outdir.mkdir(parents=True, exist_ok=True)
    names = argv[1:] or list(MUTATIONS)
    original = SRC.read_text(); h0 = sha()
    global SOURCE
    with run_edges.edge_source() as SOURCE:
        campaign(names, outdir, original, h0)
    print(f"module sha256 after campaign: {sha()} (before: {h0})")


def campaign(names, outdir, original, h0):
    for name in names:
        edits, args, rule = MUTATIONS[name]
        code0, base, _ = run(args, outdir / f"{name}.base.json")
        text = original
        for f, r in edits:
            assert text.count(f) == 1, f"{name}: find not unique/absent: {f!r}"
            text = text.replace(f, r)
        try:
            SRC.write_text(text)
            code1, mut, raw = run(args, outdir / f"{name}.mut.json")
        finally:
            SRC.write_text(original)
            assert sha() == h0, "module not restored"
        if base is None or mut is None:
            print(f"{name}: CANNOT TELL (exit {code0}/{code1})\n{raw[-800:]}", flush=True); continue
        red = [(k, mut[k][1]) for k in base if base[k][0] == "PASS" and mut.get(k, ("?",))[0] == "FAIL"]
        verdict = "CAUGHT" if red else "NOT CAUGHT"
        print(f"{name}: {verdict}  [{rule}]  baseline PASS {sum(v[0]=='PASS' for v in base.values())}/{len(base)}, "
              f"mutant PASS {sum(v[0]=='PASS' for v in mut.values())}/{len(mut)}", flush=True)
        for (subj, field), det in red:
            print(f"    red: {subj} {field}: {det[:220]}", flush=True)


if __name__ == "__main__":
    main()
