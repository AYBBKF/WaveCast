# Core Web Vitals mobile et SEO : validation finale

Date : 19/11/2026.

**Statut :**
- Tous les modèles du site sont corrigés et vérifiés en laboratoire.
- **Le problème Search Console n'est pas résolu tant que Google ne l'a pas confirmé.**
- Décision sur « Valider la correction » : section 7.

Aucune modification n'a été faite sur Google Ads, GA4, la Google Tag Gateway, le suivi ou les règles de cache Cloudflare. Seules des purges par URL ont été faites.

---

## 1. Modèles et URL vérifiés

**Liste exacte des 29 URL : non récupérable.** Les sources accessibles ne la donnent pas :
- l'API Search Console n'expose pas le rapport Signaux Web essentiels ;
- PageSpeed (quota épuisé) et CrUX (sans clé) ne répondent pas ;
- Cloudflare Web Analytics (RUM) refuse le jeton (« not authorized »).

Le tableau ci-dessous couvre donc **les 100 URL des sitemaps**, vérifiées une par une le 19/11 (`perf/couverture-urls-2026-11-19.json`). Les 29 URL du groupe en font nécessairement partie, avec ce modèle de page. **Ce n'est pas un inventaire du groupe.**

| Modèle | URL | Correctifs actifs | Feuilles CSS bloquantes restantes | Problème restant |
|---|---|---|---|---|
| Accueil (URL représentative du groupe) | 1 | CSS en ligne | 0 | aucun en labo |
| Pages villes | 9 : Casablanca, Rabat, Marrakech, Tanger, Fès, Agadir, Oujda, Meknès, Tétouan | CSS en ligne, polices locales, contraste | 0 ; Google Fonts : 0 | aucun en labo |
| Pages avec formulaire | 3 : `/ia/contact/`, `/agents-ia/`, `/rejoignez-nous/` | CSS en ligne (budget élargi), réservation de hauteur, contraste du bouton | 0 | aucun en labo |
| Pages | 26 (services, hubs, devis, légal…) | CSS en ligne | 0 | aucun en labo |
| Articles avec image à la une | 28 | CSS en ligne, préchargement de l'image LCP | 0 | variabilité liée aux scripts Google (section 4) |
| Articles sans image à la une | 29 | CSS en ligne | 0 | aucun en labo (LCP texte) |
| Archives (blog, catégories) | 4 | CSS en ligne ; 1re image de carte prioritaire et préchargée | 0 | aucun en labo |

## 2. Corrections déployées

Ce sont 3 mu-plugins. Les fichiers sources sont dans `perf/`. Aucun fichier du thème, d'une extension ou du cœur WordPress n'a été modifié.

| Fichier | Rôle | Validé par |
|---|---|---|
| `fi-perf-inline-css.php` (18–19/11) | CSS locales en ligne, tout ou rien sur le HTML final ; budget élargi pour les pages 101, 3773 et 4081 | A/B Lighthouse, captures, balises SEO, formulaires |
| `fi-perf-local-fonts.php` (18/11) | Space Grotesk et Public Sans servies depuis `uploads/fi-fonts/` | A/B, polices chargées vérifiées |
| `fi-css-fixes.php` (19/11, nouveau) | voir les 5 correctifs ci-dessous | voir ci-dessous |

Les 5 correctifs de `fi-css-fixes.php` :
1. réservation de hauteur du formulaire de contact (590 / 630 px) et du widget Turnstile (73 px) ;
2. texte blanc des boutons principaux des pages villes ;
3. texte blanc du bouton « Envoyer » du contact ;
4. préchargement de l'image à la une des articles ;
5. première image de carte des archives en `eager` et `fetchpriority="high"`, avec préchargement.

**Retour arrière :** supprimer le fichier, ou mettre la constante de mode à `'off'`, puis purger les URL.
- Modes : `FI_INLINE_CSS_MODE`, `FI_LOCAL_FONTS_MODE`, `FI_LCP_IMG_PRELOAD`, `FI_ARCHIVE_LCP`.
- Avant le 18/11, aucun de ces fichiers n'existait.

**Purge :** les 100 URL des sitemaps sont purgées par URL après chaque déploiement.

## 3. Mesures de laboratoire

Lighthouse 12, mobile simulé, médianes. A = état d'origine, B = corrigé, mesurés en alternance dans les mêmes conditions (`perf/resultats-cwv-2026-11-19.txt`, `perf/resultats-validation-2026-11-19.txt`).

| Modèle (URL testée) | Passages | FCP A → B | LCP A → B | CLS B | TBT B* |
|---|---|---|---|---|---|
| Accueil | 5 + 3 prod | 2 117 → **1 053** | 2 196 → **1 279** | 0 | 575 |
| Ville (Casablanca) | 3 + 3 | 2 232 → **1 058** | 2 921 → **1 280** | 0 | 605 |
| Ville (Rabat) | 3 + 3 | 2 220 → 1 033 | 2 740 → **1 190** | 0 | 719 |
| Contact | 3 + 3 + 3 | 2 292 → **1 193** | 2 292 → **1 385** | **0** (0,127 sans réservation) | 503 |
| Agents IA | 3 + 3 + 3 | 2 193 → 1 179 | 2 556 → **1 253** | 0 | 570 |
| Rejoignez-nous | 3 + 3 + 3 | 2 243 → 1 207 | 2 831 → **1 376** | 0 | 740 |
| Article avec image (`/automatisation-ia-pme-maroc/`) | 5 + 5 | 1 048 → 1 036 | 2 988 → **1 260** | 0 | 526 |
| Article avec image (`/chatbot-ia-whatsapp-maroc/`) | 5 + 5 | 1 060 → 1 050 | 4 054 → **1 255** | 0 | 532 |
| Archive blog (`/ia/blog/`) | 4 + 4 | 1 027 → 1 013 | 4 625 → **1 178** | 0 | 412 |
| Services | 3 prod | – → 1 031 | – → 1 221 | 0 | 622 |

\* Ce TBT reflète le processeur lent de cet environnement. PSI mesure 20 ms. Ce n'est pas un critère de décision.

Pour les deux articles et l'archive, la colonne A est la version qui avait déjà le CSS en ligne : leur FCP « avant » est donc déjà d'environ 1,0 s. Le gain affiché porte sur le préchargement de l'image ou la priorité de la carte.

**Variabilité :** environ 1 passage sur 5 sur les articles et l'archive dépasse 3 s. C'est la concurrence de bande passante avec environ 525 Ko de scripts Google (section 4).

## 4. Mesures réelles (terrain) : ce qui est connu

| Source | Donnée | Lecture |
|---|---|---|
| Search Console (vous) | groupe de 29 URL, LCP 2,7 s, URL représentative : accueil | valeur au 75e centile sur 28 jours, **avant** les correctifs |
| CrUX / PSI « vos utilisateurs » | non accessible ici (pas de clé) | script prêt (section 6) |
| Cloudflare, requêtes HTML réelles (12–18/11, navigateurs, GET 200) | HIT 1 696 · MISS 2 299 · EXPIRED 1 610 · BYPASS 2 203 · DYNAMIC 521 | voir ci-dessous |
| Cloudflare, pays | US 5 387 · MA 1 436 · LV 202 · FR 191… | le trafic marocain réel est minoritaire dans ces comptes |

**Constat terrain, hors front-end :**
- Seuls **environ 30 % des affichages HTML cacheables sont servis depuis le cache Cloudflare** (HIT / (HIT + MISS + EXPIRED)).
- L'accueil part souvent à l'origine pour de vrais mobiles : 314 MISS Chrome Mobile et 173 MISS Safari Mobile en 6 jours.
- Sur MISS, le TTFB de l'origine est de 0,35 à 0,9 s, contre 0,09 à 0,28 s en HIT. Cela pèse directement sur le LCP terrain.
- **Causes plausibles, non prouvées** : ce compte Cloudflare ne donne pas accès au champ « query string » :
  1. des URL d'arrivée avec paramètres (gclid, utm…), chacun créant une entrée de cache distincte ;
  2. de nombreux points de présence Cloudflare, chacun avec son propre cache ;
  3. l'expiration périphérique à 2 h.
- Les leviers sont des réglages Cloudflare : clé de cache ignorant les paramètres marketing, Tiered Cache. **Décision réservée** (section 8). Ignorer gclid dans la clé de cache ne retire pas le paramètre de l'URL : GA4 et Ads le lisent toujours.

**Contrôle externe, sans en-tête `Authorization` :** Firecrawl, depuis l'extérieur, reçoit bien la version déployée. Le CSS de réservation du formulaire est présent dans le HTML de `/ia/contact/`. Le statut de cache par visiteur anonyme vient des statistiques Cloudflare ci-dessus. Depuis cet environnement, le proxy force `BYPASS`.

## 5. État de robots.txt

- **Contrôle Lighthouse en échec :** ligne 7, `Content-Signal: search=yes, ai-input=yes, ai-train=no`, message « Unknown directive ».
- **Cause vérifiée :**
  - `Content-Signal` est une directive de préférence d'usage du contenu (proposition Cloudflare), placée volontairement dans le groupe `User-agent: *` et documentée en commentaire en tête du fichier.
  - Le validateur de Lighthouse ne la connaît pas.
  - Selon le RFC 9309 et la documentation de Google, **Google ignore les lignes qu'il ne reconnaît pas** : elle ne modifie ni `Disallow` ni `Allow`.
- **Preuve que Googlebot accède aux pages indexables** : inspection d'URL Search Console du 19/11 sur 10 pages (accueil, contact, agents IA, Casablanca, Rabat, article PME, services, chatbot WhatsApp, rejoignez-nous, devis). Pour toutes :
  - `robotsTxtState: ALLOWED` ;
  - `pageFetchState: SUCCESSFUL` ;
  - `indexingState: INDEXING_ALLOWED` ;
  - « Envoyée et indexée ».
- **Décision : aucune modification.** Ce n'est pas une anomalie pour Google. Retirer la ligne supprimerait votre préférence « ai-train=no » pour les robots qui la lisent. Le score SEO Lighthouse restera à 92 : c'est un faux positif connu de cet outil.

## 6. Formulaires, SEO, accessibilité

| Contrôle | Résultat |
|---|---|
| Formulaires contact, agents IA, rejoignez-nous (Playwright, sans envoi réel) | affichés, saisie OK, validation côté client identique avant/après (4 et 16 erreurs sur envoi vide), Turnstile présent, nonce chargé, 0 erreur JavaScript |
| Devis IA | application affichée, champs présents |
| Navigation | ouverture du méga-menu OK |
| CLS mobile, 3 passages par page | contact 0, agents IA 0, rejoignez-nous 0 |
| CLS desktop, 3 passages par page | contact 0, agents IA 0,0008, rejoignez-nous 0,009 à 0,013 (déjà 0,013 avant) |
| Captures avant/après, mobile et desktop | identiques au pixel près, sauf une bande de 22 × 5 px dans une image de robot sur `/agents-ia/` desktop (chargement d'image) |
| Contraste Casablanca | cause : la règle `.fi-city .sec > p a`, plus spécifique, écrasait le blanc de `.btn-primary` (ratio 1,41). Le même défaut existait sur Rabat. **Corrigé** ; accessibilité Casablanca : **96 → 100** |
| Contraste contact (trouvé pendant la vérification) | le bouton « Envoyer » avait un fond violet sans couleur de texte, donc noir par défaut (ratio 3,38). Blanc appliqué, comme sur rejoignez-nous ; accessibilité contact : **96 → 100** |
| Balises SEO sur 8 modèles | title, canonical, robots `index, follow`, 1 H1 et JSON-LD présents, identiques à l'état précédent |
| 70 tests d'indexation | **0 échec** (deux exécutions) |

**Suivi CrUX préparé : `perf/suivi_crux.py`.**
- Il interroge l'origine et chaque URL, sur mobile : LCP, FCP, CLS et INP au 75e centile, plus l'historique hebdomadaire.
- Il lui faut une clé « Chrome UX Report API ». Le formulaire sécurisé de cet environnement ne permet pas de l'enregistrer pour l'en-tête qu'exige cette API. Il faut donc l'ajouter dans les réglages de l'environnement, ou me la fournir pour une exécution locale via la variable `CRUX_API_KEY`. Elle n'est jamais écrite dans le dépôt.

## 7. Décision : « Valider la correction »

**Pas encore. Lancement recommandé à partir du 26/11**, si l'une des deux conditions suivantes est remplie :

- **Condition A** : PSI, encart « Découvrez ce que vivent vos utilisateurs », pour l'origine, ou CrUX via `suivi_crux.py`, montre un **LCP mobile au 75e centile ≤ 2,5 s** et en baisse.
- **Condition B** : vous avez tranché la question du cache Cloudflare (section 8). Si vous la refusez, lancer quand même la validation au 26/11.

**Raisons :**
1. Côté page, tout ce qui pouvait être corrigé sans toucher au suivi est corrigé et vérifié : 0 feuille bloquante sur les 100 URL, LCP labo de 1,2 à 1,4 s sur chaque modèle.
2. Le LCP terrain dépend aussi du **TTFB sur MISS**. Avec environ 70 % des affichages servis par l'origine, le 75e centile peut rester proche de 2,5 s.
3. Une validation lancée trop tôt échoue si le 75e centile reste au-dessus de 2,5 s pendant la fenêtre d'observation. Il faut alors attendre la fin de ses 28 jours avant de relancer.
4. Le LCP de groupe actuel (2,7 s) n'est que de 0,2 s au-dessus du seuil. Les gains de laboratoire (environ −1 s) rendent probable un passage sous 2,5 s, **sans garantie**.

**Procédure, le moment venu :**
1. Search Console > Signaux Web essentiels > Mobile > « Problème LCP : plus de 2,5 s ».
2. **Exporter** la liste et me l'envoyer pour le recoupement exact.
3. Cliquer **« Valider la correction »**.
4. Ne pas relancer pendant les 28 jours de suivi.

Le problème ne sera déclaré résolu qu'au statut **« Réussite »**.

## 8. Problèmes encore ouverts

| Problème | Impact | Ce qu'il faut |
|---|---|---|
| Environ 70 % des affichages HTML servis par l'origine (MISS / EXPIRED) | TTFB terrain de +0,3 à +0,7 s | **votre accord** pour une règle Cloudflare : clé de cache ignorant `gclid`, `gbraid`, `wbraid`, `fbclid`, `utm_*`, et/ou Tiered Cache. Mesure avant/après via les statistiques de cache |
| Environ 525 Ko de scripts Google (passerelle, GA4, Ads chargé deux fois) et pixel OpenAI | variabilité du LCP des pages à image | votre décision sur la passerelle (options V3) : hors périmètre ici |
| Liste exacte des 29 URL | recoupement | export Search Console |
| Données CrUX | suivi terrain | clé CrUX API |
| robots.txt `Content-Signal` | aucun pour Google ; score Lighthouse SEO 92 | rien (conserver) |
