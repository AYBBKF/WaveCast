# Rapport indexation Google Search Console : fluxintelligent.com (16/11/2026)

## 1. Résumé

**Accès Search Console : aucun.**
- Composio liste 11 propriétés GSC, mais pas fluxintelligent.com.
- La Search Console n'est pas connectée à Surfer (workspace 1403832).
- L'essai Frase a expiré.
- Le connecteur Hostinger demande une nouvelle authentification, ce qui coupe l'accès wp-admin, Rank Math et la purge du cache.

**Conséquences pour ce rapport :**
- Les URL citées dans les deux alertes du 16/11 n'ont pas pu être lues.
- Aucune inspection d'URL ni demande de validation n'a été faite.
- Tout ce qui suit vient de l'audit public et serveur.
- Aucune URL n'est déclarée « exclue par Google » faute de preuve.

| Indicateur | Valeur |
|---|---|
| URL auditées (sitemaps + contrôles) | 100 URL de sitemap + 16 URL de contrôle + 45 URL héritées ou variantes |
| URL de sitemap en 200, indexables et auto-canoniques | 97 sur 100 avant, 97 sur 98 après (lecture sans cache) |
| Anomalies confirmées | 6 |
| Corrigées et vérifiées | 2 (articles 3092 et 3288 retirés du sitemap, 301 conservée) |
| Corrections tentées sans effet | 1 (page 4473 : meta Rank Math non exposée par l'API) |
| Restantes, avec action requise | 4 (voir section 5) |
| Problème robots.txt bloquant une page publique | aucun constaté |
| Canonical modifié par JavaScript | aucun (98 pages rendues avec Chromium) |

## 2. Diagnostic

### Alerte 1 : « Page en double, Google n'a pas choisi la même URL canonique que l'utilisateur »

**Faits vérifiés.**
- Les 97 URL indexables du sitemap ont un canonical unique et auto-référent, identique en HTML brut et après rendu JavaScript.
- Elles n'ont pas d'en-tête `Link: rel=canonical` concurrent.
- Les variantes renvoient en 301 vers https non-www :
  - http et www ;
  - `index.php` ;
  - URL sans slash final ;
  - `?p=` et `?page_id=` ;
  - attachment.
- Les paramètres (`?utm_…`) ont un canonical qui pointe vers l'URL propre.
- La pagination `/ia/blog/page/2/` est auto-canonique.
- Les tags, auteurs et la recherche sont en noindex ou en 404.

**Causes racines confirmées, compatibles avec l'alerte :**
1. **3288 `/ia-hotels-tourisme-maroc-2026/`** était publié en 200 avec un canonical auto-référent jusqu'au 04/11.
   - Son contenu a été fusionné dans 3828 le 03/11, ce qui le rendait quasi dupliqué de 3828.
   - Depuis le 04/11, il redirige en 301, mais il était encore publié et listé dans post-sitemap.xml.
2. **3092 `/automatisation-entreprise-maroc/`**, cible de redirection vers `/automatisation-ia-pme-maroc/`, présente la même situation : sujet identique, encore publié et listé dans le sitemap.

**Hypothèses non prouvées, à confirmer dans GSC :**
- Pages proches par l'intention :
  - les deux pages immobilier (`/agence-ia-immobilier-maroc/` et `/ia-pour-immobilier-au-maroc-…/`) ;
  - `/chatbot-ia-whatsapp-maroc/` et `/chatbots-experience-client/chatbot-whatsapp-maroc/` ;
  - `/marketing-digital-maroc/` et `/crm-ventes-marketing-ia/agence-de-marketing-digital/` ;
  - `/ia-entreprises-casablanca/` et `/ia/automatisation-ia-casablanca/`.
- La similarité textuelle mesurée reste faible : Jaccard ≤ 0,34 en shingles de 5 mots, ≤ 0,16 entre pages villes après neutralisation du nom de ville.
- Ce ne sont donc pas des doublons de contenu au sens strict. Aucune action n'a été prise : interdiction de canonicaliser ou rediriger sans preuve.

### Alerte 2 : « Bloquée par le fichier robots.txt »

**Source du robots.txt :** fichier virtuel généré par WordPress, ce que montre l'en-tête `link: wp-json`. Ce n'est ni un fichier physique, ni Cloudflare.

**Pour Googlebot (`User-agent: *`) :** seul `/wp-admin/` est interdit, `admin-ajax.php` restant autorisé. Restent aussi autorisés :
- les pages ;
- `/wp-content/` et `/wp-includes/` (CSS, JS, images) ;
- les sitemaps.

**Fait vérifié :** aucune des 98 pages publiques ne contient de lien vers `/wp-admin/`, hormis `admin-ajax.php`, qui est autorisé.

**Conclusion probable :** les URL signalées sont des URL `/wp-admin/…` découvertes par Google, par exemple `/wp-admin/` qui redirige en 302 vers `wp-login.php`. Ce blocage est **volontaire et correct**, il n'y a rien à corriger. Deux limites :
- impossible de le confirmer sans la liste de GSC ;
- impossible de vérifier un ancien robots.txt plus restrictif, car la Wayback Machine est bloquée par la politique réseau de cet environnement.

**Robots exclus volontairement, conservés :** `Google-Extended`, `GPTBot`, `ClaudeBot`, etc. `Google-Extended` n'affecte pas l'indexation Google Search.

## 3. Corrections

| URL | Problème | Cause racine | Modification | Test après correction | Statut |
|---|---|---|---|---|---|
| /ia-hotels-tourisme-maroc-2026/ (3288) | URL redirigée en 301 mais publiée et listée dans post-sitemap.xml ; quasi-doublon de 3828 | article fusionné laissé publié | statut publish → draft (règle 301 Rank Math inchangée) | 301 en 1 saut vers 3828, puis 200 ; absent du sitemap lu sans cache | corrigé, vérifié |
| /automatisation-entreprise-maroc/ (3092) | idem, vers /automatisation-ia-pme-maroc/ | article remplacé laissé publié | statut publish → draft (301 inchangée) | 301 en 1 saut, puis 200 ; absent du sitemap lu sans cache | corrigé, vérifié |
| /entretien-en-ligne/ (page 4473) | noindex, nofollow mais listée dans page-sitemap.xml | noindex posé hors du réglage Rank Math de la page, probablement par l'extension d'entretien `[flux_entretien]` ; le sitemap ne le voit donc pas | tentative de pose de `rank_math_robots` par REST : meta non exposée, aucun effet | toujours dans le sitemap | à faire dans wp-admin |
| /automatisation-des-factures-par-ia-au-maroc/ | 301 vers la page d'accueil (non équivalente, risque de soft 404) | règle Rank Math héritée | aucune (Rank Math inaccessible) | 301 vers / | recommandé : cible /automatisation-factures-ia-maroc/ |
| http://www.fluxintelligent.com/ | chaîne de 2 redirections | règles http→https puis www→non-www appliquées séparément | aucune | 2 sauts, aboutit en 200 | recommandé : règle unique (Cloudflare ou .htaccess) |
| liens internes de /chatbots-experience-client/ (4100) et /automatisation-des-processus/ (4009) | liens écrits en dur vers 3288 et 3092 (301) | contenu antérieur aux fusions | aucune : réécrire ces pages par le MCP exige de renvoyer tout leur contenu, risque disproportionné | les liens aboutissent en 1 saut | recommandé : remplacer les 2 liens dans l'éditeur |

**Cache :** l'URL publique `post-sitemap.xml` sert encore une version en cache du cache serveur Hostinger qui liste 3092 et 3288. La version sans cache (`?nocache=…`) est à jour. La purge n'a pas été possible : le connecteur Hostinger n'est pas authentifié. Le cache expirera de lui-même, ou peut être vidé dans hPanel (Cache Manager).

## 4. Fichiers et réglages modifiés

| Élément | Avant | Après | Justification | Retour arrière |
|---|---|---|---|---|
| Article 3092, statut | publish | draft | URL déjà redirigée en 301 ; retrait du sitemap | `wp_update_post` id 3092 status publish (sauvegarde : `gsc/backup/post-3092.json`) |
| Article 3288, statut | publish | draft | idem | `wp_update_post` id 3288 status publish (`gsc/backup/post-3288.json`) |
| Page 4473 | aucune modification effective | (date de modification mise à jour) | aucune | sans objet |

**Non modifiés :** robots.txt (sauvegarde : `gsc/backup/robots-2026-11-16.txt`), redirections, règles de sécurité, Cloudflare, cœur WordPress, contenus éditoriaux.

## 5. Actions restantes (accès requis)

1. **Search Console.** Exporter les URL des deux rapports, « Page en double… » et « Bloquée par robots.txt », puis :
   - inspecter 3288, 3092 et leurs cibles ;
   - lancer « Valider la correction » sur le rapport « Page en double » ;
   - soumettre à nouveau `sitemap_index.xml`.

   Pour que je le fasse, il faut ajouter le compte Google connecté à Composio comme utilisateur de la propriété fluxintelligent.com, ou connecter la Search Console dans Surfer.
2. **wp-admin, page 4473.** Dans Rank Math, onglet Avancé, cocher No Index, ce qui retire la page du sitemap. Autre voie : exclure l'ID 4473 dans Rank Math > Sitemap > Pages.
3. **Rank Math > Redirections.** Faire pointer `automatisation-des-factures-par-ia-au-maroc` vers `/automatisation-factures-ia-maroc/`.
4. **Éditeur.** Remplacer les liens vers 3288 et 3092 dans les pages 4100 et 4009 par leurs cibles finales.
5. **hPanel.** Vider le cache, puis relancer `tests_indexation.py`.
6. **Optionnel.** Ramener `http://www` à une seule redirection.

## 6. Tests automatisés (reproductibles)

Dans `flux-editorial/gsc/` :

| Script | Rôle |
|---|---|
| `audit_indexation.py` | statut, chaîne de redirections, canonical HTML et `Link`, meta robots, X-Robots-Tag, verdict robots.txt Googlebot, présence dans le sitemap |
| `similarite.py` | doublons de contenu et de titres |
| `liens_internes.py` | liens internes vers des URL non 200 |
| `canonical_rendu.cjs` | canonical après rendu JavaScript (Playwright) |
| `tests_indexation.py` | 63 règles de non-régression |

**Résultats du 16/11 après correction :** 62 règles OK, 1 échec (page 4473 dans le sitemap, action 2). Détail : `resultats/apres/tests-2026-11-16.txt`.

**Avant et après (sitemaps lus sans cache) :**
- avant : 100 URL, dont 3 non conformes (3092 et 3288 en 301, 4473 en noindex) ;
- après : 98 URL, dont 1 non conforme (4473).

Données brutes : `resultats/avant/` et `resultats/apres/`.

**Observation.** Des requêtes HEAD simultanées, 8 à 10 en parallèle, renvoient parfois 500 (4 sur 24). En revanche, 40 GET en rafale avec l'user-agent Googlebot donnent 40 réponses 200. Googlebot explore en GET, donc pas d'impact attendu sur l'indexation. À surveiller dans le rapport « Statistiques sur l'exploration ».

## 7. Statut par étape

| Étape | 3288 / 3092 | 4473 | Alerte robots.txt |
|---|---|---|---|
| Correction vérifiée publiquement | oui, sitemap lu sans cache et 301 | non | sans objet (aucun blocage indu constaté) |
| Validation envoyée dans GSC | non (pas d'accès) | non | non |
| Nouvelle exploration par Google | inconnue | inconnue | inconnue |
| Indexation confirmée | non prouvée | non prouvée | non prouvée |

## 8. Surveillance

- **Chaque semaine :** `python3 -I tests_indexation.py` (code retour 1 en cas d'échec).
- **Après chaque fusion d'article :** passer la source en brouillon ou à la corbeille une fois la 301 créée, et vérifier qu'elle sort du sitemap.
- **GSC, à 7, 14 et 28 jours** après la validation :
  - « Pages », pour les motifs « Page en double » et « Bloquée par robots.txt » ;
  - « Sitemaps », pour le nombre d'URL découvertes ;
  - « Statistiques sur l'exploration », pour les réponses 5xx.
