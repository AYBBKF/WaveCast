#!/usr/bin/env python3
"""Graphe des liens internes (lecture seule) : pour chaque URL cible, pages qui la lient, en distinguant
le contenu principal (<main>/<article>) des zones globales (header/nav/footer/aside). Profondeur de clic depuis l'accueil.
Usage : python3 -I maillage.py <sm_urls.json> <sortie.json> [cibles...]"""
import sys, json, re, html, ssl, os, urllib.request, urllib.parse, collections
from concurrent.futures import ThreadPoolExecutor
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else None
B = "https://fluxintelligent.com"
urls = json.load(open(sys.argv[1]))
def norm(h, base):
    u = urllib.parse.urljoin(base, html.unescape(h)).split("#")[0].split("?")[0]
    p = urllib.parse.urlparse(u)
    if p.netloc not in ("fluxintelligent.com", "www.fluxintelligent.com"): return None
    path = p.path if p.path.endswith("/") or "." in p.path.rsplit("/", 1)[-1] else p.path + "/"
    return B + path
def get(u):
    try: return u, urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), context=ctx, timeout=40).read().decode("utf-8", "replace")
    except Exception: return u, ""
with ThreadPoolExecutor(3) as ex: pages = dict(ex.map(get, urls))
graph, content = {}, {}
for u, b in pages.items():
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", b, flags=re.S)
    allp = {norm(h, u) for h in re.findall(r'href=["\']([^"\']+)', body)} - {None, u}
    glob = re.sub(r"<(header|nav|footer|aside)[^>]*>.*?</\1>", " ", body, flags=re.S)
    m = re.search(r"<(main|article)[^>]*>.*</\1>", glob, re.S)
    main = m.group(0) if m else glob
    cont = {norm(h, u) for h in re.findall(r'href=["\']([^"\']+)', main)} - {None, u}
    graph[u], content[u] = allp, cont
depth = {B + "/": 0}; q = collections.deque([B + "/"])
while q:
    c = q.popleft()
    for n in graph.get(c, ()):
        if n in graph and n not in depth: depth[n] = depth[c] + 1; q.append(n)
cibles = [B + c if c.startswith("/") else c for c in sys.argv[3:]] or urls
out = {}
for t in cibles:
    src_all = sorted(u for u, s in graph.items() if t in s)
    src_cont = sorted(u for u, s in content.items() if t in s)
    out[t] = {"profondeur": depth.get(t), "liens_entrants_total": len(src_all), "liens_entrants_contenu": len(src_cont), "depuis_contenu": src_cont, "accueil": t in graph.get(B + "/", set())}
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
for t, v in out.items(): print(f"{t.replace(B,''):60s} prof={v['profondeur']} total={v['liens_entrants_total']} contenu={v['liens_entrants_contenu']} accueil={v['accueil']}")
