"""Format des prédictions d'extraction et scoreur commun aux deux méthodes.

Le scoreur repose sur `tals.evaluation` (cours) : une mention est correcte si
document, début, fin et type coïncident ; chaque prédiction est appariée au plus
une fois (comparaison d'ensembles) ; le global est une micro-moyenne (comptes
additionnés avant les ratios) ; un dénominateur nul donne 0, signalé dans la
colonne `denominateur_nul`.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

from tals import Mention, scores_par_type

from .cdr import CATEGORIES


def ecrire_predictions(mentions, methode: str, documents, chemin: Path) -> None:
    """Une ligne par (méthode, document, catégorie), segments vides compris (gabarit du guide)."""
    textes = {d.document_id: d.texte for d in documents}
    par_cle = defaultdict(list)
    for m in sorted(mentions):
        par_cle[(m.doc, m.type)].append(m)
    with open(chemin, "w", encoding="utf-8") as f:
        for d in documents:
            for cat in CATEGORIES:
                segments = [{"texte": textes[m.doc][m.debut:m.fin], "debut": m.debut, "fin": m.fin}
                            for m in par_cle.get((d.document_id, cat), [])]
                f.write(json.dumps({"methode": methode, "document_id": d.document_id, "categorie": cat,
                                    "segments": segments, "unite_positions": "caracteres"},
                                   ensure_ascii=False) + "\n")


def lire_predictions(chemin: Path, methode: str | None = None) -> set[Mention]:
    mentions = set()
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            o = json.loads(ligne)
            if methode is not None and o["methode"] != methode:
                continue
            for s in o["segments"]:
                mentions.add(Mention(o["document_id"], s["debut"], s["fin"], o["categorie"]))
    return mentions


def tableau_scores(reference, prediction, methode: str, partition: str, temps_s: float | None = None) -> pd.DataFrame:
    """VP/FP/FN/P/R/F1 par catégorie puis micro-moyenne globale."""
    resultats = scores_par_type(reference, prediction)
    lignes = []
    for cle in CATEGORIES + ["micro"]:
        s = resultats.get(cle)
        if s is None:
            continue
        lignes.append({
            "methode": methode, "partition": partition,
            "categorie": "global (micro)" if cle == "micro" else cle,
            "VP": s.TP, "FP": s.FP, "FN": s.FN,
            "precision": round(s.precision, 4), "rappel": round(s.rappel, 4), "F1": round(s.F1, 4),
            "denominateur_nul": (s.TP + s.FP == 0) or (s.TP + s.FN == 0),
            "temps_s": round(temps_s, 2) if temps_s is not None and cle == "micro" else None,
        })
    return pd.DataFrame(lignes)
