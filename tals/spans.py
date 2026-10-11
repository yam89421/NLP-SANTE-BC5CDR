"""Mentions localisées et alignement avec le texte source.

Convention du cours : indices de caractères Unicode, à partir de zéro,
intervalle semi-ouvert [debut, fin[. Le texte qui porte les offsets ne doit
jamais être réécrit ; on travaille sur des vues alignées.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

__all__ = [
    "Mention",
    "tokeniser_avec_offsets",
    "verifier_offsets",
    "cle_normalisee",
]


@dataclass(frozen=True, order=True)
class Mention:
    """Une occurrence textuelle localisée : (document, début, fin, type).

    L'identifiant de document fait partie de l'identité de la mention : deux
    documents peuvent porter la même position sans désigner la même chose.
    La classe est gelée, donc hachable : les comparaisons d'ensembles de
    l'évaluation stricte fonctionnent directement.
    """

    doc: str
    debut: int
    fin: int
    type: str

    def __post_init__(self) -> None:
        if self.debut < 0 or self.fin < self.debut:
            raise ValueError(f"Intervalle invalide : [{self.debut}, {self.fin}[")

    @property
    def longueur(self) -> int:
        return self.fin - self.debut

    def surface(self, texte: str) -> str:
        """Tranche du texte original désignée par la mention."""
        return texte[self.debut:self.fin]


def tokeniser_avec_offsets(texte: str, motif: str = r"\w+|[^\w\s]") -> list[tuple[str, int, int]]:
    """Découpe le texte en tokens en conservant leurs positions d'origine.

    Retourne une liste de (surface, debut, fin). Contrairement à une recherche
    par `texte.index(token)`, les offsets viennent du moteur de recherche
    lui-même : ils restent exacts même si un token se répète ou si le texte
    contient des apostrophes typographiques.
    """
    return [(m.group(0), m.start(), m.end()) for m in re.finditer(motif, texte)]


def verifier_offsets(texte: str, mentions, surfaces_attendues=None) -> None:
    """Vérifie que chaque mention désigne bien la surface attendue.

    Contrôle systématique recommandé par le module 1 : sans lui, un décalage
    d'alignement passe inaperçu jusqu'à l'évaluation finale.
    """
    for i, mention in enumerate(mentions):
        if mention.fin > len(texte):
            raise ValueError(f"{mention} dépasse la longueur du texte ({len(texte)}).")
        if surfaces_attendues is not None:
            obtenue = mention.surface(texte)
            attendue = surfaces_attendues[i]
            if obtenue != attendue:
                raise ValueError(
                    f"{mention} donne {obtenue!r}, attendu {attendue!r}."
                )


def cle_normalisee(forme: str, sans_accents: bool = False) -> str:
    """Clé de recherche normalisée, sans toucher au texte qui porte les offsets.

    NFC harmonise des écritures Unicode équivalentes ; il ne supprime pas les
    accents. `sans_accents=True` est une opération supplémentaire, destructive :
    elle rapproche « fievre » de « fièvre » mais efface une distinction.
    """
    cle = unicodedata.normalize("NFC", forme).casefold()
    if sans_accents:
        decompose = unicodedata.normalize("NFD", cle)
        cle = "".join(c for c in decompose if not unicodedata.combining(c))
    return cle
