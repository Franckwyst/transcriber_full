# transcriber_full

Petit projet Docker pour transcrire automatiquement des fichiers audio en texte avec Whisper, en français, sans installation Python locale.

L'objectif est simple : tu déposes un ou plusieurs fichiers audio dans le dossier `input/`, tu lances Docker, et le projet génère les transcriptions texte dans `output/`.

## A quoi sert ce projet

Ce dépôt sert à transformer des mémos vocaux, interviews, réunions ou appels enregistrés en fichiers `.txt` lisibles.

Le script :

- lit les fichiers audio présents dans `input/`
- détecte les formats audio pris en charge
- découpe automatiquement les fichiers trop longs en morceaux de 20 minutes
- transcrit chaque morceau avec le modèle Whisper `small`
- regroupe le texte final dans un fichier `.txt` dans `output/`

## Pour qui

Ce projet est adapté si tu veux :

- transcrire des mémos iPhone
- récupérer rapidement le texte d'un enregistrement
- éviter d'installer Python, ffmpeg et Whisper directement sur ta machine
- travailler avec un usage simple via Docker

## Fonctionnement simplifié

1. Tu mets ton audio dans `input/`
2. Docker lance le script Python
3. Whisper transcrit le contenu en français
4. Le texte final est enregistré dans `output/`

Si le fichier est long, le projet le coupe d'abord en plusieurs morceaux pour éviter les problèmes de mémoire.

## Structure du projet

```text
transcriber_full/
├── app/
│   └── transcribe.py
├── input/
├── output/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Prérequis

Tu dois avoir seulement :

- Docker
- Docker Compose

Aucune installation Python locale n'est nécessaire.

## Lancement rapide

### 1. Ajouter un fichier audio

Copie ton fichier audio dans le dossier `input/`.

Exemples de formats acceptés :

- `.m4a`
- `.mp3`
- `.wav`
- `.flac`
- `.aac`
- `.caf`

### 2. Construire l'image Docker

```bash
docker compose build
```

Cette étape installe notamment :

- `ffmpeg`
- `openai-whisper`
- `pydub`

### 3. Lancer la transcription

```bash
docker compose up
```

Le conteneur exécute cette commande :

```bash
python transcribe.py
```

## Résultat attendu

Pour un fichier comme :

```text
input/mon-audio.m4a
```

Tu obtiendras :

```text
output/mon-audio.txt
```

Si le fichier est trop long, le script peut aussi créer temporairement un dossier de morceaux, par exemple :

```text
input/mon-audio_chunks/
```

avec des fichiers intermédiaires `.wav` utilisés pour la transcription.

## Explication du chunking

Le "chunking" consiste à découper un fichier audio long en plusieurs petits morceaux avant de le transcrire.

Dans ce projet, le chunking se déclenche automatiquement quand un fichier dépasse `20` minutes, car la variable `MAX_CHUNK_MINUTES` est actuellement réglée à `20`.

### Pourquoi découper l'audio

Le découpage sert à éviter plusieurs problèmes :

- consommer trop de mémoire d'un coup
- ralentir fortement la transcription
- rendre le traitement plus fragile sur les gros fichiers

En pratique, au lieu d'envoyer un très long audio à Whisper en une seule fois, le script le traite morceau par morceau.

### Comment ça se passe concrètement

Prenons un fichier de `52` minutes :

- le script lit le fichier audio complet
- il calcule une taille maximale de morceau de `20` minutes
- il crée plusieurs segments successifs
- il exporte ces segments en fichiers `.wav`
- il transcrit chaque segment séparément
- il regroupe ensuite tous les textes dans le bon ordre dans un seul fichier final

Dans cet exemple, on obtiendrait en général :

- un morceau de 20 minutes
- un deuxième morceau de 20 minutes
- un dernier morceau d'environ 12 minutes

### Où sont créés les morceaux

Les morceaux sont enregistrés dans un sous-dossier créé à côté du fichier d'origine.

Exemple :

```text
input/reunion-client.m4a
```

peut produire :

```text
input/reunion-client_chunks/
├── reunion-client_part00.wav
├── reunion-client_part01.wav
└── reunion-client_part02.wav
```

Le nommage suit cette logique :

- `_chunks` pour le dossier des morceaux
- `_part00`, `_part01`, `_part02` pour l'ordre des segments

### Ce qui est transcrit au final

Même si plusieurs morceaux sont créés, le résultat final reste un seul fichier texte.

Exemple :

```text
output/reunion-client.txt
```

Le script concatène les transcriptions des morceaux dans l'ordre, avec des sauts de ligne entre les blocs.

### Important à savoir

- Le chunking ne se déclenche pas pour les fichiers de 20 minutes ou moins.
- Les morceaux sont créés en `.wav`, même si ton fichier d'origine est en `.m4a` ou `.mp3`.
- Le découpage est purement chronologique : le script ne détecte pas les silences ni les changements de sujet.
- Les dossiers de chunks sont ignorés par `.gitignore`, donc ils ne sont pas censés partir sur GitHub.

## Ce que fait exactement le script

Le fichier [app/transcribe.py](/Users/franckwystyrk/transcriber_full/app/transcribe.py:1) :

- crée automatiquement les dossiers `input/` et `output/` s'ils n'existent pas
- charge le modèle Whisper `small`
- travaille en CPU
- force la transcription en français avec `language="fr"`
- traite tous les fichiers audio trouvés dans `input/`
- sauvegarde un fichier texte par audio

## Paramètres modifiables

Dans [app/transcribe.py](/Users/franckwystyrk/transcriber_full/app/transcribe.py:1), tu peux ajuster facilement :

- `WHISPER_MODEL_NAME = "small"` : qualité, vitesse et consommation mémoire
- `MAX_CHUNK_MINUTES = 20` : durée maximale d'un morceau
- `INPUT_DIR` : dossier des fichiers source
- `OUTPUT_DIR` : dossier des résultats

### Choix du modèle Whisper

Tu peux remplacer `small` par :

- `tiny` : plus rapide, moins précis
- `base` : léger compromis
- `small` : bon équilibre actuel
- `medium` : plus précis, plus lourd
- `large` : plus précis, mais beaucoup plus lent et gourmand

## Exemple d'usage concret

Cas simple :

1. Tu exportes un mémo vocal iPhone en `.m4a`
2. Tu le places dans `input/`
3. Tu lances `docker compose up`
4. Tu récupères le texte dans `output/`
5. Tu peux ensuite copier ce texte dans ChatGPT ou un autre outil pour faire un résumé, un compte-rendu ou une analyse

## Limites actuelles

Le projet est volontairement minimal. Il ne fait pas encore :

- de résumé automatique
- de génération de titres ou chapitres
- d'horodatage `.srt` ou `.vtt`
- de détection automatique de langue
- d'interface graphique

Il produit avant tout une transcription texte brute, simple à réutiliser.

## Points importants à connaître

- La transcription se fait en CPU, donc les fichiers longs peuvent prendre du temps.
- Le premier lancement peut être plus long car Whisper doit être installé ou téléchargé dans l'environnement.
- Les dossiers `input/` et `output/` sont montés comme volumes Docker, donc les fichiers restent accessibles sur ta machine.
- Les fichiers audio, les sorties texte et les morceaux intermédiaires sont ignorés par `.gitignore`.

## Dépannage rapide

### Aucun fichier n'est transcrit

Vérifie que :

- le fichier est bien dans `input/`
- son extension est prise en charge
- le fichier n'est pas corrompu

### Docker ne démarre pas

Vérifie que Docker Desktop est bien lancé.

### La transcription est lente

C'est normal avec un traitement CPU, surtout sur des fichiers longs. Tu peux :

- tester avec un fichier plus court
- utiliser un modèle plus léger comme `tiny` ou `base`

## Commandes utiles

Construire l'image :

```bash
docker compose build
```

Lancer la transcription :

```bash
docker compose up
```

Relancer après modification du code :

```bash
docker compose up --build
```

## En résumé

`transcriber_full` est un outil simple pour convertir des fichiers audio en texte en français avec Whisper via Docker.

Il est pensé pour un usage concret, rapide et compréhensible : déposer un fichier, lancer la commande, récupérer la transcription.
