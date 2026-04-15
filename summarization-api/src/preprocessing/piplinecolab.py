# preprocessing/pipeline.py
import io
import os
import numpy as np
from pydub import AudioSegment
import librosa

from preprocessing.vad import get_segments
from preprocessing.chunks import chunk_audio
from preprocessing.audio_cleaner import clean_audio


def run_pipeline(
    audio_bytes: bytes,
    filename: str = "input.wav",
    segment_size: int = 30,
    overlap: int = 1,
    export_format: str = "wav",
) -> list[dict]:
    """
    Prend un fichier audio en bytes, applique le pipeline complet
    (nettoyage → VAD → chunking) et retourne les chunks en mémoire.

    Args:
        audio_bytes   : contenu brut du fichier audio (lu depuis UploadFile)
        filename      : nom original du fichier (pour les logs et noms des chunks)
        segment_size  : durée max d'un chunk en secondes (défaut 30)
        overlap       : chevauchement entre chunks en secondes (défaut 1)
        export_format : format d'export des chunks (défaut "wav")

    Returns:
        Liste de dicts ordonnés :
        [
            {
                "key"     : "chunk_0",               # clé multipart pour Colab
                "filename": "lecture_chunk_0.wav",   # nom du fichier
                "bytes"   : b"...",                  # contenu WAV en mémoire
                "mimetype": "audio/wav",
            },
            ...
        ]
    """
    base_name = os.path.splitext(filename)[0]
    print(f"\n🎙️  Pipeline : {filename}")

    # ── 1. Charger l'audio depuis les bytes ───────────────────
    audio_io       = io.BytesIO(audio_bytes)
    audio_np, sr   = librosa.load(audio_io, sr=16000, mono=True)

    # ── 2. Nettoyage (normalisation + débruitage) ─────────────
    audio_cleaned_np = clean_audio(audio_np, sr)

    # ── 3. Convertir numpy → AudioSegment (pour VAD + chunking) ──
    sample_width  = 2  # 16-bit PCM
    audio_clipped = np.clip(audio_cleaned_np, -1.0, 1.0)
    max_val       = float(2 ** (sample_width * 8 - 1))
    audio_int     = (audio_clipped * max_val).astype(np.int16)

    audio_segment = AudioSegment(
        audio_int.tobytes(),
        frame_rate=sr,
        sample_width=sample_width,
        channels=1,
    )

    print(f"   Durée originale : {len(audio_segment) / 1000:.1f}s")

    # ── 4. VAD — suppression des longs silences ───────────────
    cleaned_segment  = get_segments([audio_segment])[0]
    print(f"   Après VAD       : {len(cleaned_segment) / 1000:.1f}s")

    # ── 5. Découpage en chunks ────────────────────────────────
    audio_chunks = chunk_audio(cleaned_segment, segment_size, overlap)
    print(f"   → {len(audio_chunks)} chunk(s) de ~{segment_size}s")

    # ── 6. Exporter chaque chunk en bytes (sans écrire sur disque) ──
    result = []
    for i, chunk in enumerate(audio_chunks):
        buf = io.BytesIO()
        chunk.export(buf, format=export_format)
        buf.seek(0)

        result.append({
            "key"     : f"chunk_{i}",
            "filename": f"{base_name}_chunk_{i}.{export_format}",
            "bytes"   : buf.read(),
            "mimetype": f"audio/{export_format}",
        })

    print(f"   ✅ {len(result)} chunk(s) prêts en mémoire\n")
    return result