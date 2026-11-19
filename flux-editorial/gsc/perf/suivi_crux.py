#!/usr/bin/env python3
"""Suivi des données terrain CrUX (mobile) pour fluxintelligent.com.

Usage : CRUX_API_KEY=... python3 -I suivi_crux.py [urls.txt] > crux-AAAA-MM-JJ.md

- Clé : Google Cloud > API « Chrome UX Report API » > Identifiants > clé API
  (gratuite). Elle n'est jamais écrite dans ce dépôt.
- Interroge l'origine et chaque URL (formFactor PHONE) : LCP, FCP, CLS, INP au
  75e centile (fenêtre glissante de 28 jours), puis l'historique hebdomadaire
  du LCP (API History, 25 périodes) pour l'origine et l'accueil.
- Une URL absente de CrUX (trafic insuffisant) est signalée « pas de données » :
  Search Console la rattache alors au groupe et à l'URL représentative.
"""
import json, os, sys, ssl, urllib.request, urllib.error

KEY = os.environ.get("CRUX_API_KEY")
if not KEY:
    sys.exit("CRUX_API_KEY manquante")
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
ORIGIN = "https://fluxintelligent.com"
MET = ["largest_contentful_paint", "first_contentful_paint", "cumulative_layout_shift", "interaction_to_next_paint"]


def call(endpoint, body):
    req = urllib.request.Request(f"https://chromeuxreport.googleapis.com/v1/records:{endpoint}?key={KEY}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        return json.loads(urllib.request.urlopen(req, context=CTX, timeout=30).read())
    except urllib.error.HTTPError as e:
        return {"error": e.code}


def p75(rec, m):
    v = rec.get("record", {}).get("metrics", {}).get(m, {}).get("percentiles", {}).get("p75")
    return "–" if v is None else v


urls = [ORIGIN + "/"]
if len(sys.argv) > 1:
    urls += [l.strip() for l in open(sys.argv[1]) if l.strip() and l.strip() != ORIGIN + "/"]

print("| Cible | LCP p75 (ms) | FCP p75 (ms) | CLS p75 | INP p75 (ms) | Période |")
print("|---|---|---|---|---|---|")
o = call("queryRecord", {"origin": ORIGIN, "formFactor": "PHONE", "metrics": MET})
per = o.get("record", {}).get("collectionPeriod", {}).get("lastDate", {})
print(f"| origine | {p75(o, MET[0])} | {p75(o, MET[1])} | {p75(o, MET[2])} | {p75(o, MET[3])} | fin {per.get('year','?')}-{per.get('month','?')}-{per.get('day','?')} |")
for u in urls:
    r = call("queryRecord", {"url": u, "formFactor": "PHONE", "metrics": MET})
    if "error" in r:
        print(f"| {u[len(ORIGIN):]} | pas de données | | | | |")
    else:
        print(f"| {u[len(ORIGIN):]} | {p75(r, MET[0])} | {p75(r, MET[1])} | {p75(r, MET[2])} | {p75(r, MET[3])} | |")

print("\nHistorique hebdomadaire du LCP p75 (mobile) :\n")
for target in ({"origin": ORIGIN}, {"url": ORIGIN + "/"}):
    h = call("queryHistoryRecord", {**target, "formFactor": "PHONE", "metrics": ["largest_contentful_paint"]})
    if "error" in h:
        print(f"- {list(target.values())[0]} : pas de données"); continue
    vals = h["record"]["metrics"]["largest_contentful_paint"]["percentilesTimeseries"]["p75s"]
    ends = [f"{p['lastDate']['month']:02d}/{p['lastDate']['day']:02d}" for p in h["record"]["collectionPeriods"]]
    print(f"- {list(target.values())[0]} : " + ", ".join(f"{d} {v}" for d, v in list(zip(ends, vals))[-8:]))
