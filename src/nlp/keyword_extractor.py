import json
from pathlib import Path
from keybert import KeyBERT

_model: KeyBERT | None = None

def _get_model() -> KeyBERT:
    global _model
    if _model is None:
        _model = KeyBERT()
    return _model

def extract_keywords(text: str, top_k: int = 5) -> list[str]:
    if not text or not text.strip():
        return []
    model = _get_model()
    keywords = model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",       
        top_n=top_k,
    )
    return [kw[0] for kw in keywords]

def process_transcripts(transcripts: list[str]) -> list[list[str]]:
    return [extract_keywords(text) for text in transcripts]
def process_all_transcripts(
    transcripts_dir: str = "data/processed/transcripts",  # ✅ dossier seulement
    output_dir: str = "data/processed/keywords",
    top_k: int = 10,
):
    transcripts_path = Path(transcripts_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for file_path in sorted(transcripts_path.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8")
        keywords = extract_keywords(text, top_k=top_k)
        output_file = output_path / f"{file_path.stem}.json"
        output_file.write_text(
            json.dumps({"keywords": keywords}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"✅ {file_path.name} → {output_file}")

if __name__ == "__main__":
    process_all_transcripts()