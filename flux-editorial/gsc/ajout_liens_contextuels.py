#!/usr/bin/env python3
"""Ajout CIBLÉ d'un paragraphe de liens contextuels dans des pages sources indexées (aucune réécriture).
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
 ("posts", 3815, "<h2>Questions fréquentes</h2>", PLAIN(f"Vous préférez confier la mise en place à une équipe ? Notre page {a(P1,'agence IA immobilier au Maroc')} présente l'accompagnement proposé aux agences et aux promoteurs : périmètre, intégrations et déroulement d'un projet."), [P1]),
 ("pages", 3773, "</ul>\n<!-- /wp:list --></div>\n<!-- /wp:group -->", None, [P1, "/agent-ia-cabinet-dentaire-maroc/", "/agent-ia-pharmacie-maroc/", "/agent-ia-clinique-veterinaire-maroc/", "/agent-ia-institut-beaute-maroc/"]),
 ("pages", 4003, '<!-- wp:heading -->\n<h2 class="wp-block-heading">Questions fréquentes</h2>', BLOCK(f"Exemples par activité : la prise de rendez-vous dans un {a('/agent-ia-cabinet-dentaire-maroc/','cabinet dentaire')}, dans une {a('/agent-ia-clinique-veterinaire-maroc/','clinique vétérinaire')} ou dans un {a('/agent-ia-institut-beaute-maroc/','institut de beauté')}."), ["/agent-ia-cabinet-dentaire-maroc/", "/agent-ia-clinique-veterinaire-maroc/", "/agent-ia-institut-beaute-maroc/"]),
 ("pages", 3419, "<h2>Questions fréquentes sur le chatbot WhatsApp au Maroc</h2>", PLAIN(f"Deux usages détaillés à part : la {a('/confirmation-commande-cod-whatsapp-maroc/','confirmation des commandes COD par WhatsApp')} pour l'e-commerce, et l'accueil des demandes d'une {a('/agent-ia-pharmacie-maroc/','pharmacie')}."), ["/confirmation-commande-cod-whatsapp-maroc/", "/agent-ia-pharmacie-maroc/"]),
 ("posts", 3208, "<h2>Questions fréquentes</h2>", PLAIN(f"Pour aller plus loin sur les achats, notre guide sur le {a('/food-cost-restaurant-prix-achat/','calcul du food cost et le suivi des prix d’achat')} montre comment relier les factures fournisseurs à la fiche technique de chaque plat."), ["/food-cost-restaurant-prix-achat/"]),
 ("posts", 3293, "<h2>FAQ e-commerce IA</h2>", PLAIN(f"Deux étapes du paiement à la livraison sont détaillées à part : la {a('/confirmation-commande-cod-whatsapp-maroc/','confirmation des commandes COD par WhatsApp')} et le {a('/rapprochement-encaissements-cod/','rapprochement des encaissements COD')} avec les versements des sociétés de livraison."), ["/confirmation-commande-cod-whatsapp-maroc/", "/rapprochement-encaissements-cod/"]),
 ("pages", 4007, '<!-- wp:heading -->\n<h2 class="wp-block-heading">Questions fréquentes</h2>', BLOCK(f"Un cas fréquent est détaillé dans notre article {a('/suivi-relance-devis-sans-double-saisie/','relancer ses devis sans double saisie')} : suivre chaque devis envoyé et déclencher la relance au bon moment."), ["/suivi-relance-devis-sans-double-saisie/"]),
 ("posts", 4509, "<h2>Questions fréquentes</h2>", PLAIN(f"Les centres de formation partagent une partie de ces besoins (inscriptions, paiements échelonnés, échanges avec les stagiaires) : voir {a('/automatisation-centre-de-formation-maroc/','automatiser la gestion d’un centre de formation au Maroc')}."), ["/automatisation-centre-de-formation-maroc/"]),
 ("pages", 4000, '<!-- wp:heading -->\n<h2 class="wp-block-heading">Questions fréquentes</h2>', BLOCK(f"Exemple sectoriel : {a('/automatisation-centre-de-formation-maroc/','l’administratif d’un centre de formation')}. Avant de vous engager, notre méthode pour {a('/comparer-devis-automatisation-ia-maroc/','comparer deux devis d’automatisation IA')} aide à vérifier ce qui est réellement inclus."), ["/automatisation-centre-de-formation-maroc/", "/comparer-devis-automatisation-ia-maroc/"]),
]
AG = BLOCK(f"Par métier : {a(P1,'agent IA pour agences immobilières')}, {a('/agent-ia-cabinet-dentaire-maroc/','cabinets dentaires')}, {a('/agent-ia-pharmacie-maroc/','pharmacies')}, {a('/agent-ia-clinique-veterinaire-maroc/','cliniques vétérinaires')} et {a('/agent-ia-institut-beaute-maroc/','instituts de beauté')}.")
dry = "--dry-run" in sys.argv
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
cj = http.cookiejar.MozillaCookieJar(os.environ["WP_COOKIE_JAR"]); cj.load(ignore_discard=True, ignore_expires=True)
op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), urllib.request.HTTPCookieProcessor(cj))
H = {"X-WP-Nonce": os.environ["WP_NONCE"], "User-Agent": "flux-maintenance", "Content-Type": "application/json"}
def call(u, data=None):
    return json.loads(op.open(urllib.request.Request(u, data=json.dumps(data).encode() if data else None, headers=H, method="POST" if data else "GET"), timeout=90).read())
here = os.path.dirname(os.path.abspath(__file__)); os.makedirs(f"{here}/backup/maillage", exist_ok=True)
log, ok = [], True
for t, pid, anchor, ins, targets in OPS:
    if ins is None:  # agents-ia : paragraphe après la liste, dans le groupe
        ins_txt = "</ul>\n<!-- /wp:list -->\n\n" + AG.rstrip("\n") + "</div>\n<!-- /wp:group -->"
    d = call(f"{B}/wp-json/wp/v2/{t}/{pid}?context=edit&_fields=id,link,modified_gmt,content")
    raw, before = d["content"]["raw"], d["content"]["rendered"]
    n = raw.count(anchor)
    if n != 1: print(f"{pid} : ancre trouvée {n} fois, ARRÊT"); ok = False; continue
    if any(f'href="{L(x)}"' in raw for x in targets): print(f"{pid} : un lien cible existe déjà dans le brut, ARRÊT"); ok = False; continue
    new_raw = raw.replace(anchor, ins_txt) if ins is None else raw.replace(anchor, ins + anchor)
    if dry: print(f"[dry-run] {pid} {d['link'][27:]} : +{len(new_raw)-len(raw)} car. -> {targets}"); continue
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json.dump(d, open(f"{here}/backup/maillage/{t}-{pid}-{ts}.json", "w"), ensure_ascii=False)
    after = call(f"{B}/wp-json/wp/v2/{t}/{pid}?_fields=content", {"content": new_raw})["content"]["rendered"]
    sm = difflib.SequenceMatcher(None, before, after, autojunk=False)
    ops = [x for x in sm.get_opcodes() if x[0] != "equal"]
    only_insert = all(o[0] == "insert" for o in ops) and all(L(x) in after for x in targets)
    print(f"{pid} {d['link'][27:]} : écrit ; modifications du rendu = {[o[0] for o in ops]} ; uniquement ajout : {only_insert}")
    ok &= only_insert; log.append({"id": pid, "type": t, "lien": d["link"], "cibles": targets, "ajout_seul": only_insert, "sauvegarde": f"backup/maillage/{t}-{pid}-{ts}.json"})
if not dry: json.dump(log, open(f"{here}/resultats/maillage-ajouts.json", "w"), ensure_ascii=False, indent=1)
sys.exit(0 if ok else 1)
