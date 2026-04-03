# api/main.py
import os
import sys
import tempfile
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn

# Ajouter le src/ au path pour importer vos modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Imports depuis votre projet existant
from preprocessing.pipline import run_pipeline as process_audio
from asr.audio_transcriber import transcribe_audio
from nlp.summarizer import summarize_file  # ou resumer_fichier selon votre nom
from tts.test_bytts import generate_tts as tts_generate  # adaptez selon votre structure



app = FastAPI(
    title="Lecture Audio Summarization API",
    version="1.0.0"
)

# Chemins (à adapter selon votre structure)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/summarize")
async def summarize_endpoint(
    audio: UploadFile = File(...),
    reference_voice: UploadFile = File(None),
    target_words: int = Form(150),
    do_tts: bool = Form(True)
):
    """
    Audio → Transcription → Résumé → TTS
    """
    temp_id = tempfile.mkdtemp(dir=TEMP_DIR)
    
    try:
        # 1. Sauvegarder l'audio uploadé
        input_audio = os.path.join(temp_id, "input.wav")
        with open(input_audio, "wb") as f:
            f.write(await audio.read())
        
        # Sauvegarder voix de référence
        ref_voice_path = None
        if reference_voice:
            ref_voice_path = os.path.join(temp_id, "reference.wav")
            with open(ref_voice_path, "wb") as f:
                f.write(await reference_voice.read())
        
        print(f"\n🎙️ Traitement: {audio.filename}")
        
        # 2. Traitement audio (VAD + chunks) - VOTRE FONCTION
        print("[1/4] Traitement audio...")
        print(f"DEBUG tts_generate type--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: {type(tts_generate)}") 

        audio_chunks_dir = os.path.join(temp_id, "chunks")
        os.makedirs(audio_chunks_dir, exist_ok=True)  # <-- AJOUTER CETTE LIGNE

        
        # Adaptez cet appel selon la signature de votre run_pipeline
        process_audio(
            input_dir=temp_id,           # dossier contenant input.wav
            output_dir=audio_chunks_dir,
            segment_size=30,
            overlap=1,
            export_format="wav"
        )
        print(f"    ✓ Chunks créés")
        
        # 3. Transcription - VOTRE FONCTION
        print("[2/4] Transcription...")
        transcript = transcribe_audio(audio_chunks_dir)
        print(f"    ✓ Transcription: {len(transcript.split())} mots")
        
        # Sauvegarder transcription
        base_name = os.path.splitext(audio.filename)[0]
        transcript_file = f"{base_name}_transcript.txt"
        transcript_path = os.path.join(OUTPUT_DIR, transcript_file)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        # 4. Résumé - VOTRE FONCTION
        print("[3/4] Résumé...")
        
        # Créer un fichier temp pour le résumé (si votre fonction lit un fichier)
        temp_transcript = os.path.join(temp_id, "transcript.txt")
        with open(temp_transcript, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        # Appel à votre fonction de résumé
        summary_result = summarize_file(
            file_name="transcript.txt",
            target_words=target_words,
            input_dir=temp_id,
            verbose=False  # ou True selon vos besoins
        )
        
        # Si votre fonction retourne un dict, adaptez :
        if isinstance(summary_result, dict):
            summary_text = summary_result.get("summary", summary_result)
            word_count = summary_result.get("word_count", len(summary_text.split()))
            faithfulness = summary_result.get("faithfulness", 0.0)
        else:
            summary_text = summary_result
            word_count = len(summary_text.split())
            faithfulness = 0.0
        
        print(f"    ✓ Résumé: {word_count} mots")
        
        # Sauvegarder résumé
        summary_file = f"{base_name}_summary.txt"
        summary_path = os.path.join(OUTPUT_DIR, summary_file)
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)
        
        # 5. TTS - VOTRE FONCTION
        audio_url = None
        if do_tts:
            print("[4/4] TTS...")
            
            output_audio = os.path.join(OUTPUT_DIR, f"{base_name}_summary.wav")
            
            # Utiliser votre fonction TTS existante
            success = tts_generate(
                text=summary_text,
                reference_voice=ref_voice_path or "data/reference_audio/ma_voix_ref.wav",
                output_path=output_audio
            )
            
            if success and os.path.exists(output_audio):
                audio_url = f"/download/{base_name}_summary.wav"
                print(f"    ✓ Audio généré")
        
        return {
            "success": True,
            "text_summary": summary_text,
            "word_count": word_count,
            "faithfulness": faithfulness,
            "files": {
                "transcript": f"/download/{transcript_file}",
                "summary_text": f"/download/{summary_file}",
                "summary_audio": audio_url
            }
        }
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Nettoyage
        if os.path.exists(temp_id):
            shutil.rmtree(temp_id)


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    return FileResponse(file_path)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)