# Clôture opérationnelle : fluxintelligent.com

**Statut : NON TERMINÉ.** La mission ne sera close qu'après vérification des URL signalées par Google (étape 5).

Rien n'a été modifié sur le site depuis le passage de 3092 et 3288 en brouillon (16/11, 11:28 GMT).

## État vérifié avant actions (16/11, fin d'après-midi)

| URL | Réponse | Preuve |
|---|---|---|
| `/automatisation-des-factures-par-ia-au-maroc/` (avec ou sans slash) | 301 → `https://fluxintelligent.com/`, `X-Redirect-By: Rank Math` | **à corriger** |
| `/automatisation-factures-ia-maroc/` (article 3569, publié) | 200 | destination valide |
| `/entretien-en-ligne/` (page 4473, publiée) | 200, `<meta name="robots" content="nofollow, noindex"/>` | noindex conservé |
| `page-sitemap.xml` (sans cache) | contient `/entretien-en-ligne/` | **à corriger** |
| `post-sitemap.xml` (public) | 55 URL, sans 3092 ni 3288 | conforme |

---

## 1. Rank Math : page 4473 (`/entretien-en-ligne/`)

**Consigne :** exclure **uniquement l'ID 4473** du sitemap. Le noindex actuel reste tel quel. Rien n'est ajouté : la page émet déjà `nofollow, noindex` par son extension, et ce réglage n'est pas modifié.

1. wp-admin > Rank Math > **Sitemap Settings** > onglet **Pages** (ou « Général », selon la version) > champ **« Exclure des articles »**.
2. Ajouter `4473` aux ID déjà présents, séparés par des virgules. Noter auparavant la valeur existante, qui sert de sauvegarde.
3. Enregistrer.
4. Purger `page-sitemap.xml` dans Cloudflare, ou s'appuyer sur la règle de bypass du point 3.

Ne pas utiliser l'onglet Avancé de la page : il modifierait les directives robots, ce qui n'est pas demandé.

**Preuves sur l'URL publique :**

```bash
curl -s "https://fluxintelligent.com/page-sitemap.xml?nc=$RANDOM" | grep -c entretien-en-ligne
curl -s https://fluxintelligent.com/entretien-en-ligne/ | grep -o '<meta name="robots"[^>]*>'
```

- Attendu pour la première commande : `0` (état actuel : `1`).
- Attendu pour la seconde : `<meta name="robots" content="nofollow, noindex"/>`, inchangé.

**Retour arrière :** retirer `4473` du champ.

## 2. Rank Math : redirection vers l'article 3569

**Objectif :** que `/automatisation-des-factures-par-ia-au-maroc/` renvoie en une seule 301 vers `https://fluxintelligent.com/automatisation-factures-ia-maroc/`.

1. wp-admin > Rank Math > **Redirections** > rechercher `factures-par-ia`.
2. **Noter chaque règle trouvée** : source, comparaison, destination, type, statut. Faire une capture d'écran, qui sert de sauvegarde.
   - Une règle de ce type existait le 04/11, vers 3569, avec 94 hits.
   - Il y a probablement aujourd'hui une destination vide ou égale à l'accueil, ou une seconde règle prioritaire.
3. Modifier la règle de sorte que :
   - Source : `automatisation-des-factures-par-ia-au-maroc`, comparaison **Exact** ;
   - Destination : `https://fluxintelligent.com/automatisation-factures-ia-maroc/` ;
   - Type : **301**, statut **Actif**.
4. Si une seconde règle intercepte la même source vers l'accueil (comparaison « Contient » ou expression régulière), la **désactiver** sans la supprimer. Toutes les autres règles restent intactes.
   - Contrôle : le nombre total de règles actives est identique avant et après, à 1 près au plus.
5. Si aucune règle n'apparaît : Rank Math > Redirections > Paramètres > « Comportement de repli », noter la valeur sans la modifier, et me la transmettre.

**Preuves de validation :**

```bash
for u in /automatisation-des-factures-par-ia-au-maroc/ /automatisation-des-factures-par-ia-au-maroc; do curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" "https://fluxintelligent.com$u?nc=$RANDOM"; done
curl -s -o /dev/null -w "%{http_code} %{num_redirects}\n" -L "https://fluxintelligent.com/automatisation-des-factures-par-ia-au-maroc/"
```

- Attendu pour la première boucle : `301 https://fluxintelligent.com/automatisation-factures-ia-maroc/` deux fois (un paramètre `?nc=` éventuellement recopié est sans conséquence).
- Attendu pour la seconde commande : `200 1`, soit une seule redirection et aucune boucle.
- Test automatisé : « ancienne URL factures : 301 directe » doit être OK.

**Retour arrière :** remettre la règle dans l'état noté à l'étape 2.

## 3. Cloudflare : bypass des sitemaps

Voir `a-appliquer/cloudflare-regle-cache-sitemaps.md`.

**Ce qui a été vérifié :**
- **Workers.** Le compte Cloudflare accessible par l'intégration contient 2 Workers (`pick-systemsecuritytv` et `pick-systemsecuritytvs`). Ce sont des relais de playlists sans aucune référence à fluxintelligent.com, et aucune réponse du site ne présente de trace de Worker.
  - Point à contrôler dans le dashboard : Workers Routes de la zone fluxintelligent.com, qui doit être vide.
  - Point à contrôler à part : ces deux scripts contiennent des identifiants d'abonnement en clair. Ce n'est pas lié au SEO.
- **Ordre des règles.** L'intégration ne donne pas accès aux Cache Rules de la zone. Placer la règle **en dernier** : pour un même réglage, la dernière règle correspondante l'emporte.
- **Cache HTML.** La règle ne cible que les chemins de sitemap. Après déploiement, `curl -sI https://fluxintelligent.com/ | grep -i cf-cache-status` doit renvoyer la même valeur qu'avant. État actuel relevé : `BYPASS`.

## 4. Retrouver l'accès WordPress sans identifiant durable

État actuel :
- Le MCP WordPress est déconnecté (401, jeton refusé).
- Le connecteur Hostinger attend une réauthentification.
- Un mot de passe d'application est enregistré sur l'environnement **Default**, mais il est inutilisable : le serveur supprime l'en-tête `Authorization`.

**À faire maintenant, par vous** (je n'ai aucun accès pour le faire) :
1. WordPress > Utilisateurs > Profil > **Mots de passe d'application** : révoquer le mot de passe créé pour cette session, celui qui a été saisi dans le formulaire sécurisé.
   - Preuve : la ligne disparaît de la liste.
2. claude.ai > Environnements cloud > **Default** > Network secrets : supprimer l'entrée `fluxintelligent.com`.
   - Preuve : la liste des secrets de l'environnement est vide.

**Ensuite, méthode retenue :** réautoriser le connecteur **Hostinger** (réglages des connecteurs claude.ai) le temps de l'intervention. Je génère un lien de connexion automatique temporaire. Le cookie et le nonce restent dans le dossier temporaire de la session et sont supprimés à la fin. Aucun mot de passe n'est stocké.

Avec cet accès, `remplacement_liens.py --apply` corrige les liens des pages 4100 et 4009 :
- test à blanc du 16/11 : 1 occurrence par page ;
- sauvegarde automatique du contenu brut ;
- arrêt sans écriture si le nombre d'occurrences n'est pas exactement 1 ;
- contrôle que le rendu avant/après ne diffère que par l'URL.

**Autre méthode**, à n'utiliser que si Hostinger est impossible :
1. Ajouter la ligne `.htaccess` décrite dans `a-appliquer/htaccess-authorization.md`.
2. Créer un mot de passe d'application nommé `claude-temp-AAAAMMJJ`.
3. Le saisir dans le formulaire sécurisé que j'ouvrirai.
4. **Le révoquer** dans WordPress et supprimer le secret réseau **dès la fin** de l'intervention.

Avec l'une ou l'autre méthode, je pourrai appliquer moi-même les points 1 et 2, et corriger les liens internes de façon ciblée (voir plus bas).

## 5. Exports Search Console (bloquant pour la clôture)

Dans Search Console > Indexation > Pages, cliquer sur le motif, puis **Exporter > Télécharger le fichier CSV** (ZIP accepté tel quel) :
1. « Page en double : Google n'a pas choisi la même URL canonique que l'utilisateur » ;
2. « Bloquée par le fichier robots.txt ».

Les déposer dans `flux-editorial/gsc/gsc-exports/` ou les joindre à la conversation.

**Analyse prévue** : `python3 -I analyse_exports_gsc.py <doublons> <robots> resultats/analyse-gsc.md`, script testé. Pour chaque URL, il relève :
- la chaîne HTTP et le statut final ;
- la canonical déclarée et la meta robots ;
- le verdict robots.txt pour Googlebot ;
- la présence dans le sitemap public ;
- la date de dernière exploration par Google.

Il classe ensuite l'URL :
- **CORRIGEE** : corrigée côté site ;
- **VOLONTAIRE** : par exemple la zone `/wp-admin/` bloquée, ou une variante avec paramètre canonicalisée ;
- **A_CORRIGER** ;
- **A_EXAMINER** : URL auto-canonique, à comparer avec la canonique choisie par Google dans l'inspection d'URL ;
- **A_RECRAWLER** : corrigée, mais explorée par Google avant le correctif.

**« Valider la correction »** ne sera lancé que si aucune URL n'est en A_CORRIGER ou en A_EXAMINER non résolue.

## Liens internes des pages 4100 et 4009

**Non modifiés.** Ils seront corrigés uniquement par remplacement ciblé, une fois l'accès retrouvé :
1. lecture du contenu brut par REST et sauvegarde ;
2. `replace` de l'URL exacte, avec une seule occurrence attendue ;
3. renvoi ;
4. comparaison du HTML rendu avant et après, la seule différence admise étant l'URL.

Sans cet accès, la seule autre voie est la modification manuelle de 2 liens dans l'éditeur. Ces liens aboutissent aujourd'hui en 1 saut de 301.

## Surveillance (erreurs 500 non reproduites)

`python3 -I surveillance_5xx.py 20` envoie 40 requêtes séquentielles (1 par seconde, GET et HEAD). Code retour 1 en cas de 5xx.
- Dernière exécution (16/11) : 20 requêtes, 0 erreur.
- À lancer une fois par semaine et après chaque mise à jour d'extension.
- Côté Search Console : surveiller « Statistiques sur l'exploration », réponses 5xx.

## Tests

`python3 -I tests_indexation.py` contient 70 contrôles. Les résultats horodatés sont dans `resultats/apres/`.
