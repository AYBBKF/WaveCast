# Règle Cloudflare : bypass du cache pour les sitemaps XML

**Configuration réelle constatée (16/11, en-têtes publics) :**

| URL | cf-cache-status | age | Cache-Control |
|---|---|---|---|
| `/` et pages HTML | BYPASS (parfois MISS/EXPIRED) | – | absent ou max-age=14400 |
| `/post-sitemap.xml`, `/page-sitemap.xml` | **HIT** | ~5 950 s | max-age=14400, must-revalidate |
| `/sitemap_index.xml`, `/category-sitemap.xml` | MISS | – | max-age=14400, must-revalidate |
| `/main-sitemap.xsl` | HIT | ~5 940 s | max-age=14400, maxage=31536000 |

Cloudflare met donc en cache en périphérie les fichiers XML générés par Rank Math, jusqu'à 4 h. Les pages HTML ne sont pas concernées par cette règle et restent inchangées.

## Création

Dashboard Cloudflare > fluxintelligent.com > **Caching > Cache Rules > Create rule**

1. **Nom :** `Sitemaps XML - bypass`
2. **Custom filter expression** (Edit expression) :

   ```
   (http.request.uri.path eq "/sitemap_index.xml")
   or (http.request.uri.path wildcard "/*-sitemap.xml")
   or (http.request.uri.path wildcard "/*-sitemap*.xml")
   or (http.request.uri.path eq "/sitemap.xml")
   or (http.request.uri.path eq "/wp-sitemap.xml")
   ```

   Les deux dernières URL redirigent vers sitemap_index.xml, ce qui évite qu'une ancienne redirection soit servie depuis le cache.
3. **Then > Cache eligibility : Bypass cache.**
4. **Placement : dernière position** de la liste, c'est-à-dire **sous** toute règle « Eligible for cache / Cache Everything ». Dans les Cache Rules, la dernière règle qui correspond l'emporte pour un même réglage.
5. Deploy.

Ne touchez ni aux autres règles, ni à Browser Cache TTL, ni au niveau de cache global.

## Purge unique après déploiement

**Caching > Configuration > Purge Cache > Custom Purge > URL**, puis coller :

```
https://fluxintelligent.com/sitemap_index.xml
https://fluxintelligent.com/post-sitemap.xml
https://fluxintelligent.com/page-sitemap.xml
https://fluxintelligent.com/category-sitemap.xml
```

## Validation (preuves attendues)

```bash
for u in sitemap_index post-sitemap page-sitemap category-sitemap; do curl -s -o /dev/null -D - https://fluxintelligent.com/$u.xml | grep -iE 'cf-cache-status|^age'; done
```

- Attendu : `cf-cache-status: DYNAMIC` ou `BYPASS` et aucun en-tête `age`, deux fois de suite.
- Contrôle de non-régression du cache des pages : `curl -sI https://fluxintelligent.com/ | grep -i cf-cache-status` doit renvoyer la même valeur qu'avant (BYPASS, MISS ou HIT, inchangée).
- Test automatisé : `python3 -I tests_indexation.py`, contrôles « durée de cache des sitemaps ». Ils passent si la réponse porte `no-cache` ou un max-age ≤ 3600, ou si `cf-cache-status` vaut BYPASS ou DYNAMIC (voir le test mis à jour).

**Retour arrière :** désactiver la règle.
