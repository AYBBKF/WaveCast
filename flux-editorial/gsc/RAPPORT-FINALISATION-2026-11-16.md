# Finalisation des corrections SEO : fluxintelligent.com (16/11/2026, après-midi)

Fait suite à `RAPPORT-GSC-2026-11-16.md`. L'audit n'a pas été refait. Seuls les points restants ont été traités.

## Synthèse

| Point | Résultat |
|---|---|
| 1. Sitemap public | **Résolu publiquement** : `post-sitemap.xml` sert 55 URL sans 3092 ni 3288, pour un navigateur, Googlebot et curl. L'exclusion durable du cache long reste **à appliquer** (accès admin ou Cloudflare). |
| 2. Page 4473 | **Décision : rester en noindex.** Le retrait du sitemap reste **à faire** dans Rank Math. |
| 3. Redirection factures | Équivalence **confirmée**. Correction **à faire** dans Rank Math. |
| 4. Liens internes 4100 et 4009 | Localisés (1 lien par page). **Non modifiés** : aucune voie d'édition ciblée disponible. |
| 5. Réponses 500 | **Non reproduites** : 0 sur 192 requêtes contrôlées. Couche identifiée : origine Hostinger (LiteSpeed et PHP). Aucune cause de code établie. |
| 6. Search Console | **Toujours inaccessible.** Demande d'export ci-dessous. Aucune validation lancée. |

**Accès indispensables manquants :**
1. **wp-admin.** Le connecteur Hostinger demande une réauthentification. Le mot de passe d'application a bien été enregistré, mais le serveur supprime l'en-tête `Authorization` : voir `a-appliquer/htaccess-authorization.md`.
2. **Cloudflare**, zone fluxintelligent.com : aucune intégration disponible.
3. **Search Console** : propriété absente du compte Google relié.

## 1. Sitemap

**Version servie au moment du contrôle (15:20 GMT) :**
- `post-sitemap.xml` : HTTP 200, 55 `<loc>`, 0 occurrence de `automatisation-entreprise-maroc` ou de `ia-hotels-tourisme-maroc-2026`, identique pour les trois user-agents.
- À 11:40, la même URL en listait encore 57.
- Test ajouté au jeu de tests : « post-sitemap.xml public sans 3092 ni 3288 », **OK**.

**Couche responsable de la version obsolète : Cloudflare.**
- Les serveurs DNS sont `armfazh` et `tessa.ns.cloudflare.com`, donc la zone Cloudflare appartient au site.
- Les en-têtes montrent `cf-cache-status: HIT` puis `EXPIRED`, avec `age`, sur le HTML, les XML et robots.txt.
- Rank Math n'envoie pas de `Cache-Control` sur les sitemaps. Seuls `Pragma: public` et `Expires: 0` sont présents.
- La réponse reçoit donc `max-age=14400` (4 h), qui correspond au TTL navigateur par défaut de Cloudflare. Le cache serveur LiteSpeed de Hostinger est aussi actif (`x-turbo-charged-by: LiteSpeed`).
- Ce n'est pas Rank Math : une requête avec un paramètre de contournement renvoyait déjà la version corrigée à 11:40.

**Purge :** non effectuée. Le connecteur Hostinger demande une réauthentification, et je n'ai pas d'accès à l'API Cloudflare. L'expiration naturelle a fait le travail.

**Exclusion durable, prête à appliquer :** une seule des deux options suffit.
- `a-appliquer/cloudflare-regle-cache-sitemaps.md` : règle de cache Cloudflare à 5 minutes, limitée aux sitemaps.
- `a-appliquer/snippet-cache-sitemaps.php` : snippet Code Snippets qui envoie `Cache-Control: max-age=300` et exclut les sitemaps du cache LiteSpeed. Le reste du site n'est pas touché.

Test ajouté : « durée de cache ≤ 3600 s » sur les 3 sitemaps, **en échec** tant que l'une des deux options n'est pas appliquée.

## 2. Page 4473 `/entretien-en-ligne/`

**Contenu :**
- shortcode `[flux_entretien]`, rendu en 26 mots : « Cet espace est réservé aux candidats… » ;
- un bouton vers `/rejoignez-nous/` ;
- page fonctionnelle du parcours de recrutement (entretien en ligne après candidature).

**Valeur SEO :** nulle. La page n'a pas de contenu propre et sa partie utile n'est accessible qu'après candidature. L'indexer créerait une page mince. La page publique pertinente est `/rejoignez-nous/`, qui est indexable.

**Décision :** conserver le noindex et retirer la page du sitemap.

**Précision sur ma recommandation précédente :**
- La balise `noindex, nofollow` est bien émise par Rank Math, mais elle ne provient pas de la meta de la page (`rank_math_robots`). Ma tentative de la poser par l'API n'a eu aucun effet, car cette meta n'est pas exposée.
- Elle est donc imposée par un filtre, très probablement celui de l'extension d'entretien (shortcode `flux_entretien`, menu admin `fie`).
- Le générateur de sitemap Rank Math ne consulte que la meta de la page. Il ignore ce filtre et inclut donc la page.
- Cocher « No Index » dans l'onglet Avancé de Rank Math ne change pas la balise affichée : il pose la meta que lit le sitemap.
- Autre option équivalente : Rank Math > Sitemap > Pages > « Exclure des articles », ID `4473`.

**Statut :** à faire dans wp-admin. Test ajouté : « noindex conservé ET absente du sitemap », **en échec** pour l'instant.

## 3. Redirection héritée `/automatisation-des-factures-par-ia-au-maroc/`

**Équivalence :** l'ancien slug et l'article 3569 « Automatisation des factures au Maroc : le parcours d'une facture… » (`/automatisation-factures-ia-maroc/`) traitent du même sujet.

**État constaté :**
- Ma sauvegarde du tableau Rank Math (`auth/redir.html`, 04/11) montre cette source avec la destination `/automatisation-factures-ia-maroc/`, en 301, avec 94 hits.
- Aujourd'hui, la réponse est `301`, `Location: https://fluxintelligent.com` (sans slash final), `x-redirect-by: Rank Math`, puis 301 vers `/` et 200 sur l'accueil.

**Correction à faire** (Rank Math > Redirections) : rechercher `automatisation-des-factures-par-ia-au-maroc` et fixer la destination à `https://fluxintelligent.com/automatisation-factures-ia-maroc/` en 301. Si deux règles existent, supprimer celle qui pointe vers l'accueil.

Test ajouté : 301 directe vers la cible, **en échec** pour l'instant. La destination est en 200, et il n'y a pas de boucle.

## 4. Liens internes

| Page | Lien obsolète | Nouvelle destination | Contexte |
|---|---|---|---|
| 4100 `/chatbots-experience-client/` | `https://fluxintelligent.com/ia-hotels-tourisme-maroc-2026/` | `https://fluxintelligent.com/automatisation-ia-hotel-fiabilite-technique-experience-client/` | liste d'articles, ancre « L'IA dans l'hôtel… » |
| 4009 `/automatisation-des-processus/` | `https://fluxintelligent.com/automatisation-entreprise-maroc/` | `https://fluxintelligent.com/automatisation-ia-pme-maroc/` | liste, ancre « Automatisation en entreprise au Maroc » |

**Non modifiés.** Ces pages font 17 et 24 Ko de HTML rendu, avec du JSON-LD. Le seul accès en écriture disponible, le MCP WordPress, oblige à renvoyer tout le contenu, ce qui est exclu par votre consigne.

**Méthode ciblée** une fois l'accès REST rétabli : lire le contenu brut, faire `str.replace` sur l'URL exacte (une occurrence attendue), renvoyer, puis comparer le rendu avant et après pour vérifier qu'il n'y a qu'une différence d'URL.

Autre voie : dans l'éditeur, modifier les 2 liens à la main. Les deux liens aboutissent aujourd'hui en 1 saut de 301.

## 5. Réponses HTTP 500

**Observé à 11:30 :** des 500 sur des requêtes HEAD lancées à 8 en parallèle (4 sur 24, puis environ 30 sur 108 pendant la vérification des liens).

**Test contrôlé à 15:2x :** 12 URL, pour chaque niveau de concurrence 1, 2 et 4 :
- GET avec l'user-agent Googlebot ;
- HEAD avec les user-agents Googlebot, Chrome et curl.

Une rafale unique de 24 requêtes HEAD puis 24 GET a été ajoutée à 8 en parallèle. Au total, **192 requêtes, 0 erreur**.

**Couche :** origine Hostinger (LiteSpeed et PHP), pas le cache Cloudflare.
- Les requêtes HEAD passent à l'origine (`cf-cache-status: DYNAMIC`).
- La plupart des GET aussi (`BYPASS` pour 21 sur 24).
- Les en-têtes des 500 du matin n'ont pas été conservés : je ne peux donc pas exclure formellement une erreur émise par Cloudflare.

**Hypothèse la plus probable**, non prouvée faute de journaux : saturation passagère des processus PHP de l'hébergement mutualisé (limite « entry processes »), juste après mes modifications et pendant la reconstruction des caches.

**Journaux :** inaccessibles, car le connecteur Hostinger demande une réauthentification. Aucun test de charge supplémentaire n'a été fait, et aucune correction n'a été appliquée faute de cause technique établie.

**À vérifier :**
- hPanel > Utilisation des ressources : pics de processus et d'erreurs 500 autour de 11:30 GMT le 16/11 ;
- Search Console > Statistiques sur l'exploration : réponses 5xx.

## 6. Search Console

**Contrôlé à nouveau :** Composio (11 propriétés, ni `sc-domain:fluxintelligent.com` ni `https://fluxintelligent.com/`). Surfer demande une réauthentification, et aucune session de navigateur authentifiée n'est disponible.

**Demande unique.** Dans Search Console > Indexation > Pages, cliquer sur chaque motif ci-dessous, puis Exporter > CSV :
1. « Page en double : Google n'a pas choisi la même URL canonique que l'utilisateur » ;
2. « Bloquée par le fichier robots.txt ».

Déposer les deux fichiers dans `flux-editorial/gsc/gsc-exports/`, ou les joindre à la conversation. Pour les doublons, ajouter si possible la capture « Inspecter l'URL » d'une ou deux URL : canonique déclarée par l'utilisateur et canonique sélectionnée par Google.

**Autre option :** ajouter le compte Google relié à Composio comme utilisateur « Complet » de la propriété. Je pourrai alors inspecter chaque URL moi-même.

**Ensuite :**
- Je compare chaque URL à `resultats/avant/audit.json`.
- Je ne lance « Valider la correction » qu'une fois toutes les URL du rapport vérifiées comme corrigées.
- Les URL `/wp-admin/…` bloquées par robots.txt resteront exclues volontairement.

Pour l'instant, **aucune** alerte n'est confirmée ni infirmée par les données de Google. Le lien entre 3092/3288 et l'alerte canonique reste une hypothèse.

## 7. Tests

- `tests_indexation.py` contient désormais **70 contrôles** : les 63 d'origine et 7 ajoutés.
- Résultat : `resultats/apres/tests-finalisation-2026-11-16.txt`, **62 OK et 8 échecs**.
- Les 8 échecs sont tous des points connus en attente d'un accès :
  - 4473 dans le sitemap (2 contrôles) ;
  - durée de cache des 3 sitemaps (3) ;
  - redirection factures (1) ;
  - liens des pages 4100 et 4009 (2).
- Les 62 contrôles d'origine encore OK le restent : aucune régression.

## Modifications déployées cet après-midi

**Sur le site :** aucune modification de WordPress, de Rank Math, de Cloudflare ou de l'hébergement.

**Dans l'environnement cloud** (pas sur le site) : un identifiant WordPress (mot de passe d'application) a été enregistré sur l'environnement « Default », faute d'avoir pu créer un environnement dédié. Il est inutilisable tant que l'en-tête `Authorization` est supprimé par le serveur. Révocable dans WordPress (Profil > Mots de passe d'application) et dans les réglages de l'environnement.

**Dans le dépôt :**
- ajout des contrôles 64 à 70 dans `tests_indexation.py` ;
- ajout du dossier `a-appliquer/` ;
- ajout de ce rapport.
