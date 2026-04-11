import os
from pydub import AudioSegment
import webrtcvad

from preprocessing.vad import get_segments
from preprocessing.chunks import chunk_audio
from preprocessing.audio_cleaner import clean_audio
import librosa
import numpy as np


def run_pipeline(
    input_dir,
    output_dir,
    segment_size=30,
    overlap=1,
    export_format="wav"
):

    # 1. Charger tous les fichiers audio
    supported = {".wav"}
    audio_files = [
        f for f in os.listdir(input_dir)
        if os.path.splitext(f)[1].lower() in supported
    ]

    if not audio_files:
        print(f" Aucun fichier audio trouvé dans : {input_dir}")
        return

    print(f" {len(audio_files)} fichier(s) trouvé(s)\n")

    for filename in audio_files:
        filepath = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        print(f"🎙️  Traitement : {filename}")

        # 2. Chargement
        # audio = AudioSegment.from_file(filepath)
        audio, sr = librosa.load(filepath, sr=16000, mono=True)
        # sr = audio.frame_rate
        audio_cleaned = clean_audio(audio, sr)
        # 3. Suppression des longs silences

        # 4. Normalisation
        sample_width = 2

        audio_clipped = np.clip(audio, -1.0, 1.0)
        max_val = float(2 ** (sample_width * 8 - 1))
        audio_int = (audio_clipped * max_val).astype(np.int16)
        audio_cleaned =AudioSegment(
            audio_int.tobytes(),
            frame_rate=sr,
            sample_width=sample_width,
            channels=1
        )

        cleaned = get_segments([audio_cleaned])[0]
        print(f"   Durée originale : {len(audio)/1000:.1f}s → "
              f"après nettoyage : {len(cleaned)/1000:.1f}s")

        # 4. Découpage en chunks
        audio_chunks = chunk_audio(cleaned, segment_size, overlap)
        print(f"   → {len(audio_chunks)} chunk(s) de ~{segment_size}s")

        # 5. Sauvegarde
        for i, chunk in enumerate(audio_chunks):
            out_name = f"{base_name}_chunk_{i+1:04d}.{export_format}"
            out_path = os.path.join(output_dir, out_name)
            chunk.export(out_path, format=export_format)

        print(f"   ✅ Sauvegardé dans : {output_dir}\n")

    print(f"🎉 Pipeline terminé — {output_dir}")




if __name__ == "__main__":
    run_pipeline(
        input_dir="C:/Users/hp/Desktop/DL_ project/Lecture-Audio-Summarization-using-Deep-Learning/data/raw",
        output_dir="C:/Users/hp/Desktop/DL_ project/Lecture-Audio-Summarization-using-Deep-Learning/data/processed/audio_cleaned",
        segment_size=30,
        overlap=1,
        export_format="wav"
    )
