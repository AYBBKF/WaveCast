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

**Objectif :** garder la page en noindex et la retirer du sitemap, sans la rendre indexable.

1. wp-admin > Pages > « Entretien en ligne ». Contrôler l'URL de modification : `post.php?post=4473`.
2. Panneau Rank Math > onglet **Avancé** > Robots Meta :
   - cocher **No Index** ;
   - cocher **Nofollow** pour conserver la directive actuelle.
3. **Mettre à jour.**
4. Purger le sitemap dans Cloudflare (Custom Purge de `page-sitemap.xml`), ou attendre la règle de bypass du point 2.

**Si le panneau Rank Math est absent de cette page** (page générée par l'extension d'entretien) : aller dans Rank Math > Sitemap Settings > Pages > « Exclure des articles », saisir `4473`, puis enregistrer.

**Preuves de validation :**

```bash
curl -s "https://fluxintelligent.com/page-sitemap.xml?nc=$RANDOM" | grep -c entretien-en-ligne
curl -s https://fluxintelligent.com/entretien-en-ligne/ | grep -o '<meta name="robots"[^>]*>'
```

- La première commande doit afficher `0`.
- La seconde doit afficher une balise qui contient toujours `noindex`.
- Test automatisé : « page 4473 : noindex conservé ET absente du sitemap » doit être OK.

**Retour arrière :** décocher No Index dans le panneau, ou retirer l'ID 4473 de l'exclusion.

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
4. Désactiver toute autre règle qui intercepte la même source vers l'accueil (comparaison « Contient » ou expression régulière). **Ne pas supprimer** de règle sans rapport.
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

Voir `a-appliquer/cloudflare-regle-cache-sitemaps.md`. La règle est construite d'après les en-têtes réellement observés : les XML sont servis en HIT avec un `age` d'environ 5 950 s, et les pages HTML ne sont pas touchées.

**Preuves :** `cf-cache-status: BYPASS` ou `DYNAMIC` sur les 4 sitemaps, et `cf-cache-status` de la page d'accueil inchangé.

## 4. Retrouver l'accès WordPress sans identifiant durable

État actuel :
- Le MCP WordPress est déconnecté (401, jeton refusé).
- Le connecteur Hostinger attend une réauthentification.
- Un mot de passe d'application est enregistré sur l'environnement **Default**, mais il est inutilisable : le serveur supprime l'en-tête `Authorization`.

**À faire maintenant, dans tous les cas :**
1. WordPress > Utilisateurs > Profil > Mots de passe d'application : **révoquer** le mot de passe créé pour cette session.
2. claude.ai > réglages de l'environnement cloud « Default » > Network secrets : **supprimer** l'entrée `fluxintelligent.com`.

**Méthode recommandée, sans mot de passe stocké :** réautoriser le connecteur **Hostinger** dans les réglages des connecteurs claude.ai (OAuth). Je génère alors un lien de connexion automatique **temporaire**. Le cookie de session et le nonce restent dans le dossier temporaire de la session, ne sont jamais enregistrés dans le dépôt, et sont **supprimés à la fin**, comme le 04/11. La session WordPress expire d'elle-même.

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
