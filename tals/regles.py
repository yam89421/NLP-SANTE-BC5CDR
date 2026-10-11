"""Extraction par règles : dictionnaires et expressions régulières.

Version unique du motif de quantité, partagée par les notebooks du module 1.
Auparavant deux copies divergentes circulaient (`[ \\t]` contre
`[ \\t\\u00a0]`, `mg` contre `mg|g`) : une correction sur l'une ne
s'appliquait pas à l'autre.
"""
from __future__ import annotations

import re

from .spans import Mention, cle_normalisee, tokeniser_avec_offsets

__all__ = ["compiler_quantite", "extraire_quantites", "ExtracteurDictionnaire"]

#: Motif naïf du début de cours : il illustre les défauts, il n'est pas un contrat.
MOTIF_NAIF = re.compile(r"\b[0-9]+(?:[.,][0-9]+)?\s*mg\b")


def compiler_quantite(unites: str = r"mg|g") -> re.Pattern:
    """Motif contrôlé pour une quantité simple, non signée.

    Contrat explicite :
      - accepte  : entier ou décimale, espace horizontal ou insécable facultatif,
                   unité parmi `unites`, casse indifférente ;
      - refuse   : un début à l'intérieur d'un nombre ou après un signe
                   (`(?<![\\w.,+\\-])`), une unité suivie de `/`
                   (`(?![ \\t\\u00a0]*/)`), donc les concentrations ;
      - **ne traite pas** les intervalles : « 5 à 10 mg » donne encore « 10 mg ».

    Cette limite est connue et assumée : une amélioration locale n'est pas une
    grammaire des posologies.
    """
    return re.compile(
        r"(?<![\w.,+\-])"
        r"(?P<valeur>[0-9]+(?:[.,][0-9]+)?)"
        r"[ \t ]*(?P<unite>" + unites + r")\b"
        r"(?![ \t ]*/)",
        re.IGNORECASE,
    )


def extraire_quantites(texte: str, motif: re.Pattern | None = None) -> list[dict]:
    """Extrait les quantités avec leurs offsets dans le texte original.

    Chaque sortie est contrôlée : la tranche du texte doit reproduire
    exactement la surface trouvée. Convertir la valeur en `float` ne modifie
    jamais le texte qui porte les indices.
    """
    motif = motif if motif is not None else compiler_quantite()
    sorties = []
    for m in motif.finditer(texte):
        debut, fin = m.span()
        assert texte[debut:fin] == m.group(0), "Offsets désalignés du texte source."
        sorties.append({
            "surface": m.group(0),
            "debut": debut,
            "fin": fin,
            "valeur": float(m.group("valeur").replace(",", ".")),
            "unite": m.group("unite").lower(),
        })
    return sorties


class ExtracteurDictionnaire:
    """Extracteur par dictionnaire, avec arbitrage de recouvrement explicite.

    Politique appliquée : à un même point de départ, la correspondance la plus
    longue gagne ; les correspondances qui se recouvrent ensuite sont écartées.
    C'est un choix déterministe, correct **seulement** s'il correspond au guide
    d'annotation du corpus.

    La recherche se fait sur une suite de tokens, pas sur une sous-chaîne brute :
    un test de sous-chaîne reconnaîtrait « rein » dans « frein ».
    """

    def __init__(self, entrees: dict[str, str], sans_accents: bool = False):
        self.sans_accents = sans_accents
        self.entrees = {
            tuple(cle_normalisee(t, sans_accents) for t in forme.split()): type_entite
            for forme, type_entite in entrees.items()
        }
        self.longueur_max = max((len(k) for k in self.entrees), default=0)

    def extraire(self, texte: str, doc: str = "doc") -> set[Mention]:
        tokens = tokeniser_avec_offsets(texte)
        cles = [cle_normalisee(s, self.sans_accents) for s, _, _ in tokens]
        candidats: list[Mention] = []
        for i in range(len(tokens)):
            for n in range(min(self.longueur_max, len(tokens) - i), 0, -1):
                type_entite = self.entrees.get(tuple(cles[i:i + n]))
                if type_entite is not None:
                    candidats.append(
                        Mention(doc, tokens[i][1], tokens[i + n - 1][2], type_entite)
                    )
                    break  # plus longue correspondance à ce point de départ
        retenues: list[Mention] = []
        for mention in sorted(candidats, key=lambda m: (m.debut, -m.longueur)):
            if all(mention.debut >= r.fin or r.debut >= mention.fin for r in retenues):
                retenues.append(mention)
        return set(retenues)
