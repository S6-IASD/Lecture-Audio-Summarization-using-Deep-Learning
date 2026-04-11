from pydub import AudioSegment


def chunk_audio(
    audio: AudioSegment,
    chunk_duration: int = 30,   # secondes
    overlap: int = 1            # chevauchement en secondes
) -> list[AudioSegment]:
    chunk_ms   = chunk_duration * 1000
    overlap_ms = overlap * 1000
    step_ms    = chunk_ms - overlap_ms

    chunks = []
    start  = 0

    while start < len(audio):
        end   = min(start + chunk_ms, len(audio))
        chunk = audio[start:end]

        if len(chunk) >= 1000:   # ignorer les segments < 1s
            chunks.append(chunk)

        if end >= len(audio):
            break
        start += step_ms

    return chunks

