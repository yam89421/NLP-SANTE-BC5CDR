"""Rapprochement de formes : racinisation naïve, distances, similarités.

Le module 1 le répète : ces mesures *génèrent des candidats*. Aucune ne
démontre une synonymie ni une équivalence thérapeutique.
"""
from __future__ import annotations

__all__ = [
    "stem_naif",
    "levenshtein",
    "matrice_levenshtein",
    "damerau_levenshtein",
    "hamming",
    "sim_levenshtein",
    "bigrammes",
    "jaccard",
]


def stem_naif(mot: str) -> str:
    """Retire un « s » final. Règle pédagogique, **pas** un stemmer réel.

    Elle rapproche « patients » de « patient » et abîme « virus ». Snowball
    (`nltk.stem.snowball.FrenchStemmer`) utilise des conditions bien plus fines ;
    le stemmer de Porter vise l'anglais et ne convient pas au français.
    """
    return mot[:-1] if mot.endswith("s") else mot


def matrice_levenshtein(a: str, b: str) -> list[list[int]]:
    """Table complète de programmation dynamique, D[i][j] pour les préfixes."""
    D = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        D[i][0] = i
    for j in range(len(b) + 1):
        D[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,                                # suppression
                D[i][j - 1] + 1,                                # insertion
                D[i - 1][j - 1] + int(a[i - 1] != b[j - 1]),    # substitution
            )
    return D


def levenshtein(a: str, b: str) -> int:
    """Distance d'édition unitaire. Coût O(len(a)*len(b)) en temps."""
    return matrice_levenshtein(a, b)[-1][-1]


def damerau_levenshtein(a: str, b: str) -> int:
    """Variante OSA : ajoute la transposition de deux caractères adjacents.

    C'est la version *restreinte* (Optimal String Alignment), qui interdit de
    rééditer une zone déjà transposée. Ne pas la confondre avec la version
    complète de Damerau--Levenshtein.
    """
    D = matrice_levenshtein(a, b)
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + int(a[i - 1] != b[j - 1]),
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)
    return D[-1][-1]


def hamming(a: str, b: str) -> int:
    """Nombre de positions différentes. Exige des longueurs égales."""
    if len(a) != len(b):
        raise ValueError(
            "Hamming exige des chaînes de même longueur : "
            f"{len(a)} et {len(b)}. Utiliser Levenshtein pour insertion/suppression."
        )
    return sum(x != y for x, y in zip(a, b))


def sim_levenshtein(a: str, b: str) -> float:
    """Similarité normalisée 1 - d/max(|a|,|b|), avec sim('','') = 1.

    Rend visible qu'une édition pèse lourd sur une chaîne courte et peu sur une
    chaîne longue. Ce n'est pas une probabilité d'équivalence.
    """
    if not a and not b:
        return 1.0
    return 1 - levenshtein(a, b) / max(len(a), len(b))


def bigrammes(chaine: str) -> set[str]:
    """Ensemble des bigrammes de caractères, sans symboles de frontière."""
    return {chaine[i:i + 2] for i in range(len(chaine) - 1)}


def jaccard(a: str, b: str, n: int = 2) -> float:
    """Similarité de Jaccard sur les n-grammes de caractères.

    Convention annoncée : deux ensembles vides donnent 1.0. L'usage d'ensembles
    ignore les répétitions ; compter les occurrences définirait une autre mesure.
    """
    A = {a[i:i + n] for i in range(len(a) - n + 1)}
    B = {b[i:i + n] for i in range(len(b) - n + 1)}
    if not (A | B):
        return 1.0
    return len(A & B) / len(A | B)
