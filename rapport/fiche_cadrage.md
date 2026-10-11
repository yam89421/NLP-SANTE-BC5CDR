# Fiche de cadrage — Projet NLP en santé

ESIEE Paris · E5-BIO · EPIGEP-BI-5-S5-UT2 · 2026/2027
**Binôme** : AMARA Yanis, TOMAS Alban

## 1. Extraction d'informations

| Élément | Choix |
|---|---|
| Corpus | BC5CDR (BioCreative V CDR), distribution `CDR.Corpus.v010516`, NCBI — résumés PubMed en anglais |
| Accès, licence | https://ftp.ncbi.nlm.nih.gov/pub/lu/BC5CDR/ — domaine public (NCBI/NLM), citation demandée |
| Catégories | **Chemical** (5 203 mentions en TRAIN) et **Disease** (4 182 mentions en TRAIN) |
| Annotations | Mentions localisées en caractères `[début, fin[` ; toutes les positions vérifiées au chargement |
| Partitions | Officielles : TRAIN / VALIDATION / TEST = 500 / 500 / 500 résumés, sans doublon |
| Méthode par règles | Dictionnaire des formes annotées de TRAIN par catégorie (casse, priorité à la mention la plus longue), regex si un motif le justifie |
| Méthode apprise | Fine-tuning de BioBERT (`dmis-lab/biobert-base-cased-v1.1`) en BIO, repris du TD NER du cours |
| Négation | 20 phrases fictives (10 niées / 10 non niées) sur des maladies et symptômes ; règles adaptées du notebook de cours, figées avant la génération |

## 2. Question answering

| Élément | Choix |
|---|---|
| Thème | Effets indésirables de la chimiothérapie et soins de support |
| Usage | « Cet outil aide **les patients traités par chimiothérapie et leurs proches** à retrouver **les effets indésirables possibles et leur prise en charge** dans **les documents d'information de l'Institut national du cancer**. » |
| Langue | Français |
| Recherche | BM25 (`rank_bm25`), top-5 passages ; Q0 / Q1 / Q2 avec un LLM préentraîné exécuté sur Colab |

**Trois sources candidates** (Institut national du cancer, texte sélectionnable) :
1. *Comprendre la chimiothérapie*, guide patients (réf. GUICHIM11, sept. 2011, PDF de 63 p.) — cancer.fr, catalogue des publications.
2. *Cancers et soins de support*, fiche Cancer info (nov. 2024, PDF de 13 p.).
3. *Les effets indésirables généraux de la chimiothérapie*, page cancer.fr (mise à jour le 28/04/2019).

Le lien avec l'extraction est thématique : BC5CDR annote des maladies provoquées par des substances, le QA porte sur les effets indésirables des traitements, vus par les patients. Les données restent séparées.

## 3. Moyens de calcul

- **Google Colab (GPU)** pour le fine-tuning de BioBERT et l'exécution du LLM ; modèles et sorties sauvegardés sur Google Drive.
- **Machine locale (CPU)** pour la lecture du corpus, le dictionnaire, les règles de négation, BM25 et les scores.

## 4. Difficultés envisagées

- **Mentions composites** (« ovarian and testicular cancer », 253 cas) : conservées comme une seule mention continue, règle identique pour les deux méthodes.
- **Résumés plus longs que 512 sous-mots** pour BERT : découpage en fenêtres, scores recalculés au niveau du document.
- **Sessions Colab limitées** : sauvegarde régulière du modèle sur Drive.
- **Ancienneté du guide 2011** : à signaler dans le catalogue, remplaçable par les pages web récentes de cancer.fr si besoin.
- **Extraction des PDF** mis en page sur deux colonnes : contrôle de l'ordre du texte sur dix passages.
- **Redistribution des documents INCa** : si elle n'est pas autorisée, rendu du catalogue et de la procédure d'accès à la place des fichiers.
