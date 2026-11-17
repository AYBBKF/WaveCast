# Pages non indexées par Google : fluxintelligent.com (mise à jour du 17/11/2026, après corrections)

## Synthèse

- **Statut Google :** inspection API du 17/11 (compte propriétaire `fluxintelligent-owner`).
- **Contrôles techniques :** les 14 pages répondent en 200, avec une canonique auto-référente, `index, follow`, autorisées par robots.txt et présentes dans le sitemap. **Aucun blocage technique.**
- **Cause dominante confirmée : le maillage interne.**
  - Pages orphelines ou à peine reliées.
  - Liens surtout issus de pages sœurs elles-mêmes non indexées, ou des listes de catégorie et de blog.
  - Google ne cite aucune page référente pour 11 des 14 pages : il ne les connaît que par le sitemap.
- **Pas de fusion ni de réécriture importante sans accord.** Aucune demande d'indexation possible par API.

| URL | Priorité | Statut GSC avant (17/11) | Statut GSC après | Cause confirmée / hypothèse | Correction réalisée | Liens internes ajoutés (depuis des pages indexées) | Tests | Action Google restante |
|---|---|---|---|---|---|---|---|---|
| `/agence-ia-immobilier-maroc/` | **P1** | Inconnue de Google | en attente d'exploration | **confirmée** : orpheline (0 lien entrant, inaccessible depuis l'accueil). Cannibalisation du title avec l'article immobilier (même requête de tête). | title Rank Math : « IA immobilier Maroc : agent IA pour agences et promoteurs » devient « **Agence IA immobilier Maroc \| Agent IA agences et promoteurs** ». H1, contenu et canonique inchangés. | article `/ia-pour-immobilier-au-maroc-…/` (ancre « agence IA immobilier au Maroc ») ; hub `/agents-ia/` (bloc « Par métier »). Profondeur : aucune, puis 2. | public 200, title vérifié, 70/70 | **« Demander une indexation » dans l'interface Search Console** |
| `/agent-ia-cabinet-dentaire-maroc/` | P2 | Détectée, non explorée | en attente | liens surtout depuis des pages sœurs ; demande d'exploration faible. Hypothèse : gabarit proche des pages métiers sœurs (similarité 0,31 à 0,34). | aucune modification de contenu | `/agents-ia/`, `/chatbots-experience-client/prise-de-rendez-vous-ia/`. Profondeur : 3, puis 2. | 70/70 | nouvelle exploration |
| `/agent-ia-pharmacie-maroc/` | P2 | Détectée | en attente | idem | aucune | `/agents-ia/`, `/chatbots-experience-client/chatbot-whatsapp-maroc/` | 70/70 | nouvelle exploration |
| `/agent-ia-clinique-veterinaire-maroc/` | P2 | Détectée | en attente | 2 liens de contenu seulement | aucune | `/agents-ia/`, `/…/prise-de-rendez-vous-ia/`. Profondeur : 3, puis 2. | 70/70 | nouvelle exploration |
| `/agent-ia-institut-beaute-maroc/` | P2 | Détectée | en attente | 2 liens de contenu seulement | aucune | `/agents-ia/`, `/…/prise-de-rendez-vous-ia/`. Profondeur : 3, puis 2. | 70/70 | nouvelle exploration |
| `/confirmation-commande-cod-whatsapp-maroc/` | P2 | Détectée | en attente | 1 seul lien de contenu (catégorie) | aucune | `/chatbots-experience-client/chatbot-whatsapp-maroc/`, `/ecommerce-automatise-ia/` | 70/70 | nouvelle exploration |
| `/food-cost-restaurant-prix-achat/` | P2 | Inconnue | en attente | 1 seul lien (liste du blog) | aucune | `/automatisation-ia-cafes-maroc-2025/` | 70/70 | nouvelle exploration |
| `/automatisation-centre-de-formation-maroc/` | P2 | Détectée | en attente | **confirmée : orpheline** | aucune | `/gestion-ecole-privee-frais-scolarite/`, `/automatisation-des-processus/automatisation-administrative/`. Profondeur : aucune, puis 2. | 70/70 | nouvelle exploration |
| `/suivi-relance-devis-sans-double-saisie/` | P2 | Détectée | en attente | pas de lien depuis le service « relances » | aucune | `/crm-ventes-marketing-ia/relances-commerciales-automatisees/`. Profondeur : 3, puis 2. | 70/70 | nouvelle exploration |
| `/comparer-devis-automatisation-ia-maroc/` | P2 | Inconnue | en attente | publiée le 02/11 : délai normal | aucune | `/automatisation-des-processus/automatisation-administrative/`. Profondeur : 3, puis 2. | 70/70 | nouvelle exploration |
| `/rapprochement-encaissements-cod/` | P2 | Inconnue | en attente | publiée le 17/11 | aucune | `/ecommerce-automatise-ia/` | 70/70 | nouvelle exploration |
| `/automatisation-ia-agence-transport/` | P3 | Explorée, non indexée (04/08) | en attente | dernière exploration **antérieure** à l'enrichissement du 03/11 (2 367 mots aujourd'hui) | aucune : contenu déjà substantiel | aucun | 70/70 | nouvelle exploration (option : demande manuelle) |
| `/workflow-ia-coach-musculation-maroc-2025/` | P3 | Explorée, non indexée (06/09) | inchangé | **hypothèse** : contenu générique grand public, hors cœur de cible B2B, année « 2025 » datée, emojis dans les intertitres | **aucune** : proposition ci-dessous | aucun | 70/70 | aucune avant décision |
| `/ia-salon-coiffure-automatisation/` | P3 | Explorée, non indexée (16/06) | inchangé | **confirmée** : contenu mince (418 mots), liste générique, sans prérequis, limites ni indicateurs | **aucune** : enrichissement rédigé (`exec/html/ia-salon-coiffure-automatisation.html`), bloqué par la règle Surfer 80–90 | aucun | 70/70 | aucune avant enrichissement |

## Propositions soumises à accord (non appliquées)

1. **Coach musculation :** consolider vers l'article `/fidelisation-salle-de-sport/` (4505, programmé le 18/11) par une 301, une fois cet article publié et indexable. Sinon, réécrire l'article en cas B2B (salle de sport ou coach) et retirer « 2025 ».
2. **Salon de coiffure :** appliquer l'enrichissement déjà rédigé dès qu'un score Surfer entre 80 et 90 est vérifié (quota épuisé). Lien prévu ensuite depuis `/chatbots-experience-client/prise-de-rendez-vous-ia/`.
3. **Pages métiers (dentaire, pharmacie, vétérinaire, beauté) :** si elles restent non explorées 4 à 6 semaines après ces liens, différencier leur gabarit (cas d'usage propres à chaque métier) pour réduire la similarité entre pages sœurs.
4. **P1 :** le schéma Rank Math de la page est « Article ». Un type « WebPage / Service » correspondrait mieux à une page commerciale. Non modifié : changement de schéma, sans effet bloquant.

## Liens ajoutés (9 pages sources, contenu brut : ajout seul ; sauvegardes dans `backup/maillage/`)

- `/ia-pour-immobilier-au-maroc-…/` (3815)
- `/agents-ia/` (3773)
- `/chatbots-experience-client/prise-de-rendez-vous-ia/` (4003)
- `/chatbots-experience-client/chatbot-whatsapp-maroc/` (3419)
- `/automatisation-ia-cafes-maroc-2025/` (3208)
- `/ecommerce-automatise-ia/` (3293)
- `/crm-ventes-marketing-ia/relances-commerciales-automatisees/` (4007)
- `/gestion-ecole-privee-frais-scolarite/` (4509)
- `/automatisation-des-processus/automatisation-administrative/` (4000)

Détail : `resultats/maillage-ajouts.json`. Mesures avant/après : `resultats/maillage-avant.json` et `resultats/maillage-apres.json`.

**Retour arrière :** restaurer le champ `content.raw` de la sauvegarde horodatée de chaque page. Pour le title de P1 : `backup/maillage/rankmath-4489-avant.json`.
