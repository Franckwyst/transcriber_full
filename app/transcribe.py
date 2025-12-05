import os
from pathlib import Path

from pydub import AudioSegment
import whisper


# --------- PARAMÈTRES À ADAPTER SI BESOIN ---------

# Dossier où tu mets les mémos exportés de l'iPhone
INPUT_DIR = Path("input")

# Dossier où seront créés les fichiers texte
OUTPUT_DIR = Path("output")

# Modèle Whisper ("tiny", "base", "small", "medium", "large")
WHISPER_MODEL_NAME = "small"

# Durée maximum d'un morceau en minutes (pour éviter les soucis mémoire)
MAX_CHUNK_MINUTES = 20

# --------------------------------------------------


def ensure_directories() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_whisper_model():
    print(f"Chargement du modèle Whisper '{WHISPER_MODEL_NAME}' (CPU)...")
    model = whisper.load_model(WHISPER_MODEL_NAME, device="cpu")
    print("Modèle chargé.")
    return model


def split_audio_if_needed(audio_path: Path) -> list[Path]:
    """
    Coupe le fichier audio en morceaux de MAX_CHUNK_MINUTES si nécessaire.
    Retourne la liste des chemins des morceaux (un seul élément si pas de découpe).
    """
    audio = AudioSegment.from_file(audio_path)
    max_ms = MAX_CHUNK_MINUTES * 60_000  # minutes -> millisecondes

    if len(audio) <= max_ms:
        # Pas besoin de découper
        return [audio_path]

    print(f"- Fichier long détecté ({len(audio) / 60000:.1f} min), découpe en morceaux...")

    chunk_paths: list[Path] = []
    start = 0
    index = 0

    chunks_dir = audio_path.with_suffix("").parent / f"{audio_path.stem}_chunks"
    chunks_dir.mkdir(exist_ok=True)

    while start < len(audio):
        end = min(start + max_ms, len(audio))
        chunk = audio[start:end]
        chunk_path = chunks_dir / f"{audio_path.stem}_part{index:02d}.wav"
        chunk.export(chunk_path, format="wav")
        chunk_paths.append(chunk_path)
        index += 1
        start = end

    print(f"- {len(chunk_paths)} morceaux créés.")
    return chunk_paths


def transcribe_file(model, audio_path: Path) -> str:
    """
    Transcrit un seul fichier audio (éventuellement coupé en morceaux).
    Retourne tout le texte concaténé.
    """
    print(f"Traitement de : {audio_path.name}")
    chunk_paths = split_audio_if_needed(audio_path)

    full_transcript_parts: list[str] = []

    for idx, chunk_path in enumerate(chunk_paths):
        print(f"  > Transcription du morceau {idx + 1}/{len(chunk_paths)} : {chunk_path.name}")
        result = model.transcribe(str(chunk_path), language="fr", verbose=False)
        text = result.get("text", "").strip()
        full_transcript_parts.append(text)

    full_transcript = "\n\n".join(part for part in full_transcript_parts if part)
    return full_transcript


def save_transcript(audio_path: Path, transcript: str) -> None:
    """
    Sauvegarde la transcription dans OUTPUT_DIR avec le même nom de base que l'audio.
    """
    output_file = OUTPUT_DIR / f"{audio_path.stem}.txt"
    output_file.write_text(transcript, encoding="utf-8")
    print(f"  => Transcription enregistrée dans : {output_file}")


def main() -> None:
    ensure_directories()

    audio_extensions = {".m4a", ".mp3", ".wav", ".flac", ".aac", ".caf"}
    audio_files = sorted(
        [p for p in INPUT_DIR.iterdir() if p.is_file() and p.suffix.lower() in audio_extensions]
    )

    if not audio_files:
        print(f"Aucun fichier audio trouvé dans {INPUT_DIR.resolve()}")
        print("Copie d'abord tes mémos iPhone dans ce dossier, puis relance le script.")
        return

    model = load_whisper_model()

    for audio_path in audio_files:
        try:
            transcript = transcribe_file(model, audio_path)
            save_transcript(audio_path, transcript)
        except Exception as e:
            print(f"Erreur pendant la transcription de {audio_path.name} : {e}")

    print("Terminé.")


if __name__ == "__main__":
    main()
