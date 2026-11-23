#!/usr/bin/env python3
"""What a pipeline run cost, per step, read from its Claude Code transcript.

A run is one `claude -p` session plus the subagents it dispatched. Claude
Code writes the session to `<config>/projects/<cwd-slug>/<id>.jsonl` and each
subagent to `<id>/subagents/agent-*.jsonl`. This script sums the API usage
recorded there and attributes each subagent to the step it ran: the first
`prompts/.../*.prompt` named in the subagent's first message.

**Usage is counted once per API call.** The transcript writes one line per
content block of a response, and every one of those lines repeats the same
`usage`; the call is identified by `message.id`, and the last line of a call
carries its final counts. Summing lines instead counts a call as many times
as it had blocks (on the 2026-10-27 incremental: 90M instead of 41.8M).

What it reports per step: fresh input, cache write, cache read, their sum
(input processed), output, number of calls and the largest context of one
call. What it does NOT report: money. The weights of cache reads and writes
and the output price depend on the model and the date; apply them outside.

Usage:
  bin/measure-run.py <session.jsonl | session-id> [--json] [--by-agent] [--root DIR ...]

  Rows are per step: a subagent that names no prompt is charged to its
  parent's step (`parentAgentId` in its .meta.json). --by-agent lists every
  agent instead, with its description.

  A bare session id is looked up under every `projects/` directory of the
  Claude Code config roots (CLAUDE_CONFIG_DIR, ~/.claude, and any --root).

Exit codes: 0 measured · 2 no transcript found or no usage in it ·
64 wrong command line.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

PROMPT_RE = re.compile(r"prompts/[\w./-]+?\.prompt")
KEYS = ("input_tokens", "cache_creation_input_tokens",
        "cache_read_input_tokens", "output_tokens")


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return ""


def measure_file(path, count_lines=False):
    """Usage of one transcript file. `count_lines` reproduces the wrong count
    (one per line) and exists only so the test can show the two differ."""
    calls = {}
    order = []
    first_user = None
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get("message")
            if first_user is None and d.get("type") == "user" and isinstance(msg, dict):
                first_user = text_of(msg.get("content"))
            if d.get("type") != "assistant" or not isinstance(msg, dict):
                continue
            u = msg.get("usage")
            if not isinstance(u, dict):
                continue
            key = n if count_lines else (msg.get("id") or d.get("uuid") or n)
            if key not in calls:
                order.append(key)
            calls[key] = u
    tot = dict.fromkeys(KEYS, 0)
    max_ctx = 0
    for k in order:
        u = calls[k]
        for f in KEYS:
            tot[f] += int(u.get(f) or 0)
        ctx = sum(int(u.get(f) or 0) for f in KEYS[:3])
        max_ctx = max(max_ctx, ctx)
    m = PROMPT_RE.search(first_user or "")
    return {
        "file": path,
        "step": m.group(0) if m else None,
        "calls": len(order),
        "fresh_input": tot["input_tokens"],
        "cache_write": tot["cache_creation_input_tokens"],
        "cache_read": tot["cache_read_input_tokens"],
        "input_processed": sum(tot[f] for f in KEYS[:3]),
        "output": tot["output_tokens"],
        "max_context": max_ctx,
    }


def find_session(arg, roots):
    if os.path.isfile(arg):
        return arg
    for root in roots:
        hits = glob.glob(os.path.join(root, "projects", "*", arg + ".jsonl"))
        if hits:
            return hits[0]
    return None


def measure(session_path, count_lines=False, by_agent=False):
    """Rows per step (or per agent with by_agent) and the total. A subagent
    whose first message names no prompt is charged to the step of its parent
    (`parentAgentId` in its .meta.json, followed up the chain): the walkers a
    validation dispatches are the validation's cost."""
    base = session_path[:-len(".jsonl")]
    agents = []
    for sub in sorted(glob.glob(os.path.join(base, "subagents", "*.jsonl"))):
        r = measure_file(sub, count_lines)
        aid = os.path.basename(sub)[len("agent-"):-len(".jsonl")]
        meta = {}
        mp = sub[:-len(".jsonl")] + ".meta.json"
        if os.path.isfile(mp):
            with open(mp, encoding="utf-8") as fh:
                try:
                    meta = json.load(fh)
                except ValueError:
                    meta = {}
        r["agent"] = aid
        r["parent"] = meta.get("parentAgentId")
        r["description"] = meta.get("description", "")
        agents.append(r)
    own = {a["agent"]: a for a in agents}

    def step_of(a, seen=()):
        if a["step"]:
            return a["step"]
        p = own.get(a["parent"]) if a["parent"] else None
        if p is None or p["agent"] in seen:
            return "(orchestrator's own subagents)"
        return step_of(p, seen + (a["agent"],))

    orch = dict(measure_file(session_path, count_lines), step="(orchestrator)")
    fields = ("calls", "fresh_input", "cache_write", "cache_read", "input_processed", "output")
    if by_agent:
        rows = [orch] + [dict(a, step=f"{step_of(a)} ← {a['description'] or a['agent']}") for a in agents]
    else:
        grouped = {}
        order = []
        for a in agents:
            s = step_of(a)
            if s not in grouped:
                grouped[s] = dict.fromkeys(fields, 0)
                grouped[s].update(step=s, max_context=0, agents=0)
                order.append(s)
            g = grouped[s]
            for f in fields:
                g[f] += a[f]
            g["max_context"] = max(g["max_context"], a["max_context"])
            g["agents"] += 1
        rows = [orch] + [grouped[s] for s in order]
    total = {f: sum(r[f] for r in rows) for f in fields}
    total["max_context"] = max(r["max_context"] for r in rows)
    return rows, total


def fmt(n):
    return f"{n / 1e6:.2f}M" if n >= 1e5 else f"{n / 1e3:.1f}k"


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    roots = []
    i = 0
    while i < len(argv):
        if argv[i] == "--root":
            if i + 1 >= len(argv):
                usage("--root needs a directory")
            roots.append(argv[i + 1])
            args.remove(argv[i + 1])
            i += 2
            continue
        if argv[i].startswith("--") and argv[i] not in ("--json", "--root", "--by-agent"):
            usage(f"unknown flag {argv[i]}")
        i += 1
    if len(args) != 1:
        usage("one session (path or id) is required")
    roots += [r for r in (os.environ.get("CLAUDE_CONFIG_DIR"),
                          os.path.expanduser("~/.claude")) if r]
    path = find_session(args[0], roots)
    if not path:
        print(f"exit 2: no transcript for {args[0]} under {roots}")
        return 2
    rows, total = measure(path, by_agent="--by-agent" in argv)
    if total["calls"] == 0:
        print(f"exit 2: {path} has no assistant usage")
        return 2
    if as_json:
        print(json.dumps({"session": path, "steps": rows, "total": total}, indent=2))
        return 0
    print(f"session: {path}")
    print(f"{'step':58} {'input':>9} {'c.read':>9} {'c.write':>9} {'output':>8} {'calls':>6} {'max ctx':>8}")
    for r in rows:
        print(f"{r['step'][:58]:58} {fmt(r['input_processed']):>9} {fmt(r['cache_read']):>9} "
              f"{fmt(r['cache_write']):>9} {fmt(r['output']):>8} {r['calls']:>6} {fmt(r['max_context']):>8}")
    print(f"{'TOTAL':58} {fmt(total['input_processed']):>9} {fmt(total['cache_read']):>9} "
          f"{fmt(total['cache_write']):>9} {fmt(total['output']):>8} {total['calls']:>6}")
    print("counted once per API call (message.id); input = fresh + cache write + cache read; no prices applied")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
