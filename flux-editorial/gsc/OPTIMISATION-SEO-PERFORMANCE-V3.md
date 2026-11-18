# Optimisation SEO, performances et tracking V3 : fluxintelligent.com (18/11/2026)

Ce rapport fait suite à la V2 et ne refait aucun audit. Mesures et scripts : `perf/` (`scenarios.cjs`, `trace-sc.cjs`, `bench.sh`, `resultats-scenarios-2026-11-18.jsonl`).

## 1. Résumé exécutif

1. **Le suivi des leads Google n'existe pas aujourd'hui.**
   - GA4 a reçu 236 sessions « Paid Search » du 18/10 au 16/11.
   - Mais **aucun événement de lead** n'est mesuré : pas de `generate_lead`, pas de `form_submit`, pas de conversion Ads sur le site.
   - Le seul événement clé GA4 est `purchase`, sans rapport avec l'activité.
   - C'est l'écart le plus coûteux identifié : **les campagnes Google Ads ne peuvent pas être optimisées sur des leads.**
2. **Le cache HTML Cloudflare fonctionne déjà** pour les visiteurs. Le « BYPASS » de la V2 était un **artefact de mon environnement** : le proxy de sortie ajoute un en-tête `Authorization` (identifiant WordPress enregistré le 16/11) à toutes mes requêtes. Mesuré depuis un réseau extérieur : `MISS`, puis `HIT`, TTFB de 0,09 à 0,28 s en HIT. Les tests de sécurité sont conformes.
3. **Le doublon Google Ads est confirmé et documenté.** Aucune variante qui conserve la passerelle ne supprime le double chargement **tout en préservant les hits Ads**. Seule la désactivation de la passerelle (scénario C) réduit nettement le JavaScript (de 623 à 423 Ko) et le temps de blocage, avec Ads et GA4 préservés.
4. **Aucune modification de production dans cette mission.** Toutes les optimisations à effet touchent soit le tracking Ads ou Site Kit, soit une protection anti-spam : elles sont soumises à votre accord.

## 2. Causes techniques confirmées

| Cause | Preuve | Effet |
|---|---|---|
| Deux balises Google distinctes | `/0tqe/?id=GT-PZQ8SJ83` contient seulement `G-1JX1J3TWVZ` ; `/0tqe/` contient `AW-18347114778` et `GT-TBZQ6HJL` | deux conteneurs d'environ 530 à 570 Ko décompressés, inévitables tant que les balises ne sont pas regroupées côté Google |
| Conteneur Ads chargé deux fois | passerelle `/0tqe/` (et `/0tqe/e6SS…`), **et** `googletagmanager.com/gtag/js?id=AW-18347114778` (déclenché par `gtag('config','AW-…')` de Site Kit, paramètre `cx=c`) | environ 170 Ko de JS en double |
| Deux initialisations `gtag('js')` | `dataLayer` : `developer_id.dY2E1Nz` (Cloudflare) et `developer_id.dZTNiMT` (Site Kit) | sans double comptage : 1 `page_view` Ads et 1 `page_view` GA4 par page |
| La passerelle n'apporte pas de bénéfice first-party aux hits Ads actuels | état actuel : `page_view` Ads envoyé à `www.google.com/ccm/collect` et non à `/0tqe/…` | coût de la passerelle sans son bénéfice |
| Mode de consentement | Site Kit : refus par défaut **uniquement pour les pays de l'EEE, le Royaume-Uni et la Suisse** ; Maroc : accordé par défaut | conforme à la configuration choisie |
| Page contact lourde | **Cloudflare Turnstile** (anti-spam Forminator) : 1,5 Mo, plus 220 Ko | poids de 2,7 Mo ; sécurité, à conserver |
| LCP de la page Casablanca (3,6 s en laboratoire) | élément LCP = H1, délai de rendu de 2,9 s ; Google Fonts « Public Sans » chargé par le contenu de la page | à traiter éditorialement (police locale), hors tracking |
| Pixel OpenAI | `oaiq('init', {pixelId: …, debug: true})` en production | mode debug actif, à désactiver |

## 3. Architecture actuelle des balises Google

```
Cloudflare (périphérie, HTML navigateur) ── injecte : google_tags_first_party=AW-18347114778
                                                       <script src="/0tqe/">  (conteneur Ads, first-party)
                                                       gtag('js') + developer_id.dY2E1Nz
WordPress / Site Kit ── gtag/js?id=GT-PZQ8SJ83 (googletagmanager.com)  ->  GA4 G-1JX1J3TWVZ
                     ── gtag('config','GT-PZQ8SJ83') + gtag('config','AW-18347114778')
                                                       ->  recharge le conteneur Ads (googletagmanager.com)
                     ── mode de consentement (EEE refusé par défaut), événements de contenu
Site Kit Ads : conversionID AW-18347114778 ; suivi des conversions des extensions : activé, mais 0 événement détecté
                (Forminator et le module de devis ne sont pas pris en charge)
Autres : pixel OpenAI (lead_created, whatsapp_clicked, debug: true), Cloudflare Web Analytics,
         attribution maison « fdi » (UTM, gclid, gbraid, wbraid… stockés en localStorage)
```

## 4. Comparaison des scénarios

**Méthode :** simulation locale, sans rien changer en production. Le HTML reçu par le navigateur de test est modifié. Profil Pixel 5, CPU ralenti ×4, 3 passages par page, médiane (plage). Pages testées : accueil, `/automatisation-des-processus/` et `/ia/automatisation-ia-casablanca/`. Ads et GA4 = `page_view` envoyés sur 3 passages.

| Scénario | TBT (tâches longues), accueil / service / ville | LCP simulé (accueil) | JS transféré | Ads | GA4 | Conversions | Risque | Recommandation |
|---|---|---|---|---|---|---|---|---|
| **Actuel** | 922 (620–985) / 789 / 913 ms | 920 ms | 623 Ko | 3/3, vers google.com | 3/3 | aucune conversion de lead | doublon Ads | – |
| **A** : passerelle conservée, `config AW` retirée de Site Kit | 710 / 591 / 641 ms | 936 ms | 619 Ko | **0/3 : suivi Ads cassé** | 3/3 | – | **élevé** | **rejeté** |
| **A2** : passerelle conservée, `config AW` portée par la passerelle et retirée de Site Kit | 687 / 759 / 806 ms | 820 ms | 623 Ko | 3/3, **via `/0tqe/` (first-party)** | 3/3 | inchangées | moyen : dépend de la capacité réelle de la passerelle à porter la configuration (`setUpTag`, non vérifié) ; le conteneur Ads reste chargé depuis googletagmanager.com | possible si l'objectif est l'attribution first-party ; gain de performance faible |
| **A3** : passerelle conservée, balise GA4 également servie par `/0tqe/` | 940 / 977 ms | 872 ms | 445 Ko | 3/3, vers google.com | hits via `/0tqe/ga/g/c` | inchangées | moyen | non : blocage non réduit |
| **C** : passerelle désactivée | **600 / 491 / 674 ms** | 836 ms | **423 Ko** | 3/3, vers les domaines Google | 3/3 | inchangées | perte de la mesure first-party (aujourd'hui non effective pour les hits Ads) | **meilleur compromis performance et fiabilité** |

Le TBT reste une mesure de laboratoire et **ne vaut pas mesure de l'INP**. Aucune donnée terrain (CrUX) n'est accessible.

## 5. Impact sur les conversions et l'attribution

- **Aujourd'hui :** aucune conversion de lead Google n'est mesurée, dans aucun scénario.
- **Formulaire contact** (Forminator 3117 et Turnstile) : aucun événement Google à l'envoi. GA4 reçoit seulement `form_start` (mesure améliorée).
- **Devis IA** (`flux-intelligent-devis-ia/fdi.js`) : aucun appel `gtag` ou `dataLayer`. Il capte les UTM, `gclid`, `gbraid` et `wbraid` pour son propre usage.
- **WhatsApp et téléphone** (`tel:+212663002860`) : mesurés seulement par le pixel OpenAI (`whatsapp_clicked`). Côté GA4, ils n'apparaissent au mieux que dans l'événement `click` générique (45 en 30 jours).
- **Attribution :** `gclid` et les liens annexes sont gérés par Ads et GA4 (`linker` sur fluxintelligent.com). Rien n'est modifié par les scénarios testés.
- **Aucune fausse conversion créée.** Aucun envoi de formulaire réel n'a été fait.

**Proposition, soumise à accord :** ajouter des événements GA4 et Ads de lead.
- **Événements :**
  - `generate_lead` sur succès Forminator (`forminator:form:submit:success`) et sur validation du devis IA ;
  - `contact` sur les clics WhatsApp et téléphone.
- **Déploiement :** marquer ces événements comme événements clés dans GA4 et les importer dans Google Ads. Prévoir un **test dans l'aperçu Tag Assistant et DebugView**, sans compter de fausses conversions.

## 6. Cache HTML

- **Règle Cloudflare existante** « Cache HTML anonyme » (`4d2b3c2c…`) : GET uniquement, hors `/wp-admin`, `/wp-json`, `/wp-login` et `/ia/devis`, et hors cookies `wordpress_logged_in`, `wp-postpass` et `comment_author`. Mise en cache forcée 2 h.
- **Constat depuis un réseau extérieur :** l'accueil, `/automatisation-des-processus/` et `/ia/contact/` passent en `MISS` puis `HIT` (`Age: 1`). TTFB : 0,09 à 0,28 s en HIT, 0,4 à 0,65 s en MISS. L'alternance MISS/HIT vient de plusieurs centres Cloudflare.
- **Origine :** pas de `Set-Cookie`. `/ia/devis/` envoie `no-cache, no-store, private` et reste en `DYNAMIC`.
- **Génération WordPress sans cache :** environ 1,5 s (domaine technique Hostinger) ; pas de cache LiteSpeed visible.
- **Aucune modification nécessaire.** La V2 recommandait d'activer un cache HTML : ce cache existe et il est effectif. Le « BYPASS » mesuré venait de l'en-tête `Authorization` injecté par le proxy de cet environnement.

## 7. Tests de sécurité du cache (réseau extérieur, sans en-tête d'authentification)

| Test | Résultat |
|---|---|
| Deux sessions anonymes indépendantes, `/ia/contact/` | même HTML, aucune donnée personnelle, aucun `Set-Cookie` ; `forminator_nonce` identique, ce qui est normal (nonce WordPress commun aux visiteurs non connectés, valable 12 à 24 h, au-delà du cache de 2 h) |
| Cookie `wordpress_logged_in_*` | `DYNAMIC` : jamais servi depuis le cache |
| Cookie `comment_author_*` | `DYNAMIC` |
| `/wp-json/`, `/wp-admin/admin-ajax.php`, `/wp-login.php` | `DYNAMIC` |
| `/ia/devis/` | `DYNAMIC` (exclusion par la règle et `no-store` de l'origine) |
| POST sur `/ia/contact/` | `DYNAMIC` |
| Utilisateur authentifié réel | non testé : pas d'environnement de test isolé. Couvert par l'exclusion du cookie de session. |

**Conclusion :** aucun scénario de fuite d'une session à une autre n'a été observé dans le périmètre testé.

## 8. Mesures Lighthouse (mobile, 3 passages, médiane, 18/11)

Ces mesures sont faites depuis cet environnement, avec un HTML non mis en cache (artefact `Authorization`) : TTFB et LCP pessimistes. Elles servent de référence avant toute modification.

| Page | Score | LCP | TBT | Exécution JS | Poids |
|---|---|---|---|---|---|
| `/` (17/11) | 78 | 2 289 ms | 566 ms | 1 123 ms | 888 Ko |
| `/automatisation-des-processus/` | 82 | 2 226 ms | 548 ms | 1 092 ms | 797 Ko |
| `/ia/automatisation-ia-casablanca/` | 79 | 3 588 ms | 351 ms | 1 042 ms | 886 Ko |
| `/automatisation-ia-pme-maroc/` (17/11) | 77 | 2 511 ms | 642 ms | 1 173 ms | 804 Ko |
| `/ia/contact/` | 81 | 2 965 ms | 382 ms | 1 266 ms | 2 772 Ko (Turnstile) |
| `/ia/devis/` | 81 | 2 248 ms | 578 ms | 1 100 ms | 789 Ko |

**CLS : 0 partout.** Pas de mesure « après » : aucune modification n'a été appliquée.

## 9. Les 12 pages non indexées (inspection API du 18/11)

| Page | État | Dernière exploration |
|---|---|---|
| dentaire | Détectée, non indexée | – |
| pharmacie | Inconnue de Google (fluctue avec « détectée ») | – |
| vétérinaire | Détectée, non indexée | – |
| institut de beauté | Détectée, non indexée | – |
| confirmation COD | Inconnue de Google | – |
| food cost | Détectée, non indexée | – |
| centre de formation | Détectée, non indexée | – |
| suivi-relance-devis | Détectée, non indexée | – |
| comparer-devis | Détectée, non indexée | – |
| transport | Explorée, non indexée | 04/08 |
| coach | Explorée, non indexée | 06/09 |
| salon | Explorée, non indexée | 16/06 |

- **Lecture :** 9 pages attendent leur exploration (aucun problème technique), 3 ont été explorées mais non retenues, ce qui relève de l'éditorial.
- Liens ajoutés le 17/11 : toujours présents.
- Sitemaps : 0 erreur, 0 avertissement.
- Brouillons coach et salon : intacts. Contrôles programmés le 01/12 et le 22/12, conservés.

## 10. Modifications réellement appliquées

**Aucune en production.** Livrables ajoutés au dépôt :
- `perf/scenarios.cjs` (scénarios actuel, A, A2, A3, C) ;
- `perf/trace-sc.cjs` ;
- `perf/resultats-scenarios-2026-11-18.jsonl` ;
- ce rapport.

## 11. Risques et limites

- Les simulations modifient le HTML côté navigateur. Elles ne reproduisent pas exactement un changement de configuration Cloudflare ou Site Kit.
- Le scénario A2 dépend d'une capacité de la passerelle (porter la `config AW`) **non vérifiée** dans la documentation.
- **Mesures depuis cet environnement faussées par l'en-tête `Authorization` injecté** : HTML non mis en cache, TTFB plus élevé. Les comparaisons entre scénarios restent valables, car elles sont faites dans les mêmes conditions.
- Pas de CrUX, pas d'INP réel, pas de Tag Assistant, pas d'environnement de test isolé, pas d'accès à l'administration Google Ads.

## 12. Recommandation finale et décisions demandées

1. **Priorité commerciale : instrumenter les leads** (`generate_lead` : Forminator, devis IA ; `contact` : WhatsApp et téléphone), en événements clés GA4 importés dans Google Ads. Test dans l'aperçu Tag Assistant et DebugView. **Accord requis.**
2. **Performance : scénario C**, désactivation de la passerelle. Mesuré : JS de 623 à 423 Ko, TBT de −20 à −40 % selon la page, Ads et GA4 préservés.
   - **Alternative si vous tenez au first-party :** A2, à valider d'abord avec la configuration de la passerelle (sans gain notable de performance).
   - **Accord requis.**
3. **Sécurité et mesures :** supprimer les secrets `fluxintelligent.com` et `api.cloudflare.com` de l'environnement Default. Cela fiabilisera aussi les mesures de performance, l'en-tête `Authorization` injecté désactivant le cache.
4. **Petits correctifs, avec accord :**
   - passer le pixel OpenAI en `debug: false` ;
   - remplacer la police Google Fonts « Public Sans » de la page Casablanca par une police déjà auto-hébergée.
5. **Conserver tels quels :** le cache HTML Cloudflare (conforme et sûr), Turnstile, les polices auto-hébergées et la priorité donnée aux images LCP.

## 13. Plan de retour arrière (pour les opérations proposées)

| Opération | Retour arrière |
|---|---|
| Passerelle (C) | `PUT /zones/4b1d9d0347f9ee31f57447ccea74c9a2/settings/google-tag-gateway/config` avec `{"enabled": true, "endpoint": "/0tqe", "measurementId": "AW-18347114778", "setUpTag": false, "hideOriginalIp": true, "forwardClientIpHeaders": true}` (configuration lue le 17/11) |
| Événements de lead | désactivation du snippet (Code Snippets) ou de la balise, et retrait du statut d'événement clé dans GA4 |
| Site Kit Ads (A2) | remettre `conversionID` à `AW-18347114778` dans Site Kit > Ads |
| Pixel OpenAI, police | sauvegarde du snippet ou du contenu de la page avant modification, puis restauration |
