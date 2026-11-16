#!/usr/bin/env python3
"""Remplacement CIBLÉ d'une URL dans le contenu d'une page WordPress (aucune réécriture manuelle du HTML/JSON-LD).
Le contenu brut est lu par l'API, modifié par str.replace sur l'URL exacte (1 occurrence exigée), renvoyé tel quel.
Usage :
  python3 -I remplacement_liens.py --dry-run            # lecture publique, vérifie les occurrences (aucune écriture)
  WP_COOKIE_JAR=<chemin> WP_NONCE=<nonce> python3 -I remplacement_liens.py --apply
     (cookie de session temporaire via le lien d'autologin Hostinger ; jamais stocké dans le dépôt)
Sauvegarde : backup/page-<id>-raw-<horodatage>.json ; contrôle : diff du rendu avant/après = seule l'URL change."""
import sys, os, json, ssl, re, difflib, datetime, http.cookiejar, urllib.request, urllib.error
B = "https://fluxintelligent.com"
CHANGES = [
    (4100, "https://fluxintelligent.com/ia-hotels-tourisme-maroc-2026/", "https://fluxintelligent.com/automatisation-ia-hotel-fiabilite-technique-experience-client/"),
    (4009, "https://fluxintelligent.com/automatisation-entreprise-maroc/", "https://fluxintelligent.com/automatisation-ia-pme-maroc/"),
]
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
apply = "--apply" in sys.argv
hdl = [urllib.request.HTTPSHandler(context=ctx)]
if apply:
    cj = http.cookiejar.MozillaCookieJar(os.environ["WP_COOKIE_JAR"]); cj.load(ignore_discard=True, ignore_expires=True)
    hdl.append(urllib.request.HTTPCookieProcessor(cj))
op = urllib.request.build_opener(*hdl)
def call(url, data=None):
    h = {"User-Agent": "flux-maintenance", "Content-Type": "application/json"}
    if apply: h["X-WP-Nonce"] = os.environ["WP_NONCE"]
    r = op.open(urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=h, method="POST" if data else "GET"), timeout=60)
    return json.loads(r.read())
def esc(u): return u.replace("/", "\\/")
here = os.path.dirname(os.path.abspath(__file__)); ok = True
for pid, old, new in CHANGES:
    if not apply:
        rend = call(f"{B}/wp-json/wp/v2/pages/{pid}?_fields=content")["content"]["rendered"]
        n = rend.count(old); print(f"[dry-run] page {pid} : {n} occurrence(s) de {old} dans le rendu public -> remplacement par {new}"); ok &= n == 1; continue
    d = call(f"{B}/wp-json/wp/v2/pages/{pid}?context=edit&_fields=id,modified_gmt,content")
    raw, before = d["content"]["raw"], d["content"]["rendered"]
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json.dump(d, open(f"{here}/backup/page-{pid}-raw-{ts}.json", "w"), ensure_ascii=False)
    n = raw.count(old) + raw.count(esc(old))
    if n != 1: print(f"page {pid} : {n} occurrence(s) dans le brut, ARRÊT sans écriture"); ok = False; continue
    new_raw = raw.replace(old, new) if old in raw else raw.replace(esc(old), esc(new))
    assert len(new_raw) - len(raw) == len(new) - len(old)
    after = call(f"{B}/wp-json/wp/v2/pages/{pid}", {"content": new_raw})["content"]["rendered"]
    diff = [l for l in difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    seul_url = all(old in l or new in l for l in diff) and len(diff) == 2
    print(f"page {pid} : écrit ; diff du rendu = {len(diff)} ligne(s) ; uniquement l'URL : {seul_url}"); ok &= seul_url
sys.exit(0 if ok else 1)
