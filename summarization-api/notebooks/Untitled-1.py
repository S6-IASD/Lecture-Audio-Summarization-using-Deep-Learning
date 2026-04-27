# %%
# Force-remove the broken Colab-preinstalled torch stack
!pip uninstall torch torchvision torchaudio -y

# Install from PyPI (has 2.6.0, unlike the cu121 index)
!pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
    --break-system-packages -q

# Install chatterbox AFTER torch is settled
!pip install chatterbox-tts --break-system-packages -q

# Pin numpy last
!pip install "numpy>=1.24,<2.0" --force-reinstall --break-system-packages -q

print("✅ Done")

# %%
!pip install flask pyngrok -q

# %%
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from flask import Flask, request, send_file
from pyngrok import ngrok
import threading, io, tempfile, os

device = "cuda" if torch.cuda.is_available() else "cpu"
model = ChatterboxTTS.from_pretrained(device=device)

from pyngrok import ngrok

# Fermer tous les tunnels existants
ngrok.kill()
print("✅ Tous les tunnels fermés")

app = Flask(__name__)

@app.route("/tts", methods=["POST"])
def tts():
    text = request.form.get("text", "")
    exaggeration = float(request.form.get("exaggeration", 0.5))
    cfg_weight = float(request.form.get("cfg_weight", 0.5))

    if not text:
        return {"error": "No text provided"}, 400

    # Save reference audio to temp file if provided
    ref_audio_path = None
    if "reference" in request.files:
        ref_file = request.files["reference"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        ref_file.save(tmp.name)
        ref_audio_path = tmp.name

    wav = model.generate(
        text,
        audio_prompt_path=ref_audio_path,  # None = default voice
        exaggeration=exaggeration,
        cfg_weight=cfg_weight,
    )

    # Cleanup temp file
    if ref_audio_path:
        os.unlink(ref_audio_path)

    buf = io.BytesIO()
    ta.save(buf, wav, model.sr, format="wav")
    buf.seek(0)
    return send_file(buf, mimetype="audio/wav", download_name="output.wav")

# Start ngrok + Flask
ngrok.set_auth_token("2xRpM51RznsqGfGjqIvzuAnOfJJ_2zMNuiFy8ixNSugF94Wbd")
public_url = ngrok.connect(5000)
print(f"🌐 API URL: {public_url}/tts")
threading.Thread(target=lambda: app.run(port=5000)).start()


