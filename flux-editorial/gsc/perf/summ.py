import json,glob,statistics as st,sys
pat=sys.argv[1:]
for p in pat:
    r=[]
    for f in sorted(glob.glob(p)):
        try:
            d=json.load(open(f));a=d['audits'];g=lambda k:a[k]['numericValue']
            r.append((d['categories']['performance']['score']*100,g('first-contentful-paint'),g('largest-contentful-paint'),g('speed-index'),g('total-blocking-time'),g('cumulative-layout-shift'),g('server-response-time')))
        except Exception as e: pass
    m=lambda i:round(st.median([x[i] for x in r]),3 if i==5 else 0)
    print(f"{p:22s} n={len(r)} score={m(0)} FCP={m(1)} LCP={m(2)} SI={m(3)} TBT={m(4)} CLS={m(5)} TTFB={m(6)} | FCP all={[round(x[1]) for x in r]} LCP all={[round(x[2]) for x in r]}")
