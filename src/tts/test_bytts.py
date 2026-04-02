

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://91b2-34-16-241-128.ngrok-free.app/tts"
ma_voix_ref = r"..\..\data\reference_audio\ma_voix_ref.wav"

with open(ma_voix_ref, "rb") as audio_file:
    response = requests.post(
        url,
        data={
            "text": (
                "Machine learning is one of the most transformative technologies of the 21st century. "
                "It is a branch of artificial intelligence that enables computers to learn from data and "
                "improve their performance on tasks without being explicitly programmed. The field has "
                "grown rapidly over the past decade, driven by the availability of large datasets, "
                "increased computational power, and advances in algorithms."
            ),
            "exaggeration": 0.5,
            "cfg_weight": 0.5,
        },
        files={
            "reference": ("reference.wav", audio_file, "audio/wav"),
        },
        timeout=300,
        verify=False,
    )

if response.status_code == 200:
    with open("output_clone.wav", "wb") as f:
        f.write(response.content)
    print("✅ Sauvegardé : output_clone.wav")
else:
    print(f"❌ Erreur {response.status_code} : {response.text}")