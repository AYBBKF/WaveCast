# Flux Intelligent : suivi des leads, Google Ads et performance (V4)

Date : 18/11/2026. Branche `claude/vibrant-bohr-hczz37`.

**Aucune modification n'a été faite en production dans cette mission.** Le suivi des leads est prêt et testé en environnement isolé. Son déploiement attend votre autorisation (section 12).

## Résumé

| Étape du parcours | Mesurée aujourd'hui ? | Preuve / limite |
|---|---|---|
| Visiteur | **oui** | GA4 `page_view` 3 063, `session_start` 2 264 (18/10–16/11) |
| Source (canal, UTM, gclid) | **oui** | GA4 Paid Search 236 sessions. gclid relevé par GA4 et par la passerelle Ads. Le devis IA enregistre aussi UTM, gclid, gbraid et wbraid côté serveur. |
| Début de formulaire | partiel | GA4 `form_start` 60 (mesure améliorée). Le devis n'a pas d'étape « ouverture » ni « début de saisie ». |
| **Lead confirmé** | **non** | aucun `generate_lead` dans GA4. Site Kit `detectedEvents` est vide : Forminator et le devis IA ne sont pas pris en charge. |
| Conversion Google Ads | **non vérifiable** | les actions de conversion Ads n'ont pas encore pu être lues : connexion Google Ads à finaliser (section 2) |

**Après déploiement du script prêt**, les quatre premières étapes seront mesurées dans GA4. La cinquième le sera après l'import de `generate_lead` dans Ads, à faire en mode observation.

---

## 1. Architecture de suivi actuelle

```
Navigateur
 ├─ Site Kit : gtag.js?id=GT-PZQ8SJ83 → GA4 G-1JX1J3TWVZ (+ config AW-18347114778)
 ├─ Passerelle Cloudflare (Google tag gateway, injectée à l'edge dans le HTML) :
 │    /0tqe/ → conteneur AW-18347114778 en first-party, hits /0tqe/gs/ccm/collect
 ├─ Consent Mode (Site Kit) : refusé par défaut EEE/UK/CH, accordé au Maroc
 ├─ Forminator 3117 (/ia/contact/) : AJAX + Turnstile
 ├─ Devis IA (/ia/devis/, plugin fdi) : fdi_partiel → fdi_final (reCAPTCHA), PDF + SMTP côté serveur
 └─ Pixel OpenAI (debug: true)
```

- **Constat sur la double charge :** le conteneur Ads est chargé deux fois, par la passerelle (`/0tqe/`) et par la commande `config AW` de Site Kit. Conséquence : tout `gtag('event')` sans `send_to` part **aussi vers Ads**. Les essais l'ont montré : chaque événement a été envoyé 2 fois à `/0tqe/gs/ccm/collect`.
- **Correction :** le script V4 envoie uniquement vers GA4 (`send_to: 'G-1JX1J3TWVZ'`).

## 2. Inventaire : conversions Ads et événements GA4

**GA4 (propriété 518722756), données lues :**

| Élément | État |
|---|---|
| Événements clés | `purchase` seulement (sans objet sur ce site) |
| Événements 18/10–16/11 | page_view 3 063, session_start 2 264, first_visit 1 938, user_engagement 1 794, scroll 458, **form_start 60**, click 45 |
| `generate_lead` / `form_submit` | **absents** |
| Conversion tracking Site Kit | activé, mais aucun événement détecté pour ces deux formulaires |

**Google Ads (AW-18347114778) : non lu.**

Le connecteur Composio Google Ads n'est pas actif. **Je ne conclus donc pas que Ads ne suit aucun lead.** Une action de conversion peut exister, par exemple :
- une balise « Envoi de formulaire » créée dans Ads ;
- un import GA4 ;
- un objectif « appels » ;
- une détection automatique de la passerelle (`google_tags_first_party`).

**Ce que la lecture vérifiera dès la connexion** (requête GAQL `conversion_action`) :
- nom, statut, catégorie, origine (WEBPAGE / GOOGLE_ANALYTICS_4 / …) ;
- `primary_for_goal` et `counting_type` ;
- les liens GA4 ↔ Ads côté GA4 (`googleAdsLinks`) ;
- les événements clés.

Aucune preuve indirecte n'est retenue : l'absence de `generate_lead` dans GA4 ne dit rien des actions de conversion Ads.

## 3. Problèmes confirmés

1. **Aucun lead confirmé n'est mesuré dans GA4** : ni le formulaire de contact, ni le devis IA.
2. **Double chargement du conteneur Ads** : sans `send_to`, tout événement personnalisé serait **compté deux fois côté Ads**. Les essais ont montré deux hits par événement.
3. **Événements clés GA4 inadaptés** : seul `purchase` est déclaré.
4. **Pixel OpenAI en `debug: true` en production.** Ce n'est pas bloquant pour le suivi, mais ce mode est à désactiver (décision 12.5).
5. **Non vérifiable faute d'accès** : les actions de conversion Ads et leur statut Principale/Secondaire.

## 4. Événements ajoutés ou préparés

**Fichier :** `tracking/fi-lead-tracking.js` (76 lignes, autonome, sans dépendance). Statut : **préparé, non déployé.**

| Événement | Déclencheur | Paramètres (aucune donnée personnelle) | Rôle |
|---|---|---|---|
| `generate_lead` | Forminator `forminator:form:submit:success`, émis **seulement** après une réponse serveur `success:true` | `lead_source=formulaire_contact`, `form_id=forminator_3117`, `method=forminator`, `page_path` | **Lead** |
| `generate_lead` | réponse `fdi_final` avec `success:true` (observation du `fetch` du plugin, plugin non modifié) | `lead_source=devis_ia`, `form_id=devis_ia`, `method=devis_ia`, `page_path` | **Lead** |
| `contact_submit_error` | Forminator `submit:failed` (refus serveur, 500) | `form_id` | diagnostic |
| `devis_open` | présence de `#fdi-app` (1 fois par session et par page) | `form_id` | entonnoir |
| `devis_start` | première saisie | `form_id` | entonnoir |
| `devis_contact_saved` | `fdi_partiel` avec succès (1 fois par `lead_id`) | `form_id` | entonnoir |
| `devis_submit_error` | `fdi_final` en échec | `error_type` : `serveur`, `reponse_invalide` ou `reseau` | diagnostic |
| `click_phone` | clic sur un lien `tel:` | `link_location` : entete, pied ou contenu | **intention, pas un lead** |
| `click_whatsapp` | clic sur `wa.me`, `api.whatsapp.com` ou `whatsapp://` | `link_location` | **intention, pas un lead** |

**Garanties :**
- **Aucune donnée personnelle** : jamais de nom, d'e-mail, de téléphone, de message ou de numéro composé.
- **Attribution :**
  - GA4 relève lui-même UTM, gclid, gbraid et wbraid à l'arrivée ; le lead hérite de la session.
  - Le devis continue d'enregistrer ces identifiants côté serveur ; il n'est pas modifié.
- **Consent Mode :** l'envoi passe uniquement par `gtag()`. Le consentement Site Kit s'applique donc sans changement : en cas de refus, GA4 reçoit des pings sans cookie (modélisation), jamais d'identifiant.
- **Génération PDF, e-mails SMTP et données clients :** non touchés. Le script lit une **copie** de la réponse (`r.clone()`) et rend la réponse d'origine intacte au plugin.

**Mode de déploiement proposé** (au choix, section 12.1) : un petit extrait chargé dans le pied de page, uniquement sur `/ia/contact/` et `/ia/devis/`, plus le suivi des clics sur tout le site. Deux moyens :
- un mu-plugin de 10 lignes qui met le fichier en file d'attente après `google_gtagjs` ;
- ou l'ajout du fichier via WPCode, s'il est installé.

**Retour arrière :** supprimer le mu-plugin.

## 5. Résultats des tests

**Méthode :** `tracking/test-lead-tracking.cjs`, Playwright, sans aucune vraie soumission.
- Les **vraies pages** sont chargées (Site Kit, passerelle, Forminator, plugin devis réels).
- Le script est injecté localement.
- **Tous les POST `admin-ajax` sont simulés** : aucun e-mail, aucun PDF, aucun enregistrement en base.
- Turnstile est remplacé par un bouchon qui crée le champ `forminator-turnstile-response`.
- **Toutes les requêtes de collecte Google sont relevées puis bloquées** : aucune fausse conversion n'atteint GA4 ni Ads.

Résultats bruts : `tracking/resultats-tests-isoles.json`.

| Scénario | Requêtes AJAX simulées | Événements émis | Hits relevés (bloqués) | Verdict |
|---|---|---|---|---|
| Contact : succès, **puis second clic** sur Envoyer | nonce, 1 soumission | `generate_lead` ×1 | GA4 ×1 (+ copie google.com/g/collect, voir 6) ; **0 vers Ads** | ✅ |
| Contact : refus serveur (`success:false`) | nonce, soumission | `contact_submit_error` | GA4 | ✅ pas de lead |
| Contact : erreur 500 | nonce, soumission | `contact_submit_error` | GA4 | ✅ pas de lead |
| Contact : formulaire invalide (e-mail vide) | nonce seulement, **aucune soumission** | aucun | aucun | ✅ |
| Contact : rechargement de page | 2 nonces | aucun | aucun | ✅ |
| Devis : succès, avec **double** `fdi_final` | partiel, final, final | open, start, contact_saved, **`generate_lead` ×1** | GA4 | ✅ dédoublonné |
| Devis : échec serveur | partiel, final ×2 | … `devis_submit_error` ×2 | GA4 | ✅ pas de lead (2 tentatives = 2 erreurs) |
| Devis : coupure réseau | partiel, final ×2 avortés | … `devis_submit_error` ×2 (`reseau`) | GA4 | ✅ pas de lead |
| Clics : téléphone ×2 et WhatsApp ×1 | – | `click_phone` ×1, `click_whatsapp` ×1 | GA4 | ✅ double clic dédoublonné |

**Limites des tests :**
- Le chemin de validation **réel** de Turnstile et de reCAPTCHA n'est pas exercé, par construction : ils sont simulés.
- DebugView n'a pas été utilisé : aucun accès GA4 actif dans cette session, et l'utiliser aurait imposé d'envoyer de vrais hits.
- **Contrôle post-déploiement prévu :**
  - une vraie soumission de contact, signalée « TEST » ;
  - un vrai devis de test ;
  - avec `?debug_mode=1` et DebugView ;
  - ces leads de test seront supprimés côté WordPress et exclus de GA4 via le filtre de trafic interne ou développeur ;
  - à faire avec votre accord, car cela crée un e-mail et un PDF réels.
- **Consentement refusé (EEE)** : le comportement découle de Consent Mode (`gtag` inchangé) mais n'a pas été simulé séparément, car l'environnement de test est géolocalisé hors EEE.

## 6. Protection contre les doublons

| Risque | Protection |
|---|---|
| Événement envoyé deux fois à Ads (conteneur AW chargé deux fois) | `send_to: 'G-1JX1J3TWVZ'` : GA4 seulement. Ads recevra le lead **uniquement par import GA4**. |
| Double clic, double soumission | fenêtre de 4 s par formulaire (Forminator) ; 1 lead par `lead_id` et par session (devis) |
| Rechargement de la page de succès | aucun déclenchement au chargement : uniquement sur la réponse serveur |
| Script chargé deux fois | verrou `window.__fiLeadTracking` |
| Double comptage dans Ads (balise Ads « formulaire » existante + import GA4) | **à vérifier dès la lecture Ads** : s'il existe déjà une action Principale sur les formulaires, l'import GA4 reste **Secondaire** |
| Copie `www.google.com/g/collect` | ce n'est **pas** un doublon : c'est le flux Google Signals/Ads de la même balise GA4 (même `tid`), dédoublonné par Google. GA4 compte 1 événement. |
| Comptage dans Ads | action importée avec le comptage **« Une »** (une conversion par clic d'annonce) |

## 7. Passerelle Google Tag Gateway : comparaison (données V3 du 18/11, simulation Pixel 5, CPU ×4, 3 passages)

| | TBT (ms) | JS | Hits Ads | GA4 | Risque |
|---|---|---|---|---|---|
| Actuel | 922 / 789 / 913 | 623 Ko | 3/3 (via google.com) | 3/3 | conteneur AW chargé 2 fois |
| **Option A : garder la passerelle, chargement propre** (A2 : retirer `config AW` de Site Kit, la config étant portée par la passerelle) | 687 / 759 / 806 | 623 Ko | 3/3 first-party `/0tqe/gs` | 3/3 | **expérimental** : dépend du comportement non documenté de `setUpTag=false`. Le simple retrait de `config AW` (variante A) a **cassé** Ads : 0/3. |
| **Option B : désactiver la passerelle, garder Site Kit** (C) | 600 / 491 / 674 | 423 Ko (−200 Ko) | 3/3 | 3/3 | perte de la mesure first-party (adblockers, ITP), donc un peu moins de conversions Ads attribuées |
| A3 : GA4 via `/0tqe/?id=GT` | 940 / 977 | 445 Ko | 3/3 | first-party | aucun gain de TBT |

**Recommandation : Option B (désactivation) si l'objectif prioritaire est la performance**, avec 2 conditions :
1. Ads doit recevoir les leads par l'import GA4 : il n'a pas besoin de la passerelle pour cela.
2. Comparer pendant 14 jours les conversions Ads et les clics gclid avant et après.

Sinon, Option A2, mais seulement après un test sur une page isolée, car elle est fragile. Le TBT est une **mesure de laboratoire**, pas de l'INP terrain.

**Aucune modification de la passerelle n'a été faite** (décision 12.3).

## 8. Performance avant/après

Lighthouse mobile, médiane de 3 passages, 18/11. **« Après » : rien n'est déployé, il n'y a donc pas de mesure après.**

| Page | Score | LCP | TBT | Poids |
|---|---|---|---|---|
| Accueil | 78 | 2 289 ms | 566 ms | 888 Ko |
| /automatisation-des-processus/ | 82 | 2 226 ms | 548 ms | – |
| Casablanca | 79 | **3 588 ms** | 351 ms | – |
| Contact | 81 | 2 965 ms | 382 ms | **2 772 Ko** |
| Devis | 81 | 2 248 ms | 578 ms | – |

- CLS 0 partout.
- Cache HTML : actif et sûr (HIT, TTFB 0,09 à 0,28 s). **Non reconfiguré.**

## 9. Casablanca et Contact

**Casablanca (LCP 3,6 s) : correctif préparé, non appliqué.**
- **Diagnostic :** l'élément LCP est le **H1** (texte), avec un retard de rendu de 2,9 s. La police du H1 est « Public Sans », chargée depuis Google Fonts (CSS bloquant, puis fichier woff2 depuis fonts.gstatic.com), alors que les autres polices sont auto-hébergées et préchargées.
- **Correctif ciblé**, sans changement visuel :
  1. héberger localement « Public Sans » (mêmes graisses, mêmes sous-ensembles) dans le dossier des polices déjà utilisé ;
  2. la précharger (`<link rel="preload" as="font" crossorigin>`) uniquement sur cette page ;
  3. retirer la feuille Google Fonts de cette page.
  - `font-display: swap` conservé ; aucune autre règle CSS modifiée.
- **Gain attendu :** suppression de 2 connexions tierces sur le chemin critique. Le LCP devrait passer sous 2,5 s, **à confirmer par mesure** après accord.
- **Retour arrière :** restaurer l'appel Google Fonts.

**Contact (2,7 Mo, dont Turnstile ≈ 1,5 Mo) : étude, rien appliqué.**
- L'antispam est **conservé**.
- **Option proposée :** charger Turnstile **au premier contact avec le formulaire** (focus ou `pointerdown` sur un champ), et non au chargement de la page. Forminator expose `forminator_render_turnstile`, que le test a utilisé.
- **Risque :** si un robot soumet sans interaction, le champ `forminator-turnstile-response` reste vide et Forminator **refuse côté serveur**. La protection est donc maintenue.
- **Gain attendu :** environ −1,5 Mo et moins de JS au chargement.
- **Avant tout déploiement :** mesures avant/après et test des 5 scénarios de la section 5. Nécessite votre accord (12.4).

## 10. Les 12 pages non indexées

Il n'y a aucune nouvelle action et aucun changement de contenu. L'état de référence est celui de `PAGES-NON-INDEXEES.md` :
- P1 et rapprochement-COD : indexées (relevé du 18/11) ;
- les autres : en attente d'exploration.

Les contrôles GSC via Composio restent programmés au **01/12 et au 22/12**. Coach et Salon restent en attente de la validation Surfer 80–90 et de la vôtre.

## 11. Changements déployés et non déployés

| Élément | Statut |
|---|---|
| Script de suivi des leads `tracking/fi-lead-tracking.js` | **non déployé** : prêt, testé |
| Harnais de test `tracking/test-lead-tracking.cjs` + résultats | livré (dépôt) |
| Événements clés GA4, import Ads | **non faits** : accès GA4/Ads à connecter, puis votre accord |
| Passerelle Cloudflare | **inchangée** |
| Cache HTML | **inchangé** |
| Casablanca, police locale | **non déployé** |
| Contact, Turnstile différé | **non déployé** (étude) |
| Pixel OpenAI `debug: true` | **inchangé** (signalé) |

## 12. Décisions à autoriser

1. **Déployer le suivi des leads en production.**
   - Quoi : un mu-plugin `fi-lead-tracking.php` qui charge `fi-lead-tracking.js` en pied de page.
   - Sauvegarde : l'état actuel, qui ne contient aucun fichier.
   - Vérification : 1 contact et 1 devis de test en DebugView, puis suppression des leads de test.
   - Retour arrière : supprimer le fichier.
2. **GA4 et Ads** (après la connexion Composio et la lecture de l'existant) :
   - marquer `generate_lead` comme **événement clé** dans GA4 ;
   - **importer** `generate_lead` dans Ads comme conversion **Secondaire** (observation), comptage **« Une »**, fenêtre 30 jours ;
   - `click_whatsapp` et `click_phone` : événements clés GA4 facultatifs. Dans Ads, ils seraient **Secondaires**, jamais Principaux.
   - Aucune action ne devient Principale et aucune enchère n'est modifiée sans un second accord, idéalement après 2 à 4 semaines d'observation.
3. **Passerelle** : Option B (désactiver) ou garder l'état actuel. Option A2 seulement après un test isolé.
4. **Contact** : Turnstile différé au premier focus.
5. **Pixel OpenAI** : passer `debug` à `false`.
6. **Casablanca** : police Public Sans locale et préchargée.

## 13. Plan de retour arrière

| Changement | Retour arrière | Délai |
|---|---|---|
| mu-plugin de suivi | supprimer `wp-content/mu-plugins/fi-lead-tracking.php` (et son .js), puis purge ciblée des 2 URL | < 2 min |
| Événement clé GA4 | Admin > Événements > décocher « événement clé » | immédiat |
| Conversion Ads importée | statut « Masquée » ou suppression, ou repasser en Secondaire | immédiat |
| Passerelle | remettre `enabled: true` via l'API (configuration sauvegardée dans `backup/cloudflare/`) | < 5 min |
| Turnstile différé | retirer le petit script de chargement | < 2 min |
| Police Casablanca | restaurer l'appel Google Fonts | < 2 min |

**Critère de retour arrière :** toute hausse d'erreurs de formulaire, toute baisse des `page_view` GA4 de plus de 10 % sur 48 h, ou tout lead réel non reçu par e-mail.

---

### Accès à finaliser

- Connecteurs Composio **Google Ads** et **Google Analytics** : les liens d'autorisation sont dans le message de la session.
- Côté Cloudflare, toujours à faire par vous :
  - révoquer les jetons Cloudflare temporaires ;
  - supprimer les secrets réseau `fluxintelligent.com` et `api.cloudflare.com` de l'environnement Default.
