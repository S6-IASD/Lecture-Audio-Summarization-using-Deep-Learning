



import os
import re
import torch
import numpy as np
from dataclasses import dataclass
from transformers import pipeline as hf_pipeline
from sentence_transformers import SentenceTransformer, util


# ─────────────────────────────────────────────
# 1. CONFIGURATION
# ─────────────────────────────────────────────

@dataclass
class SummaryConfig:
    target_words: int        = 150
    tolerance: float         = 0.20

    # Semantic chunker
    semantic_threshold: float = 0.55
    min_chunk_words: int      = 60
    max_chunk_words: int      = 450

    # BART generation
    num_beams: int            = 4
    no_repeat_ngram_size: int = 3

    # Faithfulness
    faithfulness_threshold: float = 0.55

    # Models
    bart_model: str       = "facebook/bart-large-cnn"
    similarity_model: str = "all-MiniLM-L6-v2"

    @property
    def final_max_tokens(self) -> int:
        raw = int(self.target_words * 1.4 * (1 + self.tolerance))
        return max(30, min(raw, 1024))

    @property
    def final_min_tokens(self) -> int:
        raw = int(self.target_words * 1.4 * (1 - self.tolerance))
        return max(10, min(raw, self.final_max_tokens - 10))


# ─────────────────────────────────────────────
# 2. MODELS
# ─────────────────────────────────────────────

class ModelBundle:
    def __init__(self, config: SummaryConfig, verbose: bool = True):
        device_id  = 0 if torch.cuda.is_available() else -1
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if verbose:
            print(f"  Device : {'GPU' if torch.cuda.is_available() else 'CPU'}")

        if verbose: print(f"  Loading BART ({config.bart_model})...")
        self.bart_pipe = hf_pipeline(
            "summarization",
            model=config.bart_model,
            device=device_id,
        )

        if verbose: print(f"  Loading similarity model ({config.similarity_model})...")
        self.similarity_model = SentenceTransformer(config.similarity_model)

        if verbose: print("  Models ready.\n")


# ─────────────────────────────────────────────
# 3. TEXT CLEANING
# ─────────────────────────────────────────────

def clean_text(text: str) -> str:
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
    text = re.sub(r'[\ufffd\ufffe\uffff]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def deduplicate_sentences(text: str, min_length: int = 20) -> str:
    seen, result = set(), []
    for s in text.split(". "):
        s = s.strip()
        if s and s not in seen and len(s) > min_length:
            seen.add(s)
            result.append(s)
    return ". ".join(result)


# ─────────────────────────────────────────────
# 4. SEMANTIC CHUNKER
# ─────────────────────────────────────────────

def semantic_chunk(
    text: str,
    model: SentenceTransformer,
    threshold: float = 0.55,
    min_words: int   = 60,
    max_words: int   = 450,
) -> list[str]:

    # Split into sentences
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
    if len(sentences) <= 1:
        return [text]

    # Encode all at once
    embeddings = model.encode(sentences, batch_size=32, show_progress_bar=False)

    chunks        = []
    current       = [sentences[0]]
    current_words = len(sentences[0].split())

    for i in range(1, len(sentences)):
        w    = len(sentences[i].split())
        sim  = float(
            np.dot(embeddings[i], embeddings[i - 1]) /
            (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i - 1]) + 1e-8)
        )

        topic_shift   = sim < threshold
        too_big       = (current_words + w) > max_words

        if topic_shift or too_big:
            chunk_text = '. '.join(current) + '.'
            if current_words < min_words and chunks:
                chunks[-1] += ' ' + chunk_text   # merge tiny chunk into previous
            else:
                chunks.append(chunk_text)
            current, current_words = [sentences[i]], w
        else:
            current.append(sentences[i])
            current_words += w

    # Last chunk
    if current:
        last = '. '.join(current) + '.'
        if current_words < min_words and chunks:
            chunks[-1] += ' ' + last
        else:
            chunks.append(last)

    return chunks


# ─────────────────────────────────────────────
# 5. SUMMARIZE ONE CHUNK WITH BART
# ─────────────────────────────────────────────

def summarize_chunk(
    chunk: str,
    models: ModelBundle,
    config: SummaryConfig,
) -> str:

    word_count = len(chunk.split())
    max_len    = max(40, min(word_count // 2, 150))
    min_len    = max(20, max_len // 3)

    result = models.bart_pipe(
        chunk,
        max_length=max_len,
        min_length=min_len,
        num_beams=config.num_beams,
        no_repeat_ngram_size=config.no_repeat_ngram_size,
        do_sample=False,
        truncation=True,
    )
    return result[0]["summary_text"].strip()


# ─────────────────────────────────────────────
# 6. FAITHFULNESS CHECK
# ─────────────────────────────────────────────

def check_faithfulness(
    summary: str,
    source: str,
    models: ModelBundle,
    config: SummaryConfig,
    verbose: bool = True,
) -> float:
    emb_sum = models.similarity_model.encode(summary, convert_to_tensor=True)
    emb_src = models.similarity_model.encode(source[:2000], convert_to_tensor=True)
    score   = float(util.cos_sim(emb_sum, emb_src))

    if verbose:
        if score < config.faithfulness_threshold:
            print(f"  ⚠️  Faithfulness low : {score:.2f}")
        else:
            print(f"  ✓  Faithfulness     : {score:.2f}")
    return score


# ─────────────────────────────────────────────
# 7. MAIN PIPELINE
# ─────────────────────────────────────────────

def summarize(
    text: str,
    config: SummaryConfig,
    models: ModelBundle,
    verbose: bool = True,
) -> dict:
    # 1. Clean
    text = clean_text(text)

    # 2. Semantic chunking
    chunks = semantic_chunk(
        text,
        model=models.similarity_model,
        threshold=config.semantic_threshold,
        min_words=config.min_chunk_words,
        max_words=config.max_chunk_words,
    )

    if verbose:
        print(f"  Chunks : {len(chunks)}")
        for i, c in enumerate(chunks, 1):
            print(f"    Chunk {i}: {len(c.split())} words")
        print()

    # 3. Summarize each chunk with BART
    chunk_summaries = []
    for i, chunk in enumerate(chunks, 1):
        if verbose:
            print(f"  BART chunk {i}/{len(chunks)}...", end=" ", flush=True)
        try:
            s = summarize_chunk(chunk, models, config)
            s = deduplicate_sentences(s)
            chunk_summaries.append(s)
            if verbose:
                print(f"✓ ({len(s.split())} words)")
        except Exception as e:
            if verbose: print(f"✗ skipped ({e})")

    if not chunk_summaries:
        raise RuntimeError("All chunks failed.")

    # 4. Merge chunk summaries
    merged = deduplicate_sentences(" ".join(chunk_summaries))

    if verbose:
        print(f"\n  Merged : {len(merged.split())} words")
        print(f"  Target : ~{config.target_words} words (±{int(config.tolerance*100)}%)\n")

    # 5. Final compression pass with BART
    final = models.bart_pipe(
        merged,
        max_new_tokens=config.final_max_tokens,
        min_length=config.final_min_tokens,
        max_length=1024,
        num_beams=config.num_beams,
        no_repeat_ngram_size=config.no_repeat_ngram_size,
        do_sample=False,
        truncation=True,
    )[0]["summary_text"]

    final = deduplicate_sentences(final)

    # 6. Faithfulness
    score = check_faithfulness(final, text, models, config, verbose=verbose)

    return {
        "summary"     : final,
        "word_count"  : len(final.split()),
        "faithfulness": score,
    }


# ─────────────────────────────────────────────
# 8. ENTRY POINT
# ─────────────────────────────────────────────

def summarize_file(
    file_name: str,
    target_words: int = 150,
    input_dir: str    = "../../data/processed/transcripts",
    verbose: bool     = True,
) -> str:
    path = os.path.join(input_dir, file_name)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    config = SummaryConfig(target_words=target_words)
    models = ModelBundle(config, verbose=verbose)

    if verbose:
        print(f"\n{'='*50}")
        print(f"  BART + Semantic Chunker Pipeline")
        print(f"  File   : {file_name}")
        print(f"  Target : ~{target_words} words")
        print(f"{'='*50}\n")

    result = summarize(text, config, models, verbose=verbose)

    if verbose:
        print(f"\n{'='*50}")
        print("FINAL SUMMARY")
        print(f"{'='*50}")
        print(result["summary"])
        print(f"\n  Length      : {result['word_count']} words")
        print(f"  Faithfulness: {result['faithfulness']:.2f}")
        print(f"{'='*50}\n")

    return result["summary"]


if __name__ == "__main__":
    summarize_file("audio_cleaned.txt", target_words=150)