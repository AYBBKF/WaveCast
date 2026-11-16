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
