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
| Modèle méthode apprise | *(à compléter)* | *(à compléter)* |
| LLM utilisé pour Q1/Q2 | `gpt-4.1-mini-2025-04-14` (API OpenAI), température 0, graine 42 | Version datée, génération déterministe, coût faible ; clé dans `.env` (non versionné) |
| Recherche lexicale | BM25 du TD RAG (k1 = 1,5, b = 0,75) avec racinisation Snowball français, texte du passage indexé, top-5 | Méthode du cours ; prétraitement choisi sur DEV (REC-v2) |

## 3. Arborescence du dépôt

```
.
├── README.md                          # ce fichier
├── manifest.json                      # versions, modèle, prompts, paramètres, date du gel
├── requirements.txt                   # dépendances Python
├── CDR_Data/                          # corpus BC5CDR d'origine (PubTator, BioC), domaine public
├── src/                               # code du projet (lecteur BC5CDR, dictionnaire, scoreur, corpus QA)
├── tals/                              # paquet du cours, copié sans modification
├── data/
│   ├── partitions_extraction.csv      # PMID -> partition (2.2)
│   ├── corpus_extraction.jsonl        # corpus BC5CDR relu et vérifié (2.2)
│   ├── bio_extraction.jsonl           # tokens, positions, étiquettes BIO (2.2)
│   ├── sources_qa/                    # documents QA d'origine (INCa)
│   ├── corpus.csv                     # catalogue des documents QA
│   ├── passages.jsonl                 # passages QA découpés
│   ├── questions_dev.jsonl            # 20 questions DEV annotées
│   ├── questions_test.jsonl           # 10 questions TEST annotées
│   ├── negation.jsonl                 # 20 phrases fictives de négation
│   ├── predictions_extraction.jsonl   # sorties des 2 méthodes d'extraction sur TEST
│   └── predictions_qa.jsonl           # sorties Q0/Q1/Q2
├── notebooks/                         # un notebook par section du livret, dans l'ordre d'exécution
│   ├── 2.1_choisir_explorer_donnees.ipynb
│   ├── 2.2_partitions_bio.ipynb
│   ├── 2.3_dictionnaire_regles.ipynb
│   ├── 2.4_methode_apprise.ipynb
│   ├── 2.5_negation.ipynb
│   ├── 3_corpus_qa.ipynb
│   ├── 4.1_recherche_lexicale_q0.ipynb
│   ├── 4.2_llm_q1_q2.ipynb
│   ├── 4.3_recherche_hybride.ipynb      # approfondissement : recherche dense / hybride
│   └── 5_evaluation.ipynb
├── resultats/
│   ├── extraction/                    # tableaux VP/FP/FN, P/R/F1, erreurs commentées
│   ├── negation/                      # matrice de confusion, P/R/F1, erreurs commentées
│   └── qa/                            # Hit@5, rappel@5, BLEU/ROUGE, grille manuelle
├── gabarits/                          # exemples fictifs illustrant chaque format
└── rapport/                           # rapport final (8-12 pages hors annexes)
```

## 4. Ordre d'exécution

Les notebooks portent le numéro de la section du livret qu'ils traitent.

1. `2.1_choisir_explorer_donnees.ipynb` — chargement de BC5CDR, 5 exemples, effectifs par catégorie et
   partition, vérification de 10 mentions de TRAIN, fiche du corpus.
2. `2.2_partitions_bio.ipynb` — partitions officielles, doublons, sauvegarde des identifiants, convention
   BIO (mentions composites, aller-retour BIO, mentions hors frontière de token).
3. `2.3_dictionnaire_regles.ipynb` — dictionnaire construit sur TRAIN, réglé sur VALIDATION, figé,
   prédictions TEST.
4. `2.4_methode_apprise.ipynb` — entraînement, réglage sur VALIDATION, comparaison, gel, prédictions TEST.
5. `2.5_negation.ipynb` — règles de négation (**développées avant** la génération des phrases fictives),
   génération des 20 phrases, annotation croisée, split dev/test, évaluation.
6. `3_corpus_qa.ipynb` — thème et public (3.1), documents et passages (3.2), questions (3.3), protocole
   DEV/TEST (3.4).
7. `4.1_recherche_lexicale_q0.ipynb` — BM25, top-5 passages, sortie Q0.
8. `4.2_llm_q1_q2.ipynb` — prompts Q1/Q2, mêmes passages, mêmes paramètres.
9. `5_evaluation.ipynb` — les 4 tableaux de mesures (5.1), interprétation (5.2), analyse d'erreurs (5.3).

## 5. Installation

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

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
- Modèle pré-entraîné : BioBERT `dmis-lab/biobert-base-cased-v1.1` (Lee et al., 2020), via Hugging Face.
- Aide d'IA générative (Claude, Anthropic) : aide pour l'écriture du code, génération des 20 phrases
  fictives de négation (après le gel des règles).

## 7. Sorties produites

- `data/predictions_extraction.jsonl` : prédictions des deux méthodes d'extraction sur TEST.
- `data/predictions_qa.jsonl` : prédictions Q0/Q1/Q2 sur DEV puis TEST (réponses brutes conservées).
- `resultats/` : tableaux de scores et analyses manuelles (voir section 5 du livret).
- Les calculs coûteux (entraînement du modèle appris, appels LLM) ont leurs sorties sauvegardées
  dans `resultats/` pour ne pas nécessiter de ré-exécution complète.

## 8. Partitions et gel

- Extraction : partitions officielles si disponibles, sinon découpage par documents (ex. 70/15/15),
  identifiants sauvegardés — voir `manifest.json`.
- QA : DEV (20 questions) sert exclusivement au réglage (découpage, recherche, prompts).
  TEST (10 questions) est gelé le **06/11/2026** avec la configuration figée dans `manifest.json`,
  puis exécuté une seule fois sans nouveau réglage.

## 9. Calendrier du dépôt

| Date | Jalon | Archive |
|---|---|---|
| xx/xx/xx | E (extraction + négation) | `AMARA_TOMAS_E.zip` |
| xx/xx/xx | QA1 (corpus + questions + recherche sur DEV) | `AMARA_TOMAS_QA1.zip` |
| xx/xx/xx | Gel des configurations QA | — |
| xx/xx/xx | QA2 + soutenances (dépôt final) | `AMARA_TOMAS_final.zip` |
