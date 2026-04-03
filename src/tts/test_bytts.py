

# import os


# import requests
# import urllib3

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# url = "https://9d91-136-109-62-116.ngrok-free.app/tts"
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ma_voix_ref = os.path.join(
#     BASE_DIR,
#     "..",
#     "..",
#     "data",
#     "reference_audio",
#     "ma_voix_ref.wav"
# )

# def generate_tts(text):
#     with open(ma_voix_ref, "rb") as audio_file:
#         response = requests.post(
#             url,
#             data={
#                 "text": text,
#                 "exaggeration": 0.5,
#                 "cfg_weight": 0.5,
#             },
#             files={
#                 "reference": ("reference.wav", audio_file, "audio/wav"),
#             },
#             timeout=300,
#             verify=False,
#         )

#     if response.status_code == 200:
#         with open("output_clone.wav", "wb") as f:
#             f.write(response.content)
#         print("✅ Sauvegardé : output_clone.wav")
#     else:
#         print(f"❌ Erreur {response.status_code} : {response.text}")

import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ma_voix_ref = os.path.join(
    BASE_DIR, "..", "..", "data", "reference_audio", "ma_voix_ref.wav"
)

NGROK_URL = "https://dec1-34-16-173-102.ngrok-free.app/tts"

def generate_tts(text: str, reference_voice: str = None, output_path: str = "output_clone.wav") -> bool:
    """
    Returns True on success, False on failure.
    """
    ref_path = reference_voice if (reference_voice and os.path.exists(reference_voice)) else ma_voix_ref

    try:
        with open(ref_path, "rb") as audio_file:
            response = requests.post(
                NGROK_URL,
                data={
                    "text": text,
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
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Sauvegardé : {output_path}")
            return True
        else:
            print(f"❌ Erreur {response.status_code} : {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception TTS : {e}")
        return False