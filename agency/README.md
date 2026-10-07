# ChronoShorts — agence IA autonome de YouTube Shorts historiques

Une agence de production complète, déployable sur un VPS Hostinger, qui fabrique des
documentaires courts (9:16, 45-60 s) sur la vie quotidienne des civilisations, les
contrôle, puis les livre sur Telegram.

```
Stratège ──► DIRECTEUR (Opus) choisit le sujet et l'angle
                 │
          Historien (recherche web, bibliographie, incertitudes)
                 │
          Scénariste ⇄ fact-check historien ⇄ revue directeur (≤ 2 révisions)
                 │
          TTS de contrôle → ajustement du script au débit réel (jamais d'accélération)
                 │
          Storyboard ─┬─► Direction artistique ─► Prompt engineer ─► Animateur ─► revue directeur
                      ├─► Directeur voix
                      ├─► Monteur / sound design
                      └─► SEO
                 │
          Par scène, en parallèle : voix (ElevenLabs/edge) · image clé (FLUX) · clip (Seedance/Kling) ou composition animée
                 │
          FFmpeg : transitions, mixage avec ducking, loudnorm -14 LUFS, sous-titres mot à mot, H.264/AAC
                 │
          QA (Haiku) → décision finale (Opus) → Telegram (vidéo + description + sources + metadata.json)
```

## Les 11 agents

| # | Agent | Modèle | Rôle |
|---|-------|--------|------|
| — | **Directeur** | Claude Opus 5.5 | stratégie, choix du sujet, revues script/visuels, décision de diffusion |
| 1 | Historien | Claude Haiku 5.5 | dossier sourcé (recherche web), niveaux de confiance, fact-check |
| 2 | Stratège viral | Haiku | idées, hooks honnêtes, anti-répétition |
| 3 | Scénariste | Haiku | hook → contexte → découverte → tension → révélation → conclusion |
| 4 | Storyboard | Haiku | scènes 3-6 s, action visible, émotion, caméra, transition |
| 5 | Directeur artistique | Haiku | art bible, fiches personnages avec *consistency token* |
| 6 | Prompt engineer | Haiku | prompts image/vidéo cohérents |
| 7 | Animateur | Haiku | expressions, gestes, mouvements de caméra, anti-diaporama |
| 8 | Directeur voix | Haiku | texte TTS ponctué, émotions, persona stable |
| 9 | Monteur / son | Haiku | plan sonore (musique, ambiances, SFX, sous-titres) |
| 10 | SEO & QA | Haiku | titre, description, hashtags, sources, disclaimer, rapport QA |

Les identifiants de modèles sont vérifiés au démarrage via `GET /v1/models` ; si un
modèle n'existe pas sur le compte, la chaîne de repli configurée est utilisée (jamais
d'identifiant inventé). Les Haiku travaillent en parallèle ; Opus n'intervient qu'aux
points de décision (5 appels par vidéo).

## Garanties éditoriales et techniques

- **Rigueur** : chaque fait porte un niveau de confiance ; les scènes reconstituées sans
  preuve directe sont marquées dans le script et listées dans `metadata.json` et dans le
  disclaimer de la description.
- **Durée réelle** : la narration est synthétisée, mesurée, et le script est allongé ou
  raccourci par le scénariste jusqu'à viser 45-60 s. Aucune accélération vocale.
- **Animation réelle** : chaque scène est un clip généré par un modèle image→vidéo ; en
  cas d'échec ou sans API, une composition animée (zoom/panoramique adoucis, respiration
  lumineuse, grain) remplace la scène — jamais un diaporama fixe.
- **Sortie** : 1080×1920, 30 fps, H.264 High + AAC 192 k, -14 LUFS, sous-titres ASS mot à
  mot (mot courant surligné, RTL pour l'arabe) incrustés + SRT.
- **Reprise** : chaque étape est persistée dans `productions/<date>-<slug>/state.json` ;
  `chronoshorts produce --resume <dossier>` reprend sans refaire ce qui est fait.
- **Coûts** : suivi par agent (`state.json → costs`), envoyé dans le message Telegram.

## Installation sur le VPS Hostinger (Ubuntu)

```bash
# en root
git clone https://github.com/aybbkf/wavecast.git && cd wavecast/agency
bash deploy/install.sh          # ffmpeg, polices (Noto arabe), venv, services systemd
nano /opt/chronoshorts/.env     # clés API + Telegram (voir .env.example)
sudo -u chronoshorts /opt/chronoshorts/.venv/bin/chronoshorts check
sudo -u chronoshorts /opt/chronoshorts/.venv/bin/chronoshorts produce --seed "Une journée à Cordoue"
systemctl start chronoshorts-bot chronoshorts-scheduler
journalctl -fu chronoshorts-bot
```

Variante Docker : `docker compose -f deploy/docker-compose.yml up -d --build`.

## Utilisation

```bash
chronoshorts check                      # environnement, clés, modèles disponibles
chronoshorts produce                    # un Short, sujet choisi par le directeur
chronoshorts produce --seed "Mayas"     # avec contrainte éditoriale
chronoshorts produce --resume productions/20260101-090000-xxx
chronoshorts bot                        # Telegram : /produce [thème], /status, /history, /costs
chronoshorts schedule                   # CHRONO_DAILY_VIDEOS vidéos/jour à CHRONO_SCHEDULE_HOURS
```

## Fournisseurs

| Fonction | Défaut | Alternatives |
|----------|--------|--------------|
| Voix | ElevenLabs (`/with-timestamps`, une voix fixe pour la chaîne) | `edge` (gratuit, FR/EN/AR), `silent` (tests) |
| Images clés | Replicate `black-forest-labs/flux-1.1-pro` | tout modèle Replicate à `prompt`+`aspect_ratio`, `placeholder` |
| Clips | Replicate `bytedance/seedance-1-pro` | `kwaivgi/kling-v2.1`, `minimax/hailuo-02`, `kenburns` (local) |
| Musique | bibliothèque locale `assets/` + `library.json` | nappe synthétisée si vide |
| Livraison | Telegram Bot API | — |

Déposez vos musiques/ambiances **autorisées pour YouTube** dans `assets/` et décrivez-les
dans `assets/library.json` (humeurs : épique, mystérieux, contemplatif, tendu, chaleureux,
mélancolique). La musique est automatiquement ducked sous la voix.

## Langues

`CHRONO_LANGUAGE=fr|en|ar`. En arabe, les sous-titres utilisent `Noto Naskh Arabic`
(installée par `install.sh`) avec rendu RTL ; les prompts visuels restent en anglais.

## Tests

```bash
pip install -e ".[dev,edge]"
pytest            # 18 tests : unités, requêtes API simulées, production complète hors ligne (FFmpeg réel)
```

La production hors ligne (`tests/test_pipeline_offline.py`) exécute toute la chaîne avec
des agents factices et produit un vrai MP4 vérifié (ratio, codecs, durée, sous-titres,
métadonnées, reprise).

## Arborescence d'une production

```
productions/20260101-090000-une-nuit-a-cordoue/
├── state.json          # toutes les étapes (brief, dossier, script, storyboard, revues, QA, coûts)
├── journal.log
├── scenes/             # scene_NN.png (image clé), scene_NN_raw.mp4, scene_NN.mp4
├── audio/              # scene_NN.wav, full_N.wav, mix.wav, music_synth.wav
├── subtitles.ass / subtitles.srt
├── metadata.json       # titre, description, hashtags, sources, disclaimer, reconstitutions, rapport technique
├── thumbnail_frame.jpg
└── final.mp4
```
