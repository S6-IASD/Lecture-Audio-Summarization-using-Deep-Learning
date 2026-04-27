"""
summary_evaluator.py
====================
Evaluation metrics for the Lecture Audio Summarization pipeline.

Based on the actual project code:
  - ASR          : openai-whisper  (segment_transcriber.py / evaluate_transcript.py)
  - NLP          : BART + SentenceTransformer  (summarizer.py)
  - Keywords     : KeyBERT  (keyword_extractor.py)
  - TTS          : Chatterbox via ngrok  (test_bytts.py)
  - Preprocessing: VAD + chunking  (piplinecolab.py / chunks.py / vad.py)

Place this file at:
    summarization-api/src/evaluation/summary_evaluator.py

HOW TO USE IN COLAB
-------------------
Upload this file via the Colab Files panel, then in a new cell:

    from summary_evaluator import (
        evaluate_asr,
        evaluate_summarization,
        evaluate_tts,
        evaluate_keywords,
        evaluate_preprocessing,
        print_report,
    )
"""

import re
import time
import io
from typing import Optional


# 
# HELPER  text normalizer (same logic as evaluate_transcript.py)
# 

def _normalize(text: str) -> str:
    """Lowercase + remove punctuation + collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# 
# 1.  ASR METRICS    Whisper  (evaluate_transcript.py / segment_transcriber.py)
# 

def evaluate_asr(hypothesis: str, reference: str) -> dict:
    """
    Measure Whisper transcription quality using WER and CER.
    Uses the same jiwer library and normalization as evaluate_transcript.py.

    Parameters
    ----------
    hypothesis : str   Text produced by Whisper (transcribe_all_chunks output).
    reference  : str   The correct ground-truth transcription.

    Returns
    -------
    dict:
        wer              - Word Error Rate   (0=perfect, lower is better)
        cer              - Character Error Rate (lower is better)
        word_count_hyp   - words in hypothesis
        word_count_ref   - words in reference
        interpretation   - human-readable quality label

    Example (Colab)
    ---------------
        asr_metrics = evaluate_asr(
            hypothesis = transcription,
            reference  = "The correct text."
        )
    """
    try:
        from jiwer import wer, cer
    except ImportError:
        raise ImportError("Run:  !pip install jiwer --break-system-packages -q")

    hyp_norm = _normalize(hypothesis)
    ref_norm = _normalize(reference)

    wer_score = wer(ref_norm, hyp_norm)
    cer_score = cer(ref_norm, hyp_norm)

    if wer_score < 0.05:
        label = "Excellent"
    elif wer_score < 0.10:
        label = "Good"
    elif wer_score < 0.20:
        label = "Acceptable"
    else:
        label = "Needs improvement"

    return {
        "wer":             round(wer_score, 4),
        "cer":             round(cer_score, 4),
        "word_count_hyp":  len(hypothesis.split()),
        "word_count_ref":  len(reference.split()),
        "interpretation":  label,
    }


# 
# 2.  SUMMARIZATION METRICS    BART  (summarizer.py)
# 

def evaluate_summarization(
    summary: str,
    reference_summary: str,
    original_text: str,
    use_bertscore: bool = True,
) -> dict:
    """
    Measure BART summary quality with ROUGE, BERTScore, faithfulness,
    and compression ratio.

    The faithfulness score reuses the same SentenceTransformer
    (all-MiniLM-L6-v2) and cosine similarity logic from summarizer.py
    check_faithfulness() with the same threshold of 0.55.

    Parameters
    ----------
    summary           : str   Summary from summarize_text() or summarize().
    reference_summary : str   Human-written reference summary (ground truth).
    original_text     : str   Full transcript (faithfulness + compression).
    use_bertscore     : bool  Set False on CPU to skip slow BERTScore.

    Returns
    -------
    dict:
        rouge1            - ROUGE-1 F1  (unigram overlap,  higher is better)
        rouge2            - ROUGE-2 F1  (bigram overlap,   higher is better)
        rougeL            - ROUGE-L F1  (LCS overlap,      higher is better)
        bertscore_f1      - BERTScore F1 (semantic sim,    higher is better)
        faithfulness      - cosine sim to source (same as summarizer.py)
        compression_ratio - summary words / original words
        summary_words     - word count of summary
        original_words    - word count of original transcript

    Example (Colab)
    ---------------
        nlp_metrics = evaluate_summarization(
            summary           = resume,
            reference_summary = "Human written summary here.",
            original_text     = transcription,
        )
    """
    try:
        from rouge_score import rouge_scorer
    except ImportError:
        raise ImportError("Run:  !pip install rouge-score --break-system-packages -q")

    #  ROUGE 
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"], use_stemmer=True
    )
    scores = scorer.score(reference_summary, summary)
    rouge1 = round(scores["rouge1"].fmeasure, 4)
    rouge2 = round(scores["rouge2"].fmeasure, 4)
    rougeL = round(scores["rougeL"].fmeasure, 4)

    #  BERTScore 
    bertscore_f1 = -1.0
    if use_bertscore:
        try:
            from bert_score import score as bert_score
            _, _, F1 = bert_score(
                [summary], [reference_summary], lang="en", verbose=False
            )
            bertscore_f1 = round(float(F1[0]), 4)
        except ImportError:
            print("  BERTScore not installed. Run: !pip install bert-score -q")

    #  Faithfulness  same as summarizer.py check_faithfulness() 
    faithfulness = -1.0
    try:
        from sentence_transformers import SentenceTransformer, util
        _sim_model = SentenceTransformer("all-MiniLM-L6-v2")
        emb_sum = _sim_model.encode(summary,              convert_to_tensor=True)
        emb_src = _sim_model.encode(original_text[:2000], convert_to_tensor=True)
        faithfulness = round(float(util.cos_sim(emb_sum, emb_src)), 4)
    except ImportError:
        print("  sentence-transformers not installed  faithfulness skipped")

    #  Compression ratio 
    original_words = len(original_text.split())
    summary_words  = len(summary.split())
    compression    = round(summary_words / original_words, 4) if original_words > 0 else 0.0

    return {
        "rouge1":            rouge1,
        "rouge2":            rouge2,
        "rougeL":            rougeL,
        "bertscore_f1":      bertscore_f1,
        "faithfulness":      faithfulness,
        "compression_ratio": compression,
        "summary_words":     summary_words,
        "original_words":    original_words,
    }


# 
# 3.  KEYWORD METRICS    KeyBERT  (keyword_extractor.py)
# 

def evaluate_keywords(
    keywords: list,
    reference_keywords: list,
    summary: str,
) -> dict:
    """
    Evaluate keyword extraction quality from keyword_extractor.py.

    Parameters
    ----------
    keywords           : list   Output of extract_keywords().
    reference_keywords : list   Expected ground-truth keywords.
    summary            : str    BART summary (checks keyword coverage).

    Returns
    -------
    dict:
        precision           - fraction of extracted keywords that are correct
        recall              - fraction of reference keywords that were found
        f1                  - harmonic mean of precision and recall
        coverage_in_summary - fraction of keywords present in the summary

    Example (Colab)
    ---------------
        kw_metrics = evaluate_keywords(
            keywords           = extracted_keywords,
            reference_keywords = ["deep learning", "neural network"],
            summary            = resume,
        )
    """
    extracted_set = set(k.lower().strip() for k in keywords)
    reference_set = set(k.lower().strip() for k in reference_keywords)

    if not extracted_set or not reference_set:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "coverage_in_summary": 0.0}

    true_positives = len(extracted_set & reference_set)
    precision      = true_positives / len(extracted_set)
    recall         = true_positives / len(reference_set)
    f1             = (2 * precision * recall / (precision + recall)
                      if (precision + recall) > 0 else 0.0)

    summary_lower = summary.lower()
    covered       = sum(1 for kw in extracted_set if kw in summary_lower)
    coverage      = covered / len(extracted_set) if extracted_set else 0.0

    return {
        "precision":           round(precision, 4),
        "recall":              round(recall, 4),
        "f1":                  round(f1, 4),
        "coverage_in_summary": round(coverage, 4),
    }


# 
# 4.  TTS METRICS    Chatterbox  (test_bytts.py)
# 

def evaluate_tts(
    audio_bytes: bytes,
    generation_time_seconds: float,
    sample_rate: int = 24000,
) -> dict:
    """
    Measure Chatterbox TTS speed using Real-Time Factor (RTF).

    Wrap generate_tts_bytes() with time.time() to measure generation time:

        t0 = time.time()
        audio_bytes = generate_tts_bytes(text=resume)
        t1 = time.time()
        tts_metrics = evaluate_tts(audio_bytes, t1 - t0)

    Parameters
    ----------
    audio_bytes             : bytes  WAV bytes from generate_tts_bytes().
    generation_time_seconds : float  Wall-clock seconds to generate audio.
    sample_rate             : int    Chatterbox sample rate (default 24000).

    Returns
    -------
    dict:
        audio_duration_s  - length of generated audio in seconds
        generation_time_s - time taken to generate
        rtf               - Real-Time Factor (generation_time / audio_duration)
                            RTF < 1.0 = faster than real-time  
        interpretation    - human-readable speed label
    """
    try:
        import torchaudio
    except ImportError:
        raise ImportError("torchaudio is required (already in requirements.txt)")

    buf             = io.BytesIO(audio_bytes)
    waveform, sr    = torchaudio.load(buf)
    num_samples     = waveform.shape[-1]
    audio_duration  = num_samples / sr
    rtf             = (generation_time_seconds / audio_duration
                       if audio_duration > 0 else float("inf"))

    if rtf < 0.5:
        label = "Very fast"
    elif rtf < 1.0:
        label = "Faster than real-time"
    elif rtf < 2.0:
        label = "Slower than real-time"
    else:
        label = "Very slow"

    return {
        "audio_duration_s":  round(audio_duration, 3),
        "generation_time_s": round(generation_time_seconds, 3),
        "rtf":               round(rtf, 4),
        "interpretation":    label,
    }


# 
# 5.  PREPROCESSING METRICS    (piplinecolab.py / chunks.py / vad.py)
# 

def evaluate_preprocessing(chunks: list) -> dict:
    """
    Measure preprocessing pipeline output quality.
    Takes the output of run_pipeline() from piplinecolab.py.

    Parameters
    ----------
    chunks : list   Output of run_pipeline()  list of dicts:
                    [{'key': 'chunk_0', 'filename': '...', 'bytes': b'...', 'mimetype': '...'}, ...]

    Returns
    -------
    dict:
        num_chunks        - number of audio chunks produced
        total_duration_s  - total audio duration across all chunks
        avg_chunk_s       - average chunk duration
        min_chunk_s       - shortest chunk duration
        max_chunk_s       - longest chunk duration

    Example (Colab)
    ---------------
        chunks = run_pipeline(audio_bytes, filename="lecture.mp3")
        pre_metrics = evaluate_preprocessing(chunks)
    """
    try:
        import torchaudio
    except ImportError:
        raise ImportError("torchaudio is required")

    durations = []
    for chunk in chunks:
        buf = io.BytesIO(chunk["bytes"])
        waveform, sr = torchaudio.load(buf)
        durations.append(waveform.shape[-1] / sr)

    if not durations:
        return {
            "num_chunks": 0,
            "total_duration_s": 0.0,
            "avg_chunk_s": 0.0,
            "min_chunk_s": 0.0,
            "max_chunk_s": 0.0,
        }

    return {
        "num_chunks":       len(durations),
        "total_duration_s": round(sum(durations), 2),
        "avg_chunk_s":      round(sum(durations) / len(durations), 2),
        "min_chunk_s":      round(min(durations), 2),
        "max_chunk_s":      round(max(durations), 2),
    }


# 
# 6.  PRETTY REPORT
# 

def print_report(
    asr_metrics:  Optional[dict] = None,
    nlp_metrics:  Optional[dict] = None,
    tts_metrics:  Optional[dict] = None,
    kw_metrics:   Optional[dict] = None,
    pre_metrics:  Optional[dict] = None,
):
    """
    Print a clean formatted evaluation report for all pipeline stages.
    Pass only the metric dicts you have  any can be None and will be skipped.

    Example (Colab)
    ---------------
        print_report(
            asr_metrics = asr_metrics,
            nlp_metrics = nlp_metrics,
            tts_metrics = tts_metrics,
            kw_metrics  = kw_metrics,
            pre_metrics = pre_metrics,
        )
    """
    line = "" * 55
    print(f"\n{line}")
    print("  PIPELINE EVALUATION REPORT")
    print(line)

    #  Preprocessing 
    if pre_metrics:
        print("\n   PREPROCESSING  (VAD + Chunking)")
        print(f"   Chunks produced          : {pre_metrics['num_chunks']}")
        print(f"   Total audio duration     : {pre_metrics['total_duration_s']}s")
        print(f"   Avg chunk duration       : {pre_metrics['avg_chunk_s']}s")
        print(f"   Min / Max chunk          : {pre_metrics['min_chunk_s']}s / {pre_metrics['max_chunk_s']}s")
    else:
        print("\n   PREPROCESSING   skipped")

    #  ASR 
    if asr_metrics:
        print("\n   WHISPER  (ASR)")
        print(f"   WER  (Word Error Rate)   : {asr_metrics['wer']:.2%}  {'' if asr_metrics['wer'] < 0.10 else ' '}")
        print(f"   CER  (Char Error Rate)   : {asr_metrics['cer']:.2%}  {'' if asr_metrics['cer'] < 0.05 else ' '}")
        print(f"   Words  hyp / ref         : {asr_metrics['word_count_hyp']} / {asr_metrics['word_count_ref']}")
        print(f"   Quality                  : {asr_metrics['interpretation']}")
        print("    WER < 10%  and  CER < 5%  =  good")
    else:
        print("\n   WHISPER   no reference transcription provided, skipped")

    #  NLP 
    if nlp_metrics:
        print("\n  BART  (Summarization)")
        print(f"   ROUGE-1                  : {nlp_metrics['rouge1']:.4f}  {'' if nlp_metrics['rouge1'] > 0.35 else ' '}")
        print(f"   ROUGE-2                  : {nlp_metrics['rouge2']:.4f}  {'' if nlp_metrics['rouge2'] > 0.15 else ' '}")
        print(f"   ROUGE-L                  : {nlp_metrics['rougeL']:.4f}  {'' if nlp_metrics['rougeL'] > 0.30 else ' '}")
        if nlp_metrics["bertscore_f1"] >= 0:
            print(f"   BERTScore F1             : {nlp_metrics['bertscore_f1']:.4f}  {'' if nlp_metrics['bertscore_f1'] > 0.85 else ' '}")
        else:
            print("   BERTScore F1             : skipped")
        if nlp_metrics["faithfulness"] >= 0:
            print(f"   Faithfulness             : {nlp_metrics['faithfulness']:.4f}  {'' if nlp_metrics['faithfulness'] > 0.55 else ' '}")
        print(f"   Compression ratio        : {nlp_metrics['compression_ratio']:.2%}  ({nlp_metrics['summary_words']} / {nlp_metrics['original_words']} words)")
        print("    ROUGE-1>0.35  ROUGE-2>0.15  BERTScore>0.85  Faithfulness>0.55")
    else:
        print("\n  BART   no reference summary provided, skipped")

    #  Keywords 
    if kw_metrics:
        print("\n  KEYBERT  (Keyword Extraction)")
        print(f"   Precision                : {kw_metrics['precision']:.2%}  {'' if kw_metrics['precision'] > 0.5 else ' '}")
        print(f"   Recall                   : {kw_metrics['recall']:.2%}  {'' if kw_metrics['recall'] > 0.5 else ' '}")
        print(f"   F1                       : {kw_metrics['f1']:.2%}  {'' if kw_metrics['f1'] > 0.5 else ' '}")
        print(f"   Coverage in summary      : {kw_metrics['coverage_in_summary']:.2%}")
        print("    Precision, Recall, F1 > 50%  =  good")
    else:
        print("\n  KEYBERT   no reference keywords provided, skipped")

    #  TTS 
    if tts_metrics:
        print("\n   CHATTERBOX TTS")
        print(f"   Audio duration           : {tts_metrics['audio_duration_s']}s")
        print(f"   Generation time          : {tts_metrics['generation_time_s']}s")
        print(f"   RTF (Real-Time Factor)   : {tts_metrics['rtf']:.4f}  {'' if tts_metrics['rtf'] < 1.0 else ' '}")
        print(f"   Speed                    : {tts_metrics['interpretation']}")
        print("    RTF < 1.0  =  faster than real-time  =  good")
    else:
        print("\n   CHATTERBOX TTS   skipped")

    print(f"\n{line}\n")


# 
# SELF-TEST    python summary_evaluator.py
# 

if __name__ == "__main__":
    print("Running self-test with dummy data...\n")

    asr = evaluate_asr(
        hypothesis = "the cat sat on the mat",
        reference  = "the cat sat on the mat",
    )

    nlp = evaluate_summarization(
        summary           = "The cat sat on the mat.",
        reference_summary = "A cat was sitting on a mat.",
        original_text     = "The cat sat on the mat. It was a sunny day. The mat was red.",
        use_bertscore     = False,
    )

    kw = evaluate_keywords(
        keywords           = ["cat", "mat", "sunny day"],
        reference_keywords = ["cat", "mat", "red"],
        summary            = "The cat sat on the mat.",
    )

    import wave
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(b"\x00\x00" * 24000)
    tts = evaluate_tts(
        audio_bytes             = buf.getvalue(),
        generation_time_seconds = 0.35,
    )

    print_report(asr_metrics=asr, nlp_metrics=nlp, tts_metrics=tts, kw_metrics=kw)
