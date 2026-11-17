#!/usr/bin/env bash
# Usage : bench.sh <url> <label> [motif bloqué...]  -> 3 passages Lighthouse mobile, médiane LCP/TBT/score
U=$1; L=$2; shift 2; B=""; for p in "$@"; do B="$B --blocked-url-patterns=$p"; done
for i in 1 2 3; do timeout 150 ./node_modules/.bin/lighthouse "$U" --quiet --only-categories=performance --form-factor=mobile $B --chrome-flags="--headless=new --no-sandbox" --output=json --output-path=run-$L-$i.json >/dev/null 2>&1; done
python3 -I - "$L" <<'PY'
import json,sys,statistics as st,glob
L=sys.argv[1]; r=[]
for f in sorted(glob.glob(f"run-{L}-*.json")):
    try: d=json.load(open(f)); a=d["audits"]; r.append((d["categories"]["performance"]["score"]*100,a["largest-contentful-paint"]["numericValue"],a["total-blocking-time"]["numericValue"],a["bootup-time"]["numericValue"],a["total-byte-weight"]["numericValue"]/1024))
    except Exception as e: pass
m=lambda i: round(st.median([x[i] for x in r]))
print(f"{L:28s} n={len(r)} score={m(0)} LCP={m(1)}ms TBT={m(2)}ms JS-bootup={m(3)}ms poids={m(4)}Ko")
PY
