import webrtcvad
from pydub import AudioSegment

def get_segments(audios, webvad=2, frame_ms=30, sample_rate=16000,
                 max_silence_ms=700):
    
    vad = webrtcvad.Vad(webvad)
    new_audios = []

    for audio in audios:
        audio = audio.set_frame_rate(sample_rate).set_channels(1).set_sample_width(2)
        expected_bytes = int(sample_rate * frame_ms / 1000) * 2

        result = AudioSegment.empty()
        silence_buffer = AudioSegment.empty()  # stocke les silences en attente
        silence_duration = 0

        for start_ms in range(0, len(audio) - frame_ms, frame_ms):
            frame = audio[start_ms:start_ms + frame_ms]
            raw = frame.raw_data

            if len(raw) != expected_bytes:
                continue

            if vad.is_speech(raw, sample_rate=sample_rate):
                # Silence court avant ce mot → on le garde
                if silence_duration <= max_silence_ms:
                    result += silence_buffer

                # Réinitialiser le buffer de silence
                silence_buffer = AudioSegment.empty()
                silence_duration = 0

                # Ajouter la parole
                result += frame

            else:
                # Accumuler le silence sans l'ajouter encore
                silence_buffer += frame
                silence_duration += frame_ms
                # Si silence_duration > max_silence_ms → silence_buffer sera ignoré

        new_audios.append(result)

    return new_audios
