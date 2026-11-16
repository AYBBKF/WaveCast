#!/usr/bin/env bash
# Preuves publiques APRÈS corrections. Usage : bash valider_cloture.sh > resultats/preuves-apres-cloture.txt
B=https://fluxintelligent.com; ok=0; ko=0
t(){ if [ "$2" = "$3" ]; then echo "OK    $1 ($2)"; ok=$((ok+1)); else echo "ECHEC $1 (obtenu: $2 | attendu: $3)"; ko=$((ko+1)); fi; }
echo "# Preuves APRÈS ($(date -u +%FT%TZ))"
t "4473 absente du sitemap" "$(curl -s "$B/page-sitemap.xml?nc=$RANDOM" | grep -c entretien-en-ligne)" "0"
t "4473 noindex inchangé" "$(curl -s $B/entretien-en-ligne/ | grep -o '<meta name="robots"[^>]*>')" '<meta name="robots" content="nofollow, noindex"/>'
for u in /automatisation-des-factures-par-ia-au-maroc/ /automatisation-des-factures-par-ia-au-maroc; do
  t "301 directe $u" "$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "$B$u")" "301 $B/automatisation-factures-ia-maroc/"; done
t "factures : 1 saut, 200, destination 3569" "$(curl -s -L -o /dev/null -w '%{http_code} %{num_redirects} %{url_effective}' $B/automatisation-des-factures-par-ia-au-maroc/)" "200 1 $B/automatisation-factures-ia-maroc/"
for u in sitemap_index post-sitemap page-sitemap category-sitemap; do
  s=$(curl -s -o /dev/null -D - $B/$u.xml | grep -i cf-cache-status | tr -d '\r' | awk '{print toupper($2)}')
  case "$s" in BYPASS|DYNAMIC) t "$u.xml hors cache Cloudflare" "$s" "$s";; *) t "$u.xml hors cache Cloudflare" "$s" "BYPASS|DYNAMIC";; esac; done
echo "INFO  cache HTML accueil : $(curl -s -o /dev/null -D - $B/ | grep -i cf-cache-status | tr -d '\r')  (relevé avant : BYPASS ou HIT selon le moment ; ne doit pas devenir systématiquement DYNAMIC)"
for p in 4100:ia-hotels-tourisme-maroc-2026 4009:automatisation-entreprise-maroc; do
  t "page ${p%%:*} sans lien ${p#*:}" "$(curl -s "$B/wp-json/wp/v2/pages/${p%%:*}?_fields=content" | grep -c "${p#*:}")" "0"; done
echo "$ok OK, $ko échec(s)"
python3 -I "$(dirname "$0")/tests_indexation.py" | tail -1
