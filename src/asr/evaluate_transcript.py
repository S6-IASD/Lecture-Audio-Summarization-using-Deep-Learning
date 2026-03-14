import whisper
from jiwer import wer, cer
from datasets import load_dataset
import numpy as np
import soundfile as sf
import io
import datasets 
import re

# 1. Charger le modèle Whisper
model = whisper.load_model("base")

def normaliser(texte):
    texte = texte.lower()
    texte = re.sub(r"[^\w\s]", "", texte)  # enlever ponctuation
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte

# 2. Charger LibriSpeech
ds = load_dataset("librispeech_asr", "clean", split="test", streaming=True)
ds = ds.cast_column("audio", datasets.Audio(decode=False))  # Ne pas décoder automatiquement
ds = list(ds.take(100))

# 3. Transcription + collecte
references = []
hypotheses = []

for i, sample in enumerate(ds):
    ref = sample["text"].lower()
    
    # Décoder manuellement l'audio avec soundfile
    audio_bytes = sample["audio"]["bytes"]
    audio_array, sr = sf.read(io.BytesIO(audio_bytes))
    audio_array = audio_array.astype(np.float32)
    
    # Transcription Whisper
    result = model.transcribe(audio_array, language="en")
    hyp = result["text"].lower().strip()
    
    references.append(normaliser(ref))
    hypotheses.append(normaliser(hyp))
    
    print(f"[{i+1}/100] WER partiel : {wer(references, hypotheses):.2%}")

# 4. Résultats finaux
print("\n===== RÉSULTATS =====")
print(f"WER  : {wer(references, hypotheses):.2%}")
print(f"CER  : {cer(references, hypotheses):.2%}")
