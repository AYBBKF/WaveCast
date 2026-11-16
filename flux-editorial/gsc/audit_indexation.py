#!/usr/bin/env python3
"""Audit d'indexation reproductible de fluxintelligent.com (lecture seule).
Usage : python3 -I audit_indexation.py <dossier_sortie>
Produit audit.json et audit.csv : pour chaque URL des sitemaps + URL de contrôle,
statut HTTP, redirection, canonical (HTML + en-tête Link), meta robots, X-Robots-Tag,
verdict robots.txt pour Googlebot, présence dans le sitemap."""
import sys, json, csv, re, urllib.request, urllib.error, urllib.robotparser, ssl, os
from concurrent.futures import ThreadPoolExecutor
BASE = "https://fluxintelligent.com"
UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
out = sys.argv[1] if len(sys.argv) > 1 else "."
ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()

class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
opener = urllib.request.build_opener(NoRedir, urllib.request.HTTPSHandler(context=ctx))

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        r = opener.open(req, timeout=30); return r.status, {k.lower():v for k,v in r.headers.items()}, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, {k.lower():v for k,v in e.headers.items()}, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, {}, str(e)

def locs(xml): return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)

rp = urllib.robotparser.RobotFileParser(); rp.set_url(BASE + "/robots.txt")
rp.parse(get(BASE + "/robots.txt")[2].splitlines())

sitemap_urls, sm_meta = {}, []
st, h, idx = get(BASE + "/sitemap_index.xml")
for sm in locs(idx):
    s2, h2, x = get(sm)
    us = locs(x); sm_meta.append({"sitemap": sm, "status": s2, "n": len(us)})
    for u in us: sitemap_urls[u] = sm

extra = sys.argv[2:]  # URL de contrôle supplémentaires
def audit(url):
    chain, cur, status, headers, body = [], url, 0, {}, ""
    for _ in range(6):
        status, headers, body = get(cur)
        if status in (301, 302, 307, 308) and headers.get("location"):
            nxt = urllib.parse.urljoin(cur, headers["location"]); chain.append(f"{status}->{nxt}"); cur = nxt
        else: break
    head = body.split("</head>")[0] if "</head>" in body else body[:200000]
    canon = re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]*>', head, re.I)
    canon_href = [re.search(r'href=["\']([^"\']+)', c).group(1) for c in canon if re.search(r'href=["\']([^"\']+)', c)]
    mrob = re.findall(r'<meta[^>]+name=["\'](?:robots|googlebot)["\'][^>]*content=["\']([^"\']+)', head, re.I)
    link_canon = re.findall(r'<([^>]+)>;\s*rel="?canonical', headers.get("link", ""))
    final = cur
    return {"url": url, "in_sitemap": url in sitemap_urls, "sitemap": sitemap_urls.get(url, ""),
            "status_initial": (int(chain[0].split("->")[0]) if chain else status), "chain": chain,
            "final_url": final, "status_final": status,
            "robots_googlebot_allowed": rp.can_fetch("Googlebot", url),
            "x_robots_tag": headers.get("x-robots-tag", ""),
            "meta_robots": mrob, "canonical": canon_href, "canonical_count": len(canon_href),
            "link_header_canonical": link_canon,
            "self_canonical": (len(canon_href) == 1 and canon_href[0] == final),
            "noindex": any("noindex" in m.lower() for m in mrob) or "noindex" in (headers.get("x-robots-tag","") or "").lower()}

import urllib.parse
targets = list(sitemap_urls) + [u for u in extra if u not in sitemap_urls]
with ThreadPoolExecutor(8) as ex: rows = list(ex.map(audit, targets))
json.dump({"sitemaps": sm_meta, "rows": rows}, open(f"{out}/audit.json", "w"), ensure_ascii=False, indent=1)
with open(f"{out}/audit.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["url","in_sitemap","status_initial","chain","status_final","robots_ok","noindex","canonical","self_canonical","x_robots"])
    for r in rows: w.writerow([r["url"], r["in_sitemap"], r["status_initial"], " | ".join(r["chain"]), r["status_final"], r["robots_googlebot_allowed"], r["noindex"], " ; ".join(r["canonical"]), r["self_canonical"], r["x_robots_tag"]])
print(json.dumps(sm_meta, indent=1))
bad = [r for r in rows if not (r["status_initial"] == 200 and r["self_canonical"] and r["robots_googlebot_allowed"] and not r["noindex"])]
print(f"URL auditées: {len(rows)} ; anomalies: {len(bad)}")
for r in bad: print(r["url"], r["status_initial"], r["chain"][:2], "canon=", r["canonical"], "robots_ok=", r["robots_googlebot_allowed"], "noindex=", r["noindex"], r["meta_robots"])
