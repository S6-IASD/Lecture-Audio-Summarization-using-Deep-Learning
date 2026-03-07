import os
from pydub import AudioSegment
import webrtcvad

from vad import get_segments
from chunks import chunk_audio

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
        audio = AudioSegment.from_file(filepath)

        # 3. Suppression des longs silences
        cleaned = get_segments([audio])[0]
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
