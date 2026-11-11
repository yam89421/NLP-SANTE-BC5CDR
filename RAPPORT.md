# RAPPORT — historique des configurations et des résultats

Ce fichier centralise **chaque version** des méthodes (configuration, scores, fichiers produits) pour pouvoir
restituer à la fin des résultats comparatifs. Il est mis à jour à chaque modification d'une méthode.

**Conventions**
- Chaque version a un identifiant (`DIC-v1`, `APP-v1`…) qui ne change plus une fois écrit ; une modification crée une nouvelle version.
- Scores = micro-moyenne sur les mentions (correspondance exacte des bornes et du type), calculés par `src/extraction.py`.
- Les réglages se font sur **VALIDATION** ; **TEST** n'est évalué qu'une fois, sur les versions figées, dans `5_evaluation.ipynb`.
- Temps : extraction (+ post-traitement) sur une partition de 500 documents.

---

## 1. Tableau comparatif (extraction Chemical / Disease)

| Version | Méthode | Date | P val | R val | F1 val | F1 Chemical val | F1 Disease val | Temps val | F1 TEST | Statut |
|---|---|---|---|---|---|---|---|---|---|---|
| DIC-v1 | Dictionnaire TRAIN + regex manuelles | ≤ 2026-10-11 | 0,8835 | 0,6438 | 0,7449 | 0,7715 | 0,7127 | 1,4 s | — | remplacée |
| DIC-v2 | DIC-v1 + 5 règles de post-traitement | 2026-10-16 | 0,8889 | 0,7128 | **0,7912** | 0,8289 | 0,7434 | 1,2 s | non évaluée (remplacée avant le test) | remplacée |
| DIC-v3 | DIC-v2 + filtre corrigé, variantes singulier/pluriel, extension à droite, propagation dans le document | 2026-10-30 | 0,8811 | 0,7314 | **0,7993** | 0,8333 | 0,7569 | 4,0 s | 0,7978 | remplacée par DIC-v4 (2026-11-11) |
| DIC-v4 | DIC-v3 + lexique MeSH 2026, filtré par branche et par terme sur TRAIN | 2026-11-11 | 0,9032 | 0,8669 | **0,8847** | 0,9174 | 0,8424 | 2,8 s (+ 25 s de construction) | **0,8890** | **figée (actuelle)** |
| APP-v1 | BioBERT fine-tuné (BIO) | ≤ 2026-10-11 | 0,8533 | 0,8558 | **0,8546** | 0,9128 | 0,7813 | 18,0 s (GPU T4) | non évaluée (remplacée avant le test) | remplacée |
| APP-v2 | BioBERT, 10 époques + warmup, taux 5e-5, 4 époques retenues | 2026-10-30 | 0,8886 | 0,8973 | **0,8929** | 0,9358 | 0,8392 | 18,3 s (GPU T4) | non évaluée (remplacée avant le test) | remplacée |
| APP-v3 | PubMedBERT, recette d'APP-v2, 7 époques | 2026-10-30 | 0,9042 | 0,9197 | **0,9119** | 0,9532 | 0,8598 | 16,4 s (GPU T4) | **0,8941** | **figée (actuelle)** |
| HYB-v1 | Combinaison APP-v3 + DIC-v3 (meilleure variante : ajout des mentions DIC sans chevauchement) | 2026-11-10 | 0,8894 | 0,9277 | **0,9081** | — | — | (prédictions existantes) | non évaluée (essai non retenu) | non retenue |
| HYB-v2 | Combinaison APP-v3 + DIC-v4 (meilleure variante : ajout des mentions DIC sans chevauchement) | 2026-11-11 | 0,8807 | 0,9296 | **0,9045** | — | — | (prédictions existantes) | non évaluée (essai non retenu) | non retenue |

> `resultats/extraction/comparaison_validation.csv` recalculé le 2026-10-23 avec DIC-v2 et APP-v1 (prédictions sauvegardées, sans réentraîner BioBERT). Les sorties affichées dans le notebook 2.4 montrent encore DIC-v1.

**Erreurs sur VALIDATION (9 591 mentions de référence)**

| Version | Correctes | Frontière | Type | Manquées | Parasites |
|---|---|---|---|---|---|
| DIC-v2 | 6 836 | 576 | 8 | 2 171 | 270 |
| DIC-v3 | 7 015 | 627 | 8 | 1 941 | 312 |
| DIC-v4 | 8 314 | 437 | 8 | 832 | 446 |
| APP-v1 | 8 208 | 631 | 11 | 741 | 769 |
| APP-v2 | 8 606 | 489 | 14 | 482 | 576 |
| APP-v3 | 8 821 | 432 | 4 | 334 | 499 |

**Complémentarité DIC-v2 / APP-v1** : 6 215 mentions trouvées par les deux, 1 993 par BioBERT seul, 621 par le dictionnaire seul (*toxicity, oxygen, sodium, calcium, tumor, 5-HT, Na, K…*), 762 par aucune. Rappel de l'union : 0,921 (contre 0,856 pour BioBERT seul).

**Évaluation TEST des versions figées (2026-10-30, `5_evaluation.ipynb`, évaluées une seule fois)** — `resultats/extraction/scores_test.csv`

| Méthode | Catégorie | VP | FP | FN | P | R | F1 TEST | F1 VALIDATION | Temps TEST |
|---|---|---|---|---|---|---|---|---|---|
| DIC-v3 | Chemical | 4 085 | 401 | 1 300 | 0,9106 | 0,7586 | 0,8277 | 0,8333 | |
| DIC-v3 | Disease | 3 135 | 669 | 1 289 | 0,8241 | 0,7086 | 0,7620 | 0,7569 | |
| DIC-v3 | **global** | 7 220 | 1 070 | 2 589 | 0,8709 | 0,7361 | **0,7978** | 0,7993 | 3,3 s (CPU) |
| APP-v3 | Chemical | 5 085 | 486 | 300 | 0,9128 | 0,9443 | 0,9283 | 0,9532 | |
| APP-v3 | Disease | 3 843 | 749 | 581 | 0,8369 | 0,8687 | 0,8525 | 0,8598 | |
| APP-v3 | **global** | 8 928 | 1 235 | 881 | 0,8785 | 0,9102 | **0,8941** | 0,9119 | 16,8 s (GPU T4) |

- TEST : 500 documents, 9 809 mentions. Erreurs TEST — DIC-v3 : 695 frontières, 7 types, 1 887 manquées, 368 parasites ; APP-v3 : 476 frontières, 3 types, 402 manquées, 756 parasites.
- **Écart VALIDATION → TEST** : DIC-v3 −0,0015 (stable) ; APP-v3 −0,0178, surtout en Chemical (−0,025) et par la précision (parasites 499 → 756). Le choix d'APP-v3 (modèle, époque, graine 42 au point haut) a été fait sur VALIDATION : la baisse est l'optimisme attendu de ce choix. Sur TEST, APP-v3 reste au niveau des résultats publiés (PubMedBERT ≈ 0,933 Chemical / 0,856 Disease).
- **Comparaison** : la méthode apprise dépasse le dictionnaire de 9,6 points de F1, essentiellement par le rappel (0,910 contre 0,736) ; leur précision est proche (0,879 contre 0,871). Le dictionnaire est 5 fois plus rapide et tourne sans GPU.
- `data/predictions_extraction.jsonl` : sorties TEST des deux méthodes au format du guide (2 000 lignes).

**Évaluation TEST de DIC-v4 (2026-11-11, `5_evaluation.ipynb`, tableau 1, évaluée une seule fois)** — DIC-v4 remplace DIC-v3 comme méthode par dictionnaire figée ; `scores_test.csv` et `data/predictions_extraction.jsonl` contiennent désormais DIC-v4 et APP-v3 (lignes APP-v3 inchangées).

| Méthode | Catégorie | VP | FP | FN | P | R | F1 TEST | F1 VALIDATION | Temps TEST |
|---|---|---|---|---|---|---|---|---|---|
| DIC-v4 | Chemical | 4 956 | 396 | 429 | 0,9260 | 0,9203 | 0,9232 | 0,9174 | |
| DIC-v4 | Disease | 3 649 | 549 | 775 | 0,8692 | 0,8248 | 0,8464 | 0,8424 | |
| DIC-v4 | **global** | 8 605 | 945 | 1 204 | 0,9010 | 0,8773 | **0,8890** | 0,8847 | 2,9 s (CPU) |

- Erreurs TEST DIC-v4 : 471 frontières, 2 types, 731 manquées, 472 parasites (DIC-v3 : 695 / 7 / 1 887 / 368).
- **Écart VALIDATION → TEST** : +0,0043 (stable, comme DIC-v3) : le choix de la variante sur VALIDATION n'a pas créé d'optimisme visible.
- **Comparaison** : l'écart avec la méthode apprise passe de 9,6 à **0,5 point** (0,889 contre 0,894). DIC-v4 est plus précise (0,901 contre 0,879) mais rappelle moins (0,877 contre 0,910) ; en Chemical elle fait jeu égal (0,923 contre 0,928), en Disease elle reste 0,6 point sous APP-v3 (0,846 contre 0,853). Elle reste 6 fois plus rapide et sans GPU, mais demande ≈ 1,3 Go de mémoire.
- **Prudence** : MeSH est la ressource qui sert à normaliser les annotations de BC5CDR, et des fiches supplémentaires de MeSH sont créées lors de l'indexation des articles PubMed qui citent une nouvelle substance ; la version 2026 peut donc contenir des noms introduits à partir des résumés du corpus eux-mêmes (y compris TEST). tmChem et DNorm s'appuyaient aussi sur MeSH (versions de 2013-2015).

### Comparaison avec l'état de l'art sur BC5CDR (2026-10-30)

**A. Références directement comparables : mesurées avec notre scoreur, sur notre TEST** (`resultats/extraction/scores_test_references_officielles.csv`)

Le corpus distribué (`CDR_Data/`) contient les prédictions sur TEST des deux outils de référence fournis par les organisateurs de BioCreative V : **tmChem** pour les Chemical (CRF + lexiques, Leaman et al., 2015) et **DNorm** pour les Disease (apprentissage avec normalisation, Leaman et al., 2013). Évalués exactement comme nos méthodes (document, bornes et type exacts, micro-moyenne) :

| Système (TEST) | P | R | F1 Chemical | F1 Disease | **F1 global** |
|---|---|---|---|---|---|
| DIC-v3 (dictionnaire + règles, ce projet) | 0,871 | 0,736 | 0,828 | 0,762 | **0,798** |
| DIC-v4 (DIC-v3 + lexique MeSH, ce projet, 2026-11-11) | 0,901 | 0,877 | 0,923 | 0,846 | **0,889** |
| tmChem + DNorm (outils officiels, 2013-2015) | 0,888 | 0,849 | 0,922 | 0,802 | **0,868** |
| APP-v3 (PubMedBERT, ce projet) | 0,879 | 0,910 | 0,928 | 0,853 | **0,894** |

- Notre dictionnaire reste 7 points sous les outils officiels, surtout en Chemical (0,828 contre 0,922) : tmChem s'appuie sur de grands lexiques chimiques externes et un CRF, alors que notre dictionnaire est limité aux formes de TRAIN (choix imposé par le livret, section 2.3).
- PubMedBERT dépasse les outils officiels de 2,6 points, surtout en Disease (+5,0) ; en Chemical, l'écart est faible (+0,6), tmChem étant déjà très précis (0,947).
- **Avec MeSH (DIC-v4, 2026-11-11)**, le dictionnaire dépasse les outils officiels de 2,1 points : à égalité en Chemical (0,923 contre 0,922), +4,4 points en Disease (0,846 contre 0,802), le filtrage appris sur TRAIN adaptant le lexique aux conventions de BC5CDR. L'écart de DIC-v3 venait donc bien du vocabulaire.

**B. Résultats publiés pour les modèles du type de notre méthode apprise** (F1 entité, TEST BC5CDR, autres implémentations)

| Modèle | BC5CDR Chemical | BC5CDR Disease | Les deux types (un seul modèle) | Source |
|---|---|---|---|---|
| BERT-base (domaine général) | 89,25 | 81,44 | 86,72 | Gu et al. 2021 ; Beltagy et al. 2019 |
| scispaCy `en_ner_bc5cdr_md` (CNN, spaCy) | — | — | 84,28 | doc. scispaCy |
| BioBERT (base) | 92,85 | 84,70 | 88,85 | BLURB (Gu et al. 2021) ; Beltagy et al. 2019 |
| BioBERT v1.1 (article d'origine) | 93,47 | 87,15 | — | Lee et al. 2020, tableau 6 |
| SciBERT | 92,49 | 84,54 | 90,01 | BLURB ; Beltagy et al. 2019 |
| **PubMedBERT** (même modèle qu'APP-v3) | **93,33** | **85,62** | — | BLURB (Gu et al. 2021) |
| BioLinkBERT-base / large | 93,75 / 94,04 | 86,10 / 86,39 | — | Yasunaga et al. 2022 (LinkBERT) |
| **APP-v3 (ce projet)** | **92,83** | **85,25** | **89,41** | `scores_test.csv` |

- **Même modèle (PubMedBERT)** : nous sommes à −0,5 point en Chemical et −0,4 en Disease du résultat publié. Sur le score des deux types, APP-v3 (89,4) se place entre BioBERT (88,9) et SciBERT (90,0) entraînés eux aussi sur les deux types à la fois.
- L'écart restant s'explique par le protocole plutôt que par la méthode : BLURB entraîne **un modèle par type** (BC5-chem et BC5-disease sont deux jeux distincts) et moyenne plusieurs graines, alors que nous entraînons un seul modèle pour les deux types, avec une seule graine figée (graine 42), un seul taux d'apprentissage testé, et la convention de mentions composites du 2.2 (5 mentions TEST non représentables en BIO).

**C. Repères historiques et récents** (métriques différentes : à ne pas comparer chiffre à chiffre)

| Repère | Résultat | Source |
|---|---|---|
| Compétition BioCreative V (2015), tâche DNER (maladies), meilleure équipe — CRF | F1 86,46 (P 89,63, R 83,50), **au niveau des concepts normalisés** (identifiants MeSH par document), pas des mentions ; accord inter-annotateurs 0,8875 | Wei et al. 2016 |
| Combinaison des systèmes de la compétition | F1 88,89 (DNER) | Wei et al. 2016 |
| Plus grands modèles récents (BioMegatron, SciFive, OpenMed NER 2025) | jusqu'à ≈ 96 (Chemical) / ≈ 91 (Disease), protocoles et prétraitements variables | OpenMed NER, 2025 |
| LLM sans ajustement (GPT-4, zéro / un exemple) | Chemical 0,799 / 0,833 | Chen et al. 2023-2025 |
| LLM sans ajustement (Claude 2, zéro exemple) | Chemical 58,05 ; Disease 50,13 | Jahan et al. 2024 |
| LLM ajusté (LLaMA 2 13B fine-tuné) | Chemical 0,915 | Chen et al. 2023-2025 |

- Les LLM utilisés sans ajustement restent 10 à 15 points sous un modèle BERT biomédical ajusté : notre dictionnaire construit sur TRAIN (Chemical 0,828) fait jeu égal avec GPT-4 en zéro exemple (0,799) et un exemple (0,833).

**D. Comment fonctionnent ces références**

| Famille | Systèmes | Principe | Pourquoi ce niveau |
|---|---|---|---|
| CRF + lexiques (2013-2015) | tmChem, DNorm, équipes de la compétition | Étiquetage mot par mot (comme le BIO) à partir de caractéristiques écrites à la main (mot et voisins, préfixes/suffixes, forme « 5-FU » → « 9-XX », présence dans un lexique) ; le CRF apprend leurs poids et les enchaînements d'étiquettes. tmChem : deux CRF entraînés sur CHEMDNER, caractéristiques chimiques, sigles, rattachement à MeSH/ChEBI par grands lexiques. DNorm : repérage par CRF (BANNER) puis rattachement au vocabulaire des maladies par une similarité apprise (*learning to rank*). | Très forts en Chemical grâce aux lexiques externes ; plus faibles en Disease, entraînés sur d'autres corpus et conventions que BC5CDR. |
| Transformeurs pré-entraînés puis ajustés | BioBERT, SciBERT, PubMedBERT, BioLinkBERT (et APP-v3) | 1) pré-entraînement sans étiquettes sur des millions de textes en devinant des mots masqués : le modèle apprend le sens des mots selon leur contexte ; 2) ajustement sur TRAIN avec une couche B/I/O. Différences : textes et vocabulaire du pré-entraînement (BioBERT prolonge BERT avec son vocabulaire général ; SciBERT et PubMedBERT partent de zéro avec un vocabulaire scientifique / biomédical ; BioLinkBERT apprend aussi les liens de citation). | Le pré-entraînement apporte la connaissance des mots et du contexte ; 500 résumés suffisent à apprendre les conventions de BC5CDR. Vocabulaire biomédical : « Doxorubicin-induced cardiomyopathy » = 4 sous-mots (PubMedBERT) contre 12 (BioBERT). |
| Réseau léger entraîné sur BC5CDR | scispaCy | CNN de spaCy, sans pré-entraînement massif. | Rapide mais moins précis (84,3). |
| Grands modèles de langage | GPT-4, Claude 2 (sans ajustement) ; LLaMA 2 13B (ajusté) | Sans ajustement : une consigne et 0 à quelques exemples ; le modèle génère la liste des entités, à réaligner sur le texte. Ajusté : entraîné sur TRAIN comme un BERT. | Sans ajustement, le modèle ignore les conventions d'annotation (bornes, classes de médicaments, « hepatitis B vaccine ») : ≈ 0,80 en Chemical, comme notre dictionnaire. Ajusté : 0,915, encore sous PubMedBERT pour un modèle 100 fois plus gros. |

Notre projet couvre les deux extrêmes : DIC-v3 reprend le principe « lexique + règles » de 2015 sans CRF ni lexique externe ; APP-v3 suit la recette standard actuelle (BLURB), d'où des scores proches des publications.

**Conclusion** : APP-v3 atteint le niveau publié pour son modèle (à moins d'un point) avec un protocole plus contraint (un seul modèle, une graine, réglage limité) ; DIC-v3 se situe sous les outils officiels de 2015, l'écart venant du vocabulaire (formes absentes de TRAIN), que le livret ne permet pas de compléter par un lexique externe.

**Mise à jour (2026-11-11)** : l'ajout du lexique MeSH ayant été validé par l'enseignant, DIC-v4 (0,889) dépasse les outils officiels (0,868) et arrive à 0,5 point d'APP-v3 (0,894).

**Sources** : [Wei et al. 2016, *Database*, overview BioCreative V CDR](https://academic.oup.com/database/article/doi/10.1093/database/baw032/2630271) ; [Li et al. 2016, corpus BC5CDR](https://academic.oup.com/database/article/doi/10.1093/database/baw068/2630414) ; `CDR_Data/README.txt` (tmChem, DNorm) ; [Lee et al. 2020, BioBERT, *Bioinformatics*](https://pmc.ncbi.nlm.nih.gov/articles/PMC7703786/) ; [Gu et al. 2021, PubMedBERT / BLURB](https://arxiv.org/pdf/2007.15779) ; [classement BLURB](https://microsoft.github.io/BLURB/tasks.html) ; [Beltagy et al. 2019, SciBERT](https://arxiv.org/pdf/1903.10676) ; [Yasunaga et al. 2022, LinkBERT](https://aclanthology.org/2022.acl-long.551.pdf) ; [scispaCy](https://allenai.github.io/scispacy/) ; [OpenMed NER 2025](https://arxiv.org/html/2508.01630v1) ; [Chen et al., benchmark des LLM en TAL biomédical](https://pmc.ncbi.nlm.nih.gov/articles/PMC12478438/) ; [Jahan et al. 2024, *Computers in Biology and Medicine*](https://www.sciencedirect.com/science/article/pii/S0010482524002737).

---

## 2. Données

Corpus **BC5CDR** (PubTator, `CDR_Data/CDR.Corpus.v010516`), catégories Chemical et Disease, partitions officielles.

| Partition | Documents | Chemical | Disease | Mentions | Formes distinctes | Composites | Phrases | Phrases sans mention |
|---|---|---|---|---|---|---|---|---|
| train | 500 | 5 203 | 4 182 | 9 385 | 2 391 | 107 | 4 580 | 773 |
| validation | 500 | 5 347 | 4 244 | 9 591 | 2 239 | 89 | 4 592 | 787 |
| test | 500 | 5 385 | 4 424 | 9 809 | 2 355 | 57 | 4 821 | 837 |

Conversion BIO (`resultats/extraction/bilan_bio.csv`) : 10 mentions perdues à l'aller-retour en VALIDATION et 5 en TEST (bornes hors frontière de token), 0 en TRAIN.

**Exports lisibles (2026-10-16)**
- `data/corpus_extraction.csv` : une ligne par mention (document, partition, titre/résumé, type, mention, contexte ±50 caractères avec la mention entre `[ ]`, positions, identifiants MeSH, composite).
- `data/bio_extraction.csv` : une ligne par token (document, partition, position, token, étiquette BIO, positions).

---

## 3. Méthode par dictionnaire et règles (notebook `2.3_dictionnaire_regles.ipynb`)

### DIC-v1 — dictionnaire seul

- Dictionnaire construit sur les mentions de TRAIN (une forme → son type majoritaire), plus longue correspondance, sans chevauchement.
- **Réglage sur VALIDATION** (16 combinaisons, `dictionnaire_reglage_validation.csv`) :
  - casse : `exacte` / `insensible` ;
  - seuil de **taux d'annotation** (part des occurrences d'une forme dans TRAIN qui sont annotées) : 0 / 0,3 / 0,5 / 0,7 ;
  - regex de suffixes écrites à la main (Chemical : *-mycin, -olol, -pril…* ; Disease : *-itis, -emia, -pathy…*) : oui / non.
- **Configuration retenue** : casse insensible, seuil 0,3, regex oui → 2 348 entrées.

| Casse | Seuil | Regex | F1 val |
|---|---|---|---|
| insensible | 0,3 | oui | **0,7449** |
| insensible | 0,5 | oui | 0,7397 |
| exacte | 0 | oui | 0,7335 |
| insensible | 0 | oui | 0,6969 |
| insensible | 0 | non | 0,6802 |

Erreurs sur VALIDATION : 6 175 correctes, 578 erreurs de frontière, 13 de type, 2 825 manquées (2 808 absentes du dictionnaire), 223 fausses détections.

### Analyse du taux d'annotation (2026-10-16)

- Le filtre retire 42 entrées, évite 1 388 fausses détections et perd 128 bonnes détections (+4,8 points de F1 en casse insensible, aucun gain en casse exacte).
- **Il corrige surtout l'insensibilité à la casse** : 5 formes courtes (`mg`, `be`, `all`, `can`, `h`, c.-à-d. Mg, Be, ALL…) expliquent 85 % du gain. Un seuil de 0,05 suffit pour 0,738.
- **Biais de calcul** : une forme contenue dans une mention plus longue (« infarction » dans « myocardial infarction ») est comptée comme non annotée. 190 formes concernées ; 27 entrées sont retirées à tort au seuil 0,3 (infarction, cancer, neuropathy, edema…).
- Pistes testées, **non intégrées** (à arbitrer) :

| Variante (avec regex manuelles) | F1 val |
|---|---|
| Taux actuel, seuil 0,3 (DIC-v1) | 0,7449 |
| Taux corrigé (sans les occurrences imbriquées), seuil 0,3 | 0,7485 |
| Casse exacte pour les tokens ≤ 3 caractères, insensible sinon, sans filtre | 0,7470 |
| Seuil appliqué seulement aux formes vues ≥ 5 fois | 0,7459 |

### DIC-v2 — dictionnaire + règles de post-traitement (2026-10-16)

Cinq règles appliquées après DIC-v1, dans cet ordre (code dans le notebook, `src/` inchangé) :

| # | Règle | Construction | F1 val (règle seule) |
|---|---|---|---|
| — | aucune (DIC-v1) | — | 0,7449 |
| 1 | **Suffixes appris** : 81 suffixes Chemical (*-dipine, -anyl, -olam…*), 27 Disease (*-lemia, -bosis, -zure…*) | TRAIN : ≥ 8 occurrences, ≥ 80 % annotées du même type | 0,7610 |
| 2 | **Modificateurs à gauche** : 49 mots (*muscle, tardive, myocardial, postoperative…*) qui étendent une maladie vers la gauche | TRAIN : ≥ 3 fois et ≥ 70 % inclus dans l'annotation | 0,7504 |
| 3 | **« X-induced » / « induced by X »** → X Chemical, sauf mots génériques et adjectifs | TRAIN (82 % de Chemical) ; liste d'exclusion ajustée sur VALIDATION | 0,7479 |
| 4 | **Sigles définis** « forme longue (SIGLE) » : le sigle prend le type de la forme longue dans le document ; sinon il est retiré (sauf s'il est dans le dictionnaire) | Schwartz & Hearst (2003) ; condition de retrait ajustée sur VALIDATION | 0,7653 |
| 5 | **Préfixe anti-** : retrait des prédictions commençant par « anti » | TRAIN : mots en *anti-* presque jamais annotés | 0,7456 |
| | **Toutes, dans l'ordre** | | **0,7912** |

- Erreurs VALIDATION après règles : 6 836 correctes (+661), 576 frontière, 8 type, 2 171 manquées (−654), 270 fausses détections (+47).
- Le score VALIDATION est **légèrement optimiste** (deux réglages ajustés en regardant VALIDATION) : seul TEST juge.
- Erreurs restantes : médicaments sans suffixe reconnaissable (*lead, ammonia*), sigles jamais définis, maladies de plusieurs mots inconnues.

**Idées testées et abandonnées**

| Idée | Résultat |
|---|---|
| Regex générique pour les sigles en capitales `[A-Z]{2,6}` | 36 % de précision sur TRAIN (II, CI, HIV, DNA…) |
| Deux lettres « Xx » hors début de phrase | 29 % de précision sur TRAIN (To, We, In, Hg de « mm Hg ») |
| Liste de symboles chimiques (Na, K, Ca, Li, Mg…) | aucun gain : déjà dans le dictionnaire |

**Fichiers (version figée DIC-v2)** — `resultats/extraction/` : `dictionnaire_config_gelee.json` (configuration, règles apprises, temps), `dictionnaire.tsv`, `regles_effet_validation.csv`, `scores_dictionnaire_validation.csv`, `predictions_dictionnaire_validation.jsonl`, `predictions_dictionnaire_test.jsonl` (7 995 prédictions).

### DIC-v3 — variantes et priorités supplémentaires (2026-10-30, notebook `2.3b_dictionnaire_regles_v3.ipynb`)

- **Point de départ** : DIC-v2 reconstruite dans le notebook et vérifiée à l'identique (mêmes 7 690 prédictions VALIDATION). Le notebook 2.3 n'est pas modifié.
- **Analyse de départ (erreurs DIC-v2 sur VALIDATION)** : 2 171 manquées, dont 827 mots et 764 expressions jamais vus dans TRAIN (hors de portée d'un dictionnaire construit sur TRAIN), 338 sigles, 106 formes retirées à tort par le filtre, 54 variantes singulier/pluriel, 88 formes reconnues ailleurs dans le même résumé ; 576 frontières, dont 514 mentions prédites trop courtes.
- **Livret (section 2.3)** : dictionnaire construit à partir des formes annotées de TRAIN, choix de casse, de variantes et de priorité, regex si un motif le justifie. Un lexique externe (MeSH) a été écarté : hors du cadre décrit.
- **Quatre ajouts**, appris sur TRAIN (seuils de C repris de la règle des modificateurs à gauche, sans nouveau réglage) :

| Ajout | P | R | F1 val | Ajouts justes / faux | Effet |
|---|---|---|---|---|---|
| DIC-v2 | 0,8889 | 0,7128 | 0,7912 | — | — |
| A — filtre corrigé (occurrences incluses dans une mention plus longue ignorées) | 0,8841 | 0,7214 | 0,7945 | 83 / 57 | +27 entrées : *cancer, edema, infection, hemorrhage, atrophy…* |
| B — variantes singulier/pluriel absentes des textes de TRAIN | 0,8883 | 0,7180 | 0,7941 | 51 / 16 | 1 928 variantes : *movement disorders, visual disturbances…* |
| C — extension à droite (suites de 1 à 3 mots, ≥ 3 fois, ≥ 70 %) | 0,8892 | 0,7130 | 0,7914 | 2 / 2 | seulement 2 suites apprises (*methyl ester*, *C* de *hepatitis C*) : effet nul |
| D — propagation d'une forme retenue à ses autres occurrences dans le résumé (même casse) | 0,8866 | 0,7174 | 0,7931 | 45 / 26 | *dilevalol, ATRA, tiapride, ethambutol…* ; faux : *lesion, carbonate* |
| **A + B + C + D (DIC-v3)** | **0,8811** | **0,7314** | **0,7993** | 180 / 101 | |

- **Règle de choix** (écrite dans le notebook) : un ajout est gardé s'il améliore seul le F1 VALIDATION ; les quatre le font. C est gardé par application de la règle, mais son effet est nul (2 justes, 2 faux).
- **Bilan** : +0,8 point de F1 (Chemical 0,8289 → 0,8333, Disease 0,7434 → 0,7569) ; manquées 2 171 → 1 941, mais frontières 576 → 627 et parasites 270 → 312 (le filtre corrigé réintroduit *infection, cancer* aussi là où ils font partie d'une mention plus longue). Gain inférieur à l'estimation initiale (+2 à 3 points) : les frontières trop courtes viennent surtout de formes longues absentes de TRAIN (*migraine with aura*), que l'extension apprise ne couvre pas.
- **Limite principale** : 1 591 mentions manquées restent des formes jamais vues dans TRAIN ; c'est là que la méthode apprise (APP-v3, F1 0,912) fait la différence.
- Score VALIDATION légèrement optimiste (réglages de DIC-v2 et choix des ajouts faits sur VALIDATION) : seul TEST juge.
- Fichiers : `dictionnaire_v3_effet_validation.csv`, `scores_dictionnaire_v3_validation.csv`, `predictions_dictionnaire_v3_validation.jsonl`, `predictions_dictionnaire_v3_test.jsonl` (8 290 prédictions), `dictionnaire_v3_config_gelee.json`. Exécuté sur le serveur (CPU), environnement `~/venvs/nlp` (pandas 3.1, numpy 2.5).

### DIC-v4 — DIC-v3 + lexique MeSH (2026-11-11, notebook `2.3c_dictionnaire_mesh_v4.ipynb`, code `src/mesh.py` et `src/dictionnaire_v4.py`)

- **Motivation** : l'écart de DIC-v3 aux outils officiels (tmChem + DNorm, 0,868 sur TEST) venait surtout du vocabulaire (≈ 1 600 mentions manquées en VALIDATION ont une forme absente de TRAIN), ces outils s'appuyant sur de grands lexiques. L'enseignant a validé l'ajout d'un lexique externe (le choix « pas de MeSH » de DIC-v3 est donc levé pour cette version).
- **Point de départ** : DIC-v3 reconstruite dans le notebook et vérifiée à l'identique (7 962 prédictions VALIDATION). Le notebook 2.3b n'est pas modifié.
- **Lexique** : MeSH 2026 (NLM, fichiers XML `desc2026.gz` et `supp2026.zip`, ≈ 64 Mo, téléchargés automatiquement dans `data/mesh/`, non versionnés), réduit à 841 445 termes (`data/mesh/lexique_mesh_2026.tsv.gz`) :
  - descripteurs des arbres C et F03 → Disease (60 672 termes), D → Chemical (95 061) ;
  - concepts supplémentaires, classe 1 substances → Chemical (666 305), classe 3 maladies rares → Disease (19 407) ;
  - tous les synonymes ; un terme inversé (« Infarction, Myocardial ») est aussi ajouté à l'endroit ;
  - chaque terme garde ses branches (numéro d'arbre coupé au 2e niveau, ex. D12.776 protéines ; un concept supplémentaire prend les branches des descripteurs auxquels il est rattaché).
- **Intégration au dictionnaire** (tout appris sur TRAIN, seuils repris de DIC-v3, sans nouveau réglage) :
  1. priorité à TRAIN : une forme annotée dans TRAIN garde la décision de DIC-v3 (type, ou retrait par le filtre) ;
  2. termes de moins de 3 caractères, plus longs que la plus longue entrée de DIC-v3, ou classés à la fois Chemical et Disease : ignorés (aucun cas ambigu) ;
  3. **filtre par branche** : tous les termes MeSH sont cherchés dans les textes de TRAIN ; une branche vue ≥ 5 fois et annotée < 30 % du temps est écartée avec tous ses termes → 29 branches sur 275, dont D27.505 classes pharmacologiques (*analgesic, adrenergic* : 17 %), D12.776 protéines (11 %), D26 préparations (*drug, solution* : 0 %), D08.811 enzymes (0 %) ;
  4. **filtre par terme** : un terme MeSH trouvé dans TRAIN mais annoté < 30 % du temps est retiré (148 termes) ;
  5. les règles de DIC-v3 s'appliquent ensuite sans changement sur le dictionnaire élargi (443 740 termes MeSH ajoutés, 448 043 entrées au total).
- **Variantes comparées sur VALIDATION** (`dictionnaire_v4_effet_validation.csv`) ; règle de choix écrite dans le notebook : meilleur F1 VALIDATION.

| Variante | P | R | F1 val | F1 Chemical | F1 Disease | Termes MeSH ajoutés | Frontière | Manquées | Parasites |
|---|---|---|---|---|---|---|---|---|---|
| DIC-v3 | 0,8811 | 0,7314 | 0,7993 | 0,8333 | 0,7569 | 0 | 627 | 1 941 | 312 |
| MeSH sans filtre | 0,7733 | 0,8598 | 0,8142 | 0,8054 | 0,8268 | 824 542 | 643 | 698 | 1 771 |
| MeSH + filtre par terme | 0,8580 | 0,8633 | 0,8607 | 0,8740 | 0,8426 | 823 925 | 506 | 801 | 860 |
| + filtre par branche, niveau 1 (« D12 ») | 0,8823 | 0,8627 | 0,8724 | 0,8954 | 0,8421 | 692 858 | 465 | 842 | 629 |
| **+ filtre par branche, niveau 2 (« D12.776 ») = DIC-v4** | **0,9032** | **0,8669** | **0,8847** | **0,9174** | **0,8424** | 443 740 | 437 | 832 | 446 |
| niveau 2, descripteurs seuls | 0,9017 | 0,8458 | 0,8729 | 0,8984 | 0,8405 | 93 209 | 462 | 1 009 | 414 |

- **Scores VALIDATION de DIC-v4** (`scores_dictionnaire_v4_validation.csv`) :

| Catégorie | VP | FP | FN | P | R | F1 | DIC-v3 F1 | Gain |
|---|---|---|---|---|---|---|---|---|
| Chemical | 4 862 | 391 | 485 | 0,9256 | 0,9093 | **0,9174** | 0,8333 | +8,4 pts |
| Disease | 3 452 | 500 | 792 | 0,8735 | 0,8134 | **0,8424** | 0,7569 | +8,6 pts |
| Global (micro) | 8 314 | 891 | 1 277 | 0,9032 | 0,8669 | **0,8847** | 0,7993 | **+8,5 pts** |

- **Erreurs** : manquées 1 941 → 832, frontières 627 → 437, parasites 312 → 446, types 8 → 8. Par rapport à DIC-v3 : 1 345 mentions justes ajoutées (*iohexol, remifentanil, ammonia, torsade de pointes, optic neuropathy, vitamin C, uric acid…*), 270 fausses (*PTH, gellan, glucagon, surface antigen, essential hypertension…*), 46 perdues (*hypertension, seizures* absorbées dans une forme MeSH plus longue).
- **Lecture** : le filtre sur TRAIN est indispensable (sans lui, *drug, disease, protein* font chuter la précision à 0,77) ; le filtre par branche au 2e niveau fait passer la précision au-dessus de DIC-v3 (0,903 contre 0,881) tout en doublant presque le gain de rappel. Les concepts supplémentaires (noms de molécules rares, codes comme *SM-5887, CB 3717*) apportent +1,2 point par rapport aux descripteurs seuls.
- **Position** : le F1 VALIDATION de DIC-v4 (0,885) dépasse celui des outils officiels mesurés sur TEST (0,868) et se rapproche d'APP-v2 (0,893) ; il reste 2,7 points sous APP-v3 (0,912). Comparaison indicative à ce stade (TEST : voir ci-dessous).
- Score VALIDATION légèrement optimiste (choix de la variante sur VALIDATION parmi 5) : seul TEST juge.
- **TEST (2026-11-11, notebook 5, une seule évaluation)** : F1 **0,8890** (Chemical 0,9232, Disease 0,8464), écart VALIDATION → TEST +0,004 ; DIC-v4 remplace DIC-v3 comme version figée. Détail et précautions : section 1.
- **Coût** : construction ≈ 25 s (lecture du lexique en cache + filtres sur TRAIN ; première fois : + 1 min de téléchargement et de lecture des XML), extraction 2,8 s par partition (CPU) ; pic mémoire ≈ 1,3 Go à la construction.
- Fichiers : `dictionnaire_v4_termes_mesh.tsv.gz` (443 740 termes MeSH retenus, 3 Mo : DIC-v4 = DIC-v3 + ces termes, utilisé par l'application ; reconstruction vérifiée à l'identique sur TEST), `dictionnaire_v4_effet_validation.csv`, `scores_dictionnaire_v4_validation.csv`, `predictions_dictionnaire_v4_validation.jsonl`, `predictions_dictionnaire_v4_test.jsonl` (9 550 prédictions), `dictionnaire_v4_config_gelee.json`. Exécuté avec le venv du TD.

---

## 4. Méthode apprise (notebook `2.4_methode_apprise.ipynb`)

### APP-v1 — BioBERT

- Modèle `dmis-lab/biobert-base-cased-v1.1`, étiquetage BIO, premier sous-mot supervisé, fenêtres = phrases entières, décodage « réparer », seed 42, GPU Tesla T4.
- Paramètres du TD : lr 2e-5, batch 8, weight decay 0,01, max_length 512.
- **Réglage sur VALIDATION** (`apprise_reglage_validation.csv`) :

| Poids des entités | Époques | P | R | F1 val |
|---|---|---|---|---|
| 1 | 2 | 0,8533 | 0,8558 | **0,8546** |
| 1 | 3 | 0,8263 | 0,8826 | 0,8535 |
| 10 | 2 | 0,7182 | 0,8956 | 0,7971 |
| 1 | 1 | 0,6849 | 0,8004 | 0,7382 |

- **Configuration retenue** : poids 1, 2 époques. Entraînement 84,6 s, prédiction 18 s par partition.
- Fichiers : `apprise_config_gelee.json`, `scores_apprise_validation.csv`, `predictions_apprise_validation.jsonl`, `predictions_apprise_test.jsonl`.

### APP-v2 — BioBERT mieux entraîné (2026-10-30, notebook `2.4b_methode_apprise_v2.ipynb`, Colab GPU T4)

- **Diagnostic d'APP-v1** : 70 étapes par époque (560 fenêtres, lots de 8), soit 140 étapes pour la configuration retenue ; F1 encore en forte hausse d'une époque à l'autre (0,74 → 0,85) ; le point « 2 époques » était l'étape intermédiaire d'un entraînement prévu pour 3. Hypothèse : sous-entraînement.
- **Configuration testée** : même modèle, données, fenêtres et décodage ; 10 époques évaluées une à une sur VALIDATION ; warmup 10 % puis décroissance linéaire ; taux 3e-5 et 5e-5 ; graines 42 et 43 ; poids 1.
- **Règle de choix fixée avant exécution** : meilleure moyenne de F1 VALIDATION sur les deux graines ; à moins de 0,005 de la meilleure, le moins d'époques ; modèle figé = graine 42.

F1 VALIDATION global, moyenne des deux graines (`apprise_v2_reglage_validation.csv`) :

| Époques | 1 | 2 | 3 | **4** | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| taux 3e-5 | 0,747 | 0,867 | 0,878 | 0,881 | 0,884 | 0,882 | 0,887 | 0,885 | 0,889 | 0,887 |
| taux 5e-5 | 0,835 | 0,879 | 0,883 | **0,892** | 0,892 | 0,890 | 0,893 | 0,895 | 0,895 | **0,896** |

- **Retenu** : taux 5e-5, **4 époques** (moyenne 0,892, à 0,004 du meilleur 0,8956 à 10 époques) ; écart entre graines ≤ 0,01 → les différences au-delà de 4 époques sont de l'ordre du bruit.
- **Scores VALIDATION du modèle figé** (graine 42, `scores_apprise_v2_validation.csv`) :

| Catégorie | P | R | F1 | APP-v1 F1 | Gain |
|---|---|---|---|---|---|
| Chemical | 0,9331 | 0,9385 | **0,9358** | 0,9128 | +2,3 pts |
| Disease | 0,8331 | 0,8454 | **0,8392** | 0,7813 | **+5,8 pts** |
| Global (micro) | 0,8886 | 0,8973 | **0,8929** | 0,8546 | +3,8 pts |

- **Erreurs** : frontières 631 → 489, manquées 741 → 482, parasites 769 → 576, types 11 → 14. Le diagnostic est confirmé : le gain venait de l'entraînement, surtout pour Disease.
- **Coût** : entraînement 10 époques ≈ 3 à 4 min par run (4 runs), prédiction 18 s par partition.
- **Écart restant** aux résultats publiés de BioBERT (≈ 0,93 / 0,85 sur TEST, protocole différent) : de l'ordre de 1 point → changer de modèle (APP-v3) ne peut plus apporter qu'un gain limité.
- Fichiers : `apprise_v2_config_gelee.json`, `apprise_v2_reglage_validation.csv`, `apprise_v2_historique_entrainement.json`, `scores_apprise_v2_validation.csv`, `apprise_v2_comparaison_v1_validation.csv`, `predictions_apprise_v2_validation.jsonl`, `predictions_apprise_v2_test.jsonl` ; modèle `modeles/biobert_v2` (non versionné). Versions : torch 2.11.0, transformers 5.20.2.

### APP-v3 — autre modèle pré-entraîné, même recette (2026-10-30, notebook `2.4c_methode_apprise_v3.ipynb`, Colab GPU T4)

- **Question** : avec la recette d'APP-v2, un modèle plus spécialisé fait-il mieux que BioBERT ? Seul le modèle change.
- **Modèles** : `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext` (PubMedBERT) et `michiyasunaga/BioLinkBERT-base` ; architecture BERT, `BertTokenizer` en minuscules. Leur vocabulaire, appris sur PubMed, découpe beaucoup moins les termes biomédicaux : « Doxorubicin-induced cardiomyopathy » → 4 sous-mots (BioBERT : 12) ; d'où moins de fenêtres (518 en TRAIN contre 560).
- **Recette** (identique à APP-v2) : taux 5e-5, warmup 10 %, 10 époques évaluées une à une sur VALIDATION, graines 42 et 43, poids 1. Référence BioBERT : runs APP-v2 au taux 5e-5.
- **Règles fixées avant exécution** : époques choisies comme en APP-v2 ; remplacement d'APP-v2 si gain moyen > 0,005.

F1 VALIDATION global, moyenne des deux graines (`apprise_v3_reglage_validation.csv`) :

| Époques | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| BioBERT (APP-v2) | 0,835 | 0,879 | 0,883 | **0,892** | 0,892 | 0,890 | 0,893 | 0,895 | 0,895 | 0,896 |
| BioLinkBERT-base | 0,793 | 0,881 | 0,894 | 0,901 | **0,906** | 0,906 | 0,902 | 0,908 | 0,906 | 0,907 |
| PubMedBERT | 0,795 | 0,875 | 0,892 | 0,898 | 0,902 | 0,905 | **0,911** | 0,908 | 0,909 | 0,910 |

| Modèle (époques retenues) | F1 moyen | F1 Chemical | F1 Disease | Écart à BioBERT |
|---|---|---|---|---|
| BioBERT (4) | 0,892 | 0,935 | 0,838 | — |
| BioLinkBERT-base (5) | 0,906 | 0,948 | 0,851 | +0,014 |
| **PubMedBERT (7)** | **0,911** | **0,951** | **0,861** | **+0,019** |

- **Retenu : PubMedBERT, 7 époques** (gain +0,019 > 0,005 → remplace APP-v2). À partir de 3 époques, les deux nouveaux modèles dépassent BioBERT à chaque époque : le gain ne dépend pas du point choisi. L'écart PubMedBERT / BioLinkBERT (0,006) est en revanche proche de la variation entre graines : les deux se valent presque.
- **Scores VALIDATION du modèle figé** (graine 42, `scores_apprise_v3_validation.csv`) :

| Catégorie | P | R | F1 | APP-v2 F1 | Gain |
|---|---|---|---|---|---|
| Chemical | 0,9450 | 0,9615 | **0,9532** | 0,9358 | +1,7 pts |
| Disease | 0,8526 | 0,8671 | **0,8598** | 0,8392 | +2,1 pts |
| Global (micro) | 0,9042 | 0,9197 | **0,9119** | 0,8929 | +1,9 pts |

- **Erreurs** : frontières 489 → 432, types 14 → 4, manquées 482 → 334, parasites 576 → 499.
- **Erreurs commentées** (`erreurs_commentees.md`, réécrit pour APP-v3 ; l'analyse d'APP-v1 est conservée dans `erreurs_commentees_APP-v1.md`) : Disease concentre les erreurs (343 frontières, 218 manquées, 300 parasites) ; 251 manquées sur 334 ont une forme absente de TRAIN. Cinq cas : expression descriptive coupée (*deterioration of vision* → *of vision*), coordination et contexte de vaccination (*hepatitis B and rubella*, *hepatitis B vaccine*), sigle défini jamais annoté dans TRAIN (*COCs*, retrouvé par le dictionnaire), symptôme d'expérimentation inconnu (*contralateral rotation*), annotation irrégulière (*antidepressant* : 15/15 annoté en TRAIN, 0/15 en VALIDATION). Rappel de l'union APP-v3 + dictionnaire : 0,944 (APP-v3 seul 0,920).
- **Prudence** : la graine 42 à 7 époques est un point haut (0,9119 contre 0,9105 pour la graine 43, 0,9090 à 10 époques) ; le score TEST jugera. Seul le taux 5e-5 a été testé pour les nouveaux modèles.
- **Coût** : entraînement 10 époques ≈ 3 à 4,5 min par run (4 runs), prédiction 16 s par partition.
- Fichiers : `apprise_v3_config_gelee.json`, `apprise_v3_reglage_validation.csv`, `apprise_v3_historique_entrainement.json`, `scores_apprise_v3_validation.csv`, `apprise_v3_comparaison_v2_validation.csv`, `predictions_apprise_v3_validation.jsonl`, `predictions_apprise_v3_test.jsonl` ; modèle `modeles/apprise_v3` sur le Drive (non rapatrié, non versionné).

### HYB-v1 — essai de combinaison dictionnaire + modèle appris (2026-11-10, script `figures_oral/generer_figures.py`, figure 14) — non retenu

Combinaison des prédictions VALIDATION déjà sauvegardées de DIC-v3 et APP-v3, sans réentraînement ni nouveau réglage.

| VALIDATION (9 591 mentions) | P | R | F1 | VP | FP | FN |
|---|---|---|---|---|---|---|
| DIC-v3 | 0,8811 | 0,7314 | 0,7993 | 7 015 | 947 | 2 576 |
| APP-v3 | 0,9042 | 0,9197 | **0,9119** | 8 821 | 935 | 770 |
| Intersection (mention gardée si prédite par les deux) | 0,9714 | 0,7060 | 0,8177 | 6 771 | 199 | 2 820 |
| Union (prédite par l'une ou l'autre) | 0,8434 | 0,9452 | 0,8914 | 9 065 | 1 683 | 526 |
| APP-v3 + mentions DIC qui ne chevauchent aucune mention APP (249 ajouts, dont 77 justes) | 0,8894 | 0,9277 | 0,9081 | 8 898 | 1 107 | 693 |

- **Complémentarité** des deux méthodes sur les mentions de référence : 6 771 trouvées par les deux (70,6 %), 2 050 par APP-v3 seulement (21,4 %), 244 par DIC-v3 seulement (2,5 %), 526 par aucune (5,5 %).
- **Conclusion** : aucune combinaison ne dépasse APP-v3 seul. Le dictionnaire n'apporte presque aucune entité que le modèle ne trouve déjà, et chaque ajout coûte plus de faux positifs qu'il n'apporte de vrais. APP-v3 reste la méthode apprise figée ; pas de méthode hybride.
- Écart mineur : le rappel de l'union vaut ici 0,9452, contre 0,944 dans les erreurs commentées d'APP-v3 (calcul antérieur).
- Fichiers : aucun fichier de résultats ; scores affichés par `figures_oral/generer_figures.py` et figure `figures_oral/14_pourquoi_pas_hybride_extraction.png`.

### HYB-v2 — combinaison avec DIC-v4 (2026-11-11, script `figures_oral/generer_figures.py`, figure 14) — non retenu

Même essai que HYB-v1 avec la nouvelle version figée du dictionnaire (DIC-v4), sur les prédictions VALIDATION sauvegardées, sans réentraînement ni réglage.

| VALIDATION (9 591 mentions) | P | R | F1 | VP | FP | FN |
|---|---|---|---|---|---|---|
| DIC-v4 | 0,9032 | 0,8669 | 0,8847 | 8 314 | 891 | 1 277 |
| APP-v3 | 0,9042 | 0,9197 | **0,9119** | 8 821 | 935 | 770 |
| Intersection | 0,9707 | 0,8333 | 0,8968 | 7 992 | 241 | 1 599 |
| Union | 0,8523 | 0,9533 | 0,8999 | 9 143 | 1 585 | 448 |
| APP-v3 + mentions DIC sans chevauchement (368 ajouts, dont 95 justes) | 0,8807 | 0,9296 | 0,9045 | 8 916 | 1 208 | 675 |

- **Complémentarité** : 7 992 mentions trouvées par les deux (83,3 %), 829 par APP-v3 seulement (8,6 %), 322 par DIC-v4 seulement (3,4 %), 448 par aucune (4,7 %).
- **Conclusion** : malgré un dictionnaire bien plus fort (0,885 contre 0,799), aucune combinaison ne dépasse APP-v3 seul ; les deux méthodes trouvent désormais en grande partie les mêmes entités, et les ajouts du dictionnaire apportent plus de faux positifs que de vrais. Pas de méthode hybride.
- Fichiers : aucun fichier de résultats ; scores affichés par `figures_oral/generer_figures.py`, figure `figures_oral/14_pourquoi_pas_hybride_extraction.png` (désormais calculée avec DIC-v4).

---

## 5. Négation (notebook `2.5_negation.ipynb`)

### NEG-v0 — règles de négation (`resultats/negation/regles_v0.json`)

- 20 phrases générées (Claude, 07/10/2026) en 10 familles (négation simple, coordination, « cannot be excluded », pseudo-négation, double négation…), réparties dev / test par famille.
- Score TEST **provisoire** (référence = labels de génération, double annotation en cours) : F1 « nié » 0,80, F1 « non nié » 0,80, moyenne 0,80 (matrice 4/1/1/4).
- À faire : compléter `annotation_AMARA.csv` / `annotation_TOMAS.csv`, calculer le kappa et remplacer le score provisoire.

### Double annotation (2026-11-06, notebook `2.5_negation.ipynb`)

- Les deux feuilles sont complètes (`annotation_AMARA.csv`, `annotation_TOMAS.csv`, 20 mentions chacune). **Accord observé 0,75, kappa de Cohen 0,51** (accord modéré) ; 5 désaccords : NEG007, NEG008 (liste « no rash, jaundice or edema, and … »), NEG010 (« was confirmed »), NEG013 (« no increase in »), NEG018 (« no evidence of »). Les 15 accords sont tous égaux aux labels de génération.
- Désaccords recopiés dans `resultats/negation/desaccords_annotation.csv` ; `label_final` et `resolution` sont à remplir ensemble. Tant qu'ils sont vides, la référence reste provisoire (labels de génération) et les scores NEG-v0 ci-dessus ne changent pas (matrice et scores régénérés à l'identique).

### NEG-v0 — score TEST sur la référence finale (2026-11-06, notebooks `2.5_negation.ipynb` et `5_evaluation.ipynb`)

- **Résolution des désaccords** (ensemble, `desaccords_annotation.csv`) : NEG007 `nie` (négation prolongée par « or »), NEG008 `non_nie` (portée fermée par « and »), NEG010 `non_nie` (aucune négation), NEG013 `non_nie` (c'est la hausse qui est niée), NEG018 `nie` (« no evidence of »). Guide d'annotation inchangé.
- **Référence finale** = accords + décisions ci-dessus ; elle est identique aux labels de génération pour les 20 mentions (10 dev, 10 test, 5 de chaque label dans chaque ensemble).
- **Score TEST final** des règles NEG-v0 (inchangées) : matrice 4 / 1 / 1 / 4 ; P = R = F1 = 0,80 pour « nié » et pour « non nié » ; moyenne des deux F1 = **0,80** ; développement : 10/10. Les erreurs commentées (NEG015 double négation, NEG019 portée longue) restent valables.
- Fichiers : `resultats/negation/scores_par_classe.csv` (colonne `reference_provisoire` = False), `matrice_confusion.csv` et `predictions_test.csv` identiques ; `erreurs_commentees.md` et le tableau 2 du notebook 5 mis à jour.

---

## 6. Question-réponse (notebooks 3, 4.1, 4.2)

Cadrage : effets indésirables de la chimiothérapie / soins de support, documents INCa (`rapport/cadrage_qa.md`). Objectif : 20 questions DEV et 10 TEST.

**Corpus documentaire (2026-10-23) : 3 → 10 documents INCa** (`data/corpus.csv`, fichiers dans `data/sources_qa/`)

| ID | Document | Mise à jour | Mots (≈) |
|---|---|---|---|
| DOC001 | Comprendre la chimiothérapie (guide PDF) | 2011-09 | — |
| DOC002 | Cancers et soins de support (fiche PDF) | 2024-11 | — |
| DOC003 | Les effets indésirables généraux de la chimiothérapie | 2019-04-28 | — |
| DOC004 | Pourquoi les traitements font tomber les cheveux et les poils ? | 2024-07-01 | 1 000 |
| DOC005 | Douleurs et traitements | 2015-05-26 | 1 500 |
| DOC006 | La prise en charge de la fatigue | 2024-03-08 | 1 250 |
| DOC007 | Nausées, vomissements, diarrhées | 2024-12-01 | 800 |
| DOC008 | Nutrition | 2024-12-01 | 2 900 |
| DOC009 | Problèmes de bouche | 2015-04-08 | 500 |
| DOC010 | Problèmes de peau | 2024-07-01 | 700 |

- DOC004 à DOC010 : pages de la rubrique « Effets indésirables » de cancer.fr. Le site étant **en maintenance le 23/10/2026** (et l'URL de DOC003 renvoyant 404), elles ont été récupérées depuis la **Wayback Machine** (copie brute `id_`, capture datée indiquée dans `acces`).
- Écartées : les pages d'accueil de rubrique (alopécie, douleurs, fatigue : moins de 200 mots, sommaires), « Conseils chute des cheveux » (150 mots), « La fatigue liée aux traitements par médicaments » (gardée en réserve : recoupe DOC006).
- Recouvrements thématiques avec DOC001/DOC003 (cheveux, nausées, poids) : ce ne sont pas des doublons, mais une question peut avoir des preuves dans plusieurs documents ; à prendre en compte dans l'annotation.

### PAS-v1 — extraction du texte et découpage en passages (2026-10-23, notebook `3_corpus_qa.ipynb`, code `src/qa_corpus.py`)

- **PDF** (PyMuPDF, méthode du TD RAG) : chaque page est une planche de deux pages imprimées en 1-2 colonnes avec encadrés → blocs triés par page imprimée, flux (texte courant puis encadrés), colonne, position ; lettrines recollées ; en-têtes, pieds de page, notes de marge, légendes de schémas, champs et pointillés de formulaires, renvois vers d'autres brochures retirés ; phrases coupées par une colonne/page recollées ; césures et traits d'union résiduels (« médi-ca-ments ») recollés seulement si le mot entier est attesté dans le document (22 cas). Pages : DOC001 p. 3, 5-39, 41-58 ; DOC002 p. 2-9 (jusqu'aux « Sources de référence »).
- **HTML** (BeautifulSoup) : chapô + blocs `wysiwyg` ; navigation, « À lire aussi », vignettes de publications, crédits photo, liens seuls retirés.
- **Découpage** : paragraphes d'une même section regroupés jusqu'à **800 caractères** (TD : 650), jamais à cheval sur deux sections ; paragraphe trop long coupé aux frontières de phrases. Titres gardés dans `localisation.section` (pas dans le texte) ; localisation = section, n° de paragraphes, pages imprimées (PDF).

| Document | Passages | Car. min / méd. / max | Mots |
|---|---|---|---|
| DOC001 | 260 | 74 / 548 / 795 | 20 722 |
| DOC002 | 42 | 158 / 573 / 781 | 3 493 |
| DOC003–DOC010 | 111 | 94 / — / 800 | 8 467 |
| **Total** | **413** | | **32 682** |

- **Contrôle de 10 passages** (le plus court, le plus long, 8 tirés graine 42) : ordre, nombres/unités et négations conformes (`resultats/qa/controle_passages.csv`). Limites relevées : regroupement glouton → petits passages de fin de section (74 car.) et listes coupées entre deux passages (contexte partiel).
- **Contrôle automatique** : 2 049 phrases recherchées dans le texte brut de la source ; 37 non retrouvées telles quelles (1,8 %, DOC001/DOC002), vérifiées par sondage : artefacts du texte brut (phrase coupée par un saut de colonne, mots collés), pas d'erreur d'ordre.
- Limites restantes : tableaux de la fiche 4 de DOC001 (traitements ciblés) aplatis ; quelques légendes longues conservées (« Cathéter simple ou cathéter veineux central »).

**Preuves des questions** : annotées par **extrait verbatim** (`preuves_extraits`) ; identifiants recalculés à chaque découpage (`resoudre_preuves`). Passages donnant la même information dans un autre document : `equivalents_by_element`, hors du calcul du Rappel@5. Correspondance avec les preuves provisoires du jalon E : DOC001_P01 → DOC001_P084 + P085 (Q002 devient une question à deux passages), DOC001_P02 → DOC001_P105, DOC002_P01 → DOC002_P003, DOC002_P02 → DOC002_P009 + P010 (Q004 à deux passages), DOC003_P01 → DOC003_P008 (équivalent DOC001_P142). Justification de Q005 (sans réponse) mise à jour pour les 10 documents.

**Sources divergentes (décision du 2026-10-23)** : DOC001 (2011) indique que les cheveux « recommencent à pousser environ 6 à 8 semaines » après la fin du traitement, DOC004 (2024) qu'ils « repoussent en général dans les 3 à 6 mois ». Q001 est réannotée sur DEV (avant tout réglage) : la référence donne les deux délais avec leur source, un élément attendu par source (preuves DOC001_P105 et DOC004_P002), champs `sources_divergentes: true` et `note_annotation`.
- **Règle de rédaction** (règle 2.3 de `rapport/guide_redaction_qa.md`) : quand deux documents donnent des informations différentes, la référence les cite toutes avec leur source et leur date, sans trancher ; chaque version est un élément attendu.
- **Références reformulées (2026-10-23)** : celles de Q001, Q002 et Q004 recopiaient les passages (segments de 11 à 16 mots), ce qui avantagerait dans BLEU/ROUGE les sorties qui recopient (Q0). Elles sont réécrites de façon concise, chiffres exacts : segment recopié le plus long de 3 à 9 mots, Q001 passe de 80 à 55 mots. Règles 1.1 (questions) et 2.1 (références) du guide ; le notebook 3 signale toute question ou référence qui recopie plus de 10 mots d'une preuve.
- **Conséquences pour la suite** : le prompt Q2 doit demander de signaler les informations divergentes entre passages ; la grille manuelle jugera si la réponse mentionne les deux délais (complétude) et ne présente pas un seul délai comme certain (exactitude). Prévoir au moins une question TEST de ce type.

### Questions DEV (2026-10-23) — 20/20

| ID | Sujet (document) | Type |
|---|---|---|
| Q001 | Chute et repousse des cheveux (DOC001, DOC004) | 2 documents, sources divergentes |
| Q002 | Durée des nausées et vomissements (DOC001 ; équivalent DOC007) | 2 passages |
| Q003 | Variation de poids et diététique remboursée (DOC003, DOC002) | 2 documents |
| Q004 | Bilans de soins de support après cancer (DOC002) | 2 passages |
| Q005 | Dépistage du déficit en DPD | sans réponse |
| Q006 | Aliments à éviter en cas d'aphtes (DOC009 ; équivalent DOC001) | 1 passage, vocabulaire patient |
| Q007 / Q008 | Seuils de dénutrition (DOC008) | 1 passage ; Q008 = reformulation à prémisse inexacte (kilos) |
| Q009 | Précautions quand les plaquettes baissent (DOC001) | 1 passage |
| Q010 | Diarrhée : alimentation, boissons, alerte (DOC007 ; équivalent DOC001) | 2 passages |
| Q011 | Chimiothérapies toxiques pour les nerfs (DOC005) | 1 passage |
| Q012 | Nutrition par sonde à domicile (DOC008) | 2 passages |
| Q013 | Pamplemousse, millepertuis et anticancéreux (DOC008) | 1 passage |
| Q014 | Délai d'apparition des douleurs de chimiothérapie (DOC005) | 1 passage |
| Q015 | Mesurer sa fatigue (DOC006) | 2 passages |
| Q016 | Signes d'infection quand les globules blancs sont bas (DOC001) | 1 passage (+ équivalent « À retenir ») |
| Q017 | Remboursement de la perruque (DOC001, montant 2011) | 1 passage, information datée |
| Q018 | Remboursement du casque réfrigérant | sans réponse (sujet proche très présent) |
| Q019 | Vernis à ongles | sans réponse |
| Q020 | Conduire juste après une séance | sans réponse (DOC010 parle de conduite pour la peau des mains) |

- Bilan : 16 avec réponse dont 7 à deux passages ou plus (≥ 4 demandées), 4 sans réponse ; les 10 documents sont utilisés. Aucune question ni référence ne recopie plus de 10 mots d'une preuve (max. 9).
- Q006-Q020 rédigées avec l'aide de Claude, **à relire par le binôme** (`statut_relecture: a_relire`, guide § 5).
- Q002 : ajout de l'équivalent DOC007_P004 (nausées ≤ 3 jours, vomissements ≤ 48 h).
- **Sujets réservés à TEST** (non utilisés en DEV, pour ne pas partager de famille) : casque réfrigérant, pose et durée (DOC001 fiche 2 + DOC004, 2 documents) ; remboursement du psychologue (DOC006 « seules les consultations des psychiatres sont remboursées » vs DOC002 « Mon soutien psy », **sources divergentes**) ; syndrome main-pied (DOC005 + DOC010) ; vaccinations pendant la chimiothérapie (DOC001_P039) ; nausées anticipatoires (DOC007, DOC001) ; compléments nutritionnels oraux (DOC008) ; activité physique (DOC002) ; colorations après la repousse (DOC001, DOC004).

### Questions TEST (2026-10-23) — 10/10, mises de côté jusqu'au gel du 06/11

| ID | Sujet (document) | Type |
|---|---|---|
| Q021 | Casque réfrigérant : pose, changement, retrait (DOC001, DOC004) | 2 documents complémentaires |
| Q022 | Remboursement du psychologue (DOC006 vs DOC002) | 2 documents, **sources divergentes** |
| Q023 | Syndrome main-pied sous capécitabine (DOC005, DOC010) | 2 documents |
| Q024 | Vaccin contre la grippe pendant la chimiothérapie (DOC001) | 1 passage, question plus précise que le corpus (vaccinations en général) |
| Q025 | Nausées avant la perfusion (DOC007 ; équivalent DOC001) | 1 passage, vocabulaire patient |
| Q026 | Compléments nutritionnels oraux (DOC008) | 2 passages |
| Q027 | Activité d'endurance recommandée (DOC002) | 2 passages |
| Q028 | Ergothérapeute : rôle et remboursement (DOC006) | 2 passages |
| Q029 | Gingembre contre les nausées | sans réponse |
| Q030 | Remboursement de l'acupuncture | sans réponse (pratiques non conventionnelles citées, pas leur prise en charge) |

- 8 avec réponse dont 6 à deux passages ou plus (≥ 2 demandées), 2 sans réponse ; aucune famille partagée avec DEV (contrôle du notebook 3). Recopie maximale : 9 mots (référence), 3 mots (question).
- Mêmes cas difficiles qu'en DEV, sur d'autres sujets : sources divergentes (Q022 ↔ Q001), question plus précise que le corpus (Q024 ↔ Q008), absences proches de sujets traités (Q029-Q030 ↔ Q018-Q020).
- **Rédigées avec l'aide de Claude, à relire par le binôme** (`statut_relecture: a_relire`). Les questions TEST ne servent ni aux réglages ni d'exemples dans les prompts.

### REC-v1 — recherche lexicale BM25 et Q0 sur DEV (2026-10-28, notebook `4.1_recherche_lexicale_q0.ipynb`, code `src/qa_recherche.py`)

- BM25 **repris du TD RAG** sans modification : tokenisation `\w+` minuscules (accents, nombres, négations conservés, aucun mot vide retiré), IDF positive, k1 = 1,5, b = 0,75, top-5. Recherche des 20 questions : 0,04 s (CPU).
- Seul réglage comparé sur DEV : le texte indexé (le titre de section n'est ajouté que pour l'indexation ; Q0 et les LLM reçoivent le texte seul).

| Texte indexé (DEV, 16 questions avec réponse) | Hit@5 | Rappel@5 | Hit@5 avec équiv. | Rappel@5 avec équiv. | Couverture éléments@5 |
|---|---|---|---|---|---|
| texte | 0,688 | 0,625 | 0,750 | 0,688 | 0,677 |
| **section + texte (retenu)** | **0,750** | **0,688** | 0,812 | 0,719 | 0,719 |

- Hit@5 / Rappel@5 : formules B.3 du guide sur `evidence_ids` ; « avec équivalents » : une preuve compte si un passage équivalent du même élément est retrouvé ; couverture : part des éléments attendus disponibles dans le top-5.
- **Manques (DEV)** :
  - Q010 (diarrhée) : top-5 = passages DOC001 équivalents (P092, rang 1) ; preuves DOC007 au rang 23 → retrouvée avec équivalents.
  - Q012 (« nourri par sonde à la maison ») : le vocabulaire de la question ne recoupe pas « nutrition entérale à domicile » ; le casque réfrigérant (« posé », « perfusion ») passe devant ; preuve au rang 17.
  - Q014 (délai des douleurs de chimiothérapie) : les passages sur les douleurs de radiothérapie (DOC005_P017, « après la fin du traitement ») passent devant ; preuve au rang 10.
  - Q016 (signes d'infection) : la preuve (liste de symptômes, un seul « infection ») est au rang 17, derrière des passages répétant « globules blancs ».
  - Q001, Q015 : une preuve sur deux retrouvée (DOC004_P002 et DOC006_P003 hors top-5).
- **Q0** (premier passage tel quel) : 20 réponses DEV dans `resultats/qa/predictions_q0_dev.jsonl`. Exemple d'erreur typique : Q002 (nausées après chimiothérapie) reçoit le passage sur les nausées de **radiothérapie** (DOC007_P005).
- Pistes à tester sur DEV avant le gel (06/11) : paramètres k1/b, mots vides français, k > 5 pour les questions à deux passages ; toute modification crée REC-v2.

### REC-v2 — racinisation (2026-10-29, notebook `4.1_recherche_lexicale_q0.ipynb`)

- Prétraitement appliqué identiquement aux passages et aux questions, pour le calcul des scores seulement : **questions, références et textes transmis aux LLM inchangés**. Mots vides : liste française de NLTK **sans les négations** (ne, pas, sans, aucun, jamais, ni, rien, non, plus) ; racinisation : Snowball français ; nombres conservés.

| DEV, 16 questions avec réponse | Hit@5 | Rappel@5 | Rappel@5 avec équiv. | Couverture éléments@5 | Rappel@10 |
|---|---|---|---|---|---|
| texte, aucun | 0,688 | 0,625 | 0,688 | 0,677 | 0,781 |
| texte, mots vides | 0,750 | 0,688 | 0,750 | 0,740 | 0,781 |
| **texte, racines (REC-v2)** | **0,875** | **0,781** | **0,812** | **0,823** | 0,812 |
| texte, mots vides + racines | 0,875 | 0,781 | 0,812 | 0,823 | 0,812 |
| section + texte, aucun (REC-v1) | 0,750 | 0,688 | 0,719 | 0,719 | 0,781 |
| section + texte, mots vides | 0,750 | 0,719 | 0,750 | 0,740 | 0,781 |
| section + texte, racines | 0,812 | 0,781 | 0,781 | 0,792 | 0,844 |
| section + texte, mots vides + racines | 0,812 | 0,750 | 0,750 | 0,760 | 0,812 |

- **Choix** : texte + racinisation (meilleur Rappel@5, couverture et Hit@5 ; à égalité avec « mots vides + racines », la plus simple). Les mots vides n'apportent rien une fois la racinisation en place ; le titre de section n'aide plus.
- **Grille k1 × b** (k1 ∈ {0,6 … 2,4}, b ∈ {0,3 … 1,0}) : aucun réglage ne dépasse Rappel@5 = 0,781 ; les valeurs du TD (1,5 ; 0,75) sont sur ce plateau et sont conservées (pas de sur-ajustement sur 16 questions).
- **Effets par question** (rang de la 1re preuve, REC-v1 → REC-v2) : Q010 23 → 2 (« diarrhée/diarrhées »), Q014 10 → 5, Q017 4 → 2 ; Q001 et Q015 récupèrent leur 2e preuve ou la gardent. **Restent hors top-5** : Q012 (« nourri par sonde » vs « nutrition entérale », aucun mot commun, rang 22) et Q016 (signes d'infection, rang 140 : la liste de symptômes partage peu de mots avec la question) → relèvent d'une recherche sémantique (approfondissement C.1, dense/hybride).
- Q0 DEV régénéré avec REC-v2 (`resultats/qa/predictions_q0_dev.jsonl`). **Les réponses LLM-v1/v2 ont été produites avec les contextes REC-v1** : le notebook 4.2 doit être relancé (nouveaux appels) pour évaluer Q1/Q2 sur les contextes REC-v2.

### LLM-v1 — Q1 et Q2 sur DEV avec les prompts du guide (2026-10-28, notebook `4.2_llm_q1_q2.ipynb`, code `src/qa_llm.py`)

- Modèle `gpt-4.1-mini-2025-04-14` (API OpenAI), température 0, graine 42, 300 tokens max ; cache des requêtes. Contexte : les 5 passages BM25 de Q0 (REC-v1), même ordre, texte complet (≤ 3 500 caractères). Prompts Q1 v1 et Q2 v1 = annexe C du guide.
- Coût DEV : Q1 14 197 + 1 693 tokens, Q2 15 877 + 1 276 tokens ; 0 échec.

| DEV (20 questions) | Abstentions correctes (/4) | Abstentions sur questions avec réponse (/16) | Réponses sans citation | Citations inventées | Mots (médiane) |
|---|---|---|---|---|---|
| Q1 v1 | 0 | 0 | 1 | 0 | 54 |
| Q2 v1 | **4** | 2 (Q014, Q016) | 0 | 0 | 49 |

- **Lecture des réponses DEV** (contrôles automatiques + lecture, pas la grille officielle) :
  - Q1 ne s'abstient jamais : sur Q018-Q020 il complète avec des inférences non soutenues (« il serait prudent d'éviter de conduire », « la prudence est de mise » pour le vernis). Q2 s'abstient correctement sur les 4.
  - Q014 et Q016 : les preuves ne sont pas dans le top-5 (échec de recherche, REC-v1). Q2 s'abstient (prudent mais compté 0) ; Q1 répond à tort avec des passages sur d'autres douleurs (postopératoires, radiothérapie) → affirmations non soutenues.
  - Q010 (diarrhée) : Q1 et Q2 reprennent les conseils alimentaires **de la radiothérapie** (DOC005_P016 : « 1,5 litre », purées) comme conseils contre la diarrhée sous chimiothérapie : le titre de section, qui situait le passage, n'est pas transmis au LLM.
  - Q001 : aucune des deux ne signale la divergence sur la repousse (DOC004_P002 n'est pas retrouvé) ; Q008 : aucune ne corrige la prémisse « en kilos ».
  - Q012 : échec de recherche ; Q2 répond partiellement et signale que la durée « n'est pas précisée » (comportement attendu), Q1 répond à côté.

### LLM-v2 — contexte avec titres (c2) et prompt Q2 v2 (2026-10-28, DEV)

- **Contexte c2** (Q1 et Q2) : identifiant + titre du document + section d'origine avant chaque passage, texte inchangé. **Q2 v2** : prompt du guide + 4 consignes issues des erreurs v1 : passage portant sur la même situation que la question ; réponse partielle en signalant ce qui manque ; sources divergentes données avec leur document ; hypothèse de la question contredite par les passages signalée. Q1 garde le prompt du guide. Q2 v1 relancé en c2 pour séparer l'effet du contexte et celui des consignes.
- Coût des 60 nouveaux appels : 57 242 + 4 712 tokens ; 0 échec ; les 40 réponses v1 sont reproduites à l'identique par le cache.

| DEV (20 questions) | Abstentions correctes (/4) | Abstentions sur questions avec réponse (/16) | Réponses sans citation | Citations inventées | Mots (médiane) |
|---|---|---|---|---|---|
| Q1 v1 c1 | 0 | 0 | 1 | 0 | 54 |
| Q2 v1 c1 | 4 | 2 | 0 | 0 | 49 |
| Q1 v1 c2 | 0 | 0 | 1 | 0 | 54 |
| Q2 v1 c2 | 4 | 1 | 0 | 0 | 46 |
| Q2 v2 c2 | 4 | 2 | 0 | 0 | 48 |

- **Effet du contexte c2** (lecture) : Q1 devient plus prudent sur Q014 (« les passages ne mentionnent pas explicitement… ») au lieu d'attribuer à la chimiothérapie des douleurs postopératoires ; Q2 v1 complète Q009 (signes à surveiller). Mais Q1 reste sans abstention et continue d'inférer (Q019 « il vaut mieux éviter le vernis », Q020 « il serait prudent de ne pas conduire »).
- **Effet des consignes Q2 v2 : pas de gain net sur les erreurs visées.**
  - Q010 : les conseils de la radiothérapie (DOC005_P016, boissons gazeuses) sont encore cités, sans le « 1,5 litre » ; v2 ajoute que les documents ne précisent pas les aliments et cite à tort une recommandation générale (DOC003_P009, section poids) → la consigne « même situation » est partiellement suivie.
  - Q008 : la prémisse « en kilos » n'est corrigée par aucune configuration, malgré la consigne explicite de v2.
  - Q001 : divergence non signalée, mais la consigne ne peut pas agir : DOC004_P002 n'est pas dans le contexte (échec de recherche).
  - Q012, Q016, Q019 : v2 dit explicitement ce qui manque (« les documents ne précisent pas la durée du passage ni qui s'occupe du matériel ») ; sur Q016/Q019, la phrase d'abstention est précédée d'une explication.
- **Conclusion provisoire** : l'essentiel des erreurs restantes vient de la recherche (Q001, Q010, Q012, Q014, Q016 : preuve absente du top-5), pas de la génération. Contexte c2 à conserver ; choix entre Q2 v1 et Q2 v2 à faire au gel (06/11), après d'éventuels réglages de la recherche sur DEV (REC-v2), qui changeront les contextes transmis.

### LLM sur les contextes REC-v2 (2026-10-29, DEV)

- Mêmes 5 configurations (Q1 v1 c1, Q2 v1 c1, Q1 v1 c2, Q2 v1 c2, Q2 v2 c2), passages REC-v2 ; 100 appels, 0 échec, 105 479 + 7 877 tokens. Sorties REC-v1 archivées (`predictions_llm_dev_REC-v1.jsonl`, `llm_dev_controles_REC-v1.csv`).

| DEV (20 questions), contextes REC-v2 | Abstentions correctes (/4) | Phrase d'abstention sur questions avec réponse (/16) | Réponses sans citation | Citations inventées | Mots (médiane) |
|---|---|---|---|---|---|
| Q1 v1 c1 | 0 | 0 | 1 | 0 | 59,5 |
| Q2 v1 c1 | 4 | 2 | 0 | 0 | 43,5 |
| Q1 v1 c2 | 0 | 0 | 1 | 0 | 50,5 |
| Q2 v1 c2 | 4 | 2 | 0 | 0 | 44,5 |
| Q2 v2 c2 | 4 | 0 | 0 | 0 | 54,5 |

- Le contrôle automatique compte la phrase d'abstention même quand elle ne porte que sur une partie de la réponse : pour Q2 v1 c2, Q014 est une **réponse correcte** suivie d'une abstention partielle (« Information insuffisante… pour savoir si des douleurs persistent ») ; seule Q016 est une vraie abstention (preuve absente du top-5).
- **Ce que la meilleure recherche change** (lecture des réponses) :
  - Q014 : les trois configurations répondent juste (2-3 semaines, disparition à la fin), alors que Q1 répondait faux et Q2 s'abstenait avec REC-v1.
  - Q010 : les trois donnent les 2 litres et les signes d'alerte (DOC007_P009) ; les conseils de radiothérapie disparaissent. Les aliments restent absents (DOC007_P008 hors top-5). Q1 ajoute des conseils **contre les nausées** (DOC001_P088) et Q2 v2 une « alimentation équilibrée » tirée de la section poids (DOC003_P009) : affirmations sur une autre situation.
  - Q001 : DOC004_P002 est maintenant transmis. **Q2 v1 c2 donne les deux délais avec leur source** (6-8 semaines DOC001, 3-6 mois DOC004) ; Q2 v2 les fusionne (« ou plus généralement ») et Q1 n'en garde qu'un ; aucune ne dit explicitement que les sources divergent.
- **Erreurs restantes** :
  - Q012 : la recherche remonte la nutrition **parentérale** à domicile (DOC008_P031) ; les trois configurations s'en servent pour une question sur la sonde (entérale) → réponse sur une autre situation.
  - Q016 : preuve hors top-5 ; Q2 s'abstient, Q1 répond de façon générale.
  - Q008 : la prémisse « en kilos » n'est corrigée par aucune configuration.
  - Q1 invente davantage sur les questions sans réponse : Q020 « **il est déconseillé de prendre le volant** […] rendant la conduite dangereuse » ; Q019 « l'usage du vernis pourrait être déconseillé ».
- **Bilan pour le choix des prompts** : avec de meilleurs passages, **Q2 v1 (prompt du guide) en contexte c2 donne les réponses les plus sûres** (abstentions correctes, deux délais pour Q001, pas d'ajout hors situation) ; les consignes v2 n'apportent pas de gain et ajoutent des généralités. Proposition pour le gel : Q1 v1 + Q2 v1, contexte c2, REC-v2.

### APP-REC — approfondissement : recherche dense et hybride (2026-10-29, notebook `4.3_recherche_hybride.ipynb`, DEV)

- **Question** : une recherche sémantique retrouve-t-elle les preuves de Q012 et Q016 (mots différents de la question), sans dégrader les autres, et à quel coût ? Approfondissement C.1 du guide : le socle Q0/Q1/Q2 reste défini avec BM25.
- **Méthodes** (code du TD RAG) : dense `intfloat/multilingual-e5-small` (préfixes `passage:`/`query:`, cosinus), sur le texte seul ou sur titre de section + texte ; hybride RRF des 20 premiers BM25 REC-v2 et denses (1/(60 + rang)).

| DEV, 16 questions avec réponse | Hit@5 | Rappel@5 | Hit@5 équiv. | Rappel@5 équiv. | Couverture éléments@5 | Recherche 20 q. |
|---|---|---|---|---|---|---|
| BM25 REC-v2 | 0,875 | 0,781 | 0,875 | 0,812 | 0,823 | 0,05 s |
| dense (texte) | 0,812 | 0,719 | 0,812 | 0,750 | 0,760 | 0,55 s |
| **dense (section + texte)** | **0,938** | **0,875** | **1,000** | **0,969** | **0,979** | 0,55 s |
| hybride RRF (BM25 + dense texte) | 0,812 | 0,656 | 0,812 | 0,688 | 0,698 | 0,64 s |
| hybride RRF (BM25 + dense section + texte) | 0,875 | 0,781 | 0,875 | 0,781 | 0,802 | 0,60 s |

- **Coût** : encodage des 413 passages ≈ 35 s sur CPU (une fois, modèle de 118 M paramètres), aucun passage tronqué ; recherche ≈ 30 ms par question, contre 2-3 ms pour BM25. Aucun coût d'API.
- **Dense (section + texte)** retrouve les deux preuves visées : Q012 au rang 4 (BM25 : 22), Q016 au rang 4 (BM25 : 140), et Q014 au rang 1. Il recule sur Q006 (aphtes : rang 14, mais l'équivalent DOC001 est retrouvé, d'où Hit@5 équiv. = 1) et Q001 (rang 3).
- **Le titre de section aide la recherche dense** (0,719 → 0,875 de Rappel@5), alors qu'il n'aidait plus BM25 après racinisation : le modèle situe le passage (« Nutrition entérale à domicile », « Une diminution temporaire de certains globules blancs »).
- **La fusion RRF n'apporte rien** : elle mélange un BM25 qui rate Q012/Q016 et un dense qui rate Q006/Q009 ; à poids égaux, les erreurs de chaque méthode diluent les réussites de l'autre. Pas de pondération réglée (risque de sur-ajustement sur 16 questions).
- **Essais de fusion favorisant la recherche dense** (BM25 REC-v2 + dense section + texte ; `recherche_dev_fusion_essais.csv`) :

| DEV, 16 questions avec réponse | Hit@5 | Rappel@5 | Couverture éléments@5 | Paramètres réglés |
|---|---|---|---|---|
| BM25 REC-v2 | 0,875 | 0,781 | 0,823 | 0 |
| **dense (section + texte)** | **0,938** | **0,875** | **0,979** | 0 |
| RRF, poids dense × 1 | 0,875 | 0,781 | 0,802 | 0 |
| RRF, poids dense × 1,5 / × 2 / × 3 (identiques) | 0,938 | 0,812 | 0,844 | 1 |
| règle « grand écart » → dense (premier passage d'une méthode absent des 20 premiers de l'autre → dense seul, sinon RRF) | 0,875 | 0,781 | 0,885 | 1 |

  - La pondération récupère Q006 (aphtes, rang 14 → 3, bien vu par BM25) mais fait reculer Q012 (4 → 5) et Q016 (4 → 13), que seule la recherche dense trouvait ; au-delà de × 1,5, le poids ne change plus rien.
  - La règle « grand écart » bascule bien sur la recherche dense pour Q016 (rang 4), mais la fusion reprend la main sur Q012 (rang 7) et ne récupère pas Q006 (rang 14).
  - Ces règles ont été imaginées après avoir vu les échecs de DEV (résultat optimiste) et ajoutent un paramètre réglé sur 16 questions ; aucune ne dépasse la recherche dense seule, sans paramètre. **Retenu pour l'approfondissement : recherche dense sur titre de section + texte, sans fusion** ; BM25 REC-v2 reste le socle. À comparer une seule fois sur TEST après le gel, avec la qualité des réponses de Q2.
- **Limites** : 16 questions, 5 méthodes comparées sur le même DEV ; l'écart dense / BM25 (+0,094 de Rappel@5) repose sur 3 questions. À confirmer sur TEST après le gel, si l'approfondissement est retenu, en le rapportant à côté du socle BM25.
- **Incident d'environnement** : l'installation de `sentence-transformers` 6.2 a mis à jour `transformers` en 5.22 ; restauré en 4.57.1 (version de BioBERT) avec `sentence-transformers` 5.1.2, `pip check` sans conflit.

### APP-REC — qualité des réponses de Q2 avec la recherche dense (2026-10-29, DEV, notebook 4.2)

- Q2 v1, contexte c2, mêmes paramètres ; seule la source des 5 passages change (dense E5 section + texte au lieu de BM25 REC-v2). 20 appels, 17 694 + 1 674 tokens, 0 échec. Sorties : `resultats/qa/predictions_llm_dev_dense.jsonl`.
- Contrôles automatiques : 4/4 abstentions correctes dans les deux cas ; phrase d'abstention sur une question avec réponse : 2 (BM25 : Q014 partielle, Q016) → 1 (dense : Q014 partielle) ; 0 citation inventée ; réponses plus longues (médiane 55 mots contre 44,5).
- Lecture des 20 paires de réponses (5 identiques : Q004, Q005, Q018, Q020 et une partie de Q007/Q008/Q017 quasi identiques) :

| Question | Q2 avec BM25 REC-v2 | Q2 avec recherche dense |
|---|---|---|
| Q012 (sonde à domicile) | répond sur la nutrition **parentérale**, dit ne pas savoir comment installer le patient | **complète et juste** : position assise ou demi-assise à 30°, passage sur 18 h / 6 h couché, prestataire (DOC008_P027, P028) |
| Q016 (signes d'infection) | abstention (preuve absente) | **complète** : seuils 38 °C / 38,5 °C / 36,5 °C, autres signes, consulter immédiatement (DOC001_P118, P119) |
| Q010 (diarrhée) | boissons et alerte, **sans les aliments** | **complète** : alimentation pauvre en fibres, 2 litres, alerte (DOC001_P092-P093, DOC007_P008) |
| Q015 (mesurer sa fatigue) | échelle 0-20 seulement | échelle 0-20 **et** questionnaire quotidien (DOC006_P002, P003) |
| Q003 (poids et diététique remboursée) | complète | **régression** : DOC002_P003 (panier des 9 soins remboursés) absent ; Q2 dit honnêtement que le remboursement « n'est pas précisé ici » |
| Q001 (sources divergentes) | deux délais, deux phrases distinctes avec leur source | deux délais présentés comme **une seule histoire cohérente** (« repoussent en 3 à 6 mois, avec un début de repousse vers 6 à 8 semaines ») : la divergence entre documents n'est pas signalée |
| Q019 (vernis, sans réponse) | abstention seule | explication sur la fragilité des ongles, puis abstention (correct) |

- **Bilan** : avec la recherche dense, Q2 répond correctement à Q012 et Q016, que la configuration du socle ratait, et complète Q010 et Q015 ; une régression (Q003, élément « remboursement » manquant, sans affirmation fausse). L'erreur de Q008 (prémisse en kilos) reste la seule erreur imputable au LLM sur DEV, avec la façon de présenter la divergence de Q001.
- À reproduire sur TEST après le gel (comparaison BM25 REC-v2 / dense pour Q2), en rappelant que DEV a servi à choisir la méthode dense (résultat DEV optimiste).

### APP-REC-v2 — essai de reclassement par cross-encoder (2026-10-30, notebook `4.3_recherche_hybride.ipynb`, DEV) — non retenu

- **Question** : peut-on combiner BM25 et recherche dense sans poids à régler, en réunissant leurs candidats puis en les faisant trier par un reclasseur (pipeline RAG « hybride » classique) ?
- **Configuration fixée avant exécution** : candidats = union des 20 premiers BM25 REC-v2 et des 20 premiers denses (E5, section + texte) ; reclasseur `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (multilingue, 118 M paramètres, CPU, 512 tokens), qui lit titre de section + texte ; code `Reclasseur` dans `src/qa_recherche.py`. Variantes sans paramètre : reclassement des 20 premiers BM25 seuls, ou denses seuls.
- **Règle de choix fixée avant exécution** : retenu seulement si le Rappel@5 dépasse celui de la recherche dense seule sans perte de preuve sur aucune question.
- **Scores DEV** (16 questions avec réponse, `resultats/qa/recherche_dev_reclassement.csv`) ; rang réciproque = moyenne de 1 / rang de la 1re preuve :

| DEV | Hit@5 | Rappel@5 | Couverture éléments@5 | Rang réciproque | Temps / question (CPU) |
|---|---|---|---|---|---|
| BM25 REC-v2 | 0,875 | 0,781 | 0,823 | 0,674 | < 0,01 s |
| dense (section + texte) | **0,938** | **0,875** | **0,979** | 0,702 | 0,04 s |
| reclassement des 20 premiers BM25 | 0,875 | 0,750 | 0,781 | 0,844 | 2,1 s |
| reclassement des 20 premiers denses | 0,938 | 0,875 | 0,958 | **0,853** | 2,0 s |
| reclassement de l'union BM25 + dense | 0,938 | 0,875 | 0,958 | **0,853** | 3,5 s |

- **Lecture** : le reclasseur met la 1re preuve en tête bien plus souvent (rang 1 pour 12 questions sur 16, contre 9 avec la recherche dense seule), mais le Rappel@5 ne bouge pas. Il fait sortir du top-5 l'une des deux sources divergentes de Q001 (couverture 1 → 0,67) et fait reculer Q006 (aphtes, rang 1 avec BM25 → 7). Sur les candidats BM25 seuls, il ne peut pas rattraper Q012 et Q016, absents des 20 premiers. L'union donne exactement le même résultat que les 20 premiers denses seuls.
- **Décision** : non retenu (règle ci-dessus). Pour un coût 50 fois plus élevé (≈ 2 s par question, plus 15 s de chargement), aucun gain de rappel ; la recherche dense seule reste l'approfondissement retenu. Le meilleur ordre du top-5 n'aurait d'intérêt que pour transmettre moins de passages au LLM (k = 3), ce qui n'a pas été testé.
- **Environnement** : exécuté sur le serveur Pico (venv `~/venvs/nlp`, torch 2.15 CPU, transformers 4.57.1, sentence-transformers 5.1.2) ; les scores des méthodes déjà mesurées (BM25, dense, RRF) sont identiques à ceux du laptop, seuls les temps de `recherche_dev_hybride.csv` changent.

### Gel QA et BLEU / ROUGE sur DEV (2026-10-30, notebooks 4.2 et 5)

- **Configuration figée** (`resultats/qa/qa_config_gelee.json`, texte exact des prompts) : socle = BM25 REC-v2, 5 passages ; Q0 = premier passage tel quel ; **Q1 v1** et **Q2 v1** (prompts du guide), **contexte c2** pour les deux ; `gpt-4.1-mini-2025-04-14`, température 0, graine 42, 300 tokens. Approfondissement : Q2 v1 c2 avec les 5 passages de la recherche dense (E5, section + texte). Q2 v2 non retenu (pas de gain sur DEV, généralités en plus).
- **Calcul BLEU / ROUGE** (`src/qa_scores.py`, annexe B.4 du guide) : questions avec réponse ; citations valides et phrase d'abstention retirées (abstention = réponse vide) ; NFC, minuscules, mots `\w+` communs à BLEU et ROUGE (le tokeniseur de rouge-score supprime les accents, d'où un tokeniseur commun). BLEU de corpus 0-100, sacrebleu 2.6.0 (`nrefs:1|case:mixed|eff:no|tok:none|smooth:exp`, minuscules faites avant) ; ROUGE-1/2/L : F1 moyenné par question, rouge-score 0.1.2.
- **Scores DEV** (16 questions avec réponse, `resultats/qa/bleu_rouge_dev.csv`) :

| DEV | BLEU | ROUGE-1 | ROUGE-2 | ROUGE-L | Réponses vides | Mots (médiane) |
|---|---|---|---|---|---|---|
| Q0 (BM25 REC-v2) | 5,67 | 0,276 | 0,110 | 0,184 | 0 | 108 |
| Q1 v1 c2 | 13,04 | 0,434 | 0,209 | 0,336 | 0 | 52 |
| **Q2 v1 c2 (retenu)** | **16,16** | 0,453 | 0,231 | 0,360 | 1 | 48,5 |
| Q2 v2 c2 | 13,85 | 0,445 | 0,235 | 0,344 | 0 | 59 |
| Q2 v1 c2, recherche dense | 14,12 | **0,507** | **0,250** | **0,377** | 0 | 60,5 |

- **Lecture** : Q0 est pénalisé par sa longueur (un passage entier, ≈ 100 mots, contre des références de 30 à 55 mots). Avec la recherche dense, Q2 gagne en ROUGE (réponses plus complètes : Q010, Q012, Q015, Q016) mais perd en BLEU, plus sensible à la longueur et à la formulation exacte. Les écarts entre Q1 et Q2 sont faibles : ils ne disent rien de la justesse (Q1 ne s'abstient jamais), d'où la grille manuelle.
- **Notebook 5 préparé et répété sur DEV** : tableaux 3 (recherche TEST, socle et dense) et 4 (génération Q0/Q1/Q2/Q2 dense, BLEU/ROUGE, contrôles) et grille manuelle anonymisée (30 réponses mélangées, graine 42, `grille_manuelle.csv` + `grille_correspondance.csv`). Répétition dans une copie du projet avec les questions DEV à la place de TEST : réponses et scores identiques à ceux des notebooks 4.1-4.3 (tout depuis le cache). **TEST pas encore exécuté** : la clé OpenAI n'est pas sur le serveur ; en cas d'échec d'un appel, le notebook n'écrit rien.

### Évaluation TEST du QA (2026-11-01, `5_evaluation.ipynb`, configuration du gel, exécutée une seule fois)

- 10 questions TEST (8 avec réponse, 2 sans réponse) ; 30 appels au LLM (Q1, Q2, Q2 dense), 0 échec, 26 056 + 2 497 tokens. Sorties : `data/predictions_qa.jsonl` (Q0, Q1, Q2), `resultats/qa/predictions_llm_test_dense.jsonl` ; scores : `recherche_test.csv`, `bleu_rouge.csv`.
- **Tableau 3 — recherche** (8 questions avec réponse) :

| Recherche | Hit@5 DEV → TEST | Rappel@5 DEV → TEST | Couverture éléments@5 DEV → TEST |
|---|---|---|---|
| BM25 REC-v2 (socle) | 0,875 → 0,875 | 0,781 → 0,771 | 0,823 → 0,792 |
| dense (approfondissement) | 0,938 → **1,000** | 0,875 → 0,771 | 0,979 → 0,792 |

- **Lecture recherche** : le socle BM25 est stable de DEV à TEST. L'avantage de la recherche dense en rappel sur DEV (+0,094) **ne se confirme pas** : égalité sur TEST. Elle retrouve Q025 (« envie de vomir en arrivant à l'hôpital » → passage sur les nausées anticipatoires, que BM25 rate), mais perd des preuves que BM25 trouvait : DOC006_P009 (ergothérapeute non remboursé, Q028), DOC006_P014 (psychiatre seul remboursé, une des deux sources divergentes de Q022), DOC010_P003 (soins de la peau, Q023). Comme attendu, le résultat DEV était optimiste.
- **Tableau 4 — BLEU / ROUGE** (8 questions avec réponse ; DEV entre parenthèses) :

| TEST | BLEU | ROUGE-1 | ROUGE-2 | ROUGE-L | Mots (médiane) |
|---|---|---|---|---|---|
| Q0 (BM25) | 5,44 (5,67) | 0,297 | 0,102 | 0,210 (0,184) | 105,5 |
| Q1 v1 c2 (BM25) | 9,96 (13,04) | 0,422 | 0,173 | 0,315 (0,336) | 55 |
| Q2 v1 c2 (BM25) | 10,10 (16,16) | 0,430 | 0,178 | 0,325 (0,360) | 59 |
| Q2 v1 c2 (dense) | **13,99** (14,12) | **0,455** | **0,222** | **0,354** (0,377) | 63 |

- **Contrôles automatiques** : abstentions correctes (/2) : Q1 0, Q2 1, Q2 dense 2 ; phrase d'abstention sur une question avec réponse (/8) : Q2 dense 1 (Q028, partielle) ; 0 citation inventée.
- **Premières observations (lecture rapide, avant la grille manuelle)** :
  - Q021, Q026, Q027 : réponses complètes et justes dans les trois configurations LLM. Q2 ajoute pour Q027 un calcul absent du texte (« au moins 2 h 30 par semaine »).
  - Q025 : avec BM25, Q1 et Q2 attribuent ces nausées aux odeurs et proposent des bonbons mentholés (passage sur les nausées pendant la perfusion) ; avec la recherche dense, Q2 donne la bonne réponse (nausées anticipatoires, anxiété, médicaments ou relaxation).
  - Q022 (sources divergentes) : aucune configuration ne signale la divergence. Q1 et Q2 (BM25) fusionnent les deux sources en une règle unique (« pas remboursées sauf Mon soutien psy ») ; Q2 dense, privé de DOC006_P014, ne donne qu'une version (« oui, 12 séances »).
  - Q024 (pas de passage sur la grippe en particulier) : Q2 écrit « y compris le vaccin contre la grippe », une généralisation que le texte ne dit pas ; Q2 dense reste fidèle.
  - Q028 : Q1 et Q2 (BM25) complets ; Q2 dense ne retrouve pas le passage sur le remboursement et le dit (abstention partielle).
  - Q030 (sans réponse, acupuncture) : Q1 affirme à tort que les séances ne sont pas remboursées ; Q2 dit qu'elles « ne sont pas mentionnées comme remboursées » sans la phrase d'abstention (non compté comme abstention) ; Q2 dense s'abstient. Q029 : Q2 et Q2 dense s'abstiennent, Q1 dit que les passages n'en parlent pas sans la phrase imposée.
- **Bilan provisoire** : sur TEST, Q2 dense obtient les meilleurs scores automatiques et les seules deux abstentions correctes, mais à rappel égal avec BM25 : il gagne Q025 et perd Q028 et une source de Q022. Q1 ne s'abstient jamais et fait une affirmation non soutenue (Q030). Le classement final Q0/Q1/Q2 attend la grille manuelle (B.5).
- **À faire** : remplir `resultats/qa/grille_manuelle.csv` séparément (AMARA, TOMAS), arbitrer (`final_`), puis ouvrir `grille_correspondance.csv` ; erreurs commentées QA. Aucun réglage ne sera modifié à partir de ces résultats.

### Test comparatif Q0 / Q1 / Q2 sur une question libre (2026-11-06, notebook `4.2_llm_q1_q2.ipynb`, fin)

- Question hors DEV et TEST : « Dans le cancer du sein, dans quel cas doit-on avoir une chimio adjuvante, ou néoadjuvante ? ». Configuration figée relue dans `qa_config_gelee.json`, sans aucun réglage (BM25 REC-v2, 5 passages, Q0 / Q1 v1 / Q2 v1, contexte c2). 2 appels au LLM (Q1 806 + 73 tokens, Q2 890 + 104), ajoutés au cache ; aucune référence ni score, simple illustration.
- **Passages** : DOC001_P023, DOC001_P008, DOC004_P001, DOC001_P004, DOC001_P020. Manquent DOC001_P019 (définition de la néoadjuvante) et DOC001_P021-P022 (facteurs de risque) ; « chimio » et « chimiothérapie » n'ont pas la même racine pour BM25.
- **Réponses** : Q0 = DOC001_P023 entier (information présente mais noyée) ; Q1 et Q2 justes et cités (P023, P020), Q2 un peu plus complet (adjuvante quand elle réduit le risque de métastases). Limite commune : le corpus traite de la chimiothérapie en général, pas du cancer du sein, et ni Q1 ni Q2 ne le signale ; critères de décision absents des passages transmis.

### LLM-v3 — essai après coup : nombre de passages transmis à Q2 (2026-11-06, notebook `4.2_llm_q1_q2.ipynb`, fin, DEV) — non retenu

- **Question** : transmettre 3 ou 10 passages au lieu de 5 améliore-t-il les réponses ? Q2 v1, contexte c2, mêmes paramètres du LLM ; seule la longueur de la liste BM25 REC-v2 change (k = 3, 5, 10). **Fait après l'évaluation de TEST** : DEV seulement, configuration figée inchangée, TEST non relancé.
- 40 nouveaux appels (k = 3 : 12 825 + 1 133 tokens ; k = 10 : 34 503 + 1 535), 0 échec ; k = 5 vient du cache et redonne exactement les réponses du gel (vérifié dans le notebook). BLEU/ROUGE calculés avec sacrebleu 2.6.0 et rouge-score 0.1.2, installés dans un dossier temporaire (absents des venvs locaux).
- **Scores DEV** (16 questions avec réponse ; `resultats/qa/llm_dev_nb_passages.csv`) :

| Passages transmis | Hit | Rappel | Couverture éléments | Abstentions correctes (/4) | Abstention sur question avec réponse (/16) | BLEU | ROUGE-1 | ROUGE-2 | ROUGE-L | Mots (médiane) |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0,750 | 0,625 | 0,677 | 4 | 3 | **16,71** | 0,398 | 0,205 | 0,314 | 45,5 |
| **5 (gel)** | 0,875 | 0,781 | 0,823 | 4 | 2 | 16,16 | 0,453 | 0,231 | 0,360 | 48,5 |
| 10 | 0,875 | **0,812** | 0,823 | 4 | 2 | 14,28 | **0,472** | **0,240** | **0,367** | 56 |

- **k = 3** : les preuves de Q001 (2ᵉ source), Q008 et Q014, aux rangs 4-5, sortent du contexte. Q2 s'abstient à tort sur Q008 et Q014 et ne donne plus qu'une version pour Q001. Le BLEU monte un peu grâce à des réponses plus courtes.
- **k = 10** : une seule preuve en plus (Q002, rang 9, réponse inchangée sur le fond) ; Q003 et Q010 un peu plus complètes. **Q016** : preuve toujours absente, mais Q2 répond au lieu de s'abstenir, avec des signes qui ne sont pas ceux d'une infection (affirmation non soutenue). Q010 : conseils contre les nausées (DOC001_P088) repris pour la diarrhée (aussi à k = 3). Contexte presque 2 fois plus long.
- **Décision** : k = 5 conservé. Moins de passages fait perdre des preuves ; plus de passages ajoute surtout des passages hors sujet que Q2 utilise.
- Fichiers : `resultats/qa/predictions_llm_dev_nb_passages.jsonl` (k = 3 et 10, champ `nb_passages`), `resultats/qa/llm_dev_nb_passages.csv`, réponses ajoutées à `cache_llm.json`.

### LLM-MIS-v1 — comparaison OpenAI / Mistral sur toute la partie QA (2026-11-06, notebook `4.4_comparaison_mistral.ipynb`)

- **Principe** : les 192 prompts envoyés à OpenAI (DEV : Q1/Q2 v1 c1, v1 c2, Q2 v2 c2, Q2 dense, essai k = 3 / 10 ; TEST : Q1, Q2, Q2 dense de la configuration figée ; question libre) sont relus dans les fichiers de prédictions et renvoyés **mot pour mot** à Mistral. Seul le modèle change : `mistral-medium-2604` (version datée, même gamme que gpt-4.1-mini), température 0, `random_seed` 42 (nom du paramètre de graine chez Mistral), 300 tokens. 192 appels, 0 échec, 0 réponse tronquée.
- **Code** : `src/qa_llm.py`, `ClientLLM(..., fournisseur="mistral")` (même client OpenAI, adresse et clé `MISTRAL_API_KEY`) ; nouvelle tentative automatique en cas de limite de débit. Les requêtes OpenAI sont inchangées : leurs 30 réponses TEST reviennent du cache, à l'identique (vérifié).
- **TEST** : la configuration figée n'est pas modifiée ; on compare deux LLM sans rien régler. Grille manuelle non refaite.
- **Scores** (`resultats/qa/comparaison_openai_mistral.csv` ; BLEU 0-100, ROUGE-L 0-1, questions avec réponse) :

| Expérience | OpenAI BLEU / ROUGE-L | Mistral BLEU / ROUGE-L | Abstentions correctes OpenAI / Mistral | Abstentions à tort OpenAI / Mistral | Mots (médiane) OpenAI / Mistral |
|---|---|---|---|---|---|
| DEV Q1 v1 c2 | 13,04 / 0,336 | 19,07 / 0,394 | 0/4 / 0/4 | 0 / 0 | 52 / 48 |
| DEV Q2 v1 c2 (gel) | 16,16 / 0,360 | 20,56 / 0,374 | 4/4 / 4/4 | 2 / 1 | 48,5 / 31,5 |
| DEV Q2 v2 c2 | 13,85 / 0,344 | 20,06 / 0,372 | 4/4 / 4/4 | 0 / 1 | 59 / 37,5 |
| DEV Q2 v1 c2, dense | 14,12 / 0,377 | 16,47 / 0,377 | 4/4 / 4/4 | 1 / 0 | 60,5 / 44 |
| DEV Q2 v1 c2, k = 3 | 16,71 / 0,314 | 14,83 / 0,325 | 4/4 / 4/4 | 3 / 4 | 45,5 / 29 |
| DEV Q2 v1 c2, k = 10 | 14,28 / 0,367 | 18,86 / 0,366 | 4/4 / 4/4 | 2 / 1 | 56 / 31,5 |
| TEST Q1 v1 c2 | 9,96 / 0,315 | 11,61 / 0,343 | 0/2 / 0/2 | 0 / 0 | 55 / 48,5 |
| TEST Q2 v1 c2 | 10,10 / 0,325 | 11,66 / 0,359 | 1/2 / **2/2** | 0 / 0 | 59 / 39,5 |
| TEST Q2 v1 c2, dense | 13,99 / 0,354 | **15,34 / 0,380** | 2/2 / 2/2 | 1 / 1 | 63 / 45 |

  Q0 (sans LLM) : DEV 5,67 / 0,184, TEST 5,44 / 0,210. Aucune citation inventée chez les deux ; durée médiane ≈ 0,9 s (Mistral) contre 1,1-1,4 s (OpenAI).
- **Lecture** : Mistral a des scores automatiques un peu meilleurs, en partie parce que ses réponses sont plus courtes. Les conclusions ne changent pas : les erreurs viennent surtout de la recherche, et les deux LLM se trompent aux mêmes endroits (Q025 avec BM25, divergence de Q022 non signalée, question libre sans réserve sur le cancer du sein). Différences notables : Mistral s'abstient correctement sur Q030 (Q2) et sur Q016 avec 10 passages (OpenAI y donnait une réponse non soutenue) ; il ne fait pas la généralisation « grippe » de Q024 en Q2 ni le calcul « 2 h 30 » de Q027 ; en revanche, il ajoute à Q025 (BM25) l'« anxiété », absente du passage transmis. Avec 3 passages, les deux perdent des preuves (Mistral : 4 abstentions à tort).
- **Reproductibilité** : 5 prompts TEST renvoyés sans cache → 3 réponses identiques sur 5 malgré température 0 et graine fixe ; les sorties sont stables grâce au cache (`resultats/qa/cache_llm_mistral.json`).
- Fichiers : `notebooks/4.4_comparaison_mistral.ipynb`, `resultats/qa/predictions_mistral.jsonl`, `resultats/qa/comparaison_openai_mistral.csv`, `resultats/qa/cache_llm_mistral.json`.

### Grille de lecture QA sur TEST (2026-11-09, `resultats/qa/grille_manuelle.csv`)
- **Méthode** : les 30 réponses TEST anonymisées (10 questions × Q0/Q1/Q2) ont été notées par un **juge LLM** (Claude, sous-agents sans aucun contexte du projet) et non par les deux membres. Chaque juge ne voyait qu'un fichier contenant, par réponse : question, présence d'une réponse dans les documents, référence, éléments attendus, texte des passages transmis et réponse ; ni la configuration (`grille_correspondance.csv`), ni les autres fichiers du projet. Échelle du notebook 5 (exactitude 0-2, complétude en éléments, citations soutenues / proposées, abstention).
- Deux juges lancés séparément ont donné **exactement les mêmes notes (30/30 sur les quatre dimensions)**. Ce n'est pas un accord inter-annotateurs (même modèle, même consigne) : un seul jeu de notes est gardé (colonnes `_juge`, qui remplacent `_AMARA`, `_TOMAS` et `_final`).
- **Résultats par configuration** (TEST) :

| Configuration | Exactitude moyenne (0-2) | Complétude moyenne | Citations soutenues / proposées | Abstentions correctes / manquantes |
|---|---|---|---|---|
| Q0 | 1,4 | 0,42 | 10 / 10 | 0 / 2 |
| Q1 | 1,4 | **0,83** | 23 / 25 | 1 / 1 |
| Q2 | **1,7** | 0,76 | 18 / 19 | **2 / 0** |

- **Lecture** : Q2 est la plus exacte et la seule à s'abstenir sur les deux questions sans réponse ; Q1 est un peu plus complète. Erreurs relevées : généralisation au vaccin contre la grippe (Q024), divergence des sources non signalée (Q022), passage manquant pour Q025 avec BM25, remboursement de l'acupuncture affirmé sans source (Q030, Q1).
- **Choix du juge à relire** : une réponse qui recopie un passage juste mais hors sujet reçoit exactitude 1 (Q0 sur Q029/Q030) ou 0 (Q021, Q025) ; une réponse disant que l'information « n'est pas mentionnée », sans la phrase imposée, est comptée comme abstention correcte (Q030, Q2).
- Fichiers : `resultats/qa/grille_manuelle.csv` (colonnes `_juge`), `notebooks/5_evaluation.ipynb` et `rapport/3_question_reponse.ipynb` (section 9) adaptés.

---

## 7. Journal

| Date | Changement |
|---|---|
| ≤ 2026-10-11 | DIC-v1 et APP-v1 figées ; NEG-v0 ; corpus QA (commit `fd3fc0d`). |
| 2026-10-16 | Analyse du taux d'annotation (biais d'imbrication, rôle de la casse) — non intégrée. |
| 2026-10-16 | Exports `data/corpus_extraction.csv` et `data/bio_extraction.csv`. |
| 2026-10-16 | DIC-v2 : 5 règles de post-traitement dans le notebook 2.3 (F1 val 0,7449 → 0,7912) ; prédictions VALIDATION et TEST régénérées. |
| 2026-10-23 | Corpus QA : 7 pages INCa ajoutées (DOC004–DOC010, via Wayback Machine), catalogue `data/corpus.csv` à 10 documents. |
| 2026-10-23 | Notebook 2.3 réexécuté (résultats DIC-v2 identiques) ; `comparaison_validation.csv` recalculé avec DIC-v2. |
| 2026-10-23 | PAS-v1 : extraction (PyMuPDF / BeautifulSoup) et découpage des 10 documents en 413 passages ; preuves annotées par extrait verbatim, Q001–Q005 remappées ; contrôle de 10 passages. |
| 2026-10-23 | Q001 réannotée (sources divergentes DOC001/DOC004 sur la repousse des cheveux) ; règle de rédaction pour les sources divergentes. |
| 2026-10-23 | Guide de rédaction QA (`rapport/guide_redaction_qa.md`) ; références de Q001, Q002, Q004 reformulées ; contrôle de recopie dans le notebook 3. |
| 2026-10-23 | Questions DEV Q006–Q020 rédigées (aide Claude, à relire) : DEV complet 20/20 ; équivalent DOC007 pour Q002 ; règles 1.5 (prémisse inexacte), 1.6 (information datée) et § 5 (aide LLM) du guide. |
| 2026-10-23 | Questions TEST Q021–Q030 rédigées (aide Claude, à relire) : TEST complet 10/10, dont une question à sources divergentes (Q022). |
| 2026-10-28 | Relecture des 30 questions QA par AMARA Yanis, sans modification (`statut_relecture: relue_AMARA`). |
| 2026-10-28 | REC-v1 : BM25 du TD (section + texte indexés), DEV Hit@5 = 0,750, Rappel@5 = 0,688 ; Q0 DEV produit. |
| 2026-10-28 | LLM-v1 : Q1/Q2 (prompts du guide) sur DEV avec gpt-4.1-mini-2025-04-14 ; Q2 : 4/4 abstentions correctes, 2 abstentions dues à la recherche. |
| 2026-10-28 | LLM-v2 : contexte c2 (titres) et prompt Q2 v2 sur DEV ; pas de gain net des nouvelles consignes, erreurs restantes dominées par la recherche. |
| 2026-10-29 | REC-v2 : BM25 + racinisation Snowball, DEV Hit@5 = 0,875, Rappel@5 = 0,781 (REC-v1 : 0,750 / 0,688) ; k1/b du TD conservés ; Q0 DEV régénéré. |
| 2026-10-29 | Q1/Q2 relancés sur les contextes REC-v2 : Q014 et Q010 corrigés par la recherche ; Q2 v1 c2 meilleure configuration sur DEV ; v2 sans gain. |
| 2026-10-29 | APP-REC (approfondissement) : dense E5 section + texte, DEV Hit@5 = 0,938, Rappel@5 = 0,875 ; Q012 et Q016 retrouvées ; hybride RRF sans gain. |
| 2026-10-29 | APP-REC : essais de fusion pondérée (× 1,5 à × 3) et de règle « grand écart » sur DEV, sans gain sur la recherche dense seule (Rappel@5 0,812 / 0,781 contre 0,875) ; dense sans fusion retenu pour l'approfondissement. |
| 2026-10-29 | APP-REC : Q2 v1 c2 avec passages denses sur DEV ; Q012 et Q016 désormais justes, Q010 et Q015 complétées, régression sur Q003. |
| 2026-10-29 | Synthèse du jalon QA1 rédigée (`rapport/synthese_QA1.md`). |
| 2026-10-30 | APP-v2 préparé (notebook 2.4b) : diagnostic de sous-entraînement d'APP-v1, plan 10 époques + warmup, 2 taux × 2 graines ; exécution Colab à faire. |
| 2026-10-30 | APP-v2 exécuté (Colab T4) : taux 5e-5, 4 époques ; F1 VALIDATION 0,8546 → 0,8929 (Chemical 0,9358, Disease 0,8392) ; APP-v2 remplace APP-v1 comme méthode apprise figée. |
| 2026-10-30 | APP-v3 préparé (notebook 2.4c) : PubMedBERT et BioLinkBERT-base avec la recette d'APP-v2, 2 graines ; règle de remplacement : gain > 0,005 ; exécution Colab à faire. |
| 2026-10-30 | APP-v3 exécuté (Colab T4) : PubMedBERT 7 époques retenu ; F1 VALIDATION 0,8929 → 0,9119 (Chemical 0,9532, Disease 0,8598) ; BioLinkBERT 0,906 ; APP-v3 remplace APP-v2. |
| 2026-10-30 | Erreurs commentées réécrites pour APP-v3 (`erreurs_commentees.md`) ; version APP-v1 conservée (`erreurs_commentees_APP-v1.md`). |
| 2026-10-30 | DIC-v3 (notebook 2.3b) : filtre corrigé, variantes singulier/pluriel, extension à droite, propagation ; F1 VALIDATION 0,7912 → 0,7993 ; DIC-v3 remplace DIC-v2. |
| 2026-10-30 | Évaluation TEST (notebook 5, tableau 1) de DIC-v3 (F1 0,7978) et APP-v3 (F1 0,8941) ; `scores_test.csv`, `data/predictions_extraction.jsonl`. |
| 2026-10-30 | Comparaison avec l'état de l'art (extraction) : outils officiels tmChem + DNorm mesurés sur notre TEST (F1 0,868), résultats publiés (BioBERT, SciBERT, PubMedBERT, BioLinkBERT, LLM). |
| 2026-10-30 | État de l'art : ajout du fonctionnement des références (CRF + lexiques, transformeurs pré-entraînés, scispaCy, LLM). |
| 2026-10-30 | APP-REC-v2 (essai) : union BM25 + dense reclassée par un cross-encoder multilingue ; Rappel@5 DEV inchangé (0,875), ≈ 2 s par question ; non retenu, la recherche dense seule reste l'approfondissement. |
| 2026-10-30 | Gel QA : socle BM25 REC-v2 + Q0 / Q1 v1 / Q2 v1, contexte c2 ; approfondissement Q2 v1 c2 dense (`qa_config_gelee.json`). BLEU/ROUGE sur DEV (Q2 v1 c2 : BLEU 16,2, ROUGE-L 0,36) ; notebook 5 (tableaux 3, 4, grille) prêt, TEST à exécuter avec la clé. |
| 2026-11-01 | Évaluation TEST du QA (notebook 5, une seule fois) : recherche BM25 Hit@5 0,875 / Rappel@5 0,771, dense 1,000 / 0,771 (avantage DEV non confirmé) ; BLEU Q0 5,4, Q1 10,0, Q2 10,1, Q2 dense 14,0 ; grille manuelle créée (30 réponses anonymisées). |
| 2026-11-06 | Test comparatif Q0 / Q1 / Q2 sur une question libre (chimiothérapie adjuvante / néoadjuvante, cancer du sein), configuration figée : Q1 et Q2 justes et cités, aucun ne signale que le corpus ne parle pas du cancer du sein en particulier. |
| 2026-11-06 | LLM-v3 (essai après coup, DEV) : Q2 avec 3 / 5 / 10 passages BM25 ; k = 3 perd Q008 et Q014 (abstentions à tort), k = 10 donne une réponse non soutenue sur Q016 ; ROUGE-L 0,31 / 0,36 / 0,37 ; k = 5 conservé, configuration figée inchangée. |
| 2026-11-06 | Double annotation négation terminée (TOMAS) : accord 0,75, kappa 0,51, 5 désaccords dans `desaccords_annotation.csv`, résolution à faire ensemble ; référence encore provisoire. |
| 2026-11-06 | Désaccords de négation résolus ensemble : référence finale identique aux labels de génération ; score TEST NEG-v0 final inchangé (moyenne des deux F1 = 0,80), tableau 2 du notebook 5 et erreurs commentées mis à jour. |
| 2026-11-06 | LLM-MIS-v1 : les 192 prompts QA (DEV, TEST, question libre) renvoyés à `mistral-medium-2604` (notebook 4.4) ; TEST Q2 ROUGE-L 0,359 contre 0,325 (OpenAI), 2/2 abstentions correctes ; mêmes erreurs dues à la recherche ; configuration figée inchangée. |
| 2026-11-06 | Notebook 5 : section « Comparaison avec un second LLM : Mistral (TEST) » après le tableau 4, qui relit les réponses de LLM-MIS-v1 (mêmes chiffres que le notebook 4.4, aucun nouvel appel). |
| 2026-11-08 | Rapport rédigé en trois notebooks (`rapport/1_extraction.ipynb`, `2_negation.ipynb`, `3_question_reponse.ipynb`) : cheminement, résultats et interprétations ; scores recalculés à l'identique des versions figées, aucune méthode modifiée, aucun appel à l'API. |
| 2026-11-09 | Grille de lecture QA (30 réponses TEST) notée par un juge LLM sans contexte du projet (deux juges indépendants, notes identiques, un seul jeu gardé : colonnes `_juge`) ; exactitude moyenne Q0 1,4, Q1 1,4, Q2 1,7. |
| 2026-11-09 | Notebooks du rapport rendus autonomes : tout est recalculé depuis `CDR_Data/`, `data/sources_qa/`, les annotations et `src/` (APP-v3 rechargé et reprédit, LLM via le cache) ; résultats identiques aux versions figées (prédictions TEST extraction et QA identiques aux livrables). `src/dictionnaire_v3.py` : options pour retrouver DIC-v1/v2 et chaque ajout ; `src/apprise.py` : fonction `entrainer` ; `src/qa_llm.py` : texte des consignes `PROMPTS`. Aucune méthode modifiée. |
| 2026-11-10 | Figures de l'oral (`figures_oral/`, 15 PNG, script `generer_figures.py`) à partir des chiffres figés. HYB-v1 (essai) : combinaisons DIC-v3 + APP-v3 sur VALIDATION (intersection 0,818, union 0,891, ajouts sans chevauchement 0,908) ; aucune ne dépasse APP-v3 (0,912), non retenu. Aucune méthode figée modifiée. |
| 2026-11-11 | DIC-v4 (notebook 2.3c, `src/mesh.py`, `src/dictionnaire_v4.py`) : DIC-v3 + lexique MeSH 2026 (descripteurs + concepts supplémentaires), filtré par branche et par terme sur TRAIN ; F1 VALIDATION 0,7993 → 0,8847 (Chemical 0,917, Disease 0,842). Prédictions TEST écrites, non scorées. DIC-v3 reste la version évaluée sur TEST. |
| 2026-11-11 | Évaluation TEST de DIC-v4 (notebook 5, tableau 1, une seule fois) : F1 0,8890 (Chemical 0,9232, Disease 0,8464) ; DIC-v4 remplace DIC-v3 comme version figée (`scores_test.csv`, `data/predictions_extraction.jsonl`). Rapport `rapport/1_extraction.ipynb` mis à jour (section 4.4 DIC-v4, comparaisons et conclusion). Lignes APP-v3 inchangées. |
| 2026-11-11 | Figures de l'oral mises à jour pour DIC-v4 (figures 01, 02, 03, 04, 07, 08, 14 ; nouvelle figure 16 : construction de DIC-v4) et plan `rapport/plan_oral.md`. HYB-v2 (essai) : combinaisons DIC-v4 + APP-v3 sur VALIDATION (intersection 0,897, union 0,900, ajouts sans chevauchement 0,905) ; aucune ne dépasse APP-v3 (0,912), non retenu. Aucune méthode figée modifiée. |
| 2026-11-11 | Application Streamlit passée à DIC-v4 (`DictionnaireV4Fige` : DIC-v3 + termes MeSH retenus, lus dans `dictionnaire_v4_termes_mesh.tsv.gz` écrit par le notebook 2.3c) ; mêmes 9 550 prédictions TEST que le notebook 2.3c, démarrage ≈ 11 s comme DIC-v3. Notebook 2.3c réexécuté (prédictions identiques). Aucune méthode modifiée. |
