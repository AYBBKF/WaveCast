# Flux Intelligent : plan de croissance SEO organique

Date : 18/11/2026.

**Sources :**
- Google Search Console, propriété `https://fluxintelligent.com/` (compte Composio `google_search_console_camera-harper`), type **Web**.
- Il s'agit uniquement de **trafic organique** : Search Console ne contient pas le trafic Paid Search.
- Données disponibles jusqu'au 15/11 : 2 à 3 jours de décalage.

**Périodes comparées :**
- 28 derniers jours : 19/10 au 15/11 ;
- 28 jours précédents : 21/09 au 18/10 ;
- 3 mois : 18/08 au 15/11.

**Hors périmètre :** le projet V4 de suivi des leads est archivé sans déploiement (`archive/tracking-v4/`). Aucune configuration Google Ads, GA4, Tag Gateway ou de suivi n'a été touchée.

**Légende confiance :** 🟢 élevée, 🟡 moyenne, 🔴 faible.

---

## 1. État réel de l'indexation

Inspection d'URL par l'API Search Console, le 18/11.

| Groupe | Statut Google | Détail |
|---|---|---|
| Sitemap `sitemap_index.xml` | 0 erreur, 0 avertissement | 98 URL web soumises ; dernière lecture 17/11 ; renvoyé le 18/11 |
| Pages commerciales clés | **indexées** | `/agents-ia/` (exploré 18/11), `/ia/automatisation-ia-casablanca/`, `/ia/agence-ia-rabat/`, `/ia/automatisation-ia-oujda/`, `/chatbots-experience-client/chatbot-whatsapp-maroc/`, `/automatisation-ia-pme-maroc/` |
| Anciennes URL fusionnées | « Page avec redirection » : **normal** | `/chatbot-whatsapp-maroc/`, `/chatbot-ia-maroc-whatsapp-business-leads/`, `/agence-ia-rabat/`, `/ia/automatisation-ia-rabat/`, `/agence-ia-casablanca-automatisation-fiable/`, `/ia/about/`, `/automatisation-entreprise-maroc/` |
| **Anomalie trouvée** | « Introuvable (404) », explorée le 18/11 | `/agent-ia-maroc-pme/`, qui recevait encore des impressions (« agent ia maroc », « déploiement agents ia maroc ») : **corrigée** (section 5) |
| 12 pages suivies | 2 indexées, 10 en attente | section 7 |
| Dakhla | **aucune page publiée** | `/automatisation-ia-dakhla/` et `/ia/automatisation-ia-dakhla/` inconnues de Google et absentes du site |

## 2. Classement des mots-clés stratégiques

Position moyenne pondérée par les impressions.

| Requête | URL cible | 28 j : impr. / clics / pos. | 28 j préc. | 3 mois | Intention | Problème constaté | Action |
|---|---|---|---|---|---|---|---|
| agence ia maroc | `/` | 597 / 9 / **9,2** | 284 / 3 / 11,8 | 1 246 / 17 / 11,9 | commerciale (prestataire) | **double URL** : `/` pos. 5,1 (543 impr.), `/ia/contact/` pos. 10,9 (405 impr.), `/ia/propos-de-nous/` pos. 20 (164) | title de contact déjà neutralisé (17/11) ; observer 28 j que Google consolide sur `/` ; liens d'ancre « agence IA au Maroc » vers `/` (S1) |
| agence intelligence artificielle maroc | `/` | 28 / 2 / 6,9 | 35 / 1 / 14,2 | 96 / 3 / 18,8 | commerciale | « intelligence artificielle » absent du title de l'accueil ; « agence intelligence artificielle » : 102 impr., pos. 18,8 | test de title sur l'accueil, **avec votre accord** (section 10) |
| automatisation ia maroc | `/` | 35 / 0 / 12,1 | 15 / 1 / 4,8 | 50 / 1 / 9,9 | commerciale / info | `/` pos. 3,4, mais l'article pilier `/automatisation-ia-pme-maroc/` ne ressort pas | lien de `/automatisation-ia-pme-maroc/` vers `/agents-ia/` fait ; à surveiller |
| automatisation entreprise maroc | `/` | 29 / 0 / 20,9 | – | 29 / 0 / 20,9 | info + commerciale | `/automatisation-entreprise-maroc/` redirige (301) vers `/automatisation-ia-pme-maroc/`, qui n'est pas classée sur cette requête | enrichissement ciblé de `/automatisation-ia-pme-maroc/` (S2, accord si réécriture importante) |
| agent ia maroc | `/agents-ia/` | 28 / 0 / 27,4 | 34 / 0 / 16,1 | 95 / 0 / 22,1 | commerciale | le hub indexé ne ciblait pas « Maroc » ; Google montrait `/ia/contact/` (pos. 7,8) ; l'URL `/agent-ia-maroc-pme/` était en 404 | **title et meta corrigés, 301 posée** (section 5) |
| chatbot whatsapp maroc | `/chatbots-experience-client/chatbot-whatsapp-maroc/` | 16 / 0 / 33,1 | 7 / 0 / 19,0 | 36 / 0 / 24,6 | commerciale | pilier en baisse (210 → 93 impr. ; pos. 13,3 → 24,7) ; proximité avec `/chatbot-ia-whatsapp-maroc/` et `/agent-ia-whatsapp-business-pme-maroc/` (pos. 7,2, 66 impr.) | distinguer les intentions (section 4) |
| automatisation pme maroc | `/automatisation-ia-pme-maroc/` | 1 / 0 / 1,0 | – | 2 / 0 / 8,5 | commerciale | volume quasi nul dans Search Console | pas d'action dédiée |

**Autres requêtes commerciales relevées dans Search Console (28 j) :**

| Requête | Impr. | Pos. | URL la mieux classée | Lecture |
|---|---|---|---|---|
| agence ia | 553 | 14,8 | `/` | requête générique, hors Maroc ; lever : autorité de l'accueil |
| agence intégration ia | 31 | 2,5 | `/` | déjà bien classée ; le CTR est le levier |
| agence marketing automation maroc | 25 | 21,5 | `/crm-ventes-marketing-ia/agence-de-marketing-digital/` (pos. 14,4 sur 3 mois) | **title corrigé** |
| assistant ia base documentaire maroc | 27 | 12,2 | `/` et `/ia/nos-services/` | **aucune page dédiée** : lacune (section 3) |
| agence ia tanger | 23 | 14,3 | `/automatisation-ia-tanger/` pos. 5,4 | bon ; lien ajouté |
| agence intelligence artificielle marrakech / agence ia marrakech | 18 + 14 | 22,9 / 43,6 | `/ia/automatisation-ia-marrakech/` | page en recul (7,0 → 15,0) ; lien ajouté |
| service client ia maroc | 13 | 15,2 | `/ia/contact/` (7,8) | `/agents-ia/agent-ia-support-client/` existe mais n'est pas choisie : à renforcer |
| agence ia rabat | 11 | 5,0 | `/ia/agence-ia-rabat/` | progression (19,3 → 9,4 pour la page) |
| agence ia casablanca | 11 | 17,0 | `/` (6,7) plutôt que la page Casablanca (37,5) | page locale faible : section 3 |

**Concurrence organique :** non mesurée. Aucun outil de SERP n'a été consommé (Surfer non utilisé, aucune donnée Ahrefs ou DataForSEO pour ce domaine). À faire avec un éditeur Surfer existant ou après votre accord pour consommer des crédits.

## 3. Les 10 opportunités SEO les plus rentables

Classées par potentiel de clics à court terme, avec la preuve tirée de Search Console.

| # | Opportunité | Preuve | Action | Statut | Impact attendu | Confiance |
|---|---|---|---|---|---|---|
| 1 | Consolider « agence ia maroc » sur l'accueil | 1 246 impr. sur 3 mois, éclatées entre `/`, `/ia/contact/` et `/ia/propos-de-nous/` | title de contact neutralisé le 17/11 ; titles et meta de « à propos » et « services » nettoyés (accents) ; S1 : 3 à 5 liens d'ancre « agence IA au Maroc » vers `/` depuis des articles indexés | partiel ✅ | +1 à 3 positions sur la tête de requête ; CTR ×2 si `/` passe sous la position 5 | 🟡 |
| 2 | « agent ia maroc » vers `/agents-ia/` | 95 impr. ; hub indexé sans « Maroc » ; ancienne URL en 404 | title et meta du hub ; 301 `/agent-ia-maroc-pme/` → `/agents-ia/` ; lien contextuel depuis `/automatisation-ia-pme-maroc/` | **fait** ✅ | hub classé sur la requête d'ici 2 à 6 semaines | 🟡 |
| 3 | Page Casablanca en recul | pos. 16,6 → 23,8 ; Google préfère `/` pour « agence ia casablanca » | lien depuis l'article Casablanca `/ia-entreprises-casablanca/` ; ensuite, différenciation locale du contenu (accord) | partiel ✅ | stabilisation, puis gain si le contenu devient plus local | 🟡 |
| 4 | Marrakech en recul | pos. 7,0 → 15,0 ; seulement 4 liens, tous depuis des pages villes | lien depuis l'article riads et hôtels `/reservation-directe-whatsapp-riad/` | **fait** ✅ | retour vers le top 10 | 🟡 |
| 5 | Pilier chatbot WhatsApp en baisse | 210 → 93 impr. ; pos. 13,3 → 24,7 | distinguer les titles : pilier = service, `/chatbot-ia-whatsapp-maroc/` = comparatif, `/agent-ia-whatsapp-business-pme-maroc/` = guide tarifs | à faire (S3, titles seulement) | +5 à 10 positions sur le pilier | 🟡 |
| 6 | Accueil : « agence intelligence artificielle (maroc) » | 130 impr./28 j, pos. 7 à 19 | intégrer « intelligence artificielle » au title de l'accueil | **accord requis** | +2 à 5 positions sur ces variantes ; risque faible sur la requête principale | 🟡 |
| 7 | Marketing automation | « agence marketing automation maroc » pos. 14,4 (47 impr.) | title réécrit avec « Agence marketing automation Maroc » | **fait** ✅ | top 10 possible | 🟡 |
| 8 | Lacune « assistant IA base documentaire » | 27 impr./28 j, aucune page dédiée | page ou section de service dédiée | **accord requis** (nouveau contenu) | nouvelle requête captée | 🔴 |
| 9 | Pages villes peu reliées (Tanger, Fès, Agadir, Oujda) | 3 ou 4 liens chacune, uniquement depuis les autres pages villes | liens thématiques : industrie → Tanger, tourisme → Agadir (faits) ; Fès et Oujda : sources à trouver | partiel ✅ | meilleure exploration, +1 à 3 positions | 🟡 |
| 10 | Pages faibles qui diluent les requêtes de tête | `/systeme-agents-ia-gouverne-maroc/` pos. 40 à 60 sur « agence ia » ; `/comment-ai-revolutionne-le-controle-qualite/` pos. 60,7 | aucune suppression ; recentrer ou fusionner sur décision | **accord requis** | moins de dilution | 🔴 |

## 4. Pages à améliorer en priorité

1. **`/` (accueil)** : title à tester (#6) ; liens d'ancre (#1).
2. **`/ia/automatisation-ia-casablanca/`** : contenu plus local, sans inventer ni adresse, ni client, ni témoignage. Aujourd'hui 1 378 mots, proches des autres pages villes.
3. **`/chatbots-experience-client/chatbot-whatsapp-maroc/`**, avec ses deux articles voisins : distinguer les intentions (#5).
4. **`/ia/automatisation-ia-marrakech/`** (1 049 mots) : hôtellerie et riads plus concrets.
5. **`/automatisation-ia-tanger/`** : la plus courte des pages villes (789 mots), mais bien classée (5,4) : enrichir sans casser.
6. **`/agents-ia/agent-ia-support-client/`** : capter « service client ia maroc ».
7. **`/automatisation-ia-pme-maroc/`** : couvrir « automatisation entreprise maroc » (URL de destination de la 301).

**Pages Coach et Salon : inchangées**, toujours en brouillon. Elles attendent votre validation et un score Surfer de 80 à 90.

## 5. Corrections réellement appliquées (18/11)

| Correction | Avant → après | Sauvegarde / retour arrière | Preuve |
|---|---|---|---|
| Title et meta `/agents-ia/` (3773) | « Agents IA pour entreprises \| Flux Intelligent » → « **Agent IA Maroc \| Agents IA pour PME et entreprises** » ; meta avec « au Maroc » | `backup/rankmath-meta-avant-seo-20261118T114755Z.json` | `<title>` public vérifié après purge |
| Title `/crm-ventes-marketing-ia/agence-de-marketing-digital/` (4112) | « Marketing automation IA au Maroc \| Flux Intelligent » → « **Agence marketing automation Maroc \| IA et reporting** » | idem | vérifié |
| Title et meta `/ia/propos-de-nous/` (2991) | accents corrigés (« À propos », « Découvrez », « spécialisée ») | idem | vérifié |
| Meta `/ia/nos-services/` (1620) | accents corrigés (« automatisé », « à », « productivité ») | idem | vérifié |
| **301** `/agent-ia-maroc-pme/` → `/agents-ia/` | 404 explorée par Google le 18/11 → 301 en 1 saut | règle Rank Math n° 23 (22 règles avant, 23 après) ; retour arrière : supprimer la règle | origine : `301 → /agents-ia/` vérifié. **Public :** un 404 reste en cache Cloudflare (la purge par URL n'a pas atteint la clé) jusqu'à expiration naturelle, **au plus tard 2 h** (TTL de la règle « Cache HTML anonyme ») |
| 4 paragraphes de liens contextuels (ajout seul, aucun texte modifié) | `/reservation-directe-whatsapp-riad/` → Marrakech et Agadir ; `/ia-transformation-fabrication-mecanique/` → Tanger ; `/ia-entreprises-casablanca/` → Casablanca ; `/automatisation-ia-pme-maroc/` → `/agents-ia/` | `backup/maillage/*-20261118*.json` ; script `ajout_liens_seo_2026_11_18.py` ; journal `resultats/maillage-ajouts-seo-2026-11-18.json` | diff du rendu : **ajout uniquement** pour les 4 ; liens présents en public |
| Sitemap renvoyé à Search Console | `sitemap_index.xml` | – | API : « successfully submitted » |
| **Tests de non-régression** | 70 contrôles d'indexation | – | **0 échec** |

**Annulé, sans effet :**
- La meta description de l'accueil enregistrée dans Rank Math (page 123) n'est **pas** celle qui s'affiche : une autre source (filtre du thème) la remplace. La valeur enregistrée a été remise à l'identique.
- La description publique de l'accueil est inchangée et reste correcte.

**Non modifiés :** robots.txt, canoniques, cache, Cloudflare (hors purge ciblée de 11 URL), contenus éditoriaux existants, Coach, Salon, ainsi que tout réglage Google Ads, GA4 ou de suivi.

## 6. Évolution des clics et impressions organiques

| Période | Clics | Impressions | CTR | Position moyenne |
|---|---|---|---|---|
| 28 derniers jours (19/10–15/11) | **90** | 3 346 | **2,69 %** | 10,8 |
| 28 jours précédents (21/09–18/10) | 51 | 3 169 | 1,61 % | 10,0 |
| **Variation** | **+76 %** | +6 % | +1,1 pt | −0,8 (légère baisse) |
| 3 mois (18/08–15/11) | 242 | 9 964 | 2,43 % | 11,9 |

**Par mois :**

| Mois | Clics | Impressions | CTR |
|---|---|---|---|
| Août (à partir du 18) | 48 | 1 273 | 3,77 % |
| Septembre | 75 | 3 085 | 2,43 % |
| Octobre | 66 | 4 037 | 1,63 % |
| Novembre (1–15) | 53 | 1 569 | 3,38 % |

**Lecture :**
- La hausse des clics vient surtout de l'accueil : 34 → 71 clics, et position 8,6 → 7,8.
- Les clics de marque y contribuent : « flux intelligent », 17 clics.
- Pages en recul :
  - Casablanca : 16,6 → 23,8 ;
  - Marrakech : 7,0 → 15,0 ;
  - pilier chatbot WhatsApp : 13,3 → 24,7.
- Pages en hausse :
  - Rabat : 19,3 → 9,4 ;
  - `/agent-ia-whatsapp-business-pme-maroc/` : nouvelle, 66 impr., position 7,2 ;
  - Meknès : 1 → 2 clics.

## 7. État des 12 pages non indexées

Inspection API du 18/11 ; état précédent du 17/11.

| URL | Statut au 18/11 | Évolution | Diagnostic | Action |
|---|---|---|---|---|
| `/agence-ia-immobilier-maroc/` (P1) | **Envoyée et indexée** (exploration 17/11) | ✅ indexée | orpheline corrigée, title distinct | aucune |
| `/rapprochement-encaissements-cod/` | **Envoyée et indexée** (exploration 17/11) | ✅ indexée | – | aucune |
| `/agent-ia-cabinet-dentaire-maroc/` | Google ne reconnaît pas cette URL | stable | faible demande d'exploration ; gabarit proche des pages sœurs (similarité 0,31 à 0,34) | liens déjà en place (profondeur 2), dans le sitemap. Pas de réécriture. |
| `/agent-ia-pharmacie-maroc/` | Google ne reconnaît pas cette URL | stable | idem | idem |
| `/agent-ia-clinique-veterinaire-maroc/` | Détectée, non indexée | stable | idem | idem |
| `/agent-ia-institut-beaute-maroc/` | Détectée, non indexée | stable | idem | idem |
| `/confirmation-commande-cod-whatsapp-maroc/` | Détectée, non indexée | stable | 2 480 mots, sujet distinct | liens depuis le pilier WhatsApp et l'e-commerce (déjà en place) |
| `/food-cost-restaurant-prix-achat/` | Google ne reconnaît pas cette URL | stable | publiée le 08/11 | lien depuis l'article cafés (déjà en place) |
| `/automatisation-centre-de-formation-maroc/` | Google ne reconnaît pas cette URL | stable | publiée le 07/11 | 2 liens (déjà en place) |
| `/suivi-relance-devis-sans-double-saisie/` | Détectée, non indexée | stable | – | lien depuis la page relances (déjà en place) |
| `/comparer-devis-automatisation-ia-maroc/` | Détectée, non indexée | stable | – | 3 liens, dont `/agent-ia-whatsapp-business-pme-maroc/` |
| `/automatisation-ia-agence-transport/` | Explorée, non indexée (dernière exploration 04/08) | stable | exploration antérieure à l'enrichissement du 03/11 | **« Demander une indexation »** dans l'interface Search Console : recommandé, non faisable par API |

**Hors des 12 :** Coach (exploré le 06/09) et Salon (exploré le 16/06) restent « Explorée, non indexée ». Ils sont en brouillon d'enrichissement, en attente de validation.

**Bilan :**
- **2 sur 12 indexées en 24 h**, après les corrections de maillage du 17/11.
- Pour les 10 autres, les correctifs techniques sont faits : sitemap, liens depuis des pages indexées, profondeur 2.
- Aucune anomalie technique n'est constatée (200, canonique propre, pas de noindex).
- Le levier restant est la **demande d'exploration de Google**. Réécrire ces pages maintenant serait prématuré, conformément à votre consigne.

## 8. Plan d'action SEO sur 30, 60 et 90 jours

| Horizon | Action | Impact attendu | Confiance | Validation |
|---|---|---|---|---|
| **J+0 à J+30** | S1 : liens d'ancre « agence IA au Maroc » vers `/` depuis 3 à 5 articles indexés | consolidation de la requête de tête | 🟡 | GSC : part de `/` sur « agence ia maroc » supérieure à 70 % des impressions |
| | S3 : titles des 2 articles WhatsApp distincts du pilier | remontée du pilier | 🟡 | position du pilier sur « chatbot whatsapp maroc » sous 15 |
| | Liens vers Fès et Oujda depuis des contenus thématiques pertinents | exploration et position | 🟡 | inspection d'URL et position |
| | Demande d'indexation manuelle de `/automatisation-ia-agence-transport/` (par vous, dans l'interface GSC) | indexation | 🟡 | statut « Envoyée et indexée » |
| | Contrôle GSC du 01/12 (déjà programmé) | suivi | 🟢 | tableau section 7 mis à jour |
| **J+30 à J+60** | Enrichissement local de Casablanca puis de Marrakech (faits vérifiables, pas d'adresse inventée), avec un éditeur Surfer existant ou après accord | retour dans le top 10 | 🟡 | position page sur « agence ia casablanca » sous 15 |
| | Section ou page « assistant IA base documentaire », après accord | nouvelle requête | 🔴 | impressions sur la requête |
| | Renforcer `/agents-ia/agent-ia-support-client/` pour « service client ia maroc » | requête captée par la bonne page | 🟡 | URL classée dans GSC |
| **J+60 à J+90** | Revue des pages faibles (`/systeme-agents-ia-gouverne-maroc/`, contrôle qualité, transformer-entreprise) : recentrer ou fusionner, après accord | moins de dilution | 🔴 | positions des têtes de requête |
| | Page Dakhla : uniquement si vous la souhaitez (aucune page aujourd'hui) | nouvelle couverture locale | 🔴 | – |
| | Contrôle GSC du 22/12 (déjà programmé) | bilan 28 j après les corrections | 🟢 | comparaison avec la section 6 |

## 9. Prochaines actions autonomes

Elles restent ciblées, réversibles et sauvegardées :

1. Purge et vérification publique de la 301 `/agent-ia-maroc-pme/` après expiration du cache (au plus tard 2 h).
2. S1 : liens d'ancre vers l'accueil (ajout seul, méthode identique au 18/11).
3. S3 : titles des articles WhatsApp. Ce sont des métadonnées, pas une réécriture.
4. Liens thématiques vers Fès et Oujda, si des contenus sources pertinents existent. Sinon, rien.
5. Suivi GSC du 01/12 : 28 jours, positions des 7 mots-clés stratégiques et des 12 pages.

## 10. Éléments exigeant uniquement votre accord

| Décision | Proposition | Pourquoi l'accord |
|---|---|---|
| Title de l'accueil | « Agence IA Maroc \| Agence intelligence artificielle & automatisation IA » (au lieu de « Agence IA Maroc \| Automatisation IA & Intégration IA ») | page principale : touche la requête « agence intégration ia » (pos. 2,5) |
| Enrichissement de Casablanca et Marrakech | réécriture partielle de sections, avec faits vérifiables | réécriture importante |
| Nouvelle page « assistant IA base documentaire » | 1 page de service | nouveau contenu important |
| Pages faibles qui diluent les requêtes | recentrage ou fusion, avec 301 | fusion ou suppression |
| Page Dakhla | création | nouveau contenu important ; aucune implantation à inventer |
| Crédits Surfer | analyse de la concurrence et score pour Casablanca, Marrakech, Coach, Salon | consommation de crédits |
| Coach et Salon | publication après score Surfer 80 à 90 et votre validation | règle existante |

---

**Fichiers de cette mission :**
- `SEO-ORGANIC-GROWTH-PLAN.md` (ce rapport) ;
- `ajout_liens_seo_2026_11_18.py` ;
- `resultats/maillage-ajouts-seo-2026-11-18.json` ;
- `backup/rankmath-meta-avant-seo-20261118T114755Z.json` ;
- `backup/maillage/*-20261118*.json`.
