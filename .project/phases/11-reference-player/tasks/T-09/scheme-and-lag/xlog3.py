import json,sys
raw=json.load(open(sys.argv[1]))
def walk(o, ctx=''):
    if isinstance(o,dict):
        c = ctx + ' ' + ' '.join(str(o.get(k)) for k in ('variant','class') if k in o and not isinstance(o.get(k),(dict,list)))
        if 'moduleLog' in o:
            xs=[e['data'] for e in o['moduleLog'] if e['type']=='linear:TMPexcess']
            n=sum(1 for e in o['moduleLog'] if e['type']=='linear:TMPexcess')
            top=sorted(xs,key=lambda d:-d['x'])[:4]
            print(c.strip()[:40], 'excess>5ms:', n, 'top:', [(round(d['x'],4), round(d['dwall'],4), round(d['php'],2)) for d in top])
            for e in o['moduleLog']:
                if e['type']=='linear:crossing':
                    d=e['data']; print('   crossing', {k:d.get(k) for k in ('php','crossed','lastPhp','dphp','dwall','rate')})
        for v in o.values(): walk(v, c)
    elif isinstance(o,list):
        for v in o: walk(v, ctx)
walk(raw)
