"""Évaluation stricte au niveau des mentions.

Une prédiction est correcte si document, début, fin et type coïncident avec une
annotation de référence. Le module 1 rappelle pourquoi l'accuracy des tokens
peut tromper : ici, l'unité de score est la mention, jamais le token.

Conventions annoncées, comme l'exige le protocole du cours :
  - dénominateur nul -> score 0.0 (et non « non défini » silencieux) ;
  - micro : on additionne TP/FP/FN sur toutes les classes avant les ratios ;
  - macro : on moyenne les F1 par classe, sur les classes présentes dans la
    référence ou dans la prédiction.
"""
from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Scores", "scores", "scores_par_type", "erreurs", "tableau_comparatif"]


@dataclass(frozen=True)
class Scores:
    TP: int
    FP: int
    FN: int
    precision: float
    rappel: float
    F1: float
    support: int = 0

    def __str__(self) -> str:
        return (
            f"P={self.precision:.4f} R={self.rappel:.4f} F1={self.F1:.4f} "
            f"(TP={self.TP} FP={self.FP} FN={self.FN})"
        )


def _ratios(tp: int, fp: int, fn: int) -> Scores:
    precision = tp / (tp + fp) if tp + fp else 0.0
    rappel = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    return Scores(tp, fp, fn, precision, rappel, f1, support=tp + fn)


def scores(reference, prediction) -> Scores:
    """Score micro strict sur des ensembles de `Mention`."""
    reference, prediction = set(reference), set(prediction)
    return _ratios(
        len(reference & prediction),
        len(prediction - reference),
        len(reference - prediction),
    )


def scores_par_type(reference, prediction) -> dict[str, Scores]:
    """Scores stricts par type d'entité, plus les lignes 'micro' et 'macro'."""
    reference, prediction = set(reference), set(prediction)
    types = sorted({m.type for m in reference | prediction})

    resultat: dict[str, Scores] = {}
    for type_entite in types:
        ref_t = {m for m in reference if m.type == type_entite}
        pred_t = {m for m in prediction if m.type == type_entite}
        resultat[type_entite] = scores(ref_t, pred_t)

    resultat["micro"] = scores(reference, prediction)
    if types:
        # Macro : on moyenne les scores par classe. Les comptes TP/FP/FN ne
        # s'additionnent pas dans cette moyenne ; on reporte ceux du micro pour
        # que la ligne reste lisible sans laisser croire à des zéros mesurés.
        n = len(types)
        resultat["macro"] = Scores(
            resultat["micro"].TP,
            resultat["micro"].FP,
            resultat["micro"].FN,
            sum(resultat[t].precision for t in types) / n,
            sum(resultat[t].rappel for t in types) / n,
            sum(resultat[t].F1 for t in types) / n,
            support=sum(resultat[t].support for t in types),
        )
    return resultat


def erreurs(reference, prediction, textes=None) -> dict[str, list]:
    """Décompose les erreurs pour l'analyse demandée au chapitre évaluation.

    Catégories : frontiere (même document, même type, intervalles qui se
    recouvrent sans coïncider), type (mêmes frontières, type différent),
    manquee (aucun recouvrement côté référence), parasite (aucun recouvrement
    côté prédiction).
    """
    reference, prediction = set(reference), set(prediction)
    corrects = reference & prediction
    ref_restant = reference - corrects
    pred_restant = prediction - corrects

    sortie: dict[str, list] = {
        "correcte": sorted(corrects),
        "frontiere": [],
        "type": [],
        "manquee": [],
        "parasite": [],
    }
    apparies_pred: set = set()
    for att in sorted(ref_restant):
        candidat = None
        for obt in sorted(pred_restant - apparies_pred):
            if obt.doc != att.doc:
                continue
            if obt.debut < att.fin and att.debut < obt.fin:
                candidat = obt
                break
        if candidat is None:
            sortie["manquee"].append(att)
            continue
        apparies_pred.add(candidat)
        meme_bornes = (candidat.debut, candidat.fin) == (att.debut, att.fin)
        sortie["type" if meme_bornes else "frontiere"].append((att, candidat))
    sortie["parasite"] = sorted(pred_restant - apparies_pred)

    if textes is not None:  # confort de lecture : ajouter les surfaces
        sortie["surfaces"] = {
            "manquee": [m.surface(textes[m.doc]) for m in sortie["manquee"]],
            "parasite": [m.surface(textes[m.doc]) for m in sortie["parasite"]],
        }
    return sortie


def tableau_comparatif(resultats: dict[str, Scores], cout: dict | None = None) -> str:
    """Rend un tableau texte comparant plusieurs chaînes sur le même TEST.

    Le chapitre évaluation insiste : le coût fait partie du résultat. Passer
    `cout={"nom": "1,2 s"}` ajoute la colonne correspondante.
    """
    largeur = max([len(n) for n in resultats] + [8])
    entete = f"{'Méthode'.ljust(largeur)}  {'P':>7} {'R':>7} {'F1':>7} {'TP':>4} {'FP':>4} {'FN':>4}"
    if cout:
        entete += f"  {'Coût':>10}"
    lignes = [entete, "-" * len(entete)]
    for nom, s in resultats.items():
        ligne = (
            f"{nom.ljust(largeur)}  {s.precision:7.4f} {s.rappel:7.4f} {s.F1:7.4f} "
            f"{s.TP:4d} {s.FP:4d} {s.FN:4d}"
        )
        if cout:
            ligne += f"  {str(cout.get(nom, '—')):>10}"
        lignes.append(ligne)
    return "\n".join(lignes)
