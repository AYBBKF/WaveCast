#!/usr/bin/env python3
"""(Copie du 18/11 pour la mission SEO organique.) Ajout CIBLÉ d'un paragraphe de liens contextuels dans des pages sources indexées (aucune réécriture).
Pour chaque opération : lecture du brut, sauvegarde, ancre exigée exactement 1 fois, insertion AVANT l'ancre,
renvoi du brut modifié, contrôle : le rendu après = rendu avant + uniquement le texte inséré.
Usage : WP_COOKIE_JAR=... WP_NONCE=... python3 -I ajout_liens_contextuels.py [--dry-run]"""
import os, sys, json, ssl, re, datetime, difflib, http.cookiejar, urllib.request
B = "https://fluxintelligent.com"; L = lambda p: B + p
def a(p, t): return f'<a href="{L(p)}">{t}</a>'
P1 = "/agence-ia-immobilier-maroc/"
BLOCK = lambda h: f"<!-- wp:paragraph -->\n<p>{h}</p>\n<!-- /wp:paragraph -->\n\n"
PLAIN = lambda h: f"<p>{h}</p>\n\n"
OPS = [
 ("posts", 4517, ["<h2>Questions fréquentes</h2>", '<h2 class="wp-block-heading">Questions fréquentes</h2>'], PLAIN(f"Vous gérez un riad ou un hôtel à Marrakech ou à Agadir ? Nos pages {a('/ia/automatisation-ia-marrakech/','automatisation IA à Marrakech')} et {a('/automatisation-ia-agadir/','automatisation IA à Agadir')} présentent les usages adaptés aux établissements touristiques de ces deux villes."), ["/ia/automatisation-ia-marrakech/", "/automatisation-ia-agadir/"]),
 ("posts", 3169, ["<h2>Conclusion</h2>", '<h2 class="wp-block-heading">Conclusion</h2>'], PLAIN(f"Tanger est l’un des principaux pôles industriels et logistiques du pays : notre page {a('/automatisation-ia-tanger/','automatisation IA à Tanger')} présente les usages pour les PME industrielles et les sous-traitants de la région."), ["/automatisation-ia-tanger/"]),
 ("posts", 3200, ["<h2>Le service correspondant</h2>", '<h2 class="wp-block-heading">Le service correspondant</h2>'], PLAIN(f"Pour un projet concret dans une entreprise casablancaise, notre page {a('/ia/automatisation-ia-casablanca/','agence IA Casablanca')} détaille les automatisations les plus demandées : leads, WhatsApp, CRM, relances et reporting."), ["/ia/automatisation-ia-casablanca/"]),
 ("posts", 3507, ["<h2>Questions fréquentes</h2>", '<h2 class="wp-block-heading">Questions fréquentes</h2>'], PLAIN(f"Quand le processus exige de comprendre des messages ou de préparer des réponses, un agent IA prend le relais d’un simple workflow : voir nos {a('/agents-ia/','agents IA pour les entreprises au Maroc')}."), ["/agents-ia/"]),
]
dry = "--dry-run" in sys.argv
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
cj = http.cookiejar.MozillaCookieJar(os.environ["WP_COOKIE_JAR"]); cj.load(ignore_discard=True, ignore_expires=True)
op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), urllib.request.HTTPCookieProcessor(cj))
H = {"X-WP-Nonce": os.environ["WP_NONCE"], "User-Agent": "flux-maintenance", "Content-Type": "application/json"}
def call(u, data=None):
    return json.loads(op.open(urllib.request.Request(u, data=json.dumps(data).encode() if data else None, headers=H, method="POST" if data else "GET"), timeout=90).read())
here = os.path.dirname(os.path.abspath(__file__)); os.makedirs(f"{here}/backup/maillage", exist_ok=True)
log, ok = [], True
for t, pid, anchors, ins, targets in OPS:
    d = call(f"{B}/wp-json/wp/v2/{t}/{pid}?context=edit&_fields=id,link,modified_gmt,content")
    raw, before = d["content"]["raw"], d["content"]["rendered"]
    anchor = next((x for x in anchors if raw.count(x) == 1), anchors[0])
    if "wp:paragraph" in raw and ins.startswith("<p>"): ins = BLOCK(ins[3:ins.rindex("</p>")])
    n = raw.count(anchor)
    if n != 1: print(f"{pid} : ancre trouvée {n} fois, ARRÊT"); ok = False; continue
    if any(f'href="{L(x)}"' in raw for x in targets): print(f"{pid} : un lien cible existe déjà dans le brut, ARRÊT"); ok = False; continue
    new_raw = raw.replace(anchor, ins + anchor)
    if dry: print(f"[dry-run] {pid} {d['link'][27:]} : +{len(new_raw)-len(raw)} car. -> {targets}"); continue
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json.dump(d, open(f"{here}/backup/maillage/{t}-{pid}-{ts}.json", "w"), ensure_ascii=False)
    after = call(f"{B}/wp-json/wp/v2/{t}/{pid}?_fields=content", {"content": new_raw})["content"]["rendered"]
    sm = difflib.SequenceMatcher(None, before, after, autojunk=False)
    ops = [x for x in sm.get_opcodes() if x[0] != "equal"]
    only_insert = all(o[0] == "insert" for o in ops) and all(L(x) in after for x in targets)
    print(f"{pid} {d['link'][27:]} : écrit ; modifications du rendu = {[o[0] for o in ops]} ; uniquement ajout : {only_insert}")
    ok &= only_insert; log.append({"id": pid, "type": t, "lien": d["link"], "cibles": targets, "ajout_seul": only_insert, "sauvegarde": f"backup/maillage/{t}-{pid}-{ts}.json"})
if not dry: json.dump(log, open(f"{here}/resultats/maillage-ajouts-seo-2026-11-18.json", "w"), ensure_ascii=False, indent=1)
sys.exit(0 if ok else 1)
