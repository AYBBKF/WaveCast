# Règle Cloudflare (zone fluxintelligent.com) : cache des sitemaps

Caching > Cache Rules > Create rule

- Nom : `Sitemaps XML : TTL court`
- Expression personnalisée :
  `(http.request.uri.path eq "/sitemap_index.xml") or (http.request.uri.path wildcard "/*-sitemap*.xml")`
- Action : Eligible for cache.
  - Edge TTL : « Override origin », 5 minutes.
  - Browser TTL : « Override origin », 5 minutes.
- Placer la règle **avant** toute règle « Cache Everything » existante.

Ne pas toucher aux autres règles : le cache global du site reste inchangé.

Contrôle :
`curl -sI https://fluxintelligent.com/post-sitemap.xml | grep -iE 'cache-control|cf-cache-status|age'`

Attendu : `age` ≤ 300.

Retour arrière : désactiver la règle.
