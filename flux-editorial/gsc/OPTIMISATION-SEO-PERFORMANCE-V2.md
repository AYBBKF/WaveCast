# Optimisation SEO et performances V2 : fluxintelligent.com (17–18/11/2026)

Ce document ne refait pas l'audit 360°. Il ne traite que les écarts encore ouverts. Scripts de mesure : `perf/`.

## 1. Causes confirmées

### 1.1 `/0tqe/` : passerelle « Google tag gateway » de Cloudflare

| Point | Constat (preuve) |
|---|---|
| Nature | conteneur de balise Google (`// Copyright 2012 Google Inc.`) servi depuis le domaine du site, `server: cloudflare`, `Cache-Control: private, max-age=900` |
| Origine | **Cloudflare, zone fluxintelligent.com.** API `settings/google-tag-gateway/config` : `enabled: true`, `endpoint: /0tqe`, `measurementId: AW-18347114778`, `setUpTag: false`, `hideOriginalIp: true`, `forwardClientIpHeaders: true` |
| Mode d'insertion | **injection HTML par Cloudflare en périphérie**, absente du HTML WordPress, visible seulement avec `Accept: text/html`. En tête du `<head>` : `google_tags_first_party` (AW-18347114778), `<script async src="/0tqe/">`, puis `gtag('js')` avec `developer_id.dY2E1Nz` |
| Propriétaire | compte Cloudflare de la zone (« Boukafa.ayoub@gmail.com's Account ») ; le compte Google Ads AW-18347114778 est la destination |
| Rôle | sert la balise Google Ads en first-party et relaie les hits Ads par `/0tqe/gs/ccm/collect` |

### 1.2 Balises Google chargées sur chaque page (trace réseau, accueil)

| Chargeur | Script | Destinations |
|---|---|---|
| **Site Kit** (WordPress) | `googletagmanager.com/gtag/js?id=GT-PZQ8SJ83`, plus `gtag('config','GT-PZQ8SJ83')` et `gtag('config','AW-18347114778')`, mode de consentement (refus par défaut pour l'EEE), événements de contenu | GA4 `G-1JX1J3TWVZ` (via GT-PZQ8SJ83), Google Ads AW-18347114778 |
| **Cloudflare, passerelle** | `/0tqe/`, `/0tqe/e6SS…` | Google Ads AW-18347114778 |
| Autres (hors Google) | pixel OpenAI (`oaiq.min.js`, consentement « marketing »), Cloudflare Web Analytics, script d'attribution `fdi-source` | – |

- **Doublon confirmé :** le conteneur **Google Ads AW-18347114778 est téléchargé et exécuté deux fois** (`gtag/js?id=AW-…` depuis googletagmanager.com, plus `/0tqe/…` par la passerelle) et `gtag('js')` est initialisé deux fois.
- **Pas de double comptage observé :** 1 seul `page_view` Ads (`ccm/collect`) et 1 seul `page_view` GA4 par chargement.
- **Google Tag Assistant :** non disponible dans cet environnement. Constat établi par trace réseau Chromium et par lecture du `dataLayer`.

### 1.3 Effet mesuré de la passerelle (simulation locale, sans rien modifier en production)

**Méthode :** la page est servie telle quelle (« actuel »), puis le **seul** snippet injecté par Cloudflare est retiré du HTML reçu par le navigateur de test (« sans passerelle »). 3 passages, CPU ralenti ×4, profil Pixel 5. Médianes :

| Page | Scénario | TBT (tâches longues) | `page_view` Ads | `page_view` GA4 |
|---|---|---|---|---|
| `/` | actuel | ~950 ms | 3/3 | 2/3 |
| `/` | sans passerelle | **~598 ms** (−37 %) | **3/3** (via `pagead2.googlesyndication.com/ccm/collect`) | **3/3** |
| `/automatisation-ia-pme-maroc/` | actuel | ~870 ms | 3/3 | 2/3 |
| `/automatisation-ia-pme-maroc/` | sans passerelle | **~501 ms** (−42 %) | **3/3** | **3/3** |

**À ne pas confondre :** bloquer seulement l'URL `/0tqe/` **casse le suivi Ads** (le conteneur AW ne s'enregistre plus, aucun `page_view` Ads). Le gain Lighthouse obtenu ainsi (accueil : 78 vers 93 ; article : 77 vers 92) **n'est pas exploitable**. Seule la désactivation complète de la passerelle, injection comprise, préserve le suivi.

Le TBT reste une mesure de laboratoire, **pas l'INP réel**.

### 1.4 Autres facteurs examinés

| Élément | Constat | Correction sûre possible ? |
|---|---|---|
| 3 CSS bloquantes | 4, 17 et 38 Ko, servies depuis le cache Cloudflare (`HIT`, `max-age=31536000, immutable`) | non : gain faible, risque de flash de contenu non stylé |
| Polices | auto-hébergées, préchargées (`manrope-800`, `inter-400`), `font-display: swap` | déjà conforme |
| Image LCP de l'article | `loading="eager"`, `fetchpriority="high"`, 480 px, `srcset` | déjà conforme |
| HTML | **aucun cache** : Cloudflare `BYPASS` malgré la règle « Cache HTML anonyme » (l'origine n'envoie ni `Set-Cookie` ni `Cache-Control`) ; génération WordPress ~1,5 s (`x-hcdn-upstream-rt`) ; pas de cache LiteSpeed visible | **décision requise** (voir le point 6) |
| Réglages de vitesse Cloudflare | Rocket Loader désactivé, Early Hints désactivé, minification désactivée, Brotli et HTTP/3 activés | non modifiés |

### 1.5 Lighthouse mobile de référence (médiane de 3, 17/11, `perf/bench.sh`)

| Page | Score | LCP | TBT | Exécution JS | Poids |
|---|---|---|---|---|---|
| `/` | 78 | 2 289 ms | 566 ms | 1 123 ms | 888 Ko |
| `/automatisation-ia-pme-maroc/` | 77 | 2 511 ms | 642 ms | 1 173 ms | 804 Ko |

Les LCP de 4,1 et 4,3 s du rapport 360° étaient des passages isolés. **En médiane, le LCP est de 2,3 à 2,5 s** et le problème principal est le **temps de blocage JavaScript**.

### 1.6 CrUX (données terrain)

**Non disponibles :**
- l'API PageSpeed sans clé a épuisé son quota ;
- le projet Google de Composio n'a pas l'API PageSpeed activée ;
- le rapport « Signaux Web essentiels » n'est pas exposé par l'API Search Console.

## 2. Corrections appliquées dans cette mission

**Aucune modification du site.** Les seules optimisations à fort effet touchent le suivi publicitaire ou la configuration de cache globale : votre accord est requis. Les optimisations front-end sans risque (polices, image LCP, cache des CSS) sont déjà en place.

## 3. Les 12 pages non indexées (inspection du 17/11 au soir)

| Page | État GSC | Dernière exploration | Catégorie |
|---|---|---|---|
| `/agent-ia-cabinet-dentaire-maroc/` | Détectée, non indexée | – | en attente d'exploration |
| `/agent-ia-pharmacie-maroc/` | Détectée, non indexée | – | en attente d'exploration |
| `/agent-ia-clinique-veterinaire-maroc/` | Inconnue de Google | – | en attente d'exploration (état fluctuant entre détectée et inconnue) |
| `/agent-ia-institut-beaute-maroc/` | Détectée, non indexée | – | en attente d'exploration |
| `/confirmation-commande-cod-whatsapp-maroc/` | Détectée, non indexée | – | en attente d'exploration |
| `/food-cost-restaurant-prix-achat/` | Détectée, non indexée | – | en attente d'exploration |
| `/automatisation-centre-de-formation-maroc/` | Détectée, non indexée | – | en attente d'exploration |
| `/suivi-relance-devis-sans-double-saisie/` | Détectée, non indexée | – | en attente d'exploration |
| `/comparer-devis-automatisation-ia-maroc/` | Détectée, non indexée | – | en attente d'exploration |
| `/automatisation-ia-agence-transport/` | Explorée, non indexée | 04/08 | explorée, non retenue (antérieure à l'enrichissement du 03/11) |
| `/workflow-ia-coach-musculation-maroc-2025/` | Explorée, non indexée | 06/09 | explorée, non retenue ; brouillon B2B conservé |
| `/ia-salon-coiffure-automatisation/` | Explorée, non indexée | 16/06 | explorée, non retenue ; brouillon conservé |

- **Liens ajoutés le 17/11 :** 18 sur 18 toujours présents dans le HTML public.
- Aucun ajout de contenu ni de lien supplémentaire. Brouillons coach et salon préservés (Surfer non reconnecté).
- **Lecture :** 9 pages attendent simplement leur première exploration, 3 ont été explorées mais non retenues. Le volume d'exploration est faible : Google n'a pas visité les pages découvertes depuis le 17/11. L'effet du maillage se mesurera au contrôle du 01/12.

## 4. Page contact : cannibalisation et référence de suivi

**Constat :** sur les mêmes requêtes, deux URL distinctes sont classées : l'accueil (positions 2,6 et 7,4) et la page contact (positions 11 et 9,4). Ce ne sont pas des liens annexes (sitelinks) : les positions diffèrent.

**Recoupement démontré.** Effet négatif non démontré, car l'accueil reste bien classé. Le title modifié le 17/11 est donc **à surveiller sans nouvelle modification**.

**Référence avant changement** (18/10 au 14/11, données `all`) :

| Page | Clics | Impressions | CTR | Position | Marque (clics / impressions) | Hors marque (clics / impressions) |
|---|---|---|---|---|---|---|
| `/ia/contact/` | 1 | 635 | 0,16 % | 10,3 | 0 / 25 | 1 / 541 |
| `/` | 68 | 1 876 | 3,62 % | 7,8 | 16 / 64 | 25 / 1 119 |

| Requête | `/ia/contact/` (clics, impressions, position) | `/` (clics, impressions, position) |
|---|---|---|
| agence ia maroc | 1, 233, 11,0 | 8, 301, 2,6 |
| agence ia | 0, 213, 9,4 | 8, 280, 7,4 |
| agence intelligence artificielle maroc | 0, 13, 8,9 | 2, 13, 4,2 |
| flux intelligent | 0, 25, 1,9 | 16, 56, 1,1 |

**Mesure après :** à partir du 01/12, sur 14 jours, puis le 22/12 sur 28 jours.

## 5. Search Console

| Point | État |
|---|---|
| Sitemaps | inchangés : index 0 erreur, 0 avertissement ; sous-sitemaps 0 et 0 ; pas de nouvelle soumission |
| Indexation | sitemap : 86 sur 98 indexées. P1 immobilier et rapprochement-COD indexées le 17/11 |
| Nouveaux avertissements | aucun dans les données exposées (sitemaps, inspection) |
| Non exposé par l'API | rapport « Pages », Signaux Web essentiels, sécurité et actions manuelles, « Valider la correction » |

## 6. Opérations nécessitant votre accord

**A. Désactiver la passerelle Google tag gateway de Cloudflare.** C'est le gain principal mesuré : TBT −37 à −42 % en simulation, suivi Ads et GA4 préservé.

- **Commande prête :** `PUT /zones/4b1d9d0347f9ee31f57447ccea74c9a2/settings/google-tag-gateway/config` avec `{"enabled": false, "endpoint": "/0tqe", "measurementId": "AW-18347114778", "setUpTag": false, "hideOriginalIp": true, "forwardClientIpHeaders": true}`. Le jeton actuel n'a peut-être pas la permission d'écrire ce réglage : à vérifier lors de l'exécution.
- **Contrepartie :** perte de la mesure Google Ads en first-party (meilleure résistance aux bloqueurs et aux restrictions de cookies tiers). Les hits Ads repassent par les domaines Google classiques.
- **Après exécution :**
  - purge des seules URL HTML principales ;
  - trace réseau (1 `page_view` Ads et 1 `page_view` GA4 attendus) ;
  - `bench.sh` avant et après ;
  - contrôle des conversions Ads dans le compte Google Ads sous 48 h.
- **Rollback :** même appel avec `"enabled": true`.

**B. Variante qui conserve la passerelle :** faire passer GA4 et Ads uniquement par la passerelle (configuration Google Ads et Site Kit). Plus complexe, à décider avec la personne qui gère le compte Ads ; non simulée de façon concluante.

**C. Cache HTML.** Rendre effectif un cache HTML compatible avec les formulaires : cache Hostinger ou LiteSpeed avec exclusion des pages à formulaire (`/ia/devis/`, `/ia/contact/`, pages avec Forminator), ou correction de la règle Cloudflare. C'est une configuration de cache globale. Le cas d'une injection HTML de la passerelle qui empêcherait le cache Cloudflare est à confirmer après A.

**D. Surfer à reconnecter** pour les contenus coach et salon (brouillons prêts).

**E. Sécurité :** révoquer les jetons Cloudflare temporaires et supprimer les secrets `api.cloudflare.com` et `fluxintelligent.com` de l'environnement Default.

## 7. Problèmes restant ouverts

1. TBT élevé (doublon Ads par la passerelle) : en attente de A.
2. HTML non mis en cache, génération en ~1,5 s : en attente de C.
3. 12 pages non indexées : en attente d'exploration ; contrôles le 01/12 et le 22/12.
4. Page contact : mesure de l'effet du title à partir du 01/12.
5. CrUX et INP réels : indisponibles. À consulter dans Search Console > Signaux Web essentiels.
