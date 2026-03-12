import whisper


def transcribe_segment(audio_path):

    # charger le modèle
    model = whisper.load_model("base")
    # transcription
    result = model.transcribe(audio_path)
    # texte obtenu
    text = result["text"]

    return text

transcribed_text = transcribe_segment("../../data/processed/audio_cleaned/Shaw - Chbabi [MAg_YfqDFx4]_chunk_0002.wav")
print("-"*30, "\n", transcribed_text,"\n", "-"*30)