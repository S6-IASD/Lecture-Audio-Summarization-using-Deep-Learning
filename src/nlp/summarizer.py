from transformers import pipeline
import os


summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

SUMMARY_CONFIGS = {
    "court":  {"max_length": 100,  "min_length": 20},
    "medium": {"max_length": 130, "min_length": 60},
    "grand":  {"max_length": 250, "min_length": 130},
    "max_for_A_B":{"max_length": 400, "min_length": 270}
}

# 1. Découpage avec offset
def chunk_text(texte, max_words=400, offset=0):
    mots = texte.split()
    mots = mots[offset:]  # décaler le point de départ
    return [" ".join(mots[i:i+max_words]) for i in range(0, len(mots), max_words)]

# 2. Résumer une liste de chunks
def summarize_chunks(chunks, config):
    resumes = []
    for i, chunk in enumerate(chunks):
        # chunk trop court → ignorer
        if len(chunk.split()) < config["min_length"]:
            continue
        r = summarizer(
            chunk,
            max_length=config["max_length"],
            min_length=config["min_length"],
            do_sample=False
        )
        resumes.append(r[0]["summary_text"])
        print(f"  chunk {i+1}/{len(chunks)} ✅")
    return " ".join(resumes)

# 3. Pipeline complet avec double découpage + fusion
def summarize_double(texte, niveau="medium", chunk_size=400  , max_input_tokens=900):
    config = SUMMARY_CONFIGS[niveau]
    offset = chunk_size // 2  # décalage de la moitié

    print("[ Passe A — découpage normal ]")
    chunks_A = chunk_text(texte, max_words=chunk_size, offset=0)
    resume_A = summarize_chunks(chunks_A, SUMMARY_CONFIGS["max_for_A_B"])

    print("\n[ Passe B — découpage décalé ]")
    chunks_B = chunk_text(texte, max_words=chunk_size, offset=offset)
    resume_B = summarize_chunks(chunks_B, SUMMARY_CONFIGS["max_for_A_B"])

    print("\n[ Fusion A + B ]")
    fusion = resume_A + " " + resume_B

    print("\n",fusion,'\n')

    print(config["max_length"])

    print("\n[ Résumé final depuis la fusion ]")
    words = fusion.split()
    
    # Si le texte est court enough → résumé direct
    if len(words) <= max_input_tokens:
        resume_final = summarizer(
            fusion,
            max_length=config["max_length"],
            min_length=config["min_length"],
            do_sample=False
        )[0]["summary_text"]
    else :
        chunks = chunk_text(fusion, max_words=chunk_size, offset=offset)
        resume_final = summarize_chunks(
            chunks,
            config
        )

    print(f"\n===== RÉSUMÉ FINAL ({niveau.upper()}) =====")
    print(resume_final)
    print(f"\nLongueur : {len(resume_final.split())} mots")

    return {
        "resume_A": resume_A,
        "resume_B": resume_B,
        "fusion": fusion,
        "resume_final": resume_final
    }


def resumer_texte(file_name , input_dir='..\\\\..\\\\data\\\\processed\\\\transcripts'):

    # 2. Charger le texte
    with open(os.path.join(input_dir, file_name), "r", encoding="utf-8") as f:
        texte = f.read()
    resultats = summarize_double(texte, niveau="medium", chunk_size=400)


    
  
resumer_texte('audio_cleaned.txt')








