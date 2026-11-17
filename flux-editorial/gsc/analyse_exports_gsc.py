#!/usr/bin/env python3
"""Analyse les exports Search Console (CSV ou ZIP) URL par URL. Lecture seule.
Usage : python3 -I analyse_exports_gsc.py <export_doublons.(csv|zip)> <export_robots.(csv|zip)> [sortie.md]
Pour chaque URL : chaîne HTTP, destination finale, canonical, meta robots / X-Robots-Tag,
verdict robots.txt Googlebot, présence dans le sitemap public, date de dernière exploration Google.
Verdict : CORRIGEE | VOLONTAIRE | A_CORRIGER | A_EXAMINER | A_RECRAWLER (corrigée côté site mais explorée avant le correctif)."""
import sys, csv, io, re, zipfile, ssl, os, datetime, urllib.request, urllib.error, urllib.parse, urllib.robotparser
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
class NR(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NR, urllib.request.HTTPSHandler(context=ctx))
B = "https://fluxintelligent.com"; UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
CORRECTIF = datetime.date(2026, 11, 16)
def get(u):
    try: r = op.open(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30); return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e: return e.code, {k.lower(): v for k, v in e.headers.items()}, ""
    except Exception as e: return 0, {}, str(e)
def lire(path):
    if path.endswith(".zip"):
        z = zipfile.ZipFile(path); n = [x for x in z.namelist() if x.lower().endswith(".csv") and re.search(r"tab|table", x, re.I)] or [x for x in z.namelist() if x.endswith(".csv")]
        txt = z.read(n[0]).decode("utf-8-sig")
    else: txt = open(path, encoding="utf-8-sig").read()
    rows = list(csv.DictReader(io.StringIO(txt)))
    if not rows: return []
    ucol = next(k for k in rows[0] if re.search(r"url", k, re.I))
    dcol = next((k for k in rows[0] if re.search(r"explor|crawl", k, re.I)), None)
    return [(r[ucol].strip(), (r.get(dcol) or "").strip() if dcol else "") for r in rows if r[ucol].strip()]
rp = urllib.robotparser.RobotFileParser(); rp.parse(get(B + "/robots.txt")[2].splitlines())
sm = ""
for s in re.findall(r"<loc>([^<]+)</loc>", get(B + "/sitemap_index.xml")[2]): sm += get(s)[2]
def analyse(url, crawl, motif):
    chain, cur = [], url
    for _ in range(6):
        s, h, b = get(cur)
        if s in (301, 302, 307, 308) and h.get("location"): cur = urllib.parse.urljoin(cur, h["location"]); chain.append(f"{s}→{cur}")
        else: break
    head = b.split("</head>")[0]
    canon = re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', head)
    rob = " ".join(re.findall(r'<meta[^>]+name=["\'](?:robots|googlebot)["\'][^>]*content=["\']([^"\']+)', head)).lower() + " " + h.get("x-robots-tag", "").lower()
    allowed = rp.can_fetch("Googlebot", url); in_sm = f"<loc>{url}</loc>" in sm
    try: dc = datetime.datetime.strptime(crawl[:10], "%Y-%m-%d").date()
    except Exception: dc = None
    if motif == "robots":
        p = urllib.parse.urlparse(url).path
        if not allowed and p.startswith("/wp-admin/") and not p.startswith("/wp-admin/admin-ajax.php"): v = "VOLONTAIRE (zone admin bloquée)"
        elif allowed: v = "CORRIGEE (plus bloquée)" + (" , A_RECRAWLER" if dc and dc <= CORRECTIF else "")
        else: v = "A_CORRIGER (page publique bloquée)"
    else:
        if chain and s == 200 and not in_sm: v = "CORRIGEE (redirigée vers une page 200, hors sitemap)"
        elif s == 200 and canon == [cur] and cur != url: v = "CORRIGEE"
        elif s == 200 and "noindex" in rob and not in_sm: v = "VOLONTAIRE (noindex hors sitemap)"
        elif s == 200 and canon and canon[0] != url and not in_sm: v = "VOLONTAIRE (variante canonicalisée, hors sitemap)"
        elif s == 200 and canon == [url]: v = "A_EXAMINER (auto-canonique : comparer avec la canonique choisie par Google dans l'inspection)"
        elif s in (404, 410): v = "CORRIGEE (404/410, hors index)" if not in_sm else "A_CORRIGER (404 dans le sitemap)"
        else: v = "A_CORRIGER"
        if v.startswith("CORRIGEE") and dc and dc <= CORRECTIF: v += " , A_RECRAWLER"
    return f"| {url} | {crawl or '?'} | {' ; '.join(chain) or '-'} | {s} | {', '.join(canon) or '-'} | {rob.strip() or '-'} | {'oui' if allowed else 'non'} | {'oui' if in_sm else 'non'} | {v} |"
out = []
for path, motif, titre in [(sys.argv[1], "doublon", "Page en double : Google n'a pas choisi la même canonique"), (sys.argv[2], "robots", "Bloquée par robots.txt")]:
    urls = lire(path)
    out += [f"\n## {titre} ({len(urls)} URL)\n", "| URL | Dernière exploration | Redirections | Statut final | Canonical déclarée | Robots | robots.txt OK | Sitemap | Verdict |", "|---|---|---|---|---|---|---|---|---|"]
    out += [analyse(u, c, motif) for u, c in urls]
res = "\n".join(out); print(res)
if len(sys.argv) > 3: open(sys.argv[3], "w").write("# Analyse des exports GSC (" + datetime.date.today().isoformat() + ")\n" + res + "\n")
