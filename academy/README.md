# Flux Intelligent Academy — V1

Plateforme de formation en ligne : catalogue → page formation → compte → leçons écrites → progression enregistrée → examen final (débloqué quand toutes les leçons sont terminées) → note sur 20 et correction expliquée → certificat PDF vérifiable par QR code → espace personnel. Option : récompense « Claude Pro offert par Flux Intelligent » pour un 100 % à l'examen.

Technique : Django 5.2 (LTS), SQLite en local, PostgreSQL en production, ReportLab pour les PDF. Toutes les règles (accès, déblocage, correction, seuil, certificat, récompense) sont appliquées côté serveur.

---

## 1. Démarrer en local

```bash
cd academy
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ACADEMY_DEBUG=1
python manage.py migrate
python manage.py seed_demo          # formation de démonstration + réglages par défaut
python manage.py createsuperuser    # premier administrateur (voir §3)
python manage.py runserver
```

- Site : http://127.0.0.1:8000/
- Administration de la plateforme : http://127.0.0.1:8000/gestion/
- En local, les e-mails (vérification d'adresse, mot de passe oublié) s'affichent dans le terminal.

Tests automatisés (28 tests, les 8 parcours + la récompense) :

```bash
ACADEMY_DEBUG=1 python manage.py test learning
```

## 2. Déployer en production

L'application a besoin d'un hébergement Python (VPS, Render, Railway, Fly.io, Scalingo, PythonAnywhere…). Un hébergement mutualisé WordPress/PHP ne convient pas. Le plus simple est un sous-domaine, par exemple `academy.fluxintelligent.com`, avec un lien depuis le site WordPress.

1. Créez une base PostgreSQL.
2. Définissez les variables d'environnement listées dans `.env.example` (clé secrète longue et aléatoire, `ACADEMY_BASE_URL` = adresse publique exacte, hôtes autorisés, SMTP). L'application lit directement les variables d'environnement : elle ne charge pas de fichier `.env`.
3. Installez et préparez :
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py seed_demo
   ```
4. Lancez le serveur applicatif derrière HTTPS :
   ```bash
   gunicorn academy_site.wsgi --bind 0.0.0.0:8000 --workers 3
   ```
5. Dossiers à conserver et sauvegarder : `ACADEMY_MEDIA_ROOT` (logo, images des leçons) et `ACADEMY_PRIVATE_ROOT` (PDF des certificats, jamais servis directement). Sauvegardez aussi la base de données.

> **Important : `ACADEMY_BASE_URL`** sert à construire le lien de vérification imprimé dans le QR code de chaque certificat. Réglez-la sur l'adresse définitive **avant** de délivrer les premiers certificats : un certificat déjà délivré conserve son lien.

### Production actuelle : VPS Hostinger (Docker + Traefik)

- Projet Docker Compose **`academy`** sur le VPS `srv928744` (148.230.113.129), fichier `deploy/docker-compose.hostinger.yml`.
- Services : `academy-web` (Gunicorn), `academy-db` (PostgreSQL 16), `academy-secrets` (génère sur le serveur la clé Django et le mot de passe PostgreSQL au premier démarrage). Volumes persistants : `academy-db`, `academy-media`, `academy-private`, `academy-secrets`.
- Traefik (déjà présent sur le VPS) route `academy.fluxintelligent.com` et obtient le certificat Let's Encrypt automatiquement dès que le DNS pointe vers le VPS.
- Mise à jour : changer `ACADEMY_GIT_REF` (commit à déployer) dans les variables du projet (hPanel → VPS → Docker Manager → academy), puis redéployer.
- E-mails : `ACADEMY_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` et `ACADEMY_EMAIL_PASSWORD` (mot de passe de service@fluxintelligent.com), à saisir uniquement dans ces variables.
- `restart: unless-stopped` : redémarrage automatique après un crash ou un reboot du VPS.

## 3. Créer le premier administrateur (procédure sûre)

**Méthode recommandée en production (aucun mot de passe ne quitte votre navigateur) :**
1. Créez votre compte normalement sur `https://academy.fluxintelligent.com/inscription/`.
2. Dans hPanel → VPS → Docker Manager → projet `academy` → variables : `ACADEMY_BOOTSTRAP_ADMIN_EMAIL=votre@email`, puis redéployez.
3. Connectez-vous : `/gestion/` est accessible. Videz ensuite la variable et redéployez.

Autre méthode, depuis le terminal du VPS : `docker exec -it academy-web python manage.py createsuperuser`.


Sur le serveur, en ligne de commande :

```bash
python manage.py createsuperuser
```

- Identifiant : utilisez l'adresse e-mail (la connexion se fait par e-mail).
- Saisissez l'e-mail puis un mot de passe long et unique (10 caractères minimum) ; il est demandé de façon masquée et n'apparaît dans aucun fichier.
- Connectez-vous sur `/connexion/`, puis ouvrez `/gestion/`.
- Pour ajouter d'autres administrateurs : `/django-admin/` → Utilisateurs → cocher « Statut équipe ». Aucun compte administrateur n'est créé automatiquement et aucun mot de passe n'est stocké dans le code.

## 4. Guide d'administration

### Ajouter une formation
1. `/gestion/` → **Formations** → **Nouvelle formation** : titre, accroche, description, image de couverture (facultative), objectifs (un par ligne), niveau, durée, seuil de réussite (70 % par défaut = 14/20), nombre de tentatives (0 = illimité).
2. **Programme** : ajoutez les modules, puis les leçons de chaque module. Les flèches ↑ ↓ réordonnent modules et leçons.
3. Éditeur de leçon : titres, gras, listes, citations, liens, images (PNG/JPG/WEBP/GIF, 5 Mo max), encadrés **Exemple**, **Astuce** et **Attention**, et l'encadré **« À retenir »**. Le HTML est nettoyé à l'enregistrement (scripts et attributs dangereux supprimés).
4. Dans la liste des formations, cliquez **Publier** (au moins une leçon est requise). **Archiver** retire la formation du catalogue sans effacer les progressions, notes ou certificats.

### Modifier l'examen
**Formations** → **Examen** :
- **Nouvelle question** : QCM (jusqu'à 4 réponses, cochez la bonne) ou Vrai/Faux (cochez la 1re ligne pour Vrai, la 2e pour Faux).
- Renseignez l'**explication** affichée dans la correction et la **leçon liée** (lien « Revoir » pour l'apprenant).
- Le seuil et le nombre de tentatives se règlent dans la **fiche** de la formation. Le seuil appliqué à une tentative est figé au moment où elle commence.
- Les bonnes réponses ne sont jamais envoyées au navigateur avant la validation.

### Personnaliser le certificat et la marque
**Marque et certificat** : nom de la plateforme, nom de l'organisme, couleurs, logo, signature (image facultative), nom et fonction du signataire, texte du certificat (variables `{organisme}`, `{nom}`, `{formation}`, `{note}`), e-mail de contact. Le bouton **Aperçu du certificat** génère un PDF d'exemple sans rien enregistrer.

Les données d'un certificat (nom, formation, note, date, numéro) sont figées à sa délivrance. Un nouvel échec ne le supprime jamais ; le re-téléchargement renvoie le même document. Un certificat peut être **révoqué** (la page de vérification l'indique).

### Suivre les apprenants
- **Apprenants** : progression, dernière activité, nombre de tentatives, meilleure note, certificat.
- **Résultats** : toutes les tentatives (note /20, %, seuil, réussite).
- **Certificats** : liste, PDF, lien de vérification, révocation.

## 5. Récompense « Claude Pro offert par Flux Intelligent »

### État actuel des cartes cadeaux Anthropic
D'après le centre d'aide officiel d'Anthropic (octobre 2026), l'achat d'abonnements Claude en cadeau est **temporairement indisponible**, sans date de retour annoncée. Un lien cadeau s'active sur `claude.ai/gift/redeem`, sans carte bancaire, et il n'existe pas d'API pour en générer. La V1 prévoit donc une **remise manuelle et traçable** par l'administration (lien cadeau officiel lorsqu'il redeviendra disponible, ou autre modalité réelle que vous décrivez).

### Configurer l'offre
**Récompenses Claude Pro** → offre de la formation : durée offerte, modalités de remise, délai annoncé, confirmation du financement, activation. L'offre reste un **brouillon invisible** tant que la durée, les modalités, le délai et le financement ne sont pas renseignés. Une fois active, la page formation affiche :

> Terminez la formation et obtenez 100 % à l'examen final pour recevoir [durée] de Claude Pro offert par Flux Intelligent.

### Règles appliquées
- Éligibilité : e-mail vérifié + toutes les leçons terminées + exactement 100 % (10/10 = 20/20). Un 19/20 ne donne rien.
- Une seule récompense par bénéficiaire et par offre (contrainte en base, même en cas de double clic ou de nouvelles tentatives).
- Si l'e-mail est vérifié après le 100 %, l'éligibilité est rattrapée automatiquement.
- Écran de félicitations : « Télécharger mon certificat » et « Réclamer mon abonnement Claude Pro ». Le formulaire confirme le nom et l'e-mail, puis affiche : « Votre demande est enregistrée. Retrouvez son avancement dans votre espace personnel. »
- Statuts : Éligible → Demande enregistrée → En cours de remise → Remis. « Remis » exige un lien cadeau ou une modalité, plus une référence de livraison ; la date est enregistrée.
- Le mot de passe Claude du participant n'est jamais demandé. Le lien cadeau n'est visible que par le bénéficiaire et l'administration.

## 6. Structure

```
academy/
├── academy_site/        réglages Django, URL racine, WSGI
├── learning/
│   ├── models.py        formations, leçons, examen, tentatives, certificats, récompenses
│   ├── services.py      règles métier (déblocage, correction, seuil, certificat, récompense)
│   ├── pdf.py           certificat A4 paysage + QR code
│   ├── views/main.py    parcours apprenant
│   ├── views/staff.py   administration (/gestion/)
│   ├── management/commands/seed_demo.py
│   └── tests/           parcours de bout en bout
├── templates/           pages (français)
└── static/academy/      CSS, JavaScript, éditeur visuel
```
