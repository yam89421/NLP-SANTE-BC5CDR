# Projet NLP en santé | Extraction d'informations et Question Answering

ESIEE Paris · E5-BIO Traitement auto du langage naturel en santé | 2026/2027
Binôme : AMARA Yanis, TOMAS Alban

## 1. Objectif

Ce dépôt contient les rendu du projet de TALS, soit principalement deux outils NLP :
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
| Méthode par dictionnaire | Dictionnaire des formes de TRAIN + regex + règles de post-traitement (DIC-v3) | Version figée après trois versions réglées sur VALIDATION |
| Modèle méthode apprise | PubMedBERT (`microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext`), 7 époques (APP-v3) | Meilleur F1 VALIDATION (0,912) devant BioLinkBERT (0,906) et BioBERT (0,892), même recette d'entraînement |
| LLM utilisé pour Q1/Q2 | `gpt-4.1-mini-2025-04-14` (API OpenAI), température 0, graine 42 | Version datée, génération déterministe, coût faible ; clé dans `.env` (non versionné) |
| Recherche lexicale | BM25 du TD RAG (k1 = 1,5, b = 0,75) avec racinisation Snowball français, texte du passage indexé, top-5 | Méthode du cours ; prétraitement choisi sur DEV (REC-v2) |
| Approfondissement QA | Recherche dense `intfloat/multilingual-e5-small` (titre de section + texte), top-5, comparée au BM25 avec Q2 | Modèle du TD RAG ; meilleur rappel sur DEV, à vérifier sur TEST |

## 3. Arborescence du dépôt

```
.
├── README.md                          # ce fichier
├── RAPPORT.md                         # historique des versions, configurations et scores
├── manifest.json                      # versions, modèle, prompts, paramètres, date du gel
├── requirements.txt                   # dépendances Python
├── CDR_Data/                          # corpus BC5CDR d'origine (PubTator, BioC), domaine public
├── src/                               # code du projet (lecteur BC5CDR, dictionnaire, scoreur, corpus QA)
├── tals/                              # paquet du cours, copié sans modification
├── data/
│   ├── partitions_extraction.csv      # PMID -> partition (2.2)
│   ├── corpus_extraction.jsonl/.csv   # corpus BC5CDR relu et vérifié (2.2)
│   ├── bio_extraction.jsonl/.csv      # tokens, positions, étiquettes BIO (2.2)
│   ├── sources_qa/                    # documents QA d'origine (INCa)
│   ├── corpus.csv                     # catalogue des documents QA
│   ├── passages.jsonl                 # passages QA découpés
│   ├── questions_dev.jsonl            # 20 questions DEV annotées
│   ├── questions_test.jsonl           # 10 questions TEST annotées
│   ├── negation.jsonl                 # 20 phrases fictives de négation
│   ├── predictions_extraction.jsonl   # sorties des 2 méthodes figées (DIC-v3, APP-v3) sur TEST
│   └── predictions_qa.jsonl           # sorties Q0/Q1/Q2 sur TEST
├── notebooks/                         # un notebook par section du livret, dans l'ordre d'exécution
│   ├── 2.1_choisir_explorer_donnees.ipynb
│   ├── 2.2_partitions_bio.ipynb
│   ├── 2.3_dictionnaire_regles.ipynb
│   ├── 2.3b_dictionnaire_regles_v3.ipynb  # DIC-v3 : variantes, filtre corrigé, propagation
│   ├── 2.4_methode_apprise.ipynb
│   ├── 2.4b_methode_apprise_v2.ipynb  # APP-v2 : BioBERT mieux entraîné (Colab)
│   ├── 2.4c_methode_apprise_v3.ipynb  # APP-v3 : PubMedBERT / BioLinkBERT, même recette (Colab)
│   ├── 2.5_negation.ipynb
│   ├── 3_corpus_qa.ipynb
│   ├── 4.1_recherche_lexicale_q0.ipynb
│   ├── 4.2_llm_q1_q2.ipynb
│   ├── 4.3_recherche_hybride.ipynb      # approfondissement : recherche dense / hybride
│   ├── 4.4_comparaison_mistral.ipynb    # mêmes prompts QA avec Mistral (DEV et TEST)
│   └── 5_evaluation.ipynb
├── resultats/
│   ├── extraction/                    # tableaux VP/FP/FN, P/R/F1, erreurs commentées
│   ├── negation/                      # matrice de confusion, P/R/F1, erreurs commentées
│   └── qa/                            # Hit@5, rappel@5, BLEU/ROUGE, grille manuelle
├── gabarits/                          # exemples fictifs illustrant chaque format
└── rapport/                           # rapport en 3 notebooks (1_extraction, 2_negation, 3_question_reponse) + notes de cadrage
```

## 4. Ordre d'exécution

Les notebooks portent le numéro de la section du livret qu'ils traitent.

1. `2.1_choisir_explorer_donnees.ipynb` — chargement de BC5CDR, 5 exemples, effectifs par catégorie et
   partition, vérification de 10 mentions de TRAIN, fiche du corpus.
2. `2.2_partitions_bio.ipynb` — partitions officielles, doublons, sauvegarde des identifiants, convention
   BIO (mentions composites, aller-retour BIO, mentions hors frontière de token).
3. `2.3_dictionnaire_regles.ipynb` — dictionnaire construit sur TRAIN, réglé sur VALIDATION, figé,
   prédictions TEST (DIC-v1, DIC-v2).
   `2.3b_dictionnaire_regles_v3.ipynb` — DIC-v3 (version figée) : filtre corrigé, variantes singulier/pluriel,
   extension à droite, propagation dans le document ; ne modifie pas le notebook 2.3.
4. `2.4_methode_apprise.ipynb` — entraînement, réglage sur VALIDATION, comparaison, gel, prédictions TEST.
   `2.4b_methode_apprise_v2.ipynb` — APP-v2 (Colab GPU, ≈ 35 min) : 10 époques, warmup, 2 taux × 2 graines ; ne modifie pas APP-v1.
   `2.4c_methode_apprise_v3.ipynb` — APP-v3 (Colab GPU, ≈ 30 min) : PubMedBERT et BioLinkBERT-base avec la recette d'APP-v2, comparés à BioBERT.
5. `2.5_negation.ipynb` — règles de négation (**développées avant** la génération des phrases fictives),
   génération des 20 phrases, annotation croisée, split dev/test, évaluation.
6. `3_corpus_qa.ipynb` — thème et public (3.1), documents et passages (3.2), questions (3.3), protocole
   DEV/TEST (3.4).
7. `4.1_recherche_lexicale_q0.ipynb` — BM25, top-5 passages, sortie Q0.
8. `4.2_llm_q1_q2.ipynb` — prompts Q1/Q2, mêmes passages, mêmes paramètres.
9. `4.3_recherche_hybride.ipynb` — approfondissement sur DEV : recherche dense, hybride (RRF) et reclassement
   par cross-encoder (non retenu).
10. `5_evaluation.ipynb` — évaluation unique sur TEST des versions figées : les 4 tableaux de mesures (5.1),
   interprétation (5.2), analyse d'erreurs (5.3).
11. `4.4_comparaison_mistral.ipynb` — comparaison OpenAI / Mistral : tous les prompts QA (DEV, TEST, question libre)
    renvoyés tels quels à `mistral-medium-2604` ; à exécuter après le notebook 5 (il relit ses prédictions TEST).
    La section « Comparaison avec un second LLM » du notebook 5 relit à son tour les réponses Mistral : la relancer
    après le notebook 4.4 (aucun nouvel appel, tout vient des fichiers).

## 5. Installation


```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

**Application de démonstration** (`streamlit_app/`) : chatbot RAG, démo d'extraction (DIC-v3, APP-v3) avec
négation, tableau des scores TEST.

```bash
streamlit run streamlit_app/app.py
```

- Déploiement sur Streamlit Community Cloud : fichier principal `streamlit_app/app.py`, Python 3.12 à 3.14.
  Les dépendances sont lues dans `streamlit_app/requirements.txt` (version réduite, torch CPU).
- DIC-v3 est reconstruite au démarrage à partir de TRAIN (`src/dictionnaire_v3.py`, mêmes prédictions TEST
  que le notebook 2.3b).
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

- `data/predictions_extraction.jsonl` : prédictions des deux méthodes figées (DIC-v3, APP-v3) sur TEST.
- `data/predictions_qa.jsonl` : prédictions Q0/Q1/Q2 sur TEST (réponses brutes conservées) ; prédictions DEV
  dans `resultats/qa/`, variante Q2 avec recherche dense dans `resultats/qa/predictions_llm_test_dense.jsonl`.
- `resultats/` : tableaux de scores et analyses manuelles (voir section 5 du livret).
- Les calculs coûteux (entraînement du modèle appris, appels LLM) ont leurs sorties sauvegardées
  dans `resultats/` pour ne pas nécessiter de ré-exécution complète.

## 8. Partitions et gel

- Extraction : partitions officielles de BC5CDR (Training / Development / Test = TRAIN / VALIDATION / TEST,
  500 documents chacune), identifiants sauvegardés dans `data/partitions_extraction.csv`. Réglages sur
  VALIDATION uniquement ; DIC-v3 et APP-v3 figées le 30/10/2026, puis évaluées une seule fois sur TEST.
- QA : DEV (20 questions) sert exclusivement au réglage (découpage, recherche, prompts).
  Configuration gelée le **30/10/2026** (`resultats/qa/qa_config_gelee.json`, résumée dans `manifest.json`),
  puis TEST (10 questions) exécuté une seule fois le 01/11/2026, sans nouveau réglage.
- Le détail des versions et des scores est dans `RAPPORT.md`.
