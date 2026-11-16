#!/usr/bin/env python3
"""Liens internes des pages du sitemap qui pointent vers une URL non 200 (redirection, 404, noindex).
Usage : python3 -I liens_internes.py <audit.json> <sortie.json>"""
import sys, json, re, html, urllib.request, urllib.error, urllib.parse, ssl, os
from concurrent.futures import ThreadPoolExecutor
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else None
class NR(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NR, urllib.request.HTTPSHandler(context=ctx))
rows = [r for r in json.load(open(sys.argv[1]))["rows"] if r["in_sitemap"] and r["status_initial"] == 200]
def links(u):
    b = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), context=ctx, timeout=30).read().decode("utf-8", "replace")
    out = set()
    for h in re.findall(r'href=["\']([^"\'#]+)', b):
        h = urllib.parse.urljoin(u, html.unescape(h))
        p = urllib.parse.urlparse(h)
        if p.netloc in ("fluxintelligent.com", "www.fluxintelligent.com") and not re.search(r"/wp-(content|includes|json|admin)|\.(css|js|png|jpe?g|webp|svg|ico|xml|pdf)$|/feed/?$|xmlrpc|wp-login", p.path):
            out.add(h)
    return u, out
with ThreadPoolExecutor(int(os.environ.get("WORKERS","2"))) as ex: pages = dict(ex.map(links, [r["url"] for r in rows]))
targets = set().union(*pages.values())
def st(t):
    try: r = op.open(urllib.request.Request(t, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}), timeout=30); return t, r.status, ""
    except urllib.error.HTTPError as e: return t, e.code, e.headers.get("location", "")
    except Exception as e: return t, 0, str(e)
with ThreadPoolExecutor(int(os.environ.get("WORKERS","2"))) as ex: S = {t: (s, l) for t, s, l in ex.map(st, targets)}
bad = {}
for u, ls in pages.items():
    for t in ls:
        if S[t][0] != 200: bad.setdefault(t, {"status": S[t][0], "location": S[t][1], "depuis": []})["depuis"].append(u)
json.dump(bad, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(f"{len(targets)} cibles internes distinctes, {len(bad)} non-200")
for t, v in sorted(bad.items(), key=lambda x: -len(x[1]["depuis"])): print(v["status"], t, "->", v["location"], "| pages:", len(v["depuis"]), v["depuis"][:3])
