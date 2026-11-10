# rapport/

**Rapport sous forme de trois notebooks autonomes**, à exécuter depuis ce dossier (venv du TD, `pip install -r
../requirements.txt` pour `sacrebleu` et `rouge-score`) :

| Notebook | Contenu | Exécution (CPU) |
|---|---|---|
| `1_extraction.ipynb` | BC5CDR, dictionnaire et règles (DIC-v1 → v3), modèle appris (APP-v1 → v3), TEST, état de l'art, erreurs | ≈ 20 min |
| `2_negation.ipynb` | règles NegEx figées, 20 phrases, double annotation et kappa, test, erreurs | quelques secondes |
| `3_question_reponse.ipynb` | corpus INCa, questions, BM25 / recherche dense, Q0/Q1/Q2, TEST, grille, essais (passages, question libre, Mistral) | ≈ 6 min |

Ils remplacent les notebooks de travail de `notebooks/` : tout est recalculé à partir des **données d'origine**
(`CDR_Data/`, `data/sources_qa/`, `data/corpus.csv`, `data/negation.jsonl`), de **nos annotations** (questions
`data/questions_*.jsonl`, feuilles d'annotation de la négation, grille de lecture `resultats/qa/grille_manuelle.csv`)
et du code `src/` + `tals/`. Ne sont pas recalculés :
- les **entraînements BERT** (GPU) : le modèle figé `modeles/apprise_v3` est rechargé et prédit en direct ; les courbes
  de réglage d'APP-v1 à v3 sont celles enregistrées pendant les entraînements (`resultats/extraction/apprise*_reglage_validation.csv`) ;
  une cellule optionnelle (`REENTRAINER = True`) réentraîne APP-v3 sur GPU ;
- les **réponses des LLM**, servies par le cache des requêtes (`resultats/qa/cache_llm*.json`) : un prompt absent du
  cache est envoyé à l'API avec la clé de `.env`.

Sorties écrites dans `sorties/` : `passages.jsonl`, `predictions_extraction.jsonl`, `predictions_qa.jsonl` (identiques
aux livrables de `data/`).


Rapport final (8 à 12 pages hors annexes), déposé pour le jalon QA2 du 13/11/2026.

Plan attendu (barème, section 7.2 du livret) :
1. Définition des tâches, périmètres et exemples
2. Description des corpus et de la construction des annotations QA
3. Synthèse des comparaisons et des décisions
4. Analyse des erreurs, limites et coûts
5. Clarté, références et reproductibilité

Les corpus complets et sorties détaillées restent dans les fichiers zip joints, pas dans le rapport.

Autres documents :

- `fiche_cadrage.md`, `cadrage_qa.md` — cadrage (jalon E).
- `guide_redaction_qa.md` — guide de rédaction des questions QA et désaccords de relecture.
- `synthese_QA1.md` — synthèse du jalon QA1 (documents, questions, recherche sur DEV).
