"""Parse a behaviour.log into {(name, cls, variant): {field: outcome}}."""
import re, sys, json
RX = re.compile(r"^(PASS|FAIL|NOT_VERIFIABLE|NOT_APPLICABLE)\s+(\S+(?: \([^)]*\))?) (D\d|legacy)(?: \[([^\]]+)\])?\s+(\S+)")
def parse(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        m = RX.match(line)
        if not m:
            continue
        o, name, cls, var, field = m.groups()
        out.setdefault((name, cls, var or ""), {})[field] = o
    return out
if __name__ == "__main__":
    d = parse(sys.argv[1])
    for k, v in sorted(d.items()):
        print("|".join(k), json.dumps(v))
