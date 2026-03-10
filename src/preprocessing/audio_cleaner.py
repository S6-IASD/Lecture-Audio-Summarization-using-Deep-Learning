import librosa
import numpy as np
import soundfile as sf
import noisereduce as nr
from pathlib import Path


# Standard sample rate for speech processing
TARGET_SR = 16000


# def load_audio(file_path):
#     """Load audio and convert to mono + target sample rate."""
#     audio, sr = librosa.load(file_path, sr=TARGET_SR, mono=True)
#     return audio, sr


def normalize_audio(audio, target_peak: float = 0.95):
    """Peak-normalize waveform to a given target amplitude in [0, 1]."""
    peak = float(np.max(np.abs(audio)))
    if peak == 0.0:
        return audio
    scaled = audio / peak * float(target_peak)
    # Preserve original dtype when using NumPy arrays
    if isinstance(audio, np.ndarray):
        return scaled.astype(audio.dtype)
    return scaled


def reduce_noise(audio, sr):
    """Reduce background noise using spectral filtering."""
    return nr.reduce_noise(y=audio, sr=sr)


def clean_audio(audio, sr):
    """Full preprocessing pipeline for one audio file (without silence trimming)."""

    # 1. Load audio
    # audio, sr = load_audio(input_path)

    # 2. Normalize volume
    audio = normalize_audio(audio)

    # 3. Reduce background noise
    audio = reduce_noise(audio, sr)

    # 4. Normalize again after processing
    audio = normalize_audio(audio)

    # 5. Save cleaned audio
    # sf.write(output_path, audio, sr)
    return audio


# def main():
#     """Test the cleaner on a few example audio files."""

#     project_root = Path(__file__).resolve().parents[2]

#     # Put your test audios under: <project_root>/tests/data/audio_cleaner/input
#     input_folder = project_root / "tests" / "data" / "audio_cleaner" / "input"

#     # Cleaned files will go to: <project_root>/tests/data/audio_cleaner/output
#     output_folder = project_root / "tests" / "data" / "audio_cleaner" / "output"

#     output_folder.mkdir(exist_ok=True)

#     for file in input_folder.iterdir():

#         if file.suffix.lower() in [".wav", ".mp3", ".flac"]:
#             output_file = output_folder / f"{file.stem}_cleaned.wav"

#             print(f"Cleaning {file.name}...")
#             clean_audio(file, output_file)

#     print("Audio cleaning completed.")


# if __name__ == "__main__":
#     main()