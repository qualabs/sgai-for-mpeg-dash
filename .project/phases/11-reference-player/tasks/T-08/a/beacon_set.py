"""Exact beacon multiset check (stand-in for the comparator, whose beacon_urls
does not read <svta:Tracking>): per job of a --save-raw file, the URLs of every
request to a tracking host vs the vector's expected beacons. Exit 1 on any
difference. Usage: beacon_set.py RAW.json SOURCE_DIR"""
import json, sys, collections, yaml
raw = json.load(open(sys.argv[1])); src = sys.argv[2]
bad = 0
for j in raw['jobs']:
    v = yaml.safe_load(open(f"{src}/../{j['vector']}" if not j['vector'].startswith('/') else j['vector']))
    out = v['outcomes'][j['class']]
    exp = collections.Counter(b['url'] for b in out.get('beacons', []) if b.get('url'))
    seen = collections.Counter(r['url'] for r in j['raw']['requests'] if r['url'].startswith('https://t.example.com/'))
    ok = exp == seen
    bad += not ok
    name = j['vector'].split('/')[-1][:-5] + ' ' + j['class']
    print(('OK  ' if ok else 'DIFF') + f" {name}: expected {sum(exp.values())}, fired {sum(seen.values())}"
          + ('' if ok else f"; extra {dict(seen - exp)}; missing {dict(exp - seen)}"))
sys.exit(1 if bad else 0)
