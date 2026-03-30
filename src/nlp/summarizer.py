# # from transformers import pipeline
# # import os


# # summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# # SUMMARY_CONFIGS = {
# #     "court":  {"max_length": 100,  "min_length": 20},
# #     "medium": {"max_length": 130, "min_length": 60},
# #     "grand":  {"max_length": 250, "min_length": 130},
# #     "max_for_A_B":{"max_length": 400, "min_length": 270}
# # }

# # # 1. Découpage avec offset
# # def chunk_text(texte, max_words=400, offset=0):
# #     mots = texte.split()
# #     mots = mots[offset:]  # décaler le point de départ
# #     return [" ".join(mots[i:i+max_words]) for i in range(0, len(mots), max_words)]

# # # 2. Résumer une liste de chunks
# # def summarize_chunks(chunks, config):
# #     resumes = []
# #     for i, chunk in enumerate(chunks):
# #         # chunk trop court → ignorer
# #         if len(chunk.split()) < config["min_length"]:
# #             continue
# #         r = summarizer(
# #             chunk,
# #             max_length=config["max_length"],
# #             min_length=config["min_length"],
# #             do_sample=False
# #         )
# #         resumes.append(r[0]["summary_text"])
# #         print(f"  chunk {i+1}/{len(chunks)} ✅")
# #     return " ".join(resumes)

# # # 3. Pipeline complet avec double découpage + fusion
# # def summarize_double(texte, niveau="medium", chunk_size=400  , max_input_tokens=900):
# #     config = SUMMARY_CONFIGS[niveau]
# #     offset = chunk_size // 2  # décalage de la moitié

# #     print("[ Passe A — découpage normal ]")
# #     chunks_A = chunk_text(texte, max_words=chunk_size, offset=0)
# #     resume_A = summarize_chunks(chunks_A, SUMMARY_CONFIGS["max_for_A_B"])

# #     print("\n[ Passe B — découpage décalé ]")
# #     chunks_B = chunk_text(texte, max_words=chunk_size, offset=offset)
# #     resume_B = summarize_chunks(chunks_B, SUMMARY_CONFIGS["max_for_A_B"])

# #     print("\n[ Fusion A + B ]")
# #     fusion = resume_A + " " + resume_B

# #     print("\n",fusion,'\n')

# #     print(config["max_length"])

# #     print("\n[ Résumé final depuis la fusion ]")
# #     words = fusion.split()
    
# #     # Si le texte est court enough → résumé direct
# #     if len(words) <= max_input_tokens:
# #         resume_final = summarizer(
# #             fusion,
# #             max_length=config["max_length"],
# #             min_length=config["min_length"],
# #             do_sample=False
# #         )[0]["summary_text"]
# #     else :
# #         chunks = chunk_text(fusion, max_words=chunk_size, offset=offset)
# #         resume_final = summarize_chunks(
# #             chunks,
# #             config
# #         )

# #     print(f"\n===== RÉSUMÉ FINAL ({niveau.upper()}) =====")
# #     print(resume_final)
# #     print(f"\nLongueur : {len(resume_final.split())} mots")

# #     return {
# #         "resume_A": resume_A,
# #         "resume_B": resume_B,
# #         "fusion": fusion,
# #         "resume_final": resume_final
# #     }


# # def resumer_texte(file_name , input_dir='..\\\\..\\\\data\\\\processed\\\\transcripts'):

# #     # 2. Charger le texte
# #     with open(os.path.join(input_dir, file_name), "r", encoding="utf-8") as f:
# #         texte = f.read()
# #     resultats = summarize_double(texte, niveau="medium", chunk_size=400)


    
  
# # resumer_texte('audio_cleaned.txt')





# # from transformers import pipeline, AutoTokenizer
# # import torch
# # import os
# # import re

# # # =========================================
# # # 1. CONFIGURATION
# # # =========================================

# # MODEL_NAME = "allenai/led-base-16384"

# # SUMMARY_CONFIGS = {
# #     "court":  {"max_length": 100, "min_length": 30},
# #     "medium": {"max_length": 200, "min_length": 80},
# #     "long":   {"max_length": 400, "min_length": 150},
# # }

# # # =========================================
# # # 2. CHARGEMENT MODELE
# # # =========================================

# # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# # summarizer = pipeline(
# #     "summarization",
# #     model=MODEL_NAME,
# #     tokenizer=tokenizer,
# #     device=0 if torch.cuda.is_available() else -1
# # )

# # # =========================================
# # # 3. NETTOYAGE TEXTE
# # # =========================================

# # def clean_input(text):
# #     text = re.sub(r'[^\x00-\x7F]+', ' ', text)   # remove weird chars
# #     text = re.sub(r'\s+', ' ', text)             # normalize spaces
# #     text = re.sub(r'(.)\1{2,}', r'\1', text)     # remove repeated letters
# #     return text.strip()

# # def clean_summary(text):
# #     sentences = text.split(". ")
# #     seen = set()
# #     result = []

# #     for s in sentences:
# #         if s not in seen and len(s) > 20:
# #             seen.add(s)
# #             result.append(s)

# #     return ". ".join(result)

# # # =========================================
# # # 4. CHUNKING (TOKENS)
# # # =========================================

# # def chunk_text_tokens(text, max_tokens=4000):
# #     tokens = tokenizer.encode(text, truncation=False)
# #     chunks = []

# #     for i in range(0, len(tokens), max_tokens):
# #         chunk_tokens = tokens[i:i+max_tokens]
# #         chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
# #         chunks.append(chunk_text)

# #     return chunks

# # # =========================================
# # # 5. FILTRAGE CHUNKS
# # # =========================================

# # def is_valid_chunk(chunk):
# #     words = chunk.split()
# #     return len(words) > 50 and "���" not in chunk

# # # =========================================
# # # 6. RESUME DES CHUNKS (LED)
# # # =========================================

# # def summarize_chunk_led(chunk, config):
# #     inputs = tokenizer(
# #         chunk,
# #         return_tensors="pt",
# #         truncation=True,
# #         max_length=4096
# #     )

# #     global_attention_mask = torch.zeros_like(inputs["input_ids"])
# #     global_attention_mask[:, 0] = 1  # IMPORTANT pour LED

# #     summary_ids = summarizer.model.generate(
# #         inputs["input_ids"].to(summarizer.device),
# #         attention_mask=inputs["attention_mask"].to(summarizer.device),
# #         global_attention_mask=global_attention_mask.to(summarizer.device),
# #         max_length=config["max_length"],
# #         min_length=config["min_length"],
# #         num_beams=4,
# #         no_repeat_ngram_size=3
# #     )

# #     return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# # # =========================================
# # # 7. PIPELINE PRINCIPAL
# # # =========================================

# # def hierarchical_summarization(text, niveau="medium"):
# #     config = SUMMARY_CONFIGS[niveau]

# #     print("🧹 Nettoyage du texte...")
# #     text = clean_input(text)

# #     print("📦 Découpage en chunks...")
# #     chunks = chunk_text_tokens(text)

# #     print(f"🔢 Nombre de chunks : {len(chunks)}")

# #     summaries = []

# #     print("🧠 Résumé des chunks...")
# #     for i, chunk in enumerate(chunks):
# #         if not is_valid_chunk(chunk):
# #             print(f"❌ Chunk {i+1} ignoré")
# #             continue

# #         print(f"🔹 Chunk {i+1}/{len(chunks)}")
# #         summary = summarize_chunk_led(chunk, config)
# #         summary = clean_summary(summary)
# #         summaries.append(summary)

# #     print("🧹 Nettoyage fusion...")
# #     merged = clean_summary(" ".join(summaries))
# #     merged = clean_input(merged)

# #     print("🧾 Résumé final...")
# #     final_summary = summarizer(
# #         merged,
# #         max_length=config["max_length"],
# #         min_length=config["min_length"],
# #         do_sample=False,
# #         truncation=True
# #     )[0]["summary_text"]

# #     final_summary = clean_summary(final_summary)

# #     return final_summary

# # # =========================================
# # # 8. FONCTION UTILISATEUR
# # # =========================================

# # def resumer_texte(file_name, input_dir="../../data/processed/transcripts", niveau="medium"):
# #     path = os.path.join(input_dir, file_name)

# #     with open(path, "r", encoding="utf-8") as f:
# #         texte = f.read()

# #     print("\n🚀 Lancement du résumé...\n")

# #     resume = hierarchical_summarization(texte, niveau)

# #     print("\n===== ✅ RÉSUMÉ FINAL =====\n")
# #     print(resume)
# #     print(f"\n📏 Longueur : {len(resume.split())} mots")

# #     return resume

# # # =========================================
# # # 9. EXECUTION
# # # =========================================

# # resumer_texte("audio_cleaned.txt", niveau="medium")
# # from transformers import pipeline, AutoTokenizer
# # import torch
# # import os
# # import re

# # # =========================================
# # # 1. CONFIGURATION DES MODELES
# # # =========================================

# # # LED pour résumer les chunks longs
# # LED_MODEL = "allenai/led-base-16384"
# # led_tokenizer = AutoTokenizer.from_pretrained(LED_MODEL)
# # led_summarizer = pipeline(
# #     "summarization",
# #     model=LED_MODEL,
# #     tokenizer=led_tokenizer,
# #     device=0 if torch.cuda.is_available() else -1
# # )

# # # BART pour le résumé final lisible
# # BART_MODEL = "facebook/bart-large-cnn"
# # bart_summarizer = pipeline(
# #     "summarization",
# #     model=BART_MODEL,
# #     device=0 if torch.cuda.is_available() else -1
# # )

# # # Configurations
# # CHUNK_TOKENS = 4000  # taille chunk LED
# # BART_CONFIG = {"max_length": 200, "min_length": 80}

# # # =========================================
# # # 2. NETTOYAGE TEXTE
# # # =========================================

# # def clean_input(text):
# #     text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # supprime caractères bizarres
# #     text = re.sub(r'\s+', ' ', text)            # normalise espaces
# #     text = re.sub(r'(.)\1{2,}', r'\1', text)    # supprime lettres répétées
# #     return text.strip()

# # def clean_summary(text):
# #     sentences = text.split(". ")
# #     seen = set()
# #     result = []

# #     for s in sentences:
# #         if s not in seen and len(s) > 20:
# #             seen.add(s)
# #             result.append(s)

# #     return ". ".join(result)

# # # =========================================
# # # 3. CHUNKING LED
# # # =========================================

# # def chunk_text_tokens(text, max_tokens=CHUNK_TOKENS):
# #     tokens = led_tokenizer.encode(text, truncation=False)
# #     chunks = []
# #     for i in range(0, len(tokens), max_tokens):
# #         chunk_tokens = tokens[i:i+max_tokens]
# #         chunk_text = led_tokenizer.decode(chunk_tokens, skip_special_tokens=True)
# #         chunks.append(chunk_text)
# #     return chunks

# # # =========================================
# # # 4. FILTRAGE CHUNKS
# # # =========================================

# # def is_valid_chunk(chunk):
# #     words = chunk.split()
# #     return len(words) > 50 and "���" not in chunk

# # # =========================================
# # # 5. RESUME DES CHUNKS AVEC LED
# # # =========================================

# # def summarize_chunk_led(chunk):
# #     inputs = led_tokenizer(
# #         chunk,
# #         return_tensors="pt",
# #         truncation=True,
# #         max_length=CHUNK_TOKENS
# #     )

# #     global_attention_mask = torch.zeros_like(inputs["input_ids"])
# #     global_attention_mask[:, 0] = 1  # attention globale pour LED

# #     summary_ids = led_summarizer.model.generate(
# #         inputs["input_ids"].to(led_summarizer.device),
# #         attention_mask=inputs["attention_mask"].to(led_summarizer.device),
# #         global_attention_mask=global_attention_mask.to(led_summarizer.device),
# #         max_length=CHUNK_TOKENS//10,
# #         min_length=50,
# #         num_beams=4,
# #         no_repeat_ngram_size=3
# #     )

# #     return led_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# # # =========================================
# # # 6. PIPELINE HYBRIDE
# # # =========================================

# # def hybrid_summarization(text):
# #     # Nettoyage initial
# #     text = clean_input(text)

# #     # Découpage en chunks pour LED
# #     chunks = chunk_text_tokens(text)
# #     print(f"Nombre de chunks LED : {len(chunks)}")

# #     # Résumé chaque chunk
# #     summaries = []
# #     for i, chunk in enumerate(chunks):
# #         if not is_valid_chunk(chunk):
# #             continue
# #         print(f"Résumé LED du chunk {i+1}/{len(chunks)}")
# #         chunk_summary = summarize_chunk_led(chunk)
# #         chunk_summary = clean_summary(chunk_summary)
# #         summaries.append(chunk_summary)

# #     # Fusion des résumés LED
# #     merged = clean_summary(" ".join(summaries))

# #     # Résumé final BART pour lisibilité
# #     final_summary = bart_summarizer(
# #         merged,
# #         max_length=BART_CONFIG["max_length"],
# #         min_length=BART_CONFIG["min_length"],
# #         do_sample=False,
# #         truncation=True
# #     )[0]["summary_text"]

# #     final_summary = clean_summary(final_summary)
# #     return final_summary

# # # =========================================
# # # 7. FONCTION UTILISATEUR
# # # =========================================

# # def resumer_texte(file_name, input_dir="../../data/processed/transcripts"):
# #     path = os.path.join(input_dir, file_name)
# #     with open(path, "r", encoding="utf-8") as f:
# #         texte = f.read()

# #     print("\n🚀 Lancement du résumé hybride (LED + BART)...\n")
# #     resume = hybrid_summarization(texte)

# #     print("\n===== RÉSUMÉ FINAL =====\n")
# #     print(resume)
# #     print(f"\n📏 Longueur : {len(resume.split())} mots")
# #     return resume

# # # =========================================
# # # 8. EXECUTION
# # # =========================================

# # # Exemple :
# # resumer_texte("audio_cleaned.txt")

# """
# Pipeline de résumé hybride LED + BART
# Auteur : version propre avec contrôle de longueur
# """

# # import os
# # import re
# # import torch
# # from dataclasses import dataclass
# # from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline


# # # ─────────────────────────────────────────────
# # # 1. CONFIGURATION
# # # ─────────────────────────────────────────────

# # @dataclass
# # class SummaryConfig:
# #     """Paramètres de résumé entièrement contrôlables."""

# #     # Longueur cible du résumé final (en mots)
# #     target_words: int = 150

# #     # Tolérance ±% autour de target_words
# #     tolerance: float = 0.20

# #     # Taille des chunks envoyés à LED (en tokens)
# #     chunk_size: int = 4000

# #     # Ratio de compression par chunk (ex: 0.10 = 10% de la taille du chunk)
# #     chunk_compression_ratio: float = 0.07

# #     # Longueur min par chunk (en tokens)
# #     chunk_min_length: int = 50

# #     # Nombre de beams pour la génération
# #     num_beams: int = 4

# #     # Modèles
# #     led_model: str = "allenai/led-base-16384"
# #     bart_model: str = "facebook/bart-large-cnn"

# #     @property
# #     def final_max_tokens(self) -> int:
# #         """Convertit target_words en tokens (ratio ~1.3 tokens/mot)."""
# #         return int(self.target_words * 1.3 * (1 + self.tolerance))

# #     @property
# #     def final_min_tokens(self) -> int:
# #         return int(self.target_words * 1.3 * (1 - self.tolerance))

# #     @property
# #     def chunk_max_tokens(self) -> int:
# #         return max(50, int(self.chunk_size * self.chunk_compression_ratio))


# # # ─────────────────────────────────────────────
# # # 2. CHARGEMENT DES MODÈLES
# # # ─────────────────────────────────────────────

# # def load_models(config: SummaryConfig):
# #     """Charge LED et BART sur GPU si disponible."""
# #     device = 0 if torch.cuda.is_available() else -1

# #     led_tokenizer = AutoTokenizer.from_pretrained(config.led_model)
# #     led_model = AutoModelForSeq2SeqLM.from_pretrained(config.led_model)
# #     if torch.cuda.is_available():
# #         led_model = led_model.cuda()

# #     bart_pipe = pipeline(
# #         "summarization",
# #         model=config.bart_model,
# #         device=device,
# #     )

# #     return led_tokenizer, led_model, bart_pipe


# # # ─────────────────────────────────────────────
# # # 3. NETTOYAGE DU TEXTE
# # # ─────────────────────────────────────────────

# # def clean_text(text: str) -> str:
# #     """
# #     Nettoie le texte sans toucher aux caractères latins étendus
# #     (accents français, etc.).
# #     """
# #     # Supprime uniquement les caractères de contrôle, pas les accents
# #     text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
# #     # Supprime les séquences de caractères non imprimables (ex: ���)
# #     text = re.sub(r'[\ufffd\ufffe\uffff]', ' ', text)
# #     # Supprime les répétitions de caractères non-alphanumériques (!!!  →  !)
# #     text = re.sub(r'([^\w\sÀ-ÿ])\1{2,}', r'\1', text)
# #     # Normalise les espaces
# #     text = re.sub(r'\s+', ' ', text)
# #     return text.strip()


# # def deduplicate_sentences(text: str, min_length: int = 20) -> str:
# #     """Supprime les phrases dupliquées dans un texte."""
# #     sentences = text.split(". ")
# #     seen = set()
# #     result = []
# #     for s in sentences:
# #         s_clean = s.strip()
# #         if s_clean and s_clean not in seen and len(s_clean) > min_length:
# #             seen.add(s_clean)
# #             result.append(s_clean)
# #     return ". ".join(result)


# # # ─────────────────────────────────────────────
# # # 4. DÉCOUPAGE EN CHUNKS
# # # ─────────────────────────────────────────────

# # def split_into_chunks(text: str, tokenizer, chunk_size: int) -> list[str]:
# #     """Découpe le texte en chunks de taille fixe (en tokens)."""
# #     token_ids = tokenizer.encode(text, truncation=False)
# #     chunks = []
# #     for i in range(0, len(token_ids), chunk_size):
# #         chunk_ids = token_ids[i : i + chunk_size]
# #         chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
# #         chunks.append(chunk_text)
# #     return chunks


# # def is_valid_chunk(chunk: str, min_words: int = 50) -> bool:
# #     """Filtre les chunks trop courts ou corrompus."""
# #     words = chunk.split()
# #     return len(words) >= min_words and '\ufffd' not in chunk


# # # ─────────────────────────────────────────────
# # # 5. RÉSUMÉ DES CHUNKS AVEC LED
# # # ─────────────────────────────────────────────

# # def summarize_chunk_led(
# #     chunk: str,
# #     tokenizer,
# #     model,
# #     config: SummaryConfig,
# # ) -> str:
# #     """Résume un chunk avec LED, avec attention globale."""
# #     inputs = tokenizer(
# #         chunk,
# #         return_tensors="pt",
# #         truncation=True,
# #         max_length=config.chunk_size,
# #     )

# #     # Déplace sur le bon device
# #     device = next(model.parameters()).device
# #     input_ids = inputs["input_ids"].to(device)
# #     attention_mask = inputs["attention_mask"].to(device)

# #     # Attention globale sur le premier token (requis par LED)
# #     global_attention_mask = torch.zeros_like(input_ids)
# #     global_attention_mask[:, 0] = 1

# #     output_ids = model.generate(
# #         input_ids=input_ids,
# #         attention_mask=attention_mask,
# #         global_attention_mask=global_attention_mask,
# #         max_new_tokens=config.chunk_max_tokens,
# #         min_length=config.chunk_min_length,
# #         num_beams=config.num_beams,
# #         no_repeat_ngram_size=3,
# #         early_stopping=True,
# #     )

# #     return tokenizer.decode(output_ids[0], skip_special_tokens=True)


# # # ─────────────────────────────────────────────
# # # 6. PIPELINE PRINCIPAL
# # # ─────────────────────────────────────────────

# # def summarize(
# #     text: str,
# #     config: SummaryConfig,
# #     led_tokenizer,
# #     led_model,
# #     bart_pipe,
# #     verbose: bool = True,
# # ) -> str:
# #     """
# #     Pipeline complet : nettoyage → chunks LED → fusion → résumé BART.

# #     Args:
# #         text:           Texte brut à résumer.
# #         config:         Paramètres de résumé (longueur, compression, etc.).
# #         led_tokenizer:  Tokenizer LED chargé.
# #         led_model:      Modèle LED chargé.
# #         bart_pipe:      Pipeline BART chargé.
# #         verbose:        Affiche la progression.

# #     Returns:
# #         Résumé final en texte.
# #     """
# #     # 1. Nettoyage
# #     text = clean_text(text)

# #     # 2. Découpage
# #     chunks = split_into_chunks(text, led_tokenizer, config.chunk_size)
# #     valid_chunks = [c for c in chunks if is_valid_chunk(c)]

# #     if verbose:
# #         print(f"📄 Chunks total : {len(chunks)}  |  valides : {len(valid_chunks)}")

# #     if not valid_chunks:
# #         raise ValueError("Aucun chunk valide trouvé dans le texte fourni.")

# #     # 3. Résumé de chaque chunk avec LED
# #     chunk_summaries = []
# #     for i, chunk in enumerate(valid_chunks, 1):
# #         if verbose:
# #             print(f"  ⚙️  LED chunk {i}/{len(valid_chunks)}...", end=" ", flush=True)
# #         try:
# #             summary = summarize_chunk_led(chunk, led_tokenizer, led_model, config)
# #             summary = deduplicate_sentences(summary)
# #             chunk_summaries.append(summary)
# #             if verbose:
# #                 print(f"✓ ({len(summary.split())} mots)")
# #         except Exception as e:
# #             if verbose:
# #                 print(f"✗ ignoré ({e})")

# #     if not chunk_summaries:
# #         raise RuntimeError("Tous les chunks ont échoué.")

# #     # 4. Fusion des résumés intermédiaires
# #     merged = deduplicate_sentences(" ".join(chunk_summaries))

# #     if verbose:
# #         print(f"\n🔗 Résumés fusionnés : {len(merged.split())} mots")
# #         print(f"🎯 Cible finale     : {config.target_words} mots "
# #               f"(±{int(config.tolerance * 100)}%)\n")

# #     # 5. Résumé final avec BART
# #     final = bart_pipe(
# #         merged,
# #         max_new_tokens=config.final_max_tokens,
# #         min_length=config.final_min_tokens,
# #         do_sample=False,
# #         truncation=True,
# #     )[0]["summary_text"]

# #     return deduplicate_sentences(final)


# # # ─────────────────────────────────────────────
# # # 7. FONCTION PRINCIPALE
# # # ─────────────────────────────────────────────

# # def resumer_fichier(
# #     file_name: str,
# #     target_words: int = 150,
# #     input_dir: str = "../../data/processed/transcripts",
# #     verbose: bool = True,
# # ) -> str:
# #     """
# #     Résume un fichier texte.

# #     Args:
# #         file_name:    Nom du fichier dans input_dir.
# #         target_words: Longueur souhaitée du résumé en mots.
# #         input_dir:    Dossier contenant les fichiers.
# #         verbose:      Affiche la progression.

# #     Returns:
# #         Résumé final.

# #     Exemple:
# #         resumer_fichier("audio_cleaned.txt", target_words=200)
# #         resumer_fichier("audio_cleaned.txt", target_words=50)   # résumé court
# #         resumer_fichier("audio_cleaned.txt", target_words=400)  # résumé long
# #     """
# #     path = os.path.join(input_dir, file_name)
# #     with open(path, "r", encoding="utf-8") as f:
# #         texte = f.read()

# #     config = SummaryConfig(target_words=target_words)

# #     if verbose:
# #         print(f"\n🚀 Résumé hybride LED + BART")
# #         print(f"   Fichier  : {file_name}")
# #         print(f"   Cible    : ~{target_words} mots\n")

# #     led_tokenizer, led_model, bart_pipe = load_models(config)
# #     resume = summarize(texte, config, led_tokenizer, led_model, bart_pipe, verbose)

# #     if verbose:
# #         print("=" * 50)
# #         print("RÉSUMÉ FINAL")
# #         print("=" * 50)
# #         print(resume)
# #         print(f"\n📏 Longueur : {len(resume.split())} mots")

# #     return resume


# # # ─────────────────────────────────────────────
# # # 8. EXÉCUTION
# # # ─────────────────────────────────────────────

# # if __name__ == "__main__":
# #     # Contrôlez uniquement target_words pour ajuster la longueur
# #     resumer_fichier("audio_cleaned.txt", target_words=120)   # résumé moyen

# #     # resumer_fichier("audio_cleaned.txt", target_words=80)  # résumé court
# #     # resumer_fichier("audio_cleaned.txt", target_words=300) # résumé long


# """
# Pipeline de résumé hybride LED + BART — version améliorée
# Corrections : prompt LED structurant, truncation extractive avant BART,
#               vérification de fidélité par similarité cosinus.
# """

# # import os
# # import re
# # import torch
# # from dataclasses import dataclass
# # from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline as hf_pipeline
# # from sentence_transformers import SentenceTransformer, util


# # # ─────────────────────────────────────────────
# # # 1. CONFIGURATION
# # # ─────────────────────────────────────────────

# # @dataclass
# # class SummaryConfig:
# #     """
# #     Tous les paramètres du pipeline en un seul endroit.

# #     Utilisation rapide :
# #         config = SummaryConfig(target_words=150)   # résumé moyen
# #         config = SummaryConfig(target_words=80)    # résumé court
# #         config = SummaryConfig(target_words=300)   # résumé long
# #     """

# #     # Longueur cible du résumé final (en mots)
# #     target_words: int = 150

# #     # Tolérance ±% autour de target_words
# #     tolerance: float = 0.20

# #     # Taille des chunks envoyés à LED (en tokens)
# #     chunk_size: int = 4000

# #     # Ratio de compression LED par chunk
# #     chunk_compression_ratio: float = 0.10

# #     # Longueur min par chunk LED (en tokens)
# #     chunk_min_length: int = 50

# #     # Nombre de beams pour la génération LED et BART
# #     num_beams: int = 4

# #     # Seuil de fidélité : en dessous, un avertissement est affiché
# #     faithfulness_threshold: float = 0.45

# #     # Modèles
# #     led_model: str = "allenai/led-base-16384"
# #     bart_model: str = "facebook/bart-large-cnn"
# #     extractor_model: str = "sshleifer/distilbart-cnn-6-6"
# #     similarity_model: str = "all-MiniLM-L6-v2"

# #     @property
# #     def final_max_tokens(self) -> int:
# #         return int(self.target_words * 1.3 * (1 + self.tolerance))

# #     @property
# #     def final_min_tokens(self) -> int:
# #         return int(self.target_words * 1.3 * (1 - self.tolerance))

# #     @property
# #     def chunk_max_tokens(self) -> int:
# #         return max(50, int(self.chunk_size * self.chunk_compression_ratio))


# # # ─────────────────────────────────────────────
# # # 2. CHARGEMENT DES MODÈLES
# # # ─────────────────────────────────────────────

# # class ModelBundle:
# #     """Regroupe tous les modèles chargés une seule fois."""

# #     def __init__(self, config: SummaryConfig, verbose: bool = True):
# #         device_id = 0 if torch.cuda.is_available() else -1
# #         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# #         if verbose:
# #             print(f"  Appareil : {'GPU' if torch.cuda.is_available() else 'CPU'}")

# #         if verbose: print(f"  Chargement LED ({config.led_model})...")
# #         self.led_tokenizer = AutoTokenizer.from_pretrained(config.led_model)
# #         self.led_model = AutoModelForSeq2SeqLM.from_pretrained(config.led_model).to(self.device)

# #         if verbose: print(f"  Chargement BART ({config.bart_model})...")
# #         self.bart_pipe = hf_pipeline(
# #             "summarization",
# #             model=config.bart_model,
# #             device=device_id,
# #         )

# #         if verbose: print(f"  Chargement extracteur ({config.extractor_model})...")
# #         self.extractor_pipe = hf_pipeline(
# #             "summarization",
# #             model=config.extractor_model,
# #             device=device_id,
# #         )

# #         if verbose: print(f"  Chargement similarité ({config.similarity_model})...")
# #         self.similarity_model = SentenceTransformer(config.similarity_model)

# #         if verbose: print("  Modèles prêts.\n")


# # # ─────────────────────────────────────────────
# # # 3. NETTOYAGE DU TEXTE
# # # ─────────────────────────────────────────────

# # def clean_text(text: str) -> str:
# #     """
# #     Nettoie le texte sans supprimer les caractères latins étendus
# #     (accents français, etc.).
# #     """
# #     # Supprime les caractères de contrôle uniquement (pas les accents)
# #     text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
# #     # Supprime les caractères de remplacement Unicode (séquences corrompues)
# #     text = re.sub(r'[\ufffd\ufffe\uffff]', ' ', text)
# #     # Supprime les répétitions de ponctuations (!!!→!, ...→.)
# #     text = re.sub(r'([^\w\sÀ-ÿ])\1{2,}', r'\1', text)
# #     # Normalise les espaces
# #     text = re.sub(r'\s+', ' ', text)
# #     return text.strip()


# # def deduplicate_sentences(text: str, min_length: int = 20) -> str:
# #     """Supprime les phrases dupliquées dans un texte."""
# #     sentences = text.split(". ")
# #     seen = set()
# #     result = []
# #     for s in sentences:
# #         s_clean = s.strip()
# #         if s_clean and s_clean not in seen and len(s_clean) > min_length:
# #             seen.add(s_clean)
# #             result.append(s_clean)
# #     return ". ".join(result)


# # # ─────────────────────────────────────────────
# # # 4. DÉCOUPAGE EN CHUNKS
# # # ─────────────────────────────────────────────

# # def split_into_chunks(text: str, tokenizer, chunk_size: int) -> list[str]:
# #     """Découpe le texte en chunks de taille fixe (en tokens)."""
# #     token_ids = tokenizer.encode(text, truncation=False)
# #     chunks = []
# #     for i in range(0, len(token_ids), chunk_size):
# #         chunk_ids = token_ids[i: i + chunk_size]
# #         chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
# #         chunks.append(chunk_text)
# #     return chunks


# # def is_valid_chunk(chunk: str, min_words: int = 50) -> bool:
# #     """Filtre les chunks trop courts ou corrompus."""
# #     return len(chunk.split()) >= min_words and '\ufffd' not in chunk


# # # ─────────────────────────────────────────────
# # # 5. RÉSUMÉ DES CHUNKS AVEC LED
# # #    CORRECTIF 1 : préfixe structurant pour guider LED
# # # ─────────────────────────────────────────────

# # LED_PROMPT_PREFIX = "summarize the key concepts only: "

# # def summarize_chunk_led(
# #     chunk: str,
# #     models: ModelBundle,
# #     config: SummaryConfig,
# # ) -> str:
# #     """
# #     Résume un chunk avec LED.
# #     Le préfixe LED_PROMPT_PREFIX force le modèle à rester factuel
# #     et à ne pas fusionner des concepts différents.
# #     """
# #     prompted_chunk = LED_PROMPT_PREFIX + chunk

# #     inputs = models.led_tokenizer(
# #         prompted_chunk,
# #         return_tensors="pt",
# #         truncation=True,
# #         max_length=config.chunk_size,
# #     )

# #     input_ids = inputs["input_ids"].to(models.device)
# #     attention_mask = inputs["attention_mask"].to(models.device)

# #     # Attention globale sur le premier token (requis par LED)
# #     global_attention_mask = torch.zeros_like(input_ids)
# #     global_attention_mask[:, 0] = 1

# #     output_ids = models.led_model.generate(
# #         input_ids=input_ids,
# #         attention_mask=attention_mask,
# #         global_attention_mask=global_attention_mask,
# #         max_new_tokens=config.chunk_max_tokens,
# #         min_length=config.chunk_min_length,
# #         num_beams=config.num_beams,
# #         no_repeat_ngram_size=3,
# #         early_stopping=True,
# #     )

# #     return models.led_tokenizer.decode(output_ids[0], skip_special_tokens=True)


# # # ─────────────────────────────────────────────
# # # 6. TRUNCATION EXTRACTIVE AVANT BART
# # #    CORRECTIF 2 : évite que BART reçoive trop de texte et hallucine
# # # ─────────────────────────────────────────────

# # def truncate_for_bart(
# #     merged_text: str,
# #     models: ModelBundle,
# #     max_words: int = 400,
# #     verbose: bool = True,
# # ) -> str:
# #     """
# #     Si le texte fusionné dépasse max_words, applique un résumé extractif
# #     rapide (distilbart) avant de passer à BART.
# #     Pas de génération libre → pas d'hallucination à ce stade.
# #     """
# #     word_count = len(merged_text.split())
# #     if word_count <= max_words:
# #         return merged_text

# #     if verbose:
# #         print(f"  Texte fusionné trop long ({word_count} mots) → truncation extractive...")

# #     result = models.extractor_pipe(
# #         merged_text,
# #         max_length=350,
# #         min_length=100,
# #         truncation=True,
# #         do_sample=False,
# #     )
# #     truncated = result[0]["summary_text"]

# #     if verbose:
# #         print(f"  Après truncation : {len(truncated.split())} mots")

# #     return truncated


# # # ─────────────────────────────────────────────
# # # 7. VÉRIFICATION DE FIDÉLITÉ
# # #    CORRECTIF 3 : score de similarité cosinus résumé ↔ source
# # # ─────────────────────────────────────────────

# # def check_faithfulness(
# #     summary: str,
# #     source: str,
# #     models: ModelBundle,
# #     config: SummaryConfig,
# #     verbose: bool = True,
# # ) -> float:
# #     """
# #     Calcule la similarité cosinus entre le résumé et le texte source.
# #     Un score < threshold signale un résumé potentiellement infidèle.

# #     Retourne le score (float entre -1 et 1, idéalement > 0.45).
# #     """
# #     # On limite la source à 2000 caractères pour la vitesse
# #     source_sample = source[:2000]

# #     emb_summary = models.similarity_model.encode(summary, convert_to_tensor=True)
# #     emb_source  = models.similarity_model.encode(source_sample, convert_to_tensor=True)
# #     score = float(util.cos_sim(emb_summary, emb_source))

# #     if verbose:
# #         if score < config.faithfulness_threshold:
# #             print(f"  ⚠️  Fidélité faible : {score:.2f} (seuil : {config.faithfulness_threshold})")
# #             print("      Le résumé s'éloigne du texte source — essayez de réduire target_words.")
# #         else:
# #             print(f"  ✓  Fidélité : {score:.2f}")

# #     return score


# # # ─────────────────────────────────────────────
# # # 8. PIPELINE PRINCIPAL
# # # ─────────────────────────────────────────────

# # def summarize(
# #     text: str,
# #     config: SummaryConfig,
# #     models: ModelBundle,
# #     verbose: bool = True,
# # ) -> dict:
# #     """
# #     Pipeline complet : nettoyage → chunks LED → fusion →
# #     truncation extractive → résumé BART → vérification fidélité.

# #     Retourne un dict avec :
# #         - "summary"      : le résumé final (str)
# #         - "word_count"   : nombre de mots du résumé (int)
# #         - "faithfulness" : score de fidélité (float)
# #     """
# #     # 1. Nettoyage
# #     text = clean_text(text)

# #     # 2. Découpage en chunks
# #     chunks = split_into_chunks(text, models.led_tokenizer, config.chunk_size)
# #     valid_chunks = [c for c in chunks if is_valid_chunk(c)]

# #     if verbose:
# #         print(f"  Chunks total : {len(chunks)}  |  valides : {len(valid_chunks)}")

# #     if not valid_chunks:
# #         raise ValueError("Aucun chunk valide trouvé dans le texte fourni.")

# #     # 3. Résumé de chaque chunk avec LED
# #     chunk_summaries = []
# #     for i, chunk in enumerate(valid_chunks, 1):
# #         if verbose:
# #             print(f"  LED chunk {i}/{len(valid_chunks)}...", end=" ", flush=True)
# #         try:
# #             summary = summarize_chunk_led(chunk, models, config)
# #             summary = deduplicate_sentences(summary)
# #             chunk_summaries.append(summary)
# #             if verbose:
# #                 print(f"✓ ({len(summary.split())} mots)")
# #         except Exception as e:
# #             if verbose:
# #                 print(f"✗ ignoré ({e})")

# #     if not chunk_summaries:
# #         raise RuntimeError("Tous les chunks LED ont échoué.")

# #     # 4. Fusion des résumés intermédiaires
# #     merged = deduplicate_sentences(" ".join(chunk_summaries))

# #     if verbose:
# #         print(f"\n  Résumés fusionnés : {len(merged.split())} mots")
# #         print(f"  Cible finale     : ~{config.target_words} mots (±{int(config.tolerance*100)}%)\n")

# #     # 5. CORRECTIF 2 : truncation extractive si texte fusionné trop long
# #     merged = truncate_for_bart(merged, models, max_words=400, verbose=verbose)

# #     # 6. Résumé final avec BART
# #     final = models.bart_pipe(
# #         merged,
# #         max_new_tokens=config.final_max_tokens,
# #         min_length=config.final_min_tokens,
# #         do_sample=False,
# #         truncation=True,
# #     )[0]["summary_text"]

# #     final = deduplicate_sentences(final)

# #     # 7. CORRECTIF 3 : vérification de fidélité
# #     if verbose:
# #         print()
# #     score = check_faithfulness(final, text, models, config, verbose=verbose)

# #     return {
# #         "summary": final,
# #         "word_count": len(final.split()),
# #         "faithfulness": score,
# #     }


# # # ─────────────────────────────────────────────
# # # 9. FONCTION PRINCIPALE
# # # ─────────────────────────────────────────────

# # def resumer_fichier(
# #     file_name: str,
# #     target_words: int = 150,
# #     input_dir: str = "../../data/processed/transcripts",
# #     verbose: bool = True,
# # ) -> str:
# #     """
# #     Résume un fichier texte avec contrôle de longueur.

# #     Args:
# #         file_name:    Nom du fichier dans input_dir.
# #         target_words: Longueur souhaitée du résumé en mots.
# #         input_dir:    Dossier contenant les fichiers.
# #         verbose:      Affiche la progression.

# #     Returns:
# #         Le résumé final (str).

# #     Exemples :
# #         resumer_fichier("audio_cleaned.txt", target_words=80)   # court
# #         resumer_fichier("audio_cleaned.txt", target_words=150)  # moyen
# #         resumer_fichier("audio_cleaned.txt", target_words=300)  # long
# #     """
# #     path = os.path.join(input_dir, file_name)
# #     with open(path, "r", encoding="utf-8") as f:
# #         texte = f.read()

# #     config = SummaryConfig(target_words=target_words)

# #     if verbose:
# #         print(f"\n{'='*52}")
# #         print(f"  Pipeline résumé hybride LED + BART v2")
# #         print(f"  Fichier  : {file_name}")
# #         print(f"  Cible    : ~{target_words} mots")
# #         print(f"{'='*52}\n")
# #         print("Chargement des modèles...")

# #     models = ModelBundle(config, verbose=verbose)

# #     if verbose:
# #         print("Lancement du résumé...\n")

# #     result = summarize(texte, config, models, verbose=verbose)

# #     if verbose:
# #         print(f"\n{'='*52}")
# #         print("RÉSUMÉ FINAL")
# #         print(f"{'='*52}")
# #         print(result["summary"])
# #         print(f"\n  Longueur  : {result['word_count']} mots")
# #         print(f"  Fidélité  : {result['faithfulness']:.2f}")
# #         print(f"{'='*52}\n")

# #     return result["summary"]


# # # ─────────────────────────────────────────────
# # # 10. EXÉCUTION
# # # ─────────────────────────────────────────────

# # if __name__ == "__main__":
# #     # Ajustez uniquement target_words pour contrôler la longueur
# #     resumer_fichier("audio_cleaned.txt", target_words=150)

# #     # Autres exemples :
# #     # resumer_fichier("audio_cleaned.txt", target_words=80)   # court
# #     # resumer_fichier("audio_cleaned.txt", target_words=300)  # long
# #     # resumer_fichier("autre_fichier.txt", target_words=200, input_dir="./data")


# # """
# # Pipeline de résumé hybride LED + BART — version améliorée
# # Corrections : prompt LED structurant, truncation extractive avant BART,
# #               vérification de fidélité par similarité cosinus.
# # """

# # import os
# # import re
# # import torch
# # from dataclasses import dataclass
# # from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline as hf_pipeline
# # from sentence_transformers import SentenceTransformer, util


# # # ─────────────────────────────────────────────
# # # 1. CONFIGURATION
# # # ─────────────────────────────────────────────

# # @dataclass
# # class SummaryConfig:
# #     """
# #     Tous les paramètres du pipeline en un seul endroit.

# #     Utilisation rapide :
# #         config = SummaryConfig(target_words=150)   # résumé moyen
# #         config = SummaryConfig(target_words=80)    # résumé court
# #         config = SummaryConfig(target_words=300)   # résumé long
# #     """

# #     # Longueur cible du résumé final (en mots)
# #     target_words: int = 150

# #     # Tolérance ±% autour de target_words
# #     tolerance: float = 0.20

# #     # Taille des chunks envoyés à LED (en tokens)
# #     chunk_size: int = 4000

# #     # Ratio de compression LED par chunk
# #     chunk_compression_ratio: float = 0.10

# #     # Longueur min par chunk LED (en tokens)
# #     chunk_min_length: int = 50

# #     # Nombre de beams pour la génération LED et BART
# #     num_beams: int = 4

# #     # Seuil de fidélité : en dessous, un avertissement est affiché
# #     faithfulness_threshold: float = 0.45

# #     # Modèles
# #     led_model: str = "allenai/led-base-16384"
# #     bart_model: str = "facebook/bart-large-cnn"
# #     extractor_model: str = "sshleifer/distilbart-cnn-6-6"
# #     similarity_model: str = "all-MiniLM-L6-v2"

# #     @property
# #     def final_max_tokens(self) -> int:
# #         # Plafonné à 1024 (limite hard de BART) et jamais inférieur à 30
# #         raw = int(self.target_words * 1.3 * (1 + self.tolerance))
# #         return max(30, min(raw, 1024))

# #     @property
# #     def final_min_tokens(self) -> int:
# #         # Toujours strictement inférieur à final_max_tokens
# #         raw = int(self.target_words * 1.3 * (1 - self.tolerance))
# #         return max(10, min(raw, self.final_max_tokens - 10))

# #     @property
# #     def chunk_max_tokens(self) -> int:
# #         return max(50, int(self.chunk_size * self.chunk_compression_ratio))


# # # ─────────────────────────────────────────────
# # # 2. CHARGEMENT DES MODÈLES
# # # ─────────────────────────────────────────────

# # class ModelBundle:
# #     """Regroupe tous les modèles chargés une seule fois."""

# #     def __init__(self, config: SummaryConfig, verbose: bool = True):
# #         device_id = 0 if torch.cuda.is_available() else -1
# #         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# #         if verbose:
# #             print(f"  Appareil : {'GPU' if torch.cuda.is_available() else 'CPU'}")

# #         if verbose: print(f"  Chargement LED ({config.led_model})...")
# #         self.led_tokenizer = AutoTokenizer.from_pretrained(config.led_model)
# #         self.led_model = AutoModelForSeq2SeqLM.from_pretrained(config.led_model).to(self.device)

# #         if verbose: print(f"  Chargement BART ({config.bart_model})...")
# #         self.bart_pipe = hf_pipeline(
# #             "summarization",
# #             model=config.bart_model,
# #             device=device_id,
# #         )

# #         if verbose: print(f"  Chargement extracteur ({config.extractor_model})...")
# #         self.extractor_pipe = hf_pipeline(
# #             "summarization",
# #             model=config.extractor_model,
# #             device=device_id,
# #         )

# #         if verbose: print(f"  Chargement similarité ({config.similarity_model})...")
# #         self.similarity_model = SentenceTransformer(config.similarity_model)

# #         if verbose: print("  Modèles prêts.\n")


# # # ─────────────────────────────────────────────
# # # 3. NETTOYAGE DU TEXTE
# # # ─────────────────────────────────────────────

# # def clean_text(text: str) -> str:
# #     """
# #     Nettoie le texte sans supprimer les caractères latins étendus
# #     (accents français, etc.).
# #     """
# #     # Supprime les caractères de contrôle uniquement (pas les accents)
# #     text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
# #     # Supprime les caractères de remplacement Unicode (séquences corrompues)
# #     text = re.sub(r'[\ufffd\ufffe\uffff]', ' ', text)
# #     # Supprime les répétitions de ponctuations (!!!→!, ...→.)
# #     text = re.sub(r'([^\w\sÀ-ÿ])\1{2,}', r'\1', text)
# #     # Normalise les espaces
# #     text = re.sub(r'\s+', ' ', text)
# #     return text.strip()


# # def deduplicate_sentences(text: str, min_length: int = 20) -> str:
# #     """Supprime les phrases dupliquées dans un texte."""
# #     sentences = text.split(". ")
# #     seen = set()
# #     result = []
# #     for s in sentences:
# #         s_clean = s.strip()
# #         if s_clean and s_clean not in seen and len(s_clean) > min_length:
# #             seen.add(s_clean)
# #             result.append(s_clean)
# #     return ". ".join(result)


# # # ─────────────────────────────────────────────
# # # 4. DÉCOUPAGE EN CHUNKS
# # # ─────────────────────────────────────────────

# # def split_into_chunks(text: str, tokenizer, chunk_size: int) -> list[str]:
# #     """Découpe le texte en chunks de taille fixe (en tokens)."""
# #     token_ids = tokenizer.encode(text, truncation=False)
# #     chunks = []
# #     for i in range(0, len(token_ids), chunk_size):
# #         chunk_ids = token_ids[i: i + chunk_size]
# #         chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
# #         chunks.append(chunk_text)
# #     return chunks


# # def is_valid_chunk(chunk: str, min_words: int = 50) -> bool:
# #     """Filtre les chunks trop courts ou corrompus."""
# #     return len(chunk.split()) >= min_words and '\ufffd' not in chunk


# # # ─────────────────────────────────────────────
# # # 5. RÉSUMÉ DES CHUNKS AVEC LED
# # #    CORRECTIF 1 : préfixe structurant pour guider LED
# # # ─────────────────────────────────────────────

# # LED_PROMPT_PREFIX = "summarize the key concepts only: "

# # def summarize_chunk_led(
# #     chunk: str,
# #     models: ModelBundle,
# #     config: SummaryConfig,
# # ) -> str:
# #     """
# #     Résume un chunk avec LED.
# #     Le préfixe LED_PROMPT_PREFIX force le modèle à rester factuel
# #     et à ne pas fusionner des concepts différents.
# #     """
# #     prompted_chunk = LED_PROMPT_PREFIX + chunk

# #     inputs = models.led_tokenizer(
# #         prompted_chunk,
# #         return_tensors="pt",
# #         truncation=True,
# #         max_length=config.chunk_size,
# #     )

# #     input_ids = inputs["input_ids"].to(models.device)
# #     attention_mask = inputs["attention_mask"].to(models.device)

# #     # Attention globale sur le premier token (requis par LED)
# #     global_attention_mask = torch.zeros_like(input_ids)
# #     global_attention_mask[:, 0] = 1

# #     output_ids = models.led_model.generate(
# #         input_ids=input_ids,
# #         attention_mask=attention_mask,
# #         global_attention_mask=global_attention_mask,
# #         max_new_tokens=config.chunk_max_tokens,
# #         min_length=config.chunk_min_length,
# #         num_beams=config.num_beams,
# #         no_repeat_ngram_size=3,
# #         early_stopping=True,
# #     )

# #     decoded = models.led_tokenizer.decode(output_ids[0], skip_special_tokens=True)
# #     # LED reproduit parfois le préfixe en output — on le supprime
# #     if decoded.lower().startswith(LED_PROMPT_PREFIX.lower()):
# #         decoded = decoded[len(LED_PROMPT_PREFIX):]
# #     return decoded.strip()


# # # ─────────────────────────────────────────────
# # # 6. TRUNCATION EXTRACTIVE AVANT BART
# # #    CORRECTIF 2 : évite que BART reçoive trop de texte et hallucine
# # # ─────────────────────────────────────────────

# # def truncate_for_bart(
# #     merged_text: str,
# #     models: ModelBundle,
# #     max_words: int = 400,
# #     verbose: bool = True,
# # ) -> str:
# #     """
# #     Si le texte fusionné dépasse max_words, applique un résumé extractif
# #     rapide (distilbart) avant de passer à BART.
# #     Pas de génération libre → pas d'hallucination à ce stade.
# #     """
# #     word_count = len(merged_text.split())
# #     if word_count <= max_words:
# #         return merged_text

# #     if verbose:
# #         print(f"  Texte fusionné trop long ({word_count} mots) → truncation extractive...")

# #     result = models.extractor_pipe(
# #         merged_text,
# #         max_length=350,
# #         min_length=100,
# #         truncation=True,
# #         do_sample=False,
# #     )
# #     truncated = result[0]["summary_text"]

# #     if verbose:
# #         print(f"  Après truncation : {len(truncated.split())} mots")

# #     return truncated


# # # ─────────────────────────────────────────────
# # # 7. VÉRIFICATION DE FIDÉLITÉ
# # #    CORRECTIF 3 : score de similarité cosinus résumé ↔ source
# # # ─────────────────────────────────────────────

# # def check_faithfulness(
# #     summary: str,
# #     source: str,
# #     models: ModelBundle,
# #     config: SummaryConfig,
# #     verbose: bool = True,
# # ) -> float:
# #     """
# #     Calcule la similarité cosinus entre le résumé et le texte source.
# #     Un score < threshold signale un résumé potentiellement infidèle.

# #     Retourne le score (float entre -1 et 1, idéalement > 0.45).
# #     """
# #     # On limite la source à 2000 caractères pour la vitesse
# #     source_sample = source[:2000]

# #     emb_summary = models.similarity_model.encode(summary, convert_to_tensor=True)
# #     emb_source  = models.similarity_model.encode(source_sample, convert_to_tensor=True)
# #     score = float(util.cos_sim(emb_summary, emb_source))

# #     if verbose:
# #         if score < config.faithfulness_threshold:
# #             print(f"  ⚠️  Fidélité faible : {score:.2f} (seuil : {config.faithfulness_threshold})")
# #             print("      Le résumé s'éloigne du texte source — essayez de réduire target_words.")
# #         else:
# #             print(f"  ✓  Fidélité : {score:.2f}")

# #     return score


# # # ─────────────────────────────────────────────
# # # 8. PIPELINE PRINCIPAL
# # # ─────────────────────────────────────────────

# # def summarize(
# #     text: str,
# #     config: SummaryConfig,
# #     models: ModelBundle,
# #     verbose: bool = True,
# # ) -> dict:
# #     """
# #     Pipeline complet : nettoyage → chunks LED → fusion →
# #     truncation extractive → résumé BART → vérification fidélité.

# #     Retourne un dict avec :
# #         - "summary"      : le résumé final (str)
# #         - "word_count"   : nombre de mots du résumé (int)
# #         - "faithfulness" : score de fidélité (float)
# #     """
# #     # 1. Nettoyage
# #     text = clean_text(text)

# #     # 2. Découpage en chunks
# #     chunks = split_into_chunks(text, models.led_tokenizer, config.chunk_size)
# #     valid_chunks = [c for c in chunks if is_valid_chunk(c)]

# #     if verbose:
# #         print(f"  Chunks total : {len(chunks)}  |  valides : {len(valid_chunks)}")

# #     if not valid_chunks:
# #         raise ValueError("Aucun chunk valide trouvé dans le texte fourni.")

# #     # 3. Résumé de chaque chunk avec LED
# #     chunk_summaries = []
# #     for i, chunk in enumerate(valid_chunks, 1):
# #         if verbose:
# #             print(f"  LED chunk {i}/{len(valid_chunks)}...", end=" ", flush=True)
# #         try:
# #             summary = summarize_chunk_led(chunk, models, config)
# #             summary = deduplicate_sentences(summary)
# #             chunk_summaries.append(summary)
# #             if verbose:
# #                 print(f"✓ ({len(summary.split())} mots)")
# #         except Exception as e:
# #             if verbose:
# #                 print(f"✗ ignoré ({e})")

# #     if not chunk_summaries:
# #         raise RuntimeError("Tous les chunks LED ont échoué.")

# #     # 4. Fusion des résumés intermédiaires
# #     merged = deduplicate_sentences(" ".join(chunk_summaries))

# #     if verbose:
# #         print(f"\n  Résumés fusionnés : {len(merged.split())} mots")
# #         print(f"  Cible finale     : ~{config.target_words} mots (±{int(config.tolerance*100)}%)\n")

# #     # 5. CORRECTIF 2 : truncation extractive si texte fusionné trop long
# #     merged = truncate_for_bart(merged, models, max_words=400, verbose=verbose)

# #     # 6. Résumé final avec BART
# #     # BART a une fenêtre de 1024 tokens — on passe max_length explicitement
# #     # pour éviter le warning "no maximum length" lors du truncation
# #     final = models.bart_pipe(
# #         merged,
# #         max_new_tokens=config.final_max_tokens,
# #         min_length=config.final_min_tokens,
# #         max_length=1024,
# #         do_sample=False,
# #         truncation=True,
# #     )[0]["summary_text"]

# #     final = deduplicate_sentences(final)

# #     # 7. CORRECTIF 3 : vérification de fidélité
# #     if verbose:
# #         print()
# #     score = check_faithfulness(final, text, models, config, verbose=verbose)

# #     return {
# #         "summary": final,
# #         "word_count": len(final.split()),
# #         "faithfulness": score,
# #     }


# # # ─────────────────────────────────────────────
# # # 9. FONCTION PRINCIPALE
# # # ─────────────────────────────────────────────

# # def resumer_fichier(
# #     file_name: str,
# #     target_words: int = 150,
# #     input_dir: str = "../../data/processed/transcripts",
# #     verbose: bool = True,
# # ) -> str:
# #     """
# #     Résume un fichier texte avec contrôle de longueur.

# #     Args:
# #         file_name:    Nom du fichier dans input_dir.
# #         target_words: Longueur souhaitée du résumé en mots.
# #         input_dir:    Dossier contenant les fichiers.
# #         verbose:      Affiche la progression.

# #     Returns:
# #         Le résumé final (str).

# #     Exemples :
# #         resumer_fichier("audio_cleaned.txt", target_words=80)   # court
# #         resumer_fichier("audio_cleaned.txt", target_words=150)  # moyen
# #         resumer_fichier("audio_cleaned.txt", target_words=300)  # long
# #     """
# #     path = os.path.join(input_dir, file_name)
# #     with open(path, "r", encoding="utf-8") as f:
# #         texte = f.read()

# #     config = SummaryConfig(target_words=target_words)

# #     if verbose:
# #         print(f"\n{'='*52}")
# #         print(f"  Pipeline résumé hybride LED + BART v2")
# #         print(f"  Fichier  : {file_name}")
# #         print(f"  Cible    : ~{target_words} mots")
# #         print(f"{'='*52}\n")
# #         print("Chargement des modèles...")

# #     models = ModelBundle(config, verbose=verbose)

# #     if verbose:
# #         print("Lancement du résumé...\n")

# #     result = summarize(texte, config, models, verbose=verbose)

# #     if verbose:
# #         print(f"\n{'='*52}")
# #         print("RÉSUMÉ FINAL")
# #         print(f"{'='*52}")
# #         print(result["summary"])
# #         print(f"\n  Longueur  : {result['word_count']} mots")
# #         print(f"  Fidélité  : {result['faithfulness']:.2f}")
# #         print(f"{'='*52}\n")

# #     return result["summary"]


# # # ─────────────────────────────────────────────
# # # 10. EXÉCUTION
# # # ─────────────────────────────────────────────

# # if __name__ == "__main__":
# #     # Ajustez uniquement target_words pour contrôler la longueur
# #     resumer_fichier("audio_cleaned.txt", target_words=150)

# #     # Autres exemples :
# #     # resumer_fichier("audio_cleaned.txt", target_words=80)   # court
# #     # resumer_fichier("audio_cleaned.txt", target_words=300)  # long
# #     # resumer_fichier("autre_fichier.txt", target_words=200, input_dir="./data")


# """
# Pipeline de résumé hybride LED + BART — version améliorée
# Corrections : prompt LED structurant, truncation extractive avant BART,
#               vérification de fidélité par similarité cosinus.
# """

# import os
# import re
# import torch
# from dataclasses import dataclass
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline as hf_pipeline
# from sentence_transformers import SentenceTransformer, util


# # ─────────────────────────────────────────────
# # 1. CONFIGURATION
# # ─────────────────────────────────────────────

# @dataclass
# class SummaryConfig:
#     """
#     Tous les paramètres du pipeline en un seul endroit.

#     Utilisation rapide :
#         config = SummaryConfig(target_words=150)   # résumé moyen
#         config = SummaryConfig(target_words=80)    # résumé court
#         config = SummaryConfig(target_words=300)   # résumé long
#     """

#     # Longueur cible du résumé final (en mots)
#     target_words: int = 150

#     # Tolérance ±% autour de target_words
#     tolerance: float = 0.20

#     # Taille des chunks envoyés à LED (en tokens)
#     chunk_size: int = 4000

#     # Ratio de compression LED par chunk
#     chunk_compression_ratio: float = 0.10

#     # Longueur min par chunk LED (en tokens)
#     chunk_min_length: int = 50

#     # Nombre de beams pour la génération LED et BART
#     num_beams: int = 4

#     # Seuil de fidélité : en dessous, un avertissement est affiché
#     faithfulness_threshold: float = 0.45

#     # Modèles
#     led_model: str = "allenai/led-base-16384"
#     bart_model: str = "facebook/bart-large-cnn"
#     extractor_model: str = "sshleifer/distilbart-cnn-6-6"
#     similarity_model: str = "all-MiniLM-L6-v2"

#     @property
#     def final_max_tokens(self) -> int:
#         # Plafonné à 1024 (limite hard de BART) et jamais inférieur à 30
#         raw = int(self.target_words * 1.3 * (1 + self.tolerance))
#         return max(30, min(raw, 1024))

#     @property
#     def final_min_tokens(self) -> int:
#         # Toujours strictement inférieur à final_max_tokens
#         raw = int(self.target_words * 1.3 * (1 - self.tolerance))
#         return max(10, min(raw, self.final_max_tokens - 10))

#     @property
#     def chunk_max_tokens(self) -> int:
#         return max(50, int(self.chunk_size * self.chunk_compression_ratio))


# # ─────────────────────────────────────────────
# # 2. CHARGEMENT DES MODÈLES
# # ─────────────────────────────────────────────

# class ModelBundle:
#     """Regroupe tous les modèles chargés une seule fois."""

#     def __init__(self, config: SummaryConfig, verbose: bool = True):
#         device_id = 0 if torch.cuda.is_available() else -1
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#         if verbose:
#             print(f"  Appareil : {'GPU' if torch.cuda.is_available() else 'CPU'}")

#         if verbose: print(f"  Chargement LED ({config.led_model})...")
#         self.led_tokenizer = AutoTokenizer.from_pretrained(config.led_model)
#         self.led_model = AutoModelForSeq2SeqLM.from_pretrained(config.led_model).to(self.device)

#         if verbose: print(f"  Chargement BART ({config.bart_model})...")
#         self.bart_pipe = hf_pipeline(
#             "summarization",
#             model=config.bart_model,
#             device=device_id,
#         )

#         if verbose: print(f"  Chargement extracteur ({config.extractor_model})...")
#         self.extractor_pipe = hf_pipeline(
#             "summarization",
#             model=config.extractor_model,
#             device=device_id,
#         )

#         if verbose: print(f"  Chargement similarité ({config.similarity_model})...")
#         self.similarity_model = SentenceTransformer(config.similarity_model)

#         if verbose: print("  Modèles prêts.\n")


# # ─────────────────────────────────────────────
# # 3. NETTOYAGE DU TEXTE
# # ─────────────────────────────────────────────

# def clean_text(text: str) -> str:
#     """
#     Nettoie le texte sans supprimer les caractères latins étendus
#     (accents français, etc.).
#     """
#     # Supprime les caractères de contrôle uniquement (pas les accents)
#     text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
#     # Supprime les caractères de remplacement Unicode (séquences corrompues)
#     text = re.sub(r'[\ufffd\ufffe\uffff]', ' ', text)
#     # Supprime les répétitions de ponctuations (!!!→!, ...→.)
#     text = re.sub(r'([^\w\sÀ-ÿ])\1{2,}', r'\1', text)
#     # Normalise les espaces
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()


# def deduplicate_sentences(text: str, min_length: int = 20) -> str:
#     """Supprime les phrases dupliquées dans un texte."""
#     sentences = text.split(". ")
#     seen = set()
#     result = []
#     for s in sentences:
#         s_clean = s.strip()
#         if s_clean and s_clean not in seen and len(s_clean) > min_length:
#             seen.add(s_clean)
#             result.append(s_clean)
#     return ". ".join(result)


# def filter_corrupted_sentences(text: str, source: str, min_overlap: float = 0.25) -> str:
#     """
#     Supprime les phrases dont moins de min_overlap% des mots proviennent
#     du texte source. Ces phrases sont des fusions incohérentes ou hallucinations.
#     Exemple typique éliminé :
#       "This reduces the loss to the relevant English words when generating each French word."
#     → aucun lien clair avec un seul passage du source.
#     """
#     source_words = set(re.findall(r'\b\w+\b', source.lower()))
#     sentences = text.split(". ")
#     clean = []
#     for s in sentences:
#         s_words = set(re.findall(r'\b\w+\b', s.lower()))
#         if not s_words:
#             continue
#         overlap = len(s_words & source_words) / len(s_words)
#         if overlap >= min_overlap:
#             clean.append(s)
#     return ". ".join(clean)


# # ─────────────────────────────────────────────
# # 4. DÉCOUPAGE EN CHUNKS
# # ─────────────────────────────────────────────

# def split_into_chunks(text: str, tokenizer, chunk_size: int, overlap: int = 200) -> list[str]:
#     """
#     Découpe le texte en chunks avec chevauchement (overlap).
#     Le chevauchement évite de couper un sujet en deux entre deux chunks,
#     ce qui causait des omissions (CNN, LSTM, etc. jamais résumés).
#     """
#     token_ids = tokenizer.encode(text, truncation=False)
#     chunks = []
#     step = chunk_size - overlap
#     for i in range(0, len(token_ids), step):
#         chunk_ids = token_ids[i: i + chunk_size]
#         chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
#         chunks.append(chunk_text)
#         if i + chunk_size >= len(token_ids):
#             break
#     return chunks


# def is_valid_chunk(chunk: str, min_words: int = 50) -> bool:
#     """Filtre les chunks trop courts ou corrompus."""
#     return len(chunk.split()) >= min_words and '\ufffd' not in chunk


# # ─────────────────────────────────────────────
# # 5. RÉSUMÉ DES CHUNKS AVEC LED
# #    CORRECTIF 1 : préfixe structurant pour guider LED
# # ─────────────────────────────────────────────

# LED_PROMPT_PREFIX = "summarize each topic separately with one sentence per concept: "

# def summarize_chunk_led(
#     chunk: str,
#     models: ModelBundle,
#     config: SummaryConfig,
# ) -> str:
#     """
#     Résume un chunk avec LED.
#     Le préfixe LED_PROMPT_PREFIX force le modèle à rester factuel
#     et à ne pas fusionner des concepts différents.
#     """
#     prompted_chunk = LED_PROMPT_PREFIX + chunk

#     inputs = models.led_tokenizer(
#         prompted_chunk,
#         return_tensors="pt",
#         truncation=True,
#         max_length=config.chunk_size,
#     )

#     input_ids = inputs["input_ids"].to(models.device)
#     attention_mask = inputs["attention_mask"].to(models.device)

#     # Attention globale sur le premier token (requis par LED)
#     global_attention_mask = torch.zeros_like(input_ids)
#     global_attention_mask[:, 0] = 1

#     output_ids = models.led_model.generate(
#         input_ids=input_ids,
#         attention_mask=attention_mask,
#         global_attention_mask=global_attention_mask,
#         max_new_tokens=config.chunk_max_tokens,
#         min_length=config.chunk_min_length,
#         num_beams=config.num_beams,
#         no_repeat_ngram_size=3,
#         early_stopping=True,
#     )

#     decoded = models.led_tokenizer.decode(output_ids[0], skip_special_tokens=True)
#     # LED reproduit parfois le préfixe en output — on le supprime
#     if decoded.lower().startswith(LED_PROMPT_PREFIX.lower()):
#         decoded = decoded[len(LED_PROMPT_PREFIX):]
#     return decoded.strip()


# # ─────────────────────────────────────────────
# # 6. TRUNCATION EXTRACTIVE AVANT BART
# #    CORRECTIF 2 : évite que BART reçoive trop de texte et hallucine
# # ─────────────────────────────────────────────

# def truncate_for_bart(
#     merged_text: str,
#     models: ModelBundle,
#     max_words: int = 400,
#     verbose: bool = True,
# ) -> str:
#     """
#     Si le texte fusionné dépasse max_words, applique un résumé extractif
#     rapide (distilbart) avant de passer à BART.
#     Pas de génération libre → pas d'hallucination à ce stade.
#     """
#     word_count = len(merged_text.split())
#     if word_count <= max_words:
#         return merged_text

#     if verbose:
#         print(f"  Texte fusionné trop long ({word_count} mots) → truncation extractive...")

#     result = models.extractor_pipe(
#         merged_text,
#         max_length=350,
#         min_length=100,
#         truncation=True,
#         do_sample=False,
#     )
#     truncated = result[0]["summary_text"]

#     if verbose:
#         print(f"  Après truncation : {len(truncated.split())} mots")

#     return truncated


# # ─────────────────────────────────────────────
# # 7. VÉRIFICATION DE FIDÉLITÉ
# #    CORRECTIF 3 : score de similarité cosinus résumé ↔ source
# # ─────────────────────────────────────────────

# def check_faithfulness(
#     summary: str,
#     source: str,
#     models: ModelBundle,
#     config: SummaryConfig,
#     verbose: bool = True,
# ) -> float:
#     """
#     Calcule la similarité cosinus entre le résumé et le texte source.
#     Un score < threshold signale un résumé potentiellement infidèle.

#     Retourne le score (float entre -1 et 1, idéalement > 0.45).
#     """
#     # On limite la source à 2000 caractères pour la vitesse
#     source_sample = source[:2000]

#     emb_summary = models.similarity_model.encode(summary, convert_to_tensor=True)
#     emb_source  = models.similarity_model.encode(source_sample, convert_to_tensor=True)
#     score = float(util.cos_sim(emb_summary, emb_source))

#     if verbose:
#         if score < config.faithfulness_threshold:
#             print(f"  ⚠️  Fidélité faible : {score:.2f} (seuil : {config.faithfulness_threshold})")
#             print("      Le résumé s'éloigne du texte source — essayez de réduire target_words.")
#         else:
#             print(f"  ✓  Fidélité : {score:.2f}")

#     return score


# # ─────────────────────────────────────────────
# # 8. PIPELINE PRINCIPAL
# # ─────────────────────────────────────────────

# def summarize(
#     text: str,
#     config: SummaryConfig,
#     models: ModelBundle,
#     verbose: bool = True,
# ) -> dict:
#     """
#     Pipeline complet : nettoyage → chunks LED → fusion →
#     truncation extractive → résumé BART → vérification fidélité.

#     Retourne un dict avec :
#         - "summary"      : le résumé final (str)
#         - "word_count"   : nombre de mots du résumé (int)
#         - "faithfulness" : score de fidélité (float)
#     """
#     # 1. Nettoyage
#     text = clean_text(text)

#     # 2. Découpage en chunks
#     chunks = split_into_chunks(text, models.led_tokenizer, config.chunk_size, overlap=200)
#     valid_chunks = [c for c in chunks if is_valid_chunk(c)]

#     if verbose:
#         print(f"  Chunks total : {len(chunks)}  |  valides : {len(valid_chunks)}")

#     if not valid_chunks:
#         raise ValueError("Aucun chunk valide trouvé dans le texte fourni.")

#     # 3. Résumé de chaque chunk avec LED
#     chunk_summaries = []
#     for i, chunk in enumerate(valid_chunks, 1):
#         if verbose:
#             print(f"  LED chunk {i}/{len(valid_chunks)}...", end=" ", flush=True)
#         try:
#             summary = summarize_chunk_led(chunk, models, config)
#             summary = deduplicate_sentences(summary)
#             chunk_summaries.append(summary)
#             if verbose:
#                 print(f"✓ ({len(summary.split())} mots)")
#         except Exception as e:
#             if verbose:
#                 print(f"✗ ignoré ({e})")

#     if not chunk_summaries:
#         raise RuntimeError("Tous les chunks LED ont échoué.")

#     # 4. Fusion des résumés intermédiaires + filtrage des phrases corrompues
#     merged = deduplicate_sentences(" ".join(chunk_summaries))
#     merged = filter_corrupted_sentences(merged, text, min_overlap=0.25)

#     if verbose:
#         print(f"\n  Résumés fusionnés (filtrés) : {len(merged.split())} mots")
#         print(f"  Cible finale                : ~{config.target_words} mots (±{int(config.tolerance*100)}%)\n")

#     # 5. CORRECTIF 2 : truncation extractive si texte fusionné trop long
#     merged = truncate_for_bart(merged, models, max_words=400, verbose=verbose)

#     # 6. Résumé final avec BART
#     # BART a une fenêtre de 1024 tokens — on passe max_length explicitement
#     # pour éviter le warning "no maximum length" lors du truncation
#     final = models.bart_pipe(
#         merged,
#         max_new_tokens=config.final_max_tokens,
#         min_length=config.final_min_tokens,
#         max_length=1024,
#         do_sample=False,
#         truncation=True,
#     )[0]["summary_text"]

#     final = deduplicate_sentences(final)

#     # 7. CORRECTIF 3 : vérification de fidélité
#     if verbose:
#         print()
#     score = check_faithfulness(final, text, models, config, verbose=verbose)

#     return {
#         "summary": final,
#         "word_count": len(final.split()),
#         "faithfulness": score,
#     }


# # ─────────────────────────────────────────────
# # 9. FONCTION PRINCIPALE
# # ─────────────────────────────────────────────

# def resumer_fichier(
#     file_name: str,
#     target_words: int = 150,
#     input_dir: str = "../../data/processed/transcripts",
#     verbose: bool = True,
# ) -> str:
#     """
#     Résume un fichier texte avec contrôle de longueur.

#     Args:
#         file_name:    Nom du fichier dans input_dir.
#         target_words: Longueur souhaitée du résumé en mots.
#         input_dir:    Dossier contenant les fichiers.
#         verbose:      Affiche la progression.

#     Returns:
#         Le résumé final (str).

#     Exemples :
#         resumer_fichier("audio_cleaned.txt", target_words=80)   # court
#         resumer_fichier("audio_cleaned.txt", target_words=150)  # moyen
#         resumer_fichier("audio_cleaned.txt", target_words=300)  # long
#     """
#     path = os.path.join(input_dir, file_name)
#     with open(path, "r", encoding="utf-8") as f:
#         texte = f.read()

#     config = SummaryConfig(target_words=target_words)

#     if verbose:
#         print(f"\n{'='*52}")
#         print(f"  Pipeline résumé hybride LED + BART v2")
#         print(f"  Fichier  : {file_name}")
#         print(f"  Cible    : ~{target_words} mots")
#         print(f"{'='*52}\n")
#         print("Chargement des modèles...")

#     models = ModelBundle(config, verbose=verbose)

#     if verbose:
#         print("Lancement du résumé...\n")

#     result = summarize(texte, config, models, verbose=verbose)

#     if verbose:
#         print(f"\n{'='*52}")
#         print("RÉSUMÉ FINAL")
#         print(f"{'='*52}")
#         print(result["summary"])
#         print(f"\n  Longueur  : {result['word_count']} mots")
#         print(f"  Fidélité  : {result['faithfulness']:.2f}")
#         print(f"{'='*52}\n")

#     return result["summary"]


# # ─────────────────────────────────────────────
# # 10. EXÉCUTION
# # ─────────────────────────────────────────────

# if __name__ == "__main__":
#     # Ajustez uniquement target_words pour contrôler la longueur
#     resumer_fichier("audio_cleaned.txt", target_words=150)

#     # Autres exemples :
#     # resumer_fichier("audio_cleaned.txt", target_words=80)   # court
#     # resumer_fichier("audio_cleaned.txt", target_words=300)  # long
#     # resumer_fichier("autre_fichier.txt", target_words=200, input_dir="./data")


# import os
# import re
# import torch
# import numpy as np
# from dataclasses import dataclass
# from transformers import AutoModelForSeq2SeqLM, pipeline as hf_pipeline
# from sentence_transformers import SentenceTransformer, util


# # ─────────────────────────────────────────────
# # 1. CONFIGURATION
# # ─────────────────────────────────────────────

# @dataclass
# class SummaryConfig:
#     # Longueur cible du résumé final (en mots)
#     target_words: int = 150

#     # Tolérance ±% autour de target_words
#     tolerance: float = 0.20

#     # ── Semantic chunker ──────────────────────
#     # Seuil de similarité cosinus : en dessous → nouveau chunk
#     semantic_threshold: float = 0.60
#     # Taille min d'un chunk (en mots) — évite les chunks orphelins
#     min_chunk_words: int = 50
#     # Taille max d'un chunk (en mots) — évite de surcharger LED/BART
#     max_chunk_words: int = 600

#     # Ratio de compression LED par chunk
#     chunk_compression_ratio: float = 0.10

#     # Longueur min par chunk LED (en tokens)
#     chunk_min_length: int = 50

#     # Nombre de beams pour la génération
#     num_beams: int = 4

#     # Seuil de fidélité
#     faithfulness_threshold: float = 0.55   # relevé de 0.45 → 0.55

#     # Modèles
#     led_model: str    = "allenai/led-base-16384"
#     bart_model: str   = "facebook/bart-large-cnn"
#     extractor_model: str = "sshleifer/distilbart-cnn-6-6"
#     similarity_model: str = "all-MiniLM-L6-v2"

#     @property
#     def final_max_tokens(self) -> int:
#         raw = int(self.target_words * 1.3 * (1 + self.tolerance))
#         return max(30, min(raw, 1024))

#     @property
#     def final_min_tokens(self) -> int:
#         raw = int(self.target_words * 1.3 * (1 - self.tolerance))
#         return max(10, min(raw, self.final_max_tokens - 10))

#     @property
#     def chunk_max_tokens(self) -> int:
#         # Utilisé pour LED : basé sur max_chunk_words × 1.3 (ratio mots→tokens)
#         return max(50, int(self.max_chunk_words * 1.3 * self.chunk_compression_ratio))


# # ─────────────────────────────────────────────
# # 2. CHARGEMENT DES MODÈLES
# # ─────────────────────────────────────────────

# class ModelBundle:
#     def __init__(self, config: SummaryConfig, verbose: bool = True):
#         device_id = 0 if torch.cuda.is_available() else -1
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#         if verbose:
#             print(f"  Appareil : {'GPU' if torch.cuda.is_available() else 'CPU'}")

#         # LED — gardé pour les chunks longs
#         if verbose: print(f"  Chargement LED ({config.led_model})...")
#         from transformers import AutoTokenizer
#         self.led_tokenizer = AutoTokenizer.from_pretrained(config.led_model)
#         self.led_model = AutoModelForSeq2SeqLM.from_pretrained(config.led_model).to(self.device)

#         if verbose: print(f"  Chargement BART ({config.bart_model})...")
#         self.bart_pipe = hf_pipeline(
#             "summarization", model=config.bart_model, device=device_id,
#         )

#         if verbose: print(f"  Chargement extracteur ({config.extractor_model})...")
#         self.extractor_pipe = hf_pipeline(
#             "summarization", model=config.extractor_model, device=device_id,
#         )

#         # all-MiniLM-L6-v2 : utilisé DEUX fois (chunker + fidélité)
#         if verbose: print(f"  Chargement similarité ({config.similarity_model})...")
#         self.similarity_model = SentenceTransformer(config.similarity_model)

#         if verbose: print("  Modèles prêts.\n")


# # ─────────────────────────────────────────────
# # 3. NETTOYAGE DU TEXTE
# # ─────────────────────────────────────────────

# def clean_text(text: str) -> str:
#     text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)
#     text = re.sub(r'[\ufffd\ufffe\uffff]', ' ', text)
#     text = re.sub(r'([^\w\sÀ-ÿ])\1{2,}', r'\1', text)
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()


# def deduplicate_sentences(text: str, min_length: int = 20) -> str:
#     sentences = text.split(". ")
#     seen, result = set(), []
#     for s in sentences:
#         s_clean = s.strip()
#         if s_clean and s_clean not in seen and len(s_clean) > min_length:
#             seen.add(s_clean)
#             result.append(s_clean)
#     return ". ".join(result)


# def filter_corrupted_sentences(text: str, source: str, min_overlap: float = 0.30) -> str:
#     """Seuil relevé 0.25 → 0.30 pour mieux filtrer les hallucinations."""
#     source_words = set(re.findall(r'\b\w+\b', source.lower()))
#     sentences = text.split(". ")
#     clean = []
#     for s in sentences:
#         s_words = set(re.findall(r'\b\w+\b', s.lower()))
#         if not s_words:
#             continue
#         overlap = len(s_words & source_words) / len(s_words)
#         if overlap >= min_overlap:
#             clean.append(s)
#     return ". ".join(clean)


# # ─────────────────────────────────────────────
# # 4. SEMANTIC CHUNKER  ← remplace split_into_chunks
# # ─────────────────────────────────────────────

# def split_into_chunks(
#     text: str,
#     model: SentenceTransformer,        # passe models.similarity_model
#     similarity_threshold: float = 0.75,
#     min_chunk_words: int = 50,
#     max_chunk_words: int = 500,
# ) -> list[str]:
#     """
#     Découpe le texte sur les frontières sémantiques plutôt que sur
#     un nombre fixe de tokens.

#     Algorithme :
#       1. Découpe en phrases sur '. '
#       2. Encode toutes les phrases en un seul batch (rapide)
#       3. Compare chaque phrase avec la précédente :
#            sim < threshold  →  rupture sémantique  →  nouveau chunk
#            word_count > max →  chunk trop grand    →  nouveau chunk
#       4. Fusionne les chunks trop courts avec le précédent
#     """
#     # ── Découpe en phrases ────────────────────
#     sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
#     if len(sentences) <= 1:
#         return [text]

#     # ── Encodage batch ────────────────────────
#     embeddings = model.encode(sentences, batch_size=32, show_progress_bar=False)

#     # ── Détection des ruptures ────────────────
#     chunks: list[str] = []
#     current_sentences: list[str] = [sentences[0]]
#     current_words: int = len(sentences[0].split())

#     for i in range(1, len(sentences)):
#         word_count  = len(sentences[i].split())
#         would_exceed = (current_words + word_count) > max_chunk_words

#         # Similarité cosinus entre phrase i et phrase i-1
#         sim = float(np.dot(embeddings[i], embeddings[i - 1]) / (
#               np.linalg.norm(embeddings[i]) *
#               np.linalg.norm(embeddings[i - 1]) + 1e-8))

#         topic_shift = sim < similarity_threshold

#         if topic_shift or would_exceed:
#             chunk_text = '. '.join(current_sentences) + '.'

#             # Chunk trop court → fusionner avec le précédent
#             if current_words < min_chunk_words and chunks:
#                 chunks[-1] += ' ' + chunk_text
#             else:
#                 chunks.append(chunk_text)

#             current_sentences = [sentences[i]]
#             current_words     = word_count
#         else:
#             current_sentences.append(sentences[i])
#             current_words += word_count

#     # ── Dernier chunk ─────────────────────────
#     if current_sentences:
#         last = '. '.join(current_sentences) + '.'
#         if current_words < min_chunk_words and chunks:
#             chunks[-1] += ' ' + last
#         else:
#             chunks.append(last)

#     return chunks


# def is_valid_chunk(chunk: str, min_words: int = 50) -> bool:
#     return len(chunk.split()) >= min_words and '\ufffd' not in chunk


# # ─────────────────────────────────────────────
# # 5. RÉSUMÉ DES CHUNKS AVEC LED
# # ─────────────────────────────────────────────

# LED_PROMPT_PREFIX = "summarize each topic separately with one sentence per concept: "

# def summarize_chunk_led(chunk: str, models: ModelBundle, config: SummaryConfig) -> str:
#     prompted_chunk = LED_PROMPT_PREFIX + chunk

#     inputs = models.led_tokenizer(
#         prompted_chunk,
#         return_tensors="pt",
#         truncation=True,
#         max_length=16384,          # fenêtre max de LED
#     )

#     input_ids      = inputs["input_ids"].to(models.device)
#     attention_mask = inputs["attention_mask"].to(models.device)

#     global_attention_mask = torch.zeros_like(input_ids)
#     global_attention_mask[:, 0] = 1

#     output_ids = models.led_model.generate(
#         input_ids=input_ids,
#         attention_mask=attention_mask,
#         global_attention_mask=global_attention_mask,
#         max_new_tokens=config.chunk_max_tokens,
#         min_length=config.chunk_min_length,
#         num_beams=config.num_beams,
#         no_repeat_ngram_size=3,
#         early_stopping=True,
#     )

#     decoded = models.led_tokenizer.decode(output_ids[0], skip_special_tokens=True)
#     if decoded.lower().startswith(LED_PROMPT_PREFIX.lower()):
#         decoded = decoded[len(LED_PROMPT_PREFIX):]
#     return decoded.strip()


# # ─────────────────────────────────────────────
# # 6. TRUNCATION EXTRACTIVE AVANT BART
# # ─────────────────────────────────────────────

# def truncate_for_bart(
#     merged_text: str, models: ModelBundle,
#     max_words: int = 400, verbose: bool = True,
# ) -> str:
#     if len(merged_text.split()) <= max_words:
#         return merged_text

#     if verbose:
#         print(f"  Texte fusionné trop long ({len(merged_text.split())} mots) → truncation extractive...")

#     result = models.extractor_pipe(
#         merged_text, max_length=350, min_length=100,
#         truncation=True, do_sample=False,
#     )
#     truncated = result[0]["summary_text"]

#     if verbose:
#         print(f"  Après truncation : {len(truncated.split())} mots")
#     return truncated


# # ─────────────────────────────────────────────
# # 7. VÉRIFICATION DE FIDÉLITÉ
# # ─────────────────────────────────────────────

# def check_faithfulness(
#     summary: str, source: str,
#     models: ModelBundle, config: SummaryConfig,
#     verbose: bool = True,
# ) -> float:
#     emb_summary = models.similarity_model.encode(summary, convert_to_tensor=True)
#     emb_source  = models.similarity_model.encode(source[:2000], convert_to_tensor=True)
#     score = float(util.cos_sim(emb_summary, emb_source))

#     if verbose:
#         if score < config.faithfulness_threshold:
#             print(f"  ⚠️  Fidélité faible : {score:.2f} (seuil : {config.faithfulness_threshold})")
#         else:
#             print(f"  ✓  Fidélité : {score:.2f}")
#     return score


# # ─────────────────────────────────────────────
# # 8. PIPELINE PRINCIPAL
# # ─────────────────────────────────────────────

# def summarize(
#     text: str, config: SummaryConfig,
#     models: ModelBundle, verbose: bool = True,
# ) -> dict:

#     # 1. Nettoyage
#     text = clean_text(text)

#     # 2. Semantic chunking  ← CHANGEMENT PRINCIPAL
#     chunks = split_into_chunks(
#         text,
#         model=models.similarity_model,          # réutilise le modèle déjà chargé
#         similarity_threshold=config.semantic_threshold,
#         min_chunk_words=config.min_chunk_words,
#         max_chunk_words=config.max_chunk_words,
#     )
#     valid_chunks = [c for c in chunks if is_valid_chunk(c)]

#     if verbose:
#         print(f"  Chunks total : {len(chunks)}  |  valides : {len(valid_chunks)}")
#         for i, c in enumerate(valid_chunks, 1):
#             print(f"    Chunk {i}: {len(c.split())} mots")  # aide au débogage

#     if not valid_chunks:
#         raise ValueError("Aucun chunk valide trouvé.")

#     # 3. Résumé de chaque chunk avec LED
#     chunk_summaries = []
#     for i, chunk in enumerate(valid_chunks, 1):
#         if verbose:
#             print(f"  LED chunk {i}/{len(valid_chunks)}...", end=" ", flush=True)
#         try:
#             summary = summarize_chunk_led(chunk, models, config)
#             summary = deduplicate_sentences(summary)
#             chunk_summaries.append(summary)
#             if verbose:
#                 print(f"✓ ({len(summary.split())} mots)")
#         except Exception as e:
#             if verbose: print(f"✗ ignoré ({e})")

#     if not chunk_summaries:
#         raise RuntimeError("Tous les chunks LED ont échoué.")

#     # 4. Fusion + filtrage
#     merged = deduplicate_sentences(" ".join(chunk_summaries))
#     merged = filter_corrupted_sentences(merged, text, min_overlap=0.30)

#     if verbose:
#         print(f"\n  Résumés fusionnés (filtrés) : {len(merged.split())} mots")
#         print(f"  Cible finale                : ~{config.target_words} mots (±{int(config.tolerance*100)}%)\n")

#     # 5. Truncation extractive si nécessaire
#     merged = truncate_for_bart(merged, models, max_words=400, verbose=verbose)

#     # 6. Résumé final BART
#     final = models.bart_pipe(
#         merged,
#         max_new_tokens=config.final_max_tokens,
#         min_length=config.final_min_tokens,
#         max_length=1024,
#         do_sample=False,
#         truncation=True,
#     )[0]["summary_text"]

#     final = deduplicate_sentences(final)

#     # 7. Fidélité
#     if verbose: print()
#     score = check_faithfulness(final, text, models, config, verbose=verbose)

#     return {"summary": final, "word_count": len(final.split()), "faithfulness": score}


# # ─────────────────────────────────────────────
# # 9. FONCTION PRINCIPALE
# # ─────────────────────────────────────────────

# def resumer_fichier(
#     file_name: str,
#     target_words: int = 150,
#     input_dir: str = "../../data/processed/transcripts",
#     verbose: bool = True,
# ) -> str:
#     path = os.path.join(input_dir, file_name)
#     with open(path, "r", encoding="utf-8") as f:
#         texte = f.read()

#     config = SummaryConfig(target_words=target_words)

#     if verbose:
#         print(f"\n{'='*52}")
#         print(f"  Pipeline résumé hybride LED + BART v3 (semantic)")
#         print(f"  Fichier  : {file_name}")
#         print(f"  Cible    : ~{target_words} mots")
#         print(f"{'='*52}\n")
#         print("Chargement des modèles...")

#     models = ModelBundle(config, verbose=verbose)

#     if verbose: print("Lancement du résumé...\n")

#     result = summarize(texte, config, models, verbose=verbose)

#     if verbose:
#         print(f"\n{'='*52}")
#         print("RÉSUMÉ FINAL")
#         print(f"{'='*52}")
#         print(result["summary"])
#         print(f"\n  Longueur  : {result['word_count']} mots")
#         print(f"  Fidélité  : {result['faithfulness']:.2f}")
#         print(f"{'='*52}\n")

#     return result["summary"]


# # ─────────────────────────────────────────────
# # 10. EXÉCUTION
# # ─────────────────────────────────────────────

# if __name__ == "__main__":
#     resumer_fichier("audio_cleaned.txt", target_words=150)



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