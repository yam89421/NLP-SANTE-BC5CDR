# Projet NLP en santé | Extraction d'informations et Question Answering

ESIEE Paris · E5-BIO Traitement auto du langage naturel en santé | 2026/2027
Binôme : AMARA Yanis, TOMAS Alban

## 1. Objectif

Ce dépôt contient le rendu du projet de TALS, soit principalement deux outils NLP :
1. **Extraction d'informations** médicales (2 catégories minimum), avec une méthode par
   dictionnaire/règles et une méthode apprise, plus une étude séparée de la **négation**.
2. **Question answering (QA)** sur un corpus documentaire constitué par le binôme, comparant
   une recherche lexicale seule (Q0), un LLM en zero-shot (Q1) et un LLM avec prompt structuré (Q2).

## 2. Choix effectués

| Élément | Choix | Justification |
|---|---|---|
| Corpus d'extraction | BC5CDR (`CDR.Corpus.v010516`, PubTator) | Partitions officielles, positions en caractères vérifiées, domaine public |
| Catégories retenues | Chemical, Disease | Deux catégories annotées du même corpus, ~5 000 et ~4 200 mentions en TRAIN |
| Thème QA | Effets indésirables de la chimiothérapie et soins de support ; 10 documents INCa | Sources publiques, fiables, en français, sous licence ouverte |
| Public visé (QA) | Patients traités par chimiothérapie et leurs proches | Documents INCa écrits pour ce public |
| Méthode par dictionnaire | Dictionnaire des formes de TRAIN + lexique MeSH 2026 filtré sur TRAIN + regex + règles de post-traitement (DIC-v4) | Version figée après quatre versions réglées sur VALIDATION ; ajout de MeSH validé par l'enseignant |
| Modèle méthode apprise | PubMedBERT (`microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext`), 7 époques (APP-v3) | Meilleur F1 VALIDATION (0,912) devant BioLinkBERT (0,906) et BioBERT (0,892), même recette d'entraînement |
| LLM utilisé pour Q1/Q2 | `gpt-4.1-mini-2025-04-14` (API OpenAI), température 0, graine 42 | Version datée, génération déterministe, coût faible ; clé dans `.env` (non versionné) |
| Recherche lexicale | BM25 du TD RAG (k1 = 1,5, b = 0,75) avec racinisation Snowball français, texte du passage indexé, top-5 | Méthode du cours ; prétraitement choisi sur DEV (REC-v2) |
| Approfondissement QA | Recherche dense `intfloat/multilingual-e5-small` (titre de section + texte), top-5, comparée au BM25 avec Q2 | Modèle du TD RAG ; meilleur rappel sur DEV, résultat TEST dans `rapport/3_question_reponse.ipynb` |

## 3. Arborescence du dépôt

```
.
├── README.md                          # ce fichier
├── manifest.json                      # versions, modèle, prompts, paramètres, date du gel
├── requirements.txt                   # dépendances Python
├── rapport/                           # LE RAPPORT : trois notebooks exécutés
│   ├── 1_extraction.ipynb             # BC5CDR, dictionnaire + règles (DIC-v1 → v4), modèle appris (APP-v1 → v3), TEST, erreurs
│   ├── 2_negation.ipynb               # règles de négation, 20 phrases, double annotation, test, erreurs
│   ├── 3_question_reponse.ipynb       # corpus INCa, questions, BM25 / recherche dense, Q0/Q1/Q2, TEST, grille manuelle
│   └── sorties/                       # fichiers réécrits par les notebooks (voir section 7)
├── CDR_Data/                          # corpus BC5CDR d'origine (PubTator, BioC), domaine public
├── src/                               # code du projet (lecteur BC5CDR, dictionnaires, modèle, négation, QA)
├── tals/                              # paquet du cours, copié sans modification
├── data/
│   ├── partitions_extraction.csv      # PMID -> partition
│   ├── corpus_extraction.jsonl/.csv   # corpus BC5CDR relu et vérifié
│   ├── bio_extraction.jsonl/.csv      # tokens, positions, étiquettes BIO
│   ├── sources_qa/                    # documents QA d'origine (INCa)
│   ├── corpus.csv                     # catalogue des documents QA
│   ├── passages.jsonl                 # passages QA découpés
│   ├── questions_dev.jsonl            # 20 questions DEV annotées
│   ├── questions_test.jsonl           # 10 questions TEST annotées
│   ├── negation.jsonl                 # 20 phrases fictives de négation
│   ├── predictions_extraction.jsonl   # sorties des 2 méthodes figées (DIC-v4, APP-v3) sur TEST
│   └── predictions_qa.jsonl           # sorties Q0/Q1/Q2 sur TEST
├── resultats/
│   ├── extraction/                    # configs figées, courbes d'entraînement, prédictions et scores TEST
│   ├── negation/                      # guide et feuilles d'annotation, désaccords, règles figées, scores TEST
│   └── qa/                            # config figée, caches des réponses LLM, grille manuelle, scores TEST
├── streamlit_app/                     # application de démonstration
├── figures_oral/                      # figures de la soutenance et leur script
└── assets/                            # logo de l'application
```

## 4. Ordre d'exécution

Le rapport tient en **trois notebooks autonomes**, à exécuter depuis le dossier `rapport/`, dans l'ordre :

| Notebook | Contenu | Durée (CPU) |
|---|---|---|
| `1_extraction.ipynb` | BC5CDR, dictionnaire et règles (DIC-v1 → v4), modèle appris (APP-v1 → v3), évaluation TEST, état de l'art, erreurs | ≈ 20 min |
| `2_negation.ipynb` | règles de négation figées, 20 phrases, double annotation et kappa, test, erreurs | quelques secondes |
| `3_question_reponse.ipynb` | corpus INCa, questions, BM25 / recherche dense, Q0/Q1/Q2, évaluation TEST, grille manuelle, essais complémentaires (nombre de passages, question libre, Mistral) | ≈ 6 min |

Tout est recalculé à partir des **données d'origine** (`CDR_Data/`, `data/sources_qa/`, `data/corpus.csv`,
`data/negation.jsonl`), de **nos annotations** (questions `data/questions_*.jsonl`, feuilles d'annotation de la
négation, grille de lecture `resultats/qa/grille_manuelle.csv`) et du code `src/` + `tals/`. Ne sont pas recalculés :
- les **entraînements BERT** (GPU, Google Colab) : le modèle figé APP-v3 est rechargé depuis `modeles/apprise_v3`
  s'il existe (non versionné), sinon téléchargé depuis Hugging Face
  ([yam89421/app-v3-pubmedbert-bc5cdr](https://huggingface.co/yam89421/app-v3-pubmedbert-bc5cdr)) ; les courbes de
  réglage d'APP-v1 à v3 sont celles enregistrées pendant les entraînements (`resultats/extraction/apprise*_reglage_validation.csv`) ;
  une cellule optionnelle (`REENTRAINER = True`) réentraîne APP-v3 (GPU conseillé) ;
- les **réponses des LLM**, servies par le cache des requêtes (`resultats/qa/cache_llm.json`, `cache_llm_mistral.json`) :
  un prompt absent du cache serait envoyé à l'API avec la clé lue dans `.env` (`OPENAI_API_KEY`, `MISTRAL_API_KEY`).

Le lexique MeSH 2026 (≈ 64 Mo) est téléchargé automatiquement dans `data/mesh/` (non versionné) à la première exécution
du notebook 1.

## 5. Installation


```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

**Application de démonstration** (`streamlit_app/`, facultative) : chatbot RAG, démo d'extraction (DIC-v4, APP-v3)
avec négation, tableau des scores TEST.

```bash
streamlit run streamlit_app/app.py
```

- Déploiement sur Streamlit Community Cloud : fichier principal `streamlit_app/app.py`, Python 3.12 à 3.14.
  Les dépendances sont lues dans `streamlit_app/requirements.txt` (version réduite, torch CPU).
- DIC-v4 est reconstruite au démarrage (≈ 10 s) : DIC-v3 construite sur TRAIN + termes MeSH retenus, lus dans
  `resultats/extraction/dictionnaire_v4_termes_mesh.tsv.gz` (3 Mo). MeSH n'est donc pas téléchargé par l'application ;
  mêmes prédictions TEST que la version figée (`src/dictionnaire_v4.py`, `verifier_dic_v4`).
- Le modèle APP-v3 est lu dans `modeles/apprise_v3` s'il existe (non versionné), sinon téléchargé depuis
  Hugging Face : https://huggingface.co/yam89421/app-v3-pubmedbert-bc5cdr.
- La clé OpenAI est saisie dans l'application et reste dans la session ; sans clé, le chatbot affiche
  seulement les passages trouvés.

## 6. Ressources reprises

- `tals/` : copie non modifiée du paquet `Commun/tals` du cours (classe `Mention`, scoreur strict
  `scores` / `scores_par_type`, conversions BIO), pour que le dépôt se réexécute sans le dossier du cours.
- `src/cdr.py` : lecteur PubTator de BC5CDR écrit pour le projet (vérification de toutes les positions,
  mentions composites signalées, relations CID ignorées).
- Corpus BC5CDR : Li J. et al., *Annotating chemicals, diseases and their interactions in biomedical
  literature*, BioCreative V, 2015 ; Wei C.-H. et al., *Overview of the BioCreative V CDR Task*, 2015.
  Domaine public (NCBI/NLM), https://ftp.ncbi.nlm.nih.gov/pub/lu/BC5CDR/.
- Documents QA : Institut national du cancer (INCa), catalogue dans `data/corpus.csv` ; licence ouverte
  de réutilisation INCa (11-07-2023), avec mention de la source et de la date de mise à jour.
- `src/apprise.py` : entraînement et décodage repris du TD NER du cours
  (`Extraction/BERT/TD/Tuto1_NER/Partie3_Entrainement_et_Eval`) — mêmes paramètres de départ et même perte
  pondérée ; ajouts : fenêtres de phrases entières, alignement par `tals.aligner_sous_mots`, reconstruction
  des mentions au niveau du document.
- `src/negation.py` : règles de négation à la manière de NegEx (Chapman et al., 2001), d'après le cours
  « Qualification et normalisation » (diapositives 6 à 9).
- Modèles pré-entraînés (Hugging Face) : PubMedBERT `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext`
  (Gu et al., 2021), modèle retenu ; comparés : BioBERT `dmis-lab/biobert-base-cased-v1.1` (Lee et al., 2020) et
  BioLinkBERT `michiyasunaga/BioLinkBERT-base` (Yasunaga et al., 2022).
- `src/qa_recherche.py` : BM25 et recherche dense repris du TD RAG du cours ; modèle d'embeddings
  `intfloat/multilingual-e5-small` (Wang et al., 2024) ; cross-encoder `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
  (essai non retenu).
- `src/qa_scores.py` : BLEU (sacrebleu) et ROUGE (rouge-score) selon l'annexe B.4 du guide.
- Aide d'IA générative (Claude, Anthropic) : aide pour l'écriture du code, génération des 20 phrases
  fictives de négation (après le gel des règles).

## 7. Sorties produites

- `data/predictions_extraction.jsonl` : prédictions des deux méthodes figées (DIC-v4, APP-v3) sur TEST.
- `data/predictions_qa.jsonl` : prédictions Q0/Q1/Q2 sur TEST au format complet (passages retrouvés et transmis,
  réponse brute, durée, échec éventuel) ; variante Q2 avec recherche dense dans `resultats/qa/predictions_llm_test_dense.jsonl`.
- `rapport/sorties/` : fichiers réécrits à chaque exécution des notebooks. `passages.jsonl` et
  `predictions_extraction.jsonl` sont identiques à ceux de `data/` ; `predictions_qa.jsonl` contient les mêmes
  réponses et les mêmes passages transmis, sous une forme plus courte.
- `resultats/` : configurations figées, prédictions et scores TEST, annotations manuelles (voir section 5 du livret).
- Les calculs coûteux (entraînement du modèle appris, appels LLM) ont leurs sorties sauvegardées
  (modèle sur Hugging Face, caches LLM dans `resultats/qa/`) pour ne pas nécessiter de ré-exécution complète.

## 8. Partitions et gel

- Extraction : partitions officielles de BC5CDR (Training / Development / Test = TRAIN / VALIDATION / TEST,
  500 documents chacune), identifiants sauvegardés dans `data/partitions_extraction.csv`. Réglages sur
  VALIDATION uniquement ; DIC-v3 et APP-v3 figées le 30/10/2026, puis évaluées une seule fois sur TEST ; DIC-v4
  (DIC-v3 + MeSH) figée le 11/11/2026 sur VALIDATION et évaluée une seule fois sur TEST, elle remplace DIC-v3.
- QA : DEV (20 questions) sert exclusivement au réglage (découpage, recherche, prompts).
  Configuration gelée le **30/10/2026** (`resultats/qa/qa_config_gelee.json`, résumée dans `manifest.json`),
  puis TEST (10 questions) exécuté une seule fois le 01/11/2026, sans nouveau réglage.
- Le détail des versions et des scores est dans les notebooks de `rapport/`.
