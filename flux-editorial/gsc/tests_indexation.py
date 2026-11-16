#!/usr/bin/env python3
"""Tests de non-régression indexation fluxintelligent.com. Usage : python3 -I tests_indexation.py
Sortie : une ligne OK/ECHEC par règle, code retour 1 si un échec."""
import re, sys, os, ssl, urllib.request, urllib.error, urllib.parse, urllib.robotparser, random
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
class NR(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NR, urllib.request.HTTPSHandler(context=ctx))
UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
B = "https://fluxintelligent.com"
def get(u):
    try: r = op.open(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30); return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e: return e.code, {k.lower(): v for k, v in e.headers.items()}, ""
def canon(b): return re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', b.split("</head>")[0])
def robots(b): return " ".join(re.findall(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']+)', b.split("</head>")[0])).lower()
fails = 0
def check(nom, ok, detail=""):
    global fails; fails += (not ok); print(("OK    " if ok else "ECHEC ") + nom + (f"  [{detail}]" if detail and not ok else ""))
# 1. Pages stratégiques : 200, canonical unique auto-référent, indexables
STRAT = ["/", "/ia/blog/", "/agents-ia/", "/automatisation-des-processus/", "/chatbots-experience-client/", "/crm-ventes-marketing-ia/",
         "/ia/automatisation-ia-casablanca/", "/ia/agence-ia-rabat/", "/ia/automatisation-ia-marrakech/", "/automatisation-ia-tanger/",
         "/automatisation-ia-fes/", "/automatisation-ia-meknes/", "/automatisation-ia-agadir/", "/ia/automatisation-ia-oujda/",
         "/ia/automatisation-ia-tetouan/", "/agence-ia-immobilier-maroc/", "/ia/nos-services/", "/ia/devis/", "/ia/contact/",
         "/automatisation-ia-pme-maroc/", "/automatisation-ia-hotel-fiabilite-technique-experience-client/", "/automatisation-factures-ia-maroc/"]
for p in STRAT:
    s, h, b = get(B + p); c = canon(b); r = robots(b)
    check(f"{p} 200 + canonical auto-référent + index", s == 200 and c == [B + p] and "noindex" not in r and "noindex" not in h.get("x-robots-tag", "").lower(), f"{s} {c} {r}")
# 2. Variantes d'hôte/protocole -> https non-www
for v in ["http://fluxintelligent.com/", "https://www.fluxintelligent.com/", "http://www.fluxintelligent.com/"]:
    cur, hops = v, 0
    while hops < 5:
        s, h, _ = get(cur)
        if s in (301, 308) and h.get("location"): cur = urllib.parse.urljoin(cur, h["location"]); hops += 1
        else: break
    check(f"{v} -> {B}/ en 301 ({hops} saut(s))", cur == B + "/" and s == 200, f"fin={cur} {s}")
# 3. Redirections de fusion : 1 saut 301 vers la cible, puis 200
for src, dst in [("/ia-hotels-tourisme-maroc-2026/", "/automatisation-ia-hotel-fiabilite-technique-experience-client/"),
                 ("/automatisation-entreprise-maroc/", "/automatisation-ia-pme-maroc/"), ("/ia/about/", "/ia/propos-de-nous/")]:
    s, h, _ = get(B + src); s2 = get(B + dst)[0]
    check(f"{src} 301 -> {dst}", s == 301 and h.get("location", "").rstrip("/") == (B + dst).rstrip("/") and s2 == 200, f"{s} {h.get('location')}")
# 4. Paramètres : canonical vers l'URL propre
s, h, b = get(B + "/ia/blog/?utm_source=test")
check("paramètre utm -> canonical propre", canon(b) == [B + "/ia/blog/"], str(canon(b)))
# 5. robots.txt : Googlebot autorisé sur les pages, bloqué sur /wp-admin/ seulement
rp = urllib.robotparser.RobotFileParser(); rp.parse(get(B + "/robots.txt")[2].splitlines())
for p in STRAT + ["/wp-content/uploads/2026/11/x.webp", "/wp-includes/js/jquery/jquery.min.js", "/wp-admin/admin-ajax.php", "/sitemap_index.xml"]:
    check(f"robots.txt autorise Googlebot sur {p}", rp.can_fetch("Googlebot", B + p))
check("robots.txt bloque /wp-admin/ pour Googlebot", not rp.can_fetch("Googlebot", B + "/wp-admin/"))
check("robots.txt déclare le sitemap", B + "/sitemap_index.xml" in (rp.site_maps() or []))
# 6. Sitemap : uniquement des URL 200 indexables auto-canoniques (lecture sans cache)
bust = f"?nocache={random.randint(1, 10**9)}"
st, _, idx = get(B + "/sitemap_index.xml" + bust); check("sitemap_index.xml 200", st == 200)
urls = []
for sm in re.findall(r"<loc>([^<]+)</loc>", idx):
    s, _, x = get(sm + bust); check(f"{sm} 200 XML", s == 200 and "<urlset" in x); urls += re.findall(r"<loc>([^<]+)</loc>", x)
bad = []
for u in urls:
    s, h, b = get(u)
    if not (s == 200 and canon(b) == [u] and "noindex" not in robots(b)): bad.append(f"{u} {s} {canon(b)} {robots(b)}")
check(f"sitemap : {len(urls)} URL toutes 200/indexables/auto-canoniques", not bad, " ; ".join(bad))

# 7. Contrôles ajoutés le 16/11 (finalisation)
s, h, x = get(B + "/post-sitemap.xml")   # version PUBLIQUE, sans contournement du cache
check("post-sitemap.xml public sans 3092 ni 3288", s == 200 and "automatisation-entreprise-maroc" not in x and "ia-hotels-tourisme-maroc-2026" not in x)
for sm in ["/sitemap_index.xml", "/post-sitemap.xml", "/page-sitemap.xml"]:
    s, h, _ = get(B + sm); cc = h.get("cache-control", "")
    m = re.search(r"(?:s-maxage|max-age)=(\d+)", cc)
    check(f"{sm} : durée de cache <= 3600 s (actuel : {cc or 'absent'})", ("no-cache" in cc or "no-store" in cc) or (m is not None and int(m.group(1)) <= 3600))
s, h, _ = get(B + "/automatisation-des-factures-par-ia-au-maroc/")
check("ancienne URL factures : 301 directe vers /automatisation-factures-ia-maroc/", s == 301 and h.get("location", "").rstrip("/") == B + "/automatisation-factures-ia-maroc", h.get("location"))
s, h, b = get(B + "/entretien-en-ligne/")
pm = get(B + "/page-sitemap.xml?nocache=" + str(random.randint(1, 10**9)))[2]
check("page 4473 : noindex conservé ET absente du sitemap", "noindex" in robots(b) and B + "/entretien-en-ligne/" not in pm)
for pid in (4100, 4009):
    import json as _j
    c = _j.loads(get(f"{B}/wp-json/wp/v2/pages/{pid}?_fields=content")[2])["content"]["rendered"]
    check(f"page {pid} : aucun lien vers 3092/3288", "ia-hotels-tourisme-maroc-2026" not in c and "automatisation-entreprise-maroc" not in c)
print(f"\n{fails} échec(s)"); sys.exit(1 if fails else 0)
