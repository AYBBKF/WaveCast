# État de clôture : fluxintelligent.com (16/11/2026, 22:40 UTC)

**Mission NON terminée.** Les corrections techniques sont déployées, mais aucune validation Google n'a été faite : les exports Search Console ne sont pas encore fournis.

## A. Corrections techniques déployées et vérifiées publiquement

| # | Correction | Modification réelle | Preuve publique après | Rollback |
|---|---|---|---|---|
| 1 | 4473 hors sitemap | Rank Math sitemap : `exclude_posts` passe de *(vide)* à `4473`. Autres réglages identiques (seule la représentation false/'' diffère). | `page-sitemap.xml` public : 39 URL, 0 `entretien-en-ligne` (40 avant) ; meta toujours `nofollow, noindex` | vider `exclude_posts` (sauvegarde : `backup/rankmath-sitemap-settings-avant.json`) |
| 2 | 301 factures vers 3569 | **Cause réelle** : le média 3568 (image mise en avant de 3569) portait le slug `automatisation-des-factures-par-ia-au-maroc`. Rank Math redirigeait cette page de pièce jointe vers l'accueil (`attachment_redirect_default`), avant la règle 17, qui était déjà correcte. Seul le slug du média a été modifié, en `…-image`. Fichier, URL de l'image et association à l'article inchangés. | `301 → /automatisation-factures-ia-maroc/` (avec et sans slash), 1 saut, puis 200 ; image de 3569 toujours en 200 | remettre le slug (sauvegarde : `backup/media-3568-avant.json`) |
| 3 | Liens des pages 4100 et 4009 | `remplacement_liens.py --apply`, 1 occurrence par page. Le diff du brut ne porte que sur l'URL (+32 et −4 caractères). JSON-LD (1/1) et blocs (53/53, 72/72) inchangés. | HTML public : 0 ancienne URL, nouvelles URL présentes, pages en 200 | `backup/page-4100-raw-*.json`, `backup/page-4009-raw-*.json` |
| – | Cache | Cache serveur Hostinger purgé (`hosting_cache_clear`). | – | – |
| (avant) | 3092 et 3288 hors sitemap | statut draft, 301 conservées | `post-sitemap.xml` public : 0 occurrence | republier |

**Aucune autre** page, réglage SEO, règle de redirection ou règle de sécurité n'a été modifiée. Les 21 règles Rank Math sont sauvegardées et inchangées (`backup/rankmath-redirections-avant.json`).

## B. Tests (preuves techniques, pas des preuves d'indexation)

- `valider_cloture.sh` : 7 OK sur 11. Les 4 échecs portent tous sur le cache Cloudflare des sitemaps. Fichier : `resultats/preuves-apres-cloture.txt`.
- `tests_indexation.py` : 67 OK sur 70. Les 3 échecs portent sur ce même cache. Fichier : `resultats/apres/tests-apres-corrections-2026-11-16.txt`.
- Surveillance 5xx : 20 requêtes, 0 erreur.

## C. Toujours bloqué

- **Cache Rule Cloudflare** : ni l'intégration Cloudflare ni Hostinger ne gèrent les Cache Rules de la zone. Règle à appliquer manuellement : `a-appliquer/cloudflare-regle-cache-sitemaps.md`.
- **Ancien mot de passe d'application** : à révoquer dans WordPress, et l'entrée `fluxintelligent.com` à supprimer des Network secrets de l'environnement Default.

## D. Validations Google encore nécessaires

- Exports CSV « Page en double… » et « Bloquée par robots.txt » : à analyser avec `analyse_exports_gsc.py` sur les URL réelles.
- Ensuite seulement : inspection d'URL, « Valider la correction », nouvelle soumission de `sitemap_index.xml`, puis attente de la nouvelle exploration par Google.
- Aucune des deux alertes n'est déclarée résolue.

## E. Contrôle après la règle Cloudflare annoncée (16/11, 22:48–23:00 UTC)

- **En-têtes** (`resultats/entetes-cloudflare-apres-regle.txt`) :
  - les 4 sitemaps passent de `MISS` à `HIT` avec `Age` de 2 à 4 s : Cloudflare les **met toujours en cache**, la règle de bypass **ne s'applique pas** ;
  - la page d'accueil reste en `BYPASS`, inchangée.
- **`valider_cloture.sh`** : 7 OK sur 11. Les 4 échecs portent sur le cache des sitemaps.
- **70 tests** : 67 OK sur 70. Les 3 échecs portent sur le cache des sitemaps.
- **Incident passager** : deux exécutions des tests ont été interrompues par des coupures de connexion, et deux réponses 502 ont été observées sur `/` et `/ia/blog/`. Elles coïncident avec une coupure du tunnel de sortie relevée par le proxy de l'environnement d'exécution. Le site est revenu en 200 juste après (12 requêtes vérifiées, moins de 1 s chacune). Une erreur passagère côté origine n'est pas exclue.

## F. Cloudflare via l'API (17/11)

- **Zone :** `fluxintelligent.com`, id `4b1d9d0347f9ee31f57447ccea74c9a2`, offre Free. Sauvegardes : `backup/cloudflare/`.
- **Constat :** le ruleset de cache de la zone (`d753763b19b54d0c9d43156ea2e7c92a`, phase `http_request_cache_settings`) a été modifié pour la dernière fois le **2026-09-06**. La règle « Sitemaps XML - bypass » **n'existe pas** dans cette zone.
- **Configuration observée :**
  - Workers Routes : aucune.
  - `cache_level` : aggressive.
  - `browser_cache_ttl` : 14400.
- **Cause racine, déduction non confirmée par lecture des règles :** une règle de ce ruleset, créée avant le 06/09, rend les XML éligibles au cache. Elle est lue par les en-têtes : XML en MISS puis HIT, alors que Cloudflare ne met pas en cache les .xml par défaut.
- **Bloqué :** le jeton API ne peut ni lire ni modifier les Cache Rules (« request is not authorized »), ni lire les Page Rules (code 9109).
- **Permissions manquantes :**
  - Zone > Cache Rules : Edit ;
  - Zone > Page Rules : Read ;
  - Zone > Cache Purge : Purge.
- **Aucune modification Cloudflare effectuée, aucune purge.**

## G. Correction Cloudflare appliquée (17/11, 11:14 UTC)

- **Cause racine confirmée :** la Cache Rule existante « Cache HTML anonyme » (`4d2b3c2cd0b944f28b45faa9e42fc8cc`, ruleset `d753763b19b54d0c9d43156ea2e7c92a`) met en cache toutes les requêtes GET anonymes, avec un TTL de périphérie forcé à 7 200 s (`override_origin`). Les sitemaps y sont inclus. Il n'y a ni Page Rule, ni Workers Route.
- **Modification :** ajout d'une seule règle, **`87a66295df1c4106845b0b0506c1cda0`** « Sitemaps XML - bypass », en dernière position (ruleset passé de la version 1 à la version 2) :
  - expression : `(http.host eq "fluxintelligent.com" and http.request.uri.path in {"/sitemap_index.xml" "/post-sitemap.xml" "/page-sitemap.xml" "/category-sitemap.xml"})` ;
  - action : `set_cache_settings`, `cache: false`.

  La règle « Cache HTML anonyme » n'a pas été modifiée.
- **Purge :** uniquement les 4 URL de sitemap, deux fois. La seconde purge a été faite après la propagation de la règle : un serveur Cloudflare avait remis `category-sitemap.xml` en cache pendant celle-ci.
- **Preuves** (`backup/cloudflare/`) :
  - `entetes-avant.txt` : sitemaps en EXPIRED puis HIT, avec un `Age` allant jusqu'à 1 346 s ;
  - `entetes-apres-propagation.txt` : les 4 sitemaps en `DYNAMIC` sur 3 requêtes, en HTTP 200, sans `Age` ; page d'accueil toujours en `BYPASS`.
- **Contenu des sitemaps :** XML valide. `post-sitemap.xml` contient 56 URL (un article programmé a été publié le 17/11 à 09:00 Maroc), `page-sitemap.xml` 39. Aucune occurrence de 3092, 3288 ni 4473.
- **`valider_cloture.sh` :** 11 OK sur 11.
- **70 tests :** 70 OK sur 70. Fichier : `resultats/apres/tests-apres-bypass-cloudflare.txt`.
- **Rollback :** `DELETE /zones/4b1d9d0347f9ee31f57447ccea74c9a2/rulesets/d753763b19b54d0c9d43156ea2e7c92a/rules/87a66295df1c4106845b0b0506c1cda0`. Configuration initiale : `backup/cloudflare/cache-ruleset-d753-avant.json`.
- **Ce sont des preuves techniques**, pas une validation Google. Les deux alertes Search Console restent à vérifier sur les exports réels.
- **Sécurité :** révoquer les deux jetons API Cloudflare et supprimer l'entrée `api.cloudflare.com` des Network secrets de l'environnement Default.

## H. Search Console : prise en charge (17/11, 11:20 UTC)

### Accès

| Accès | Résultat |
|---|---|
| Composio (compte Google relié) | propriété `fluxintelligent.com` absente : 404 en préfixe d'URL comme en domaine |
| **Site Kit**, sur le site | **connecté** à `https://fluxintelligent.com/` (permission `siteOwner`, propriétaire du module : l'admin WP n° 1). Seule donnée exposée : `searchanalytics`. Pas d'inspection d'URL, pas de sitemaps. |
| Rank Math Analytics | non connecté à Google (`isConsoleConnected` vaut false) |
| Navigateur authentifié | aucun disponible dans la session |
| **Limite de l'API Google** | l'API Search Console ne fournit **ni** l'export des rapports « Pages / motif d'exclusion », **ni** le bouton « Valider la correction ». Seules l'inspection d'URL et la soumission de sitemaps sont possibles par API, avec un compte ayant accès à la propriété. |

### Données Google réelles exploitées : URL avec impressions sur 90 jours (via Site Kit)

- **91 URL** avec impressions entre le 17/08 et le 15/11 (`resultats/gsc-searchanalytics-pages-90j.json`).
- **27** ne font pas partie des URL canoniques en 200 du sitemap. Elles ont été analysées avec `analyse_exports_gsc.py` (`resultats/analyse-gsc-searchanalytics-hors-sitemap.md`).

| Verdict | Nb | URL |
|---|---|---|
| Corrigée : 301 vers une page 200, hors sitemap | 20 | anciennes URL et variantes `/ia/` ou racine, dont 3288, 3092 et la redirection factures |
| Légitime : 404, page supprimée | 2 | `/agent-ia-maroc-pme/`, `/automatisation-ia-cliniques/` (aucun équivalent certain : pas de redirection forcée) |
| Légitime : noindex hors sitemap | 1 | `/domain-name-maroc/` |
| Légitime : 301 externe volontaire (PayPal) | 1 | `/crm-intelligent-pret-a-lemploi/` |
| Légitime : pagination auto-canonique | 2 | `/ia/blog/page/2/`, `/category/agents-ia-blog/page/2/`. Candidats plausibles au motif « Google a choisi une autre canonique », à confirmer par inspection. |
| **Anomalie corrigée** | 1 | `/🏨-comment-lia-transforme-les-hotels-et-le-tourisme-en-2026/` (voir ci-dessous) |

**Ces URL ne sont pas les listes des deux alertes.** Ces listes ne sont disponibles que dans l'interface Search Console.

### Correction complémentaire

- **Problème :** l'ancien slug à emoji de 3288 (5 impressions) passait par la redirection automatique d'ancien slug de WordPress vers `/?p=3288`, qui renvoie 404 depuis que 3288 est en brouillon.
- **Correction :** ajout de la **règle Rank Math 22**, en correspondance exacte, 301 vers `/automatisation-ia-hotel-fiabilite-technique-experience-client/` (3828).
  - Sauvegarde : `backup/rankmath-redirections-avant-17-11.json`.
  - Rollback : supprimer la règle 22.
- **Vérification à l'origine :** 301 Rank Math vers 3828, vérifiée avec un paramètre anti-cache.
- **Public :** l'ancienne redirection reste en cache Cloudflare (`HIT`). La purge par URL ne correspond pas à la clé de cache de cette URL encodée. Expiration naturelle au plus tard 2 h après la mise en cache (TTL de la règle « Cache HTML anonyme »). Recontrôle programmé le 17/11 vers 13:32 UTC.
- **Tests après cette correction :** 70 sur 70 et 11 sur 11.

### Demandes de validation Google

- **Aucune envoyée.** Pas d'accès API à la propriété, et le bouton « Valider la correction » n'existe que dans l'interface.

### Sécurité des accès temporaires

| Accès | État | Action |
|---|---|---|
| Sessions WordPress temporaires (autologin Hostinger) | fichiers de session supprimés après chaque intervention | aucune |
| Mots de passe d'application WordPress | 3 existants, créés en mai et juin 2026, **aucun créé le 16/11**. Celui saisi le 16/11 n'a jamais fonctionné (en-tête supprimé par le serveur). | non révoqués : ce sont des accès permanents possibles. Supprimer l'entrée `fluxintelligent.com` des Network secrets de l'environnement Default. |
| Jeton Cloudflare actuel (id `5a893482c1951519968c61b0a104972b`, sans expiration) | sans permission « API Tokens » : je ne peux pas le révoquer | à révoquer dans Cloudflare, Profil > Jetons API, après le recontrôle de 13:32 UTC |
| Premier jeton Cloudflare (droits larges) | remplacé dans l'environnement, toujours actif côté Cloudflare | à révoquer dans Cloudflare |
| Secrets de l'environnement Default | `fluxintelligent.com` et `api.cloudflare.com` | à supprimer : aucun outil ne me permet de le faire |

## I. Point du 17/11, 11:30 UTC

- **Navigateur authentifié :** aucun disponible.
  - Pas d'outil navigateur dans la session.
  - Les dossiers de l'ordinateur « AYOUBBKF » ne sont pas proposés aux sessions cloud.
- **Données des alertes :** les impressions Site Kit ne sont **pas** utilisées comme substitut. Exports CSV attendus dans `gsc-exports/`.
- **URL à emoji :** toujours servie depuis le cache Cloudflare (`HIT`, `Age` 479 s, ancienne cible `/?p=3288`, donc 404). L'origine est correcte : 301 Rank Math vers 3828. Expiration prévue vers 13:23 UTC, recontrôle programmé à 13:32 UTC. **Non encore conforme publiquement.**
- **Jetons Cloudflare :** révocation impossible avec les droits du jeton actuel (pas de permission « API Tokens »). Révocation à faire par l'utilisateur.

## J. Vérification Composio / Google Search Console (17/11, 11:34 UTC)

- **Connexion Composio GSC :** active (`google_search_console_belter-stan`).
- **Compte Google authentifié** (lu par l'API userinfo) : `salesandshop22@gmail.com` (« BW Startup »).
- **Outils GSC disponibles :** LIST_SITES, GET_SITE, SEARCH_ANALYTICS_QUERY, INSPECT_URL, LIST_SITEMAPS, GET_SITEMAP, SUBMIT_SITEMAP, ADD_SITE.
- **Propriétés accessibles :** 11, sans `fluxintelligent.com`. `GET_SITE` renvoie 404 « not a verified Search Console site in this account » pour `https://fluxintelligent.com/` comme pour `sc-domain:fluxintelligent.com`.
- **Propriétaire actuel de la propriété** `https://fluxintelligent.com/` : le compte Google relié à Site Kit sur le site, différent du compte Composio.
- **Autorisation manquante :** ajouter `salesandshop22@gmail.com` comme utilisateur **Complet** (ou Propriétaire) de la propriété `https://fluxintelligent.com/`.
- **Limite de l'API, même avec cet accès :** aucun point d'accès pour exporter les listes du rapport « Pages » (motifs d'exclusion), ni pour « Valider la correction ». L'inspection d'URL, les statistiques et les sitemaps sont possibles.

## K. Search Console via Composio : accès obtenu et inspections (17/11, 11:40–11:50 UTC)

- **Accès :** nouveau compte Composio `google_search_console_camera-harper` (alias `fluxintelligent-owner`), permission **`siteOwner`** sur `https://fluxintelligent.com/`.
- **Inspection d'URL (API) : 126 URL**, soit les 98 du sitemap public et 28 URL hors sitemap connues de Google (27 issues des impressions sur 90 jours, plus 4473). Aucune erreur API.

### Motif « Page en double : Google n'a pas choisi la même URL canonique que l'utilisateur » : 2 URL confirmées par Google

| URL | Dernière exploration Google | Canonique déclarée à ce moment | Canonique choisie par Google | État actuel du site | Statut |
|---|---|---|---|---|---|
| `/ia-hotels-tourisme-maroc-2026/` (3288) | 2026-10-23 | elle-même | `/automatisation-ia-hotel-fiabilite-technique-experience-client/` (3828) | 301 Rank Math en 1 saut vers 3828, puis 200 ; retirée du sitemap | **corrigée, en attente de nouvelle exploration** |
| `/🏨-comment-lia-transforme-les-hotels-et-le-tourisme-en-2026/` (ancien slug de 3288) | 2026-08-23 | elle-même | 3828 | origine : 301 Rank Math (règle 22) vers 3828. **Public : encore servie depuis le cache Cloudflare** (ancienne cible `/?p=3288`, donc 404), expiration vers 13:23 UTC | corrigée à l'origine, **vérification publique en attente** (recontrôle à 13:32 UTC) |

- **Sur les 98 URL du sitemap : 0 conflit de canonique.**

### Motif « Bloquée par le fichier robots.txt »

- **0 URL bloquée** parmi les 126 inspectées. Toutes sont `ALLOWED` ou inconnues de Google.
- **Limite de l'API :** elle ne liste pas les URL d'un motif du rapport « Pages ». Les URL concernées ne sont donc pas connues avec certitude. Le seul blocage du robots.txt pour Googlebot porte sur `/wp-admin/` (sauf `admin-ajax.php`), volontaire.
- **Aucune correction à faire et aucune validation à demander** tant que la liste du rapport ne montre pas d'URL publique.

### Autres états relevés (hors périmètre des deux alertes, aucune anomalie technique)

| État | Nb | Détail |
|---|---|---|
| Envoyée et indexée | 84 sur 98 | |
| Détectée, actuellement non indexée | 9 | surtout des contenus récents (programmés en novembre) |
| Explorée, actuellement non indexée | 3 | `/automatisation-ia-agence-transport/`, `/ia-salon-coiffure-automatisation/`, `/workflow-ia-coach-musculation-maroc-2025/` |
| Inconnue de Google | 2 | `/rapprochement-encaissements-cod/` (publiée le 17/11), `/agent-ia-institut-beaute-maroc/` |

- **Hors sitemap, toujours indexées chez Google** mais redirigées aujourd'hui en 301, en attente de nouvelle exploration :
  - `/chatbots-` ;
  - `/qualification-scoring-leads-ia/` ;
  - `/💼-lavenir-des-jobs-au-maroc-…/`.
- **Exclusions légitimes confirmées par Google :**
  - 404 : `/agent-ia-maroc-pme/`, `/automatisation-ia-cliniques/` ;
  - noindex : `/domain-name-maroc/` ;
  - redirection externe : `/crm-intelligent-pret-a-lemploi/` ;
  - 4473 inconnue de Google et hors sitemap.

### Sitemap

- **Avant :** `sitemap_index.xml` téléchargé par Google le 2026-11-14 (avant nettoyage), 98 URL web soumises, 0 erreur, 1 avertissement.
- **Action :** **nouvelle soumission le 17/11, acceptée par l'API.**

### Validations Google

- « Valider la correction » n'existe que dans l'interface : l'API ne l'expose pas.
- **Motif « Page en double » :** à lancer dans Search Console **après** le recontrôle public de l'URL à emoji (13:32 UTC). Les 2 URL confirmées seront alors corrigées. Une demande de validation n'est pas une indexation confirmée.
- **Motif « Bloquée par robots.txt » :** ne pas valider si le rapport ne contient que des URL `/wp-admin/` (exclusion volontaire).

## L. Clôture : vérifications du 17/11 (11:52–12:00 UTC)

### 1-2. Anciennes URL de 3288 (public et Google)

| URL | Réponse publique (navigateur et Googlebot) | Google : couverture / canonique choisie / dernière exploration |
|---|---|---|
| `/ia-hotels-tourisme-maroc-2026/` | **301 Rank Math vers 3828, 1 saut, 200** | Page en double / 3828 / 2026-10-23 |
| `/🏨-comment-lia-transforme-…-2026/` | **NON CONFORME** : cache Cloudflare `HIT` (`Age` 1 832 s), ancienne cible `/?p=3288`, donc 404. L'origine est conforme (règle 22 vers 3828). | Page en double / 3828 / 2026-08-23 |

- **Canonique choisie par Google pour les deux URL :** 3828. Google ne les a pas réexplorées depuis les corrections.
- **Liste non exhaustive :** ces 2 URL sont les cas « Page en double » **confirmés par inspection** parmi les 126 URL inspectées. L'API ne fournit pas le rapport complet de ce motif.

### 4. Pages non indexées : 14, classées par priorité

Toutes sont en 200, indexables, auto-canoniques et présentes dans le sitemap (70 tests). **Aucune n'est une exclusion légitime. Aucune n'a été forcée.**

| Priorité | Page | Publiée | Mots | État Google | Lecture |
|---|---|---|---|---|---|
| P1 | `/agence-ia-immobilier-maroc/` (page commerciale) | 04/11 | 1 607 | Détectée, non explorée | file d'exploration normale. Demande d'indexation possible uniquement dans l'interface. |
| P2 | `/confirmation-commande-cod-whatsapp-maroc/`, `/food-cost-restaurant-prix-achat/`, `/automatisation-centre-de-formation-maroc/`, `/suivi-relance-devis-sans-double-saisie/`, `/comparer-devis-automatisation-ia-maroc/` | 02–08/11 | 1 515 à 2 572 | Détectées | contenus de moins de 3 semaines : délai normal |
| P2 | `/rapprochement-encaissements-cod/` | 17/11 | – | Inconnue | publiée aujourd'hui |
| P2 | `/agent-ia-cabinet-dentaire-maroc/`, `/agent-ia-pharmacie-maroc/`, `/agent-ia-clinique-veterinaire-maroc/` | 12–14/08 | 1 906 à 2 179 | Détectées, jamais explorées en 3 mois | signal de priorité d'exploration faible, probablement le maillage interne : à renforcer éditorialement |
| P2 | `/agent-ia-institut-beaute-maroc/` | 18/08 | 2 094 | Inconnue | même diagnostic |
| P3 | `/automatisation-ia-agence-transport/` | 2025 | 2 369 | Explorée, non indexée (04/08) | enrichie le 03/11 : à réévaluer après nouvelle exploration |
| P3 | `/workflow-ia-coach-musculation-maroc-2025/` | 2025 | 903 | Explorée, non indexée (06/09) | qualité ou intérêt jugés insuffisants par Google |
| P3 | `/ia-salon-coiffure-automatisation/` | 04/2026 | 418 | Explorée, non indexée (16/06) | contenu mince. L'enrichissement est rédigé mais non appliqué (règle Surfer 80–90, quota épuisé). |

### 5. Sitemap

- `sitemap_index.xml` soumis le 2026-11-17 à 11:45:23 UTC et **téléchargé par Google à 11:45:24 UTC**.
- 0 erreur, 0 avertissement (1 avant), 98 URL web.

### 6. robots.txt

- **0 URL publique bloquée** parmi les 126 inspectées.
- Le seul blocage pour Googlebot est `/wp-admin/` (sauf `admin-ajax.php`) : **exclusion intentionnelle, conservée**.
- La liste exacte du motif n'est pas fournie par l'API.

### 7. Validations manuelles

- **« Page en double… » :** à lancer **une seule fois, après** confirmation publique de l'URL à emoji (cache Cloudflare attendu à expiration vers 13:23 UTC, recontrôle programmé à 13:32 UTC).
- **« Bloquée par robots.txt » :** **ne pas valider** si le rapport ne contient que des URL `/wp-admin/`.
- **Pages « Détectée / Explorée, non indexée » :** pas de validation. Option : « Demander une indexation » pour la seule page P1, dans l'interface.

### Restent ouverts

1. URL à emoji : vérification publique après expiration du cache.
2. Validation « Page en double », dans l'interface, après le point 1.
3. Nouvelle exploration par Google des 2 URL corrigées et des 14 pages non indexées.
4. Révocation des 2 jetons Cloudflare et suppression des secrets de l'environnement Default (action utilisateur).

## M. Correction finale de l'URL à emoji et contrôle Google (17/11, 11:55–12:05 UTC)

### Cause et correction

- **Origine :** déjà conforme (règle Rank Math 22), 301 vers 3828.
- **Cloudflare :** la purge par URL fonctionne sur la zone (test sur `robots.txt` : `HIT`, `Age` 4 286 s, devenu `BYPASS`). Pour l'URL à emoji, elle **reste sans effet** malgré trois formes d'encodage (`%F0%9F%8F%A8`, `%f0%9f%8f%a8`, UTF-8 brut), avec la normalisation d'URL `cloudflare` sur les requêtes entrantes. La clé de cache stockée pour ce chemin ne correspond pas à l'URL purgée. Cause exacte non exposée par l'API (offre Free, sans Custom Cache Key).
- **Correction :** Cache Rule **`f5886706fe2e4cbd84acdf46b177eb6b`** « Ancienne URL emoji 3288 - bypass », ajoutée en dernière position (ruleset `d753…` passé de la version 2 à la version 3).
  - Expression : `(http.host eq "fluxintelligent.com" and ends_with(http.request.uri.path, "-comment-lia-transforme-les-hotels-et-le-tourisme-en-2026/"))`.
  - Action : `cache: false`.
  - Effet limité à cette seule URL. La règle globale « Cache HTML anonyme » n'est pas modifiée.
  - Sauvegarde : `backup/cloudflare/cache-ruleset-d753-v2-avant-regle-emoji.json`.
  - Rollback : `DELETE …/rulesets/d753763b19b54d0c9d43156ea2e7c92a/rules/f5886706fe2e4cbd84acdf46b177eb6b`.

### Preuves publiques

- **URL à emoji :** 4 requêtes GET avec l'user-agent Googlebot, toutes en `DYNAMIC`, `Location` vers `/automatisation-ia-hotel-fiabilite-technique-experience-client/`, `X-Redirect-By: Rank Math`. Résolution finale : **200 en 1 saut**.
- **Autres URL, sans régression :**

  | URL | Réponse |
  |---|---|
  | `/` | BYPASS, 200 |
  | 3828 | BYPASS, 200 |
  | `/post-sitemap.xml` | DYNAMIC, 200 |
  | `/robots.txt` | BYPASS, 200 (vidé par la purge de test) |

- Recontrôle programmé de 13:32 UTC annulé, devenu inutile.

### Google (inspection API)

| URL | Couverture | Canonique déclarée lors de l'exploration | Canonique choisie par Google | Dernière exploration |
|---|---|---|---|---|
| `/ia-hotels-tourisme-maroc-2026/` | Page en double | elle-même | 3828 | 2026-10-23 |
| `/🏨-comment-lia-transforme-…-2026/` | Page en double | elle-même | 3828 | 2026-08-23 |
| 3828 `/automatisation-ia-hotel-fiabilite-technique-experience-client/` | **Envoyée et indexée**, verdict PASS, autorisée par robots.txt | elle-même | elle-même | 2026-11-08 |

- **Lecture :** Google avait déjà regroupé ces deux URL sur 3828. Elles redirigent maintenant en 301 vers 3828. À la prochaine exploration, elles devraient passer en « Page avec redirection », une exclusion normale.
- **Ces 2 URL ne sont pas la liste exhaustive du motif.** L'API ne fournit pas le rapport complet.

### Pages non indexées

- Liste séparée : `PAGES-NON-INDEXEES.md` (14 pages, priorités P1 à P3).
- Aucune modification ni publication.
