# ╔══════════════════════════════════════════════════════════════════════╗
# ║     EVALUATION CELLS — paste into pipeline_api_colab_(1) (2).ipynb ║
# ║     Add these AFTER the existing 4 pipeline cells                  ║
# ╚══════════════════════════════════════════════════════════════════════╝


# ─────────────────────────────────────────────────────────────────────────────
# CELL A — Install evaluation libraries
# Add right after the existing !pip install cell (Cell 1)
# ─────────────────────────────────────────────────────────────────────────────

!pip install jiwer rouge-score bert-score --break-system-packages -q
print("✅ Evaluation libraries installed")


# ─────────────────────────────────────────────────────────────────────────────
# CELL B — Upload + import evaluator
# 1. In Colab left sidebar → Files → Upload → select summary_evaluator.py
# 2. Then run this cell
# ─────────────────────────────────────────────────────────────────────────────

from summary_evaluator import (
    evaluate_asr,
    evaluate_summarization,
    evaluate_tts,
    evaluate_keywords,
    evaluate_preprocessing,
    print_report,
)
import time
print("✅ Evaluator imported")


# ─────────────────────────────────────────────────────────────────────────────
# CELL C — Set your reference texts (ground truth)
# Fill these in with the correct expected outputs for your audio file
# ─────────────────────────────────────────────────────────────────────────────

# The correct transcription of your audio file (what Whisper SHOULD produce)
# If you don't have one → set to None to skip ASR metrics
REFERENCE_TRANSCRIPTION = """
Paste the correct word-for-word transcription of your audio here.
"""

# A human-written summary of your audio (what BART SHOULD produce)
# If you don't have one → set to None to skip ROUGE/BERTScore
REFERENCE_SUMMARY = """
Paste a good human-written summary of your audio here.
"""

# Keywords you expect to be extracted from your audio
# If you don't have any → set to empty list [] to skip keyword metrics
REFERENCE_KEYWORDS = ["keyword1", "keyword2", "keyword3"]

print("✅ Reference texts set")


# ─────────────────────────────────────────────────────────────────────────────
# CELL D — Run full pipeline WITH evaluation
# This replaces your manual calls to transcribe + summarize + tts
# ─────────────────────────────────────────────────────────────────────────────

# ── You need audio chunks ready — either from run_pipeline() or manually ──
# Example: load your audio file bytes
# with open("your_audio.mp3", "rb") as f:
#     audio_bytes = f.read()
# chunks = run_pipeline(audio_bytes, filename="your_audio.mp3")
# pre_metrics = evaluate_preprocessing(chunks)

# ── For testing, assume transcription and resume already exist ────────────
# transcription = transcribe_all_chunks(request.files)  ← from the API
# resume        = summarize_text(transcription)          ← from the API

# ── 1. Preprocessing metrics (if you have chunks) ────────────────────────
# pre_metrics = evaluate_preprocessing(chunks)   # uncomment if you have chunks
pre_metrics = None   # comment this out if you uncomment the line above

# ── 2. ASR metrics ───────────────────────────────────────────────────────
if REFERENCE_TRANSCRIPTION and REFERENCE_TRANSCRIPTION.strip():
    asr_metrics = evaluate_asr(
        hypothesis = transcription,
        reference  = REFERENCE_TRANSCRIPTION,
    )
else:
    asr_metrics = None

# ── 3. Summarization metrics ─────────────────────────────────────────────
if REFERENCE_SUMMARY and REFERENCE_SUMMARY.strip():
    nlp_metrics = evaluate_summarization(
        summary           = resume,
        reference_summary = REFERENCE_SUMMARY,
        original_text     = transcription,
        use_bertscore     = True,   # set False on CPU to save time
    )
else:
    nlp_metrics = None

# ── 4. Keyword metrics ────────────────────────────────────────────────────
# First extract keywords from the transcription
from nlp.keyword_extractor import extract_keywords
extracted_keywords = extract_keywords(transcription, top_k=10)
print(f"🔑 Extracted keywords: {extracted_keywords}")

if REFERENCE_KEYWORDS:
    kw_metrics = evaluate_keywords(
        keywords           = extracted_keywords,
        reference_keywords = REFERENCE_KEYWORDS,
        summary            = resume,
    )
else:
    kw_metrics = None

# ── 5. TTS metrics ────────────────────────────────────────────────────────
t0 = time.time()
audio_bytes = generate_tts_bytes(text=resume)
t1 = time.time()

tts_metrics = evaluate_tts(
    audio_bytes             = audio_bytes,
    generation_time_seconds = t1 - t0,
    sample_rate             = tts_model.sr,
)

# ── 6. Print the full report ──────────────────────────────────────────────
print_report(
    pre_metrics = pre_metrics,
    asr_metrics = asr_metrics,
    nlp_metrics = nlp_metrics,
    kw_metrics  = kw_metrics,
    tts_metrics = tts_metrics,
)


# ─────────────────────────────────────────────────────────────────────────────
# CELL E — Optional: add metrics to the API /resumeaudio response
# Replace the return jsonify({...}) inside route_resume_audio() with this
# ─────────────────────────────────────────────────────────────────────────────

"""
# Inside route_resume_audio(), after generating audio_bytes:

ref_transcription = request.form.get("ref_transcription", "").strip()
ref_summary       = request.form.get("ref_summary",       "").strip()
ref_keywords      = request.form.get("ref_keywords",      "").strip().split(",")

asr_metrics = evaluate_asr(transcription, ref_transcription) if ref_transcription else None
nlp_metrics = evaluate_summarization(resume, ref_summary, transcription) if ref_summary else None
kw_metrics  = evaluate_keywords(extracted_keywords, ref_keywords, resume) if ref_keywords else None
tts_metrics = evaluate_tts(audio_bytes, tts_time)

return jsonify({
    'transcription' : transcription,
    'resume'        : resume,
    'audio_base64'  : base64.b64encode(audio_bytes).decode('utf-8'),
    'audio_format'  : 'wav',
    'target_words'  : target_words,
    'word_count'    : len(resume.split()),
    'metrics': {
        'asr': asr_metrics,
        'nlp': nlp_metrics,
        'kw' : kw_metrics,
        'tts': tts_metrics,
    }
})
"""
