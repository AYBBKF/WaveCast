# Mesures de performance reproductibles

## Lighthouse mobile, médiane de 3 passages

```bash
cd <dossier contenant node_modules/lighthouse>
export CHROME_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
bash bench.sh https://fluxintelligent.com/ home-avant
```

Variante : ajouter des motifs d'URL à bloquer en arguments.

## Simulation de la désactivation de la passerelle

```bash
NODE_PATH=$(npm root -g) node simu-gateway.cjs <url> actuel 3
NODE_PATH=$(npm root -g) node simu-gateway.cjs <url> sans-passerelle 3
```

- Le script retire du HTML reçu par le navigateur de test **uniquement** le snippet injecté par Cloudflare (Google tag gateway).
- Il mesure le TBT (tâches longues, CPU ralenti ×4), le LCP, le JavaScript et les hits Google Ads (`ccm/collect` `page_view`) et GA4 (`g/collect` `page_view`).

## Trace réseau des balises Google

```bash
NODE_PATH=$(npm root -g) node trace-block.cjs <url> [block]
```
