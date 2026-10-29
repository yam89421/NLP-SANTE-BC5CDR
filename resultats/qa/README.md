# resultats/qa/

Produits par `3_corpus_qa.ipynb` :

- `bilan_passages.csv` — par document : paragraphes, sections, passages, longueurs, mots.
- `controle_passages.csv` — contrôle manuel de dix passages (le plus court, le plus long, huit tirés avec la
  graine 42) : ordre du texte, nombres et unités, négations.

Produits par `4.1_recherche_lexicale_q0.ipynb` (DEV seulement) :

- `recherche_dev_variantes.csv` — 8 variantes BM25 sur DEV (texte indexé × mots vides × racinisation), moyennes.
- `recherche_dev_grille_k1_b.csv` — grille k1 × b sur la variante retenue.
- `recherche_dev.csv` — par question avec réponse : Hit@5, Rappel@5 (stricts et avec équivalents), couverture des
  éléments@5, rang de la première preuve.
- `predictions_q0_dev.jsonl` — Q0 sur les 20 questions DEV (top-5, passage transmis, réponse, durée).

Produit par `4.3_recherche_hybride.ipynb` (approfondissement, DEV) :

- `recherche_dev_hybride.csv` — BM25 REC-v2, dense (E5) et hybride RRF : mesures de recherche et temps.
- `recherche_dense_top5_dev.jsonl` — top-5 de la recherche dense (section + texte) pour les questions DEV.
- `recherche_dev_fusion_essais.csv` — essais de fusion favorisant la recherche dense (RRF pondérée, règle « grand écart »).

Produits par `4.2_llm_q1_q2.ipynb` (DEV seulement) :

- `predictions_llm_dev.jsonl` — Q1 et Q2 sur les 20 questions DEV, toutes versions de prompt (prompt exact,
  passages transmis, réponse brute, modèle, empreinte système, paramètres, tokens, durée).
- `predictions_llm_dev_dense.jsonl` — Q2 v1 c2 avec les passages de la recherche dense (approfondissement).
- `cache_llm.json` — cache des requêtes au LLM (empreinte SHA-256 → réponse), sans clé ni en-têtes.

À déposer ici (notebooks 4.1, 4.2 et 5_evaluation) :

- `recherche_dev.csv` — Hit@5, Rappel@5, couverture des éléments, sur DEV (questions répondables).
- `recherche_test.csv` — mêmes mesures sur TEST, après gel.
- `bleu_rouge.csv` — BLEU (corpus, 0–100) et ROUGE-1/2/L (F1 moyenné par question, 0–1) pour Q0/Q1/Q2.
- `grille_manuelle.csv` — jugements individuels des deux membres + décision finale (exactitude,
  complétude, citations, abstentions) sur les 30 réponses (10 questions × 3 configurations).
- `erreurs_commentees.md` — passage manqué, réponse incomplète, affirmation non soutenue, absence
  d'information, désaccord score automatique / lecture humaine.
