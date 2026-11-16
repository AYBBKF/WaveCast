#!/usr/bin/env python3
"""Surveillance douce des erreurs 5xx (production) : séquentiel, 1 requête/seconde, GET et HEAD.
Usage : python3 -I surveillance_5xx.py [nb_urls=20]   (code retour 1 si au moins une 5xx)
Ne fait AUCUN test de charge."""
import sys, re, time, ssl, os, urllib.request, urllib.error, datetime
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
B = "https://fluxintelligent.com"; n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
def req(u, m):
    try: r = urllib.request.urlopen(urllib.request.Request(u, method=m, headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"}), context=ctx, timeout=30); return r.status, r.headers.get("cf-cache-status", ""), r.headers.get("server", "")
    except urllib.error.HTTPError as e: return e.code, e.headers.get("cf-cache-status", ""), e.headers.get("server", "")
    except Exception as e: return 0, "", str(e)[:60]
urls = re.findall(r"<loc>([^<]+)</loc>", urllib.request.urlopen(urllib.request.Request(B + "/post-sitemap.xml", headers={"User-Agent": "Mozilla/5.0"}), context=ctx).read().decode())[:n]
erreurs = 0
for u in urls:
    for m in ("GET", "HEAD"):
        s, cf, sv = req(u, m); time.sleep(1)
        if s >= 500 or s == 0: erreurs += 1; print(f"{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S}Z {m} {s} cf={cf} server={sv} {u}")
print(f"{len(urls)*2} requêtes, {erreurs} erreur(s) 5xx/réseau"); sys.exit(1 if erreurs else 0)
