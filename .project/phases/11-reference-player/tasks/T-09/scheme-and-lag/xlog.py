import json,sys
raw=json.load(open(sys.argv[1]))
def walk(o):
    if isinstance(o,dict):
        if 'moduleLog' in o:
            for e in o['moduleLog']:
                if e['type'] in ('linear:crossing','linear:execute'): print(e['type'], {k:e['data'].get(k) for k in ('php','crossed','dphp','dwall','rate','PRTA','lag','APDA')})
        for v in o.values(): walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
walk(raw)
