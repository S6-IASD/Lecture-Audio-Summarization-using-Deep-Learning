# Lecture Audio Summarization using Deep Learning

## 📁 Structure du projet

```
data/
└── external/
    └── talksumm/
        ├── data/
        │   ├── talksumm_summaries/   # 1705 résumés .txt
        │   ├── pdf/                  # PDFs des papers
        │   └── talksumm_papers_urls.txt
        └── glove.6B.300d.txt         # Embeddings GloVe
```

---

## ⚙️ Installation

```bash
git clone https://github.com/<votre-repo>
pip install -r data/external/talksumm/requirements.txt
```

---

## 📦 Données externes (non incluses dans le repo)

Les fichiers `data/` sont exclus du repo Git (trop volumineux).  
👉 **Télécharge les données depuis Google Drive** :  
https://drive.google.com/drive/folders/1N-qLYoSXAffxWHn-_5VjszfpIC1r8Dv-?usp=sharing

Place les fichiers téléchargés dans `data/external/talksumm/`.

---

## 🔁 Ou reproduire les données manuellement

### 1. Cloner TalkSumm
```bash
git clone https://github.com/levguy/talksumm data/external/talksumm
```

### 2. Extraire les résumés
```bash
cd data/external/talksumm/data
unzip talksumm_summaries.zip
# → 1705 fichiers .txt dans talksumm_summaries/
```

### 3. Télécharger les PDFs
```bash
python data/external/talksumm/data/get_pdfs.py
# → PDFs dans data/external/talksumm/data/pdf/
```

### 4. Télécharger GloVe
```bash
wget http://nlp.stanford.edu/data/glove.6B.zip
unzip glove.6B.zip glove.6B.300d.txt
# Placer glove.6B.300d.txt dans data/external/talksumm/
```

---

## ✅ Résultat attendu

| Fichier / Dossier | Description |
|---|---|
| `data/talksumm_summaries/` | 1705 résumés de papers |
| `data/pdf/` | PDFs des papers |
| `glove.6B.300d.txt` | Embeddings GloVe 300 dimensions |
