"""Méthode par dictionnaire et règles pour BC5CDR (section 2.3 du livret).

Reprend la politique de `tals.regles.ExtracteurDictionnaire` (cours) : recherche
sur une suite de tokens, plus longue correspondance à un même point de départ,
puis rejet des correspondances qui en recouvrent une déjà retenue.

Modifications apportées au code du cours :
  - les formes du dictionnaire sont découpées avec le même tokeniseur que le
    texte (le cours découpait sur les espaces, si bien que « alpha-methyldopa »
    ou « 5-FU » n'étaient jamais retrouvés) ;
  - une forme annotée avec deux types reçoit son type majoritaire dans TRAIN ;
  - filtre optionnel par taux d'annotation mesuré sur TRAIN : une forme est
    gardée seulement si, parmi ses occurrences dans les textes de TRAIN, la part
    annotée atteint le seuil (« cocaine » ~1, « drug » ou « lead » plus bas) ;
  - expressions régulières optionnelles sur des suffixes de surface, de priorité
    inférieure au dictionnaire.
Le texte n'est jamais modifié : la normalisation ne porte que sur les clés.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass

from tals import Mention, cle_normalisee, tokeniser_avec_offsets

# Suffixes de surface fréquents (dénominations communes de médicaments, termes
# pathologiques). Retenus seulement s'ils améliorent le F1 sur VALIDATION.
REGEX = {
    "Chemical": re.compile(
        r"\b[A-Za-z][a-z]{2,}(?:mycin|micin|cillin|cycline|azole|olol|pril|sartan|platin|statin|"
        r"tidine|azepam|azolam|caine|profen|oxacin|vudine|navir|parin|semide|thiazide|triptyline|"
        r"pramine|peridol|zodone|xetine|barbital)\b"),
    "Disease": re.compile(
        r"\b[A-Za-z][a-z]{2,}(?:itis|emia|aemia|pathy|toxicity|algia|plegia|penia|cytosis|"
        r"trophy|oma|uria)\b"),
}


@dataclass
class ConfigDictionnaire:
    casse: str = "insensible"      # "exacte" ou "insensible"
    seuil_annotation: float = 0.0  # taux d'annotation minimal dans TRAIN
    regex: bool = False

    def nom(self) -> str:
        return f"casse={self.casse}, seuil={self.seuil_annotation}, regex={'oui' if self.regex else 'non'}"


class DictionnaireCDR:
    def __init__(self, config: ConfigDictionnaire):
        self.config = config
        self.entrees: dict[tuple, str] = {}
        self.stats: dict[tuple, dict] = {}
        self.longueur_max = 0

    def _cle(self, surface: str) -> tuple:
        toks = [s for s, _, _ in tokeniser_avec_offsets(surface)]
        if self.config.casse == "insensible":
            toks = [cle_normalisee(t) for t in toks]
        return tuple(toks)

    # --- construction sur TRAIN uniquement ---------------------------------
    def construire(self, documents_train) -> "DictionnaireCDR":
        types = defaultdict(Counter)
        for d in documents_train:
            for m in d.mentions:
                types[self._cle(m.texte)][m.type] += 1
        self.entrees = {cle: c.most_common(1)[0][0] for cle, c in types.items() if cle}
        self.longueur_max = max(len(k) for k in self.entrees)

        # Taux d'annotation : correspondances trouvées dans TRAIN qui coïncident
        # exactement avec une annotation du même type.
        trouvees, annotees = Counter(), Counter()
        for d in documents_train:
            ref = {(m.debut, m.fin, m.type) for m in d.mentions}
            for cle, debut, fin, type_ in self._correspondances(d.texte):
                trouvees[cle] += 1
                annotees[cle] += (debut, fin, type_) in ref
        self.stats = {
            cle: {"type": t, "annotations": sum(types[cle].values()),
                  "occurrences": trouvees[cle], "taux": annotees[cle] / trouvees[cle] if trouvees[cle] else 0.0}
            for cle, t in self.entrees.items()
        }
        seuil = self.config.seuil_annotation
        self.entrees = {cle: t for cle, t in self.entrees.items() if self.stats[cle]["taux"] >= seuil}
        self.longueur_max = max(len(k) for k in self.entrees)
        return self

    # --- recherche -----------------------------------------------------------
    def _correspondances(self, texte: str):
        """Plus longue correspondance du dictionnaire à chaque point de départ."""
        tokens = tokeniser_avec_offsets(texte)
        cles = [s if self.config.casse == "exacte" else cle_normalisee(s) for s, _, _ in tokens]
        for i in range(len(tokens)):
            for n in range(min(self.longueur_max, len(tokens) - i), 0, -1):
                cle = tuple(cles[i:i + n])
                type_ = self.entrees.get(cle)
                if type_ is not None:
                    yield cle, tokens[i][1], tokens[i + n - 1][2], type_
                    break

    def extraire(self, texte: str, doc: str) -> set[Mention]:
        candidats = [Mention(doc, a, b, t) for _, a, b, t in self._correspondances(texte)]
        retenues: list[Mention] = []
        for m in sorted(candidats, key=lambda m: (m.debut, -m.longueur)):
            if all(m.debut >= r.fin or r.debut >= m.fin for r in retenues):
                retenues.append(m)
        if self.config.regex:  # priorité inférieure : seulement hors des mentions retenues
            for type_, motif in REGEX.items():
                for r in motif.finditer(texte):
                    m = Mention(doc, r.start(), r.end(), type_)
                    if all(m.debut >= x.fin or x.debut >= m.fin for x in retenues):
                        retenues.append(m)
        return set(retenues)

    def extraire_corpus(self, documents) -> set[Mention]:
        sortie = set()
        for d in documents:
            sortie |= self.extraire(d.texte, d.document_id)
        return sortie
