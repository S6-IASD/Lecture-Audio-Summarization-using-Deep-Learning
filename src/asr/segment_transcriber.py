import whisper


def transcribe_segment(audio_path):

    # charger le modèle
    model = whisper.load_model("base")
    # transcription
    result = model.transcribe(audio_path)
    # texte obtenu
    text = result["text"]

    return text

