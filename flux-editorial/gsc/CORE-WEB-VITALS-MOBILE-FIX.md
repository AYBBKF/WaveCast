# Core Web Vitals mobile : correction FCP / LCP

Date : 19/11/2026.

**Statut : corrections déployées en production. Le problème n'est PAS déclaré résolu.** Seules les données terrain (CrUX, Search Console) pourront le confirmer, sur une fenêtre glissante de 28 jours.

Périmètre respecté : aucune modification de Google Ads, GA4, Google Tag Gateway, des conversions ou du cache Cloudflare (purges ciblées par URL uniquement).

---

## 1. Diagnostic de l'accueil

**Élément LCP exact :**
- ce n'est **pas une image** ;
- c'est le paragraphe d'introduction du hero, `section.fi-hero > div.wrap > div > p.lead` (« Flux Intelligent est l'agence IA au Maroc qui conçoit, déploie et optimise… ») ;
- sur mobile, il est plus grand à l'écran que le H1.

**Décomposition du LCP** (Lighthouse mobile, avant correction) :

| Phase | Durée | Part |
|---|---|---|
| TTFB | 1 060 ms | 39 % |
| Délai de chargement / chargement | 0 ms | 0 % (texte) |
| **Délai de rendu** | **1 686 ms** | **61 %** |

**Pourquoi le premier contenu n'apparaît qu'après environ 3,3 s (PSI) :**

1. **Rien ne peut être peint avant 3 feuilles CSS bloquantes**, demandées seulement *après* la réception du HTML :
   - `block-library/common.min.css` ;
   - `fi-css/global-styles-….css` ;
   - `main.css`.
   - Elles sont petites (15 Ko compressés au total) : le coût vient de l'**aller-retour réseau** supplémentaire, que la simulation 4G lente de PSI pénalise fortement, et pas de leur poids.
   - Chaîne critique mesurée : HTML (fin à 1,1 s), puis CSS (fin à 2,0 s), puis polices.
   - Le FCP et le LCP sont donc quasi simultanés : texte, donc pas d'image à attendre.
2. **TTFB :** le HTML sort du cache Cloudflare quand il y est (HIT, 0,09 à 0,28 s, mesuré le 18/11 depuis un réseau externe). Sinon l'origine Hostinger répond en 0,35 à 0,9 s. Les URL peu visitées repassent souvent par l'origine, car le cache périphérique expire au bout de 2 h.
3. **Pages villes et `/rejoignez-nous/` :** une feuille **Google Fonts** (Space Grotesk et Public Sans) est insérée dans le contenu, dans le `<body>`.
   - C'est une ressource tierce bloquante : DNS, TLS, puis CSS, puis woff2 sur fonts.gstatic.com.
   - Le H1 et les paragraphes de ces pages en dépendent.
4. **JavaScript : ce n'est pas la cause principale du FCP et du LCP.**
   - PSI mesure un TBT de 20 ms. Le TBT de 550 à 850 ms mesuré ici vient du processeur lent de cet environnement de test, pas d'une régression : il n'est pas utilisé comme critère.
   - En revanche, environ **525 Ko de scripts Google** (passerelle `/0tqe/`, gtag GA4, gtag Ads) **se disputent la bande passante** avec l'image LCP des articles (section 7).
5. **Polices :** `font-display: swap` est partout, donc elles ne bloquent pas le texte. La police Inter 400 du `p.lead` est déjà préchargée.

## 2. Les 29 URL du groupe Search Console

**Non récupérables par API.** L'API Search Console (Composio) n'expose pas le rapport Signaux Web essentiels, et l'API PageSpeed/CrUX est hors quota sans clé.

**Modèles probables**, d'après le LCP de groupe de 2,7 s et la structure du site (à confirmer avec l'export) :

| Modèle WordPress | Pages | Cause identifiée | Corrigé |
|---|---|---|---|
| Accueil `front-page.php` | 1 | chaîne CSS bloquante | ✅ |
| Pages villes (canevas avec `<style>` dans le contenu) | 9 (Casablanca, Rabat, Marrakech, Tanger, Fès, Agadir, Oujda, Meknès, Tétouan) | chaîne CSS + **Google Fonts tierce** | ✅ |
| Pages de service et hubs (`page.php`, `service.php`) | environ 15 | chaîne CSS bloquante | ✅ |
| Articles (`single.php`) | ~55 | chaîne CSS ; LCP = image à la une, ralentie par les scripts Google | ✅ (CSS) ; ⚠️ scripts : hors périmètre |
| Pages avec formulaire Forminator : `/ia/contact/`, `/agents-ia/`, `/rejoignez-nous/` | 3 | 11 à 15 feuilles CSS (190 Ko) | ❌ volontairement exclues (section 6) ; `/rejoignez-nous/` profite des polices locales |

**À faire par vous :** Search Console > Signaux Web essentiels > Mobile > « Problème LCP : plus de 2,5 s » > ouvrir le groupe > **Exporter**. Avec l'export, je vérifierai que chaque URL est couverte.

## 3. Terrain et laboratoire : deux mesures distinctes

| | Données terrain (Search Console / CrUX) | Laboratoire (PSI, Lighthouse) |
|---|---|---|
| Source | vrais visiteurs Chrome, 28 jours glissants, 75e centile | 1 chargement simulé (Moto G, 4G lente, processeur ×4) |
| Valeur actuelle | LCP de groupe 2,7 s (29 URL, avant correction) | PSI du 19/11, avant correction : FCP 3,3 s, LCP 3,3 s, Speed Index 4,5 s, TBT 20 ms |
| Réaction aux corrections | progressive, sur environ 28 jours | immédiate |

Les mesures ci-dessous sont des mesures **de laboratoire** (Lighthouse 12, mobile, passages multiples, médiane).

**Limite :** depuis cet environnement, le cache HTML Cloudflare est contourné, car le proxy ajoute un en-tête `Authorization`. Le TTFB mesuré ici (0,5 à 0,6 s) est donc **plus pessimiste** que pour un visiteur servi depuis le cache. Les comparaisons avant/après restent valides : mêmes conditions des deux côtés.

## 4. Modifications appliquées

Les deux modifications sont des mu-plugins neufs : aucun fichier existant n'a été modifié, ni thème, ni extension, ni cœur WordPress.

### 4.1 `wp-content/mu-plugins/fi-perf-inline-css.php` (source : `perf/fi-perf-inline-css.php`)

- Les feuilles **locales** bloquantes sont imprimées en ligne dans le `<head>` : même contenu, même ordre, mêmes priorités. Seuls les `url()` relatifs deviennent absolus.
- **Tout ou rien :**
  - la décision se prend sur le HTML final, après la remontée par WordPress des styles imprimés en pied de page ;
  - s'il reste une feuille `<link>` bloquante, les balises d'origine sont **restaurées** et la page est servie comme avant.
- **Budget :** 120 Ko non compressés au maximum, 60 Ko par fichier.
- **HTML :** +13 à 19 Ko compressés par page, contre 3 à 5 requêtes CSS en moins (environ 15 Ko). L'effet sur le poids d'une première visite est neutre.
- Le mode de test `?fi_inline=1` / `?fi_inline=2` reste dans le code, mais il est inactif en production.

### 4.2 `wp-content/mu-plugins/fi-perf-local-fonts.php` (source : `perf/fi-perf-local-fonts.php`)

- Ne s'applique qu'aux 10 pages dont le contenu appelle `fonts.googleapis.com` (Space Grotesk 500/600/700 et Public Sans 400/500/600).
- Le `<link>` Google Fonts est retiré du contenu et remplacé, dans le `<head>`, par les **mêmes fichiers woff2** servis depuis `wp-content/uploads/fi-fonts/` :
  - 6 fichiers ;
  - sous-ensembles latin, latin-ext et vietnamien ;
  - unicode-range et `font-display: swap` identiques.
  - Copie dans `perf/fi-fonts/`.
- Les 2 fichiers latins sont **préchargés**.
- Licence : SIL Open Font License, auto-hébergement autorisé.

### 4.3 Purge

- Purge Cloudflare **par URL** des 100 URL des sitemaps (4 lots de 30, tous réussis).
- Pas de « Purge Everything ». Règles de cache inchangées.

### 4.4 Essayé puis annulé

- **Priorité normale pour le logo sur les articles :** aucun effet mesurable (Chrome garde l'image en priorité haute). Retiré.
- **Mise en ligne de toutes les feuilles sur contact (11 feuilles) :** LCP 2,3 → 1,2 s, mais **CLS 0,127**. Le bloc WhatsApp/téléphone se décale quand le formulaire se construit. **Non déployé.**

## 5. Résultats avant/après (laboratoire)

Lighthouse mobile, médianes. A = état d'origine, B = corrections, mesurés en alternance dans les mêmes conditions. Prod = après déploiement.

| Page (modèle) | Passages | FCP avant → après | LCP avant → après | Speed Index avant → après | CLS |
|---|---|---|---|---|---|
| Accueil | 5 A / 5 B / 5 prod | 2 117 → **1 022 ms** | 2 196 → **1 228 ms** | 2 955 → **2 243 ms** | 0 → 0 |
| Casablanca (ville) | 3 / 3 / 3 | 2 232 → **1 041 ms** | 2 921 → **1 235 ms** | 3 160 → **2 341 ms** | 0 → 0 |
| Rabat (ville) | 3 / 3 | 2 220 → **1 033 ms** | 2 740 → **1 190 ms** | 3 197 → **2 089 ms** | 0 → 0 |
| Marrakech (ville), prod | 3 | – → 1 030 ms | – → **1 236 ms** | – → 2 148 ms | 0 |
| Services (page) | 3 prod | – → 1 052 ms | – → **1 263 ms** | – → 2 157 ms | 0 |
| Article `/automatisation-ia-pme-maroc/` | 3 / 3 / 5 | 2 250 → **1 012 ms** | 2 250 → **2 300 à 2 900 ms** (variable) | 2 965 → **2 108 ms** | 0 → 0 |
| Article `/agent-ia-whatsapp-business-pme-maroc/` | 5 prod | – → 1 043 ms | – → **1 134 ms** | – → 2 072 ms | 0 |
| Contact (exclu) | 3 | 2 199 (inchangé) | 2 343 (inchangé) | 4 039 | 0 |

Résultats bruts : `perf/resultats-cwv-2026-11-19.txt`.

**Écart avec PSI :** PSI mesurait 3,3 s pour le FCP et le LCP. Son TTFB et sa localisation diffèrent de cet environnement. L'aller-retour CSS supprimé est toutefois le même : un gain du même ordre est attendu (environ −1 s sur le FCP et le LCP en laboratoire). **Aucun score PSI précis n'est garanti.**

## 6. Contrôles de non-régression

| Contrôle | Résultat |
|---|---|
| Rendu visuel : 6 modèles × mobile et desktop, captures A/B | **11 sur 12 identiques au pixel près.** Seul écart : 22 × 5 px dans l'image d'un robot sur `/agents-ia/` desktop (chargement d'image, sans lien avec le CSS) |
| Balises SEO (title, description, robots, canonical, H1, JSON-LD) | **identiques** sur 4 modèles |
| Contenu du `<body>` | identique ; seule différence sur les pages villes : le `<link>` Google Fonts retiré |
| Polices des pages villes | H1 en « Space Grotesk », polices Space Grotesk et Public Sans chargées depuis le site |
| Formulaires | Forminator (contact, agents IA) non touché. Devis IA : application `#fdi-app` affichée et champs présents. Menu : ouverture du méga-menu OK. Aucune erreur JavaScript. |
| Accessibilité (Lighthouse) | accueil 100 ; Casablanca 96 (contraste de couleurs, réglé dans le CSS du contenu de la page, que ces plugins ne modifient pas) |
| SEO (Lighthouse) | 92 : seul le contrôle `robots.txt` échoue. robots.txt n'a pas été touché, mais je n'ai pas pu vérifier si ce contrôle échouait déjà avant : non résolu |
| 70 tests d'indexation | **0 échec** |

## 7. Problèmes restants

1. **Pages avec formulaire** (`/ia/contact/`, `/agents-ia/`, `/rejoignez-nous/`) : LCP labo environ 2,3 à 2,4 s, FCP environ 2,2 s.
   - Correction possible : mettre aussi en ligne les CSS Forminator (testé : LCP 1,2 s) **et** réserver la hauteur du formulaire pour supprimer le CLS de 0,127.
   - Ce point demande un test dédié du formulaire : **non fait ici**.
2. **Articles dont le LCP est l'image à la une :** l'image est légère (8 Ko), mais elle est ralentie par environ 525 Ko de scripts Google chargés en parallèle. Le conteneur Ads est chargé deux fois (passerelle `/0tqe/` et gtag Site Kit).
   - C'est l'option « désactiver la passerelle » déjà documentée en V3/V4 (−200 Ko de JS).
   - **Hors périmètre : votre décision.**
3. **Pixel OpenAI** (`oaiq.min.js`, 37 Ko, encore en `debug: true`) : même nature, non touché.
4. **TTFB quand la page n'est pas en cache :** 0,35 à 0,9 s à l'origine.
   - Leviers possibles : Tiered Cache ou cache d'origine (LiteSpeed / Hostinger).
   - Le cache Cloudflare n'a pas été reconfiguré, conformément à la consigne.
5. Les **données terrain** ne bougeront qu'à mesure que les 28 jours CrUX se renouvellent.

## 8. Procédure « Valider la correction » (à lancer par vous)

L'API ne permet pas de lancer une validation.

1. **Attendre au moins 7 jours, jusqu'au 26/11,** pour que les visites post-correction pèsent dans CrUX. Vérifier dans PSI, encart « Découvrez ce que vivent vos utilisateurs », que le LCP au 75e centile de l'accueil et d'une page ville passe sous 2,5 s.
2. Search Console > **Signaux Web essentiels** > **Mobile** > **Ouvrir le rapport** > ligne « Problème LCP : plus de 2,5 s (mobile) ».
3. **Exporter** la liste des URL et me l'envoyer : je confirme la couverture, et les éventuelles pages avec formulaire restantes.
4. Cliquer **« Valider la correction »**. Google observe alors les données terrain pendant **28 jours**. Ne pas relancer pendant la validation.
5. Issue :
   - « Réussite » : le groupe passe en « Bon » ;
   - « Échec » : je reprends avec la liste des URL encore lentes.

**Ne pas considérer le problème comme résolu avant « Réussite ».**

## 9. Sauvegardes et retour arrière

| Élément | État avant | Retour arrière |
|---|---|---|
| `mu-plugins/fi-perf-inline-css.php` | n'existait pas | supprimer ou renommer en `.off`, puis purger les URL |
| `mu-plugins/fi-perf-local-fonts.php` | n'existait pas | idem ; le `<link>` Google Fonts du contenu revient tel quel (le contenu n'a pas été modifié en base) |
| `uploads/fi-fonts/` (7 fichiers) | n'existait pas | peut rester ou être supprimé après le retour arrière |

- Désactivation sans suppression : définir `FI_INLINE_CSS_MODE` / `FI_LOCAL_FONTS_MODE` à `'off'` (constante dans le fichier ou dans `wp-config.php`).
- **Critère de retour arrière :**
  - régression visuelle signalée ;
  - CLS terrain supérieur à 0,1 ;
  - erreur de formulaire ;
  - LCP terrain en hausse 14 jours après le déploiement.

**Scripts de test :** `perf/vis.cjs` (captures A/B), `perf/fn.cjs` (contrôles fonctionnels), `perf/summ.py` (médianes Lighthouse).
