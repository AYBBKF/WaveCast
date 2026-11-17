#!/usr/bin/env python3
"""Contrôle lecture seule : contenu mixte (ressources http://), liens internes non-200, liens externes cassés.
Usage : python3 -I controle_https_liens.py <sm_urls.json> <sortie.json>  (2 requêtes parallèles max)"""
import sys, json, re, html, ssl, os, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else None
class NR(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NR, urllib.request.HTTPSHandler(context=ctx))
UA = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"}
urls = json.load(open(sys.argv[1]))
def page(u):
    try: return u, urllib.request.urlopen(urllib.request.Request(u, headers=UA), context=ctx, timeout=40).read().decode("utf-8", "replace")
    except Exception as e: return u, ""
with ThreadPoolExecutor(2) as ex: pages = dict(ex.map(page, urls))
mixed, internes, externes = {}, {}, {}
for u, b in pages.items():
    b2 = re.sub(r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>.*?</script>", " ", b, flags=re.S)
    for m in re.findall(r'(?:src|srcset|data-src)=["\'](http://[^"\'\s]+)', b2) + re.findall(r'<link[^>]+href=["\'](http://[^"\']+)["\'][^>]*rel=["\']stylesheet', b2):
        mixed.setdefault(m, []).append(u)
    for h in re.findall(r'<a[^>]+href=["\']([^"\'#]+)', b2):
        h = urllib.parse.urljoin(u, html.unescape(h).strip())
        p = urllib.parse.urlparse(h)
        if p.scheme not in ("http", "https"): continue
        tgt = internes if p.netloc in ("fluxintelligent.com", "www.fluxintelligent.com") else externes
        if tgt is internes and re.search(r"/wp-(admin|json|login)|xmlrpc|/feed/?$", p.path): continue
        tgt.setdefault(h, set()).add(u)
def st(t):
    try: r = op.open(urllib.request.Request(t, headers=UA, method="GET"), timeout=25); return t, r.status, ""
    except urllib.error.HTTPError as e: return t, e.code, e.headers.get("location", "") or ""
    except Exception as e: return t, 0, str(e)[:60]
with ThreadPoolExecutor(2) as ex: si = list(ex.map(st, internes))
with ThreadPoolExecutor(4) as ex: se = list(ex.map(st, externes))
bad_i = [{"url": t, "status": s, "loc": l, "depuis": sorted(internes[t])[:5], "n": len(internes[t])} for t, s, l in si if s != 200]
bad_e = [{"url": t, "status": s, "info": l, "depuis": sorted(externes[t])[:5], "n": len(externes[t])} for t, s, l in se if s >= 400 or s == 0]
out = {"pages": len(pages), "pages_vides": [u for u, b in pages.items() if not b], "contenu_mixte": mixed, "internes_total": len(internes), "internes_non_200": bad_i, "externes_total": len(externes), "externes_en_erreur": bad_e}
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print("pages", len(pages), "| vides", out["pages_vides"], "| contenu mixte", len(mixed), "| internes", len(internes), "non-200", len(bad_i), "| externes", len(externes), "en erreur", len(bad_e))
for x in bad_i: print(" INT", x["status"], x["url"], "->", x["loc"], "| pages:", x["n"], [d[27:] for d in x["depuis"][:3]])
for x in bad_e: print(" EXT", x["status"], x["url"][:100], x["info"], "| pages:", x["n"], [d[27:] for d in x["depuis"][:3]])
for k, v in list(mixed.items())[:10]: print(" MIX", k, [d[27:] for d in v[:3]])
