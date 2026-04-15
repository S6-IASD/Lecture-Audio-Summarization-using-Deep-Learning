# api/main.py
import os
import sys
import base64
import requests
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import traceback

# Ajouter src/ au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessing.piplinecolab import run_pipeline



COLAB_API_URL = os.environ.get("COLAB_API_URL", "https://7a86-34-6-70-29.ngrok-free.app")

# ─────────────────────────────────────────────────────────────
# Dossiers
# ─────────────────────────────────────────────────────────────
BASE_DIR   = os.path.join(os.path.dirname(__file__), '..')
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


app = FastAPI(
    title="Lecture Audio Summarization API",
    description="Pipeline local (VAD + chunking) → Colab API (Whisper + BART + TTS)",
    version="3.0.0",
)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

async def audio_to_chunks_payload(
    audio: UploadFile,
    reference: UploadFile = None,
) -> tuple[list, dict]:
    """
    Lit l'audio uploadé → run_pipeline (VAD + chunking en mémoire)
    → construit le payload multipart prêt pour l'API Colab.

    Returns:
        files_payload : liste de tuples pour requests.post(files=...)
        meta          : { "filename": str, "nb_chunks": int }
    """
    audio_bytes = await audio.read()
    filename    = audio.filename or "input.wav"

    # Pipeline local : nettoyage → VAD → chunks en mémoire
    chunks = run_pipeline(audio_bytes=audio_bytes, filename=filename)

    if not chunks:
        raise HTTPException(
            status_code=422,
            detail=(
                "Le pipeline n'a produit aucun chunk. "
                "Vérifie que l'audio contient de la parole détectable."
            )
        )

    files_payload = [
        (chunk["key"], (chunk["filename"], chunk["bytes"], chunk["mimetype"]))
        for chunk in chunks
    ]

    # Ajouter la voix de référence TTS si fournie
    if reference is not None:
        ref_bytes = await reference.read()
        ref_name  = reference.filename or "reference.wav"
        files_payload.append(
            ("reference", (ref_name, ref_bytes, "audio/wav"))
        )

    meta = {"filename": filename, "nb_chunks": len(chunks)}
    return files_payload, meta


def call_colab(
    route: str,
    files_payload: list,
    data: dict,
    timeout: int = 300,
) -> dict:
    """
    Envoie le payload multipart à l'API Colab et retourne le JSON.
    Lève HTTPException en cas d'erreur réseau ou réponse Colab en erreur.
    """
    url = f"{COLAB_API_URL}/{route}"
    print(f"  → Appel Colab : POST {url}")
    try:
        resp = requests.post(url, files=files_payload, data=data, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Impossible de joindre l'API Colab ({COLAB_API_URL}). "
                "Vérifie que le notebook Colab est lancé et que COLAB_API_URL est à jour."
            )
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="L'API Colab a mis trop de temps à répondre (timeout)."
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erreur Colab API : {e}")

    result = resp.json()
    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Erreur Colab : {result['error']}")

    return result



@app.post("/transcript")
async def transcript_endpoint(
    audio: UploadFile = File(...),
):
    
    try:
        # ... ton code existant ...
        print(f"\n[/transcript] Reçu : {audio.filename}")

        files_payload, meta = await audio_to_chunks_payload(audio)
        print(f"  Pipeline : {meta['nb_chunks']} chunks créés")

        data = call_colab("transcript", files_payload, data={})

        return {
            "success"      : True,
            "transcription": data["transcription"],
            "nb_chunks"    : data.get("nb_chunks", meta["nb_chunks"]),
            "word_count"   : data.get("word_count", len(data["transcription"].split())),
        }
        pass
    except Exception as e:
        traceback.print_exc()          
        return {'error': str(e), 'trace': traceback.format_exc()}, 500




@app.post("/resume")
async def resume_endpoint(
    audio       : UploadFile = File(...),
    target_words: int = Form(150),
):
    print(f"\n[/resume] Reçu : {audio.filename} | target_words={target_words}")

    files_payload, meta = await audio_to_chunks_payload(audio)
    print(f"  Pipeline : {meta['nb_chunks']} chunks créés")

    data = call_colab(
        "resume",
        files_payload,
        data={"target_words": target_words},
    )

    transcription = data["transcription"]
    resume        = data["resume"]

    base            = os.path.splitext(meta["filename"])[0]
    transcript_file = f"{base}_transcript.txt"
    summary_file    = f"{base}_summary.txt"

    with open(os.path.join(OUTPUT_DIR, transcript_file), "w", encoding="utf-8") as f:
        f.write(transcription)
    with open(os.path.join(OUTPUT_DIR, summary_file), "w", encoding="utf-8") as f:
        f.write(resume)

    return {
        "success"      : True,
        "transcription": transcription,
        "resume"       : resume,
        "target_words" : data.get("target_words", target_words),
        "word_count"   : data.get("word_count", len(resume.split())),
        "files": {
            "transcript"  : f"/download/{transcript_file}",
            "summary_text": f"/download/{summary_file}",
        }
    }



@app.post("/resumeaudio")
async def resumeaudio_endpoint(
    audio       : UploadFile = File(...),
    reference   : UploadFile = File(None),
    target_words: int   = Form(150),
    exaggeration: float = Form(0.5),
    cfg_weight  : float = Form(0.5),
):
    print(f"\n[/resumeaudio] Reçu : {audio.filename} | target_words={target_words}")

    files_payload, meta = await audio_to_chunks_payload(audio, reference=reference)
    print(f"  Pipeline : {meta['nb_chunks']} chunks créés")

    data = call_colab(
        "resumeaudio",
        files_payload,
        data={
            "target_words": target_words,
            "exaggeration": exaggeration,
            "cfg_weight"  : cfg_weight,
        },
        timeout=600,  
    )

    transcription = data["transcription"]
    resume        = data["resume"]
    audio_b64     = data.get("audio_base64")


    base            = os.path.splitext(meta["filename"])[0]
    transcript_file = f"{base}_transcript.txt"
    summary_file    = f"{base}_summary.txt"
    audio_file      = f"{base}_summary.wav"

    with open(os.path.join(OUTPUT_DIR, transcript_file), "w", encoding="utf-8") as f:
        f.write(transcription)
    with open(os.path.join(OUTPUT_DIR, summary_file), "w", encoding="utf-8") as f:
        f.write(resume)

    audio_url = None
    if audio_b64:
        audio_bytes = base64.b64decode(audio_b64)
        with open(os.path.join(OUTPUT_DIR, audio_file), "wb") as f:
            f.write(audio_bytes)
        audio_url = f"/download/{audio_file}"
        print(f"  ✓ Audio sauvegardé : {audio_file}")

    return {
        "success"      : True,
        "transcription": transcription,
        "resume"       : resume,
        "word_count"   : data.get("word_count", len(resume.split())),
        "faithfulness" : data.get("faithfulness", 0.0),
        "files": {
            "transcript"   : f"/download/{transcript_file}",
            "summary_text" : f"/download/{summary_file}",
            "summary_audio": audio_url,
        }
    }


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    return FileResponse(file_path)



@app.get("/health")
async def health():
    colab_status = "unknown"
    try:
        r = requests.get(f"{COLAB_API_URL}/health", timeout=5)
        colab_status = r.json().get("status", "ok") if r.ok else "unreachable"
    except Exception:
        colab_status = "unreachable"

    return {
        "status"      : "ok",
        "colab_api"   : COLAB_API_URL,
        "colab_status": colab_status,
    }


if __name__ == "__main__":
    print("─" * 55)
    print(f"🚀 API locale  → http://0.0.0.0:8080")
    print(f"🌐 Colab API   → {COLAB_API_URL}")
    print("─" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8080)