# resultats/qa/

À déposer ici (notebooks 4.1, 4.2 et 5_evaluation) :

- `recherche_dev.csv` — Hit@5, Rappel@5, couverture des éléments, sur DEV (questions répondables).
- `recherche_test.csv` — mêmes mesures sur TEST, après gel.
- `bleu_rouge.csv` — BLEU (corpus, 0–100) et ROUGE-1/2/L (F1 moyenné par question, 0–1) pour Q0/Q1/Q2.
- `grille_manuelle.csv` — jugements individuels des deux membres + décision finale (exactitude,
  complétude, citations, abstentions) sur les 30 réponses (10 questions × 3 configurations).
- `erreurs_commentees.md` — passage manqué, réponse incomplète, affirmation non soutenue, absence
  d'information, désaccord score automatique / lecture humaine.
