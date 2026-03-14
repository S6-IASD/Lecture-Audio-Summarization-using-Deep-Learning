import os
from segment_transcriber import transcribe_segment


def transcribe_audio(audio_segments_dir: str) -> str:
    audio_name = os.path.basename(audio_segments_dir)
    full_transcript = ''
    segments = sorted(os.listdir(audio_segments_dir))
    for segment_file in segments:
        if not segment_file.endswith('.wav'):
            continue
        segment_path = os.path.join(audio_segments_dir, segment_file)
        text = transcribe_segment(segment_path)
        full_transcript += text.strip() + ' '
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'transcripts', f'{audio_name}.txt')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_transcript.strip())
    return full_transcript.strip()


if __name__ == '__main__':
    transcribe_audio('..\\\\..\\\\data\\\\processed\\\\audio_cleaned')
