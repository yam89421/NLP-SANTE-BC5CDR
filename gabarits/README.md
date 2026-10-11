# Gabarits

Ces fichiers illustrent, avec des exemples **fictifs**, les formats attendus décrits dans le guide
pratique (annexe A). Copiez la structure dans `data/` et `manifest.json` puis remplacez le contenu
par vos vraies données. Ne laissez aucun exemple fictif dans les fichiers finaux du dépôt.

- `corpus.csv`, `passages.jsonl` : catalogue et passages QA.
- `questions_dev.jsonl`, `questions_test.jsonl` : reprend l'exemple du guide (section A.1), plus une
  question à deux passages et une question sans réponse.
- `negation.jsonl` : reprend l'exemple du livret (« Pas de fièvre, mais une toux. ») et illustre aussi
  une coordination et un cas « impossible d'exclure ».
- `predictions_extraction.jsonl`, `predictions_qa.jsonl` : format de sortie attendu pour le scoring.
- `manifest.json` : exemple entièrement rempli (corpus fictif « BC5CDR », thème QA fictif).
