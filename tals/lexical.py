"""Représentations creuses : sac de mots, n-grammes, TF-IDF.

Point de vigilance corrigé ici : le polycopié et les diapositives emploient la
convention **non lissée** `idf(w) = ln(N / df(w))`, avec les valeurs publiées
0,4055 et 1,0986. C'est donc la valeur par défaut. `lissage=True` fournit la
variante `ln((N+1)/(df+1)) + 1` répandue dans les bibliothèques : les deux sont
disponibles précisément pour que l'écart soit observable, comme le cours le
demande (« indiquer la convention, pas seulement écrire TF-IDF »).
"""
from __future__ import annotations

import math
import re
from collections import Counter

__all__ = ["tokens", "bigrammes_mots", "Vectoriseur"]


def tokens(texte: str) -> list[str]:
    """Tokens alphabétiques Unicode en minuscules.

    Ce découpage écarte les chiffres : il convient à la démonstration TF-IDF,
    pas à l'extraction de doses. Aucun nettoyage n'est universel.
    """
    return re.findall(r"[^\W\d_]+", texte.lower())


def bigrammes_mots(texte: str) -> list[tuple[str, str]]:
    """Bigrammes de mots : rendent observable l'ordre que le sac de mots efface."""
    t = tokens(texte)
    return list(zip(t, t[1:]))


class Vectoriseur:
    """Sac de mots ou TF-IDF, ajusté sur TRAIN puis figé.

    L'API `ajuster` / `transformer` matérialise la règle du protocole : le
    vocabulaire et l'IDF viennent de TRAIN ; VALIDATION et TEST sont transformés
    avec ces paramètres fixés. Recalculer l'IDF sur le test serait une fuite.
    """

    def __init__(self, lissage: bool = False, normaliser: bool = False):
        self.lissage = lissage
        self.normaliser = normaliser
        self.vocabulaire: list[str] = []
        self.df: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.n_documents = 0

    def ajuster(self, documents) -> "Vectoriseur":
        documents = list(documents)
        self.n_documents = len(documents)
        self.vocabulaire = sorted({t for d in documents for t in tokens(d)})
        self.df = {
            t: sum(t in set(tokens(d)) for d in documents) for t in self.vocabulaire
        }
        if self.lissage:
            self.idf = {
                t: math.log((self.n_documents + 1) / (self.df[t] + 1)) + 1
                for t in self.vocabulaire
            }
        else:
            self.idf = {
                t: math.log(self.n_documents / self.df[t]) for t in self.vocabulaire
            }
        return self

    def _verifier_ajuste(self) -> None:
        if not self.vocabulaire:
            raise RuntimeError("Appeler ajuster(train) avant de transformer.")

    def sac_de_mots(self, texte: str) -> list[float]:
        self._verifier_ajuste()
        tf = Counter(tokens(texte))
        return [float(tf[t]) for t in self.vocabulaire]

    def transformer(self, texte: str) -> list[float]:
        """Vecteur TF-IDF d'un document. Les formes hors vocabulaire sont ignorées."""
        self._verifier_ajuste()
        tf = Counter(tokens(texte))
        vecteur = [tf[t] * self.idf[t] for t in self.vocabulaire]
        if self.normaliser:
            norme = math.sqrt(sum(x * x for x in vecteur))
            if norme > 0:
                vecteur = [x / norme for x in vecteur]
        return vecteur
