#!/usr/bin/env python3
"""Similarité de contenu (shingles de 5 mots, Jaccard) entre les URL 200 des sitemaps + titres/H1 dupliqués.
Usage : python3 -I similarite.py <audit.json> <sortie.json>"""
import sys, json, re, html, urllib.request, ssl, os, itertools
from concurrent.futures import ThreadPoolExecutor
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else None
rows = [r for r in json.load(open(sys.argv[1]))["rows"] if r["in_sitemap"] and r["status_initial"] == 200]
def fetch(u):
    b = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30, context=ctx).read().decode("utf-8", "replace")
    title = html.unescape((re.search(r"<title>(.*?)</title>", b, re.S) or [None, ""])[1]).strip()
    h1 = [html.unescape(re.sub("<[^>]+>", "", h)).strip() for h in re.findall(r"<h1[^>]*>(.*?)</h1>", b, re.S)]
    m = re.search(r"<main.*?</main>", b, re.S) or re.search(r"<article.*?</article>", b, re.S)
    body = m.group(0) if m else b
    body = re.sub(r"<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", body, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", body)).lower()
    words = re.findall(r"\w+", txt)
    sh = {" ".join(words[i:i+5]) for i in range(max(0, len(words)-4))}
    return u, title, h1, len(words), sh
with ThreadPoolExecutor(8) as ex: data = list(ex.map(fetch, [r["url"] for r in rows]))
pairs = []
for a, b in itertools.combinations(data, 2):
    if a[4] and b[4]:
        j = len(a[4] & b[4]) / len(a[4] | b[4])
        if j >= 0.25: pairs.append({"a": a[0], "b": b[0], "jaccard": round(j, 3)})
pairs.sort(key=lambda p: -p["jaccard"])
dup_titles = {}
for u, t, h, n, _ in data: dup_titles.setdefault(t, []).append(u)
out = {"pairs": pairs, "titres_dupliques": {t: us for t, us in dup_titles.items() if len(us) > 1},
       "pages": [{"url": u, "title": t, "h1": h, "mots": n} for u, t, h, n, _ in data]}
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
for p in pairs: print(p["jaccard"], p["a"], "<>", p["b"])
print("titres dupliqués:", out["titres_dupliques"])
for p in out["pages"]:
    if len(p["h1"]) != 1 or p["mots"] < 300: print("H1/mots:", p["url"], len(p["h1"]), p["mots"])
