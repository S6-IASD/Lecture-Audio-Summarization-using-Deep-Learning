# Lecture Audio Summarization using Deep Learning

This is a project we built for our S6 IASD coursework. The idea is simple: you give it an audio recording (a lecture, a conference talk, whatever), and it gives you back a transcript, a short text summary, and even an audio version of that summary spoken in a cloned voice.

It's split into three parts that talk to each other: a React frontend, a Django backend for auth and storage, and a FastAPI service that handles the actual audio processing. Because the ML models (Whisper, BART, the TTS model) are heavy, the FastAPI service doesn't run everything locally — it does the light preprocessing on your machine and then sends the audio chunks to a Google Colab notebook (for the free GPU) through an ngrok tunnel.

## How it fits together
<img width="1050" height="582" alt="image" src="https://github.com/user-attachments/assets/f9bb532c-6773-4049-bcfd-93b0d010933e" />


<img width="1040" height="587" alt="image" src="https://github.com/user-attachments/assets/9976492c-fa41-4ea8-87af-df3e35dac075" />

Basically: the user drops a file in the browser, the React app sends it to Django (which checks you're logged in and will store the result), Django forwards it to the local FastAPI service which does the preprocessing (cleaning, VAD, chunking into ~30s pieces), and that service ships the chunks over an ngrok tunnel to the Colab notebook where the actual heavy models run. The JSON result (transcript + summary + audio) travels all the way back the same path.

So there are 4 moving pieces total if you count Colab, but only 3 you actually run on your own computer.

## Repo layout

```
backend/                 Django project
  accounts/               register / login / profile (JWT)
  summaries/               create / list / detail / download summaries
  config/                  settings, urls, FASTAPI_URL etc.

front-end/                React + Vite + Tailwind app
  src/api/axios.js          axios instance, handles token refresh
  src/pages/                Home, Login, Register, Dashboard, Create, SummaryDetail, Profile
  src/components/           upload zone, sidebar, summary card, protected route

summarization-api/
  api/
    main.py                 fully local pipeline (Whisper + BART + TTS on your machine)
    maincolab.py             the one actually used — local preprocessing + calls to Colab
  src/
    preprocessing/           audio cleaning, VAD, chunking
    asr/                     Whisper transcription
    nlp/                     BART summarizer + keyword extraction (KeyBERT)
    tts/                     calls the voice cloning TTS service
    evaluation/              WER/CER, faithfulness score, etc.
  notebooks/                 the Colab notebooks (pipeline + TTS generation)
  outputs/                   example transcripts/summaries

requirements.txt          all the python deps (ML + Django, kind of merged together)
start_project.bat         windows script that launches the 3 services at once
```

## What the pipeline actually does

1. **Clean the audio** — normalize volume, reduce background noise (`audio_cleaner.py`).
2. **VAD** — cut out the long silences using `webrtcvad`, but keep short pauses so it doesn't sound choppy (`vad.py`).
3. **Chunking** — split into ~30s pieces with 1s overlap, because the models can't handle arbitrarily long audio (`chunks.py`).
4. **Transcription** — each chunk goes through Whisper (`base` model), then everything gets stitched back together.
5. **Summarization** — this part does semantic chunking first (splitting the transcript by topic using sentence embeddings + cosine similarity), summarizes each semantic chunk with BART (`facebook/bart-large-cnn`), merges everything, dedupes repeated sentences, then does one more compression pass to hit the target word count you asked for.
6. **Faithfulness score** — basically checks how semantically close the final summary is to the original text, so you get a rough sense of whether it's making stuff up.
7. **TTS** — takes the summary text and a reference voice sample and generates an audio version, using a voice-cloning TTS model reached through ngrok.
8. (optional) keyword extraction with KeyBERT.

## Before you run it

- Python 3.10+
- Node.js + npm for the frontend
- ffmpeg (there's a Windows `ffmpeg.exe` already bundled under `src/asr` and `src/tts`, but on Linux/Mac install it yourself, e.g. `apt install ffmpeg`)
- A Google account for Colab, with GPU turned on — this is what runs Whisper/BART/TTS
- If you'd rather not use Colab, `api/main.py` runs everything locally, but you'll need a decent GPU for that to be usable

Heads up: the root `requirements.txt` pins some pretty recent versions (torch 2.10, transformers 4.44...). Depending on when you're installing this and your Python version, some of these might not resolve. If pip complains, just relax the version pins.

## Setting it up

**1. Clone it**

```bash
git clone https://github.com/S6-IASD/Lecture-Audio-Summarization-using-Deep-Learning.git
cd Lecture-Audio-Summarization-using-Deep-Learning
```

**2. Set up the Colab notebook**

Open [Google Colab](https://colab.research.google.com), import `summarization-api/notebooks/pipeline_api_colab_(1) (2).ipynb`.

Turn on the GPU: Runtime → Change runtime type → GPU.

Run all cells (Runtime → Run all) and wait — it prints an ngrok URL once it's ready. Copy that URL and paste it into `summarization-api/api/maincolab.py`, replacing the `COLAB_API_URL` default value:

```python
COLAB_API_URL = os.environ.get("COLAB_API_URL", "https://your-ngrok-url.ngrok-free.app")
```

(you can also just set it as an env var instead of editing the file — probably cleaner)

Note: this URL changes every time you restart the Colab notebook, so you'll need to update it again next session.

**3. Install python deps**

```bash
python -m venv venv
venv\Scripts\activate        # windows
source venv/bin/activate     # linux/mac

pip install -r requirements.txt
```

If you only care about running the Django backend and not touching the ML side, `backend/requirements.txt` alone is enough.

**4. Install frontend deps**

```bash
cd front-end
npm install
cd ..
```

**5. Django migrations**

```bash
cd backend
python manage.py migrate
cd ..
```

**6. Run everything**

Windows, easy way: just double-click `start_project.bat` at the root, it'll ask for your virtualenv path and then open 3 terminal windows for you.

Otherwise, three terminals manually:

```bash
# terminal 1
cd summarization-api/api
python maincolab.py

# terminal 2
cd backend
python manage.py runserver

# terminal 3
cd front-end
npm run dev
```

Then go to http://localhost:5173.

## API endpoints

### Django backend — localhost:8000

- `POST /api/auth/register/` — create account
- `POST /api/auth/login/` — login, returns JWT tokens
- `POST /api/auth/refresh/` — refresh access token
- `GET /api/auth/profile/` — current user profile
- `POST /api/summaries/create/` — upload audio (+ optional reference voice), runs the whole pipeline
- `GET /api/summaries/` — list your summaries
- `GET /api/summaries/<id>/` — get one summary
- `DELETE /api/summaries/<id>/` — delete it
- `GET /api/summaries/<id>/download/<file_type>/` — download transcript / summary / audio
- `GET /api/summaries/health/` — check if the FastAPI service is reachable

### FastAPI service — localhost:8080 (maincolab.py)

- `POST /transcript` — transcription only
- `POST /resume` — transcript + text summary (`target_words` param)
- `POST /resumeaudio` — transcript + summary + audio summary (`target_words`, `exaggeration`, `cfg_weight`)
- `GET /download/{filename}` — download generated files
- `GET /health` — checks both this service and whether Colab is reachable

## Evaluation

There's an evaluation module at `summarization-api/src/evaluation/summary_evaluator.py` with functions for scoring each stage:

- ASR — WER/CER using jiwer
- Summarization — faithfulness score + ROUGE-style metrics
- Keywords — relevance of extracted keywords
- TTS — some basic audio quality metrics

Also included: `src/evaluation/evaluation.ipynb` and `COLAB_EVALUATION_CELLS.py` if you want to run the evaluation directly in Colab.

Here's what we got when we actually ran it on our test set:

<img width="1042" height="587" alt="image" src="https://github.com/user-attachments/assets/62965a02-1ed4-4123-8869-4b49e13469b9" />


The ASR and summarization numbers are solid (WER 3.84%, CER 2.66%, well under threshold). The TTS real-time factor is just barely over 1.0, meaning generating the audio summary takes slightly longer than the audio itself lasts — not great if you need near real-time output, but fine for an async "upload and come back later" use case like this one.

## Config you might need to touch

- `backend/config/settings.py` → `FASTAPI_URL`, points to the local FastAPI service (default `http://127.0.0.1:8080`)
- `summarization-api/api/maincolab.py` → `COLAB_API_URL`, the ngrok URL, changes every Colab session
- `summarization-api/src/tts/test_bytts.py` → `NGROK_URL`, the TTS endpoint (matches the `generation_audio_colab_api.ipynb` notebook)
- `target_words` controls how long the summary should be (±20% tolerance), `exaggeration`/`cfg_weight` tweak the cloned voice style

## Known issues / things to fix eventually

- Everything depends on a live Colab session — annoying, but that's the tradeoff for free GPU. The ngrok URL has to be updated by hand each time.
- `db.sqlite3` and the Django `SECRET_KEY` are currently committed to the repo. Fine for a school project, not fine for anything real — regenerate the key and stop tracking the db before deploying anywhere.
- `start_project.bat` only works on Windows. On Linux/Mac just start the 3 services manually like shown above.
- Some pinned versions in the root `requirements.txt` are quite recent and might need adjusting depending on your OS/Python version.
