"""Lecture du corpus BC5CDR (BioCreative V CDR, version v010516) au format PubTator.

Conventions retenues pour tout le projet (identiques pour les deux méthodes) :
  - texte d'un document = titre + " " + résumé, exactement comme dans PubTator ;
  - positions en caractères, à partir de zéro, intervalle semi-ouvert [debut, fin[ ;
  - catégories : Chemical et Disease ;
  - mention composite (« ovarian and testicular cancer ») : conservée telle
    qu'annotée, comme une seule mention continue ; elle est signalée par
    `composite=True` mais jamais découpée ni fusionnée ;
  - les lignes de relation (CID) sont ignorées : les relations sont hors socle.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

CATEGORIES = ["Chemical", "Disease"]

# Partitions officielles : fichier PubTator -> nom de partition du projet.
FICHIERS = {
    "train": "CDR_TrainingSet.PubTator.txt",
    "validation": "CDR_DevelopmentSet.PubTator.txt",
    "test": "CDR_TestSet.PubTator.txt",
}

_LIGNE_TEXTE = re.compile(r"^(\d+)\|([ta])\|(.*)$")


@dataclass
class MentionCDR:
    debut: int
    fin: int
    texte: str
    type: str
    identifiants: str          # identifiants MeSH, "|" pour une mention composite, "-1" si absent
    composite: bool = False
    sous_mentions: list[str] = field(default_factory=list)


@dataclass
class DocumentCDR:
    document_id: str           # PMID
    partition: str
    titre: str
    resume: str
    mentions: list[MentionCDR] = field(default_factory=list)

    @property
    def texte(self) -> str:
        return f"{self.titre} {self.resume}"


def lire_pubtator(chemin: Path, partition: str) -> list[DocumentCDR]:
    """Lit un fichier PubTator et vérifie chaque position au chargement."""
    documents: dict[str, DocumentCDR] = {}
    with open(chemin, encoding="utf-8") as f:
        for numero, ligne in enumerate(f, start=1):
            ligne = ligne.rstrip("\n")
            if not ligne:
                continue
            m = _LIGNE_TEXTE.match(ligne)
            if m:
                pmid, champ, contenu = m.groups()
                doc = documents.setdefault(pmid, DocumentCDR(pmid, partition, "", ""))
                if champ == "t":
                    doc.titre = contenu
                else:
                    doc.resume = contenu
                continue
            colonnes = ligne.split("\t")
            if len(colonnes) >= 4 and colonnes[1] == "CID":
                continue
            if len(colonnes) < 6:
                raise ValueError(f"{chemin.name}:{numero} : ligne inattendue {ligne!r}")
            pmid, debut, fin, surface, type_, ids = colonnes[:6]
            sous = colonnes[6].split("|") if len(colonnes) > 6 else []
            documents[pmid].mentions.append(MentionCDR(
                int(debut), int(fin), surface, type_, ids,
                composite=bool(sous), sous_mentions=sous,
            ))

    for doc in documents.values():
        for men in doc.mentions:
            if doc.texte[men.debut:men.fin] != men.texte:
                raise ValueError(
                    f"Position décalée dans {doc.document_id} : "
                    f"[{men.debut}, {men.fin}[ = {doc.texte[men.debut:men.fin]!r} ≠ {men.texte!r}"
                )
        doc.mentions.sort(key=lambda x: (x.debut, x.fin))
    return list(documents.values())


def charger_cdr(dossier: Path) -> dict[str, list[DocumentCDR]]:
    """Charge les trois partitions officielles : {"train": [...], "validation": [...], "test": [...]}."""
    dossier = Path(dossier)
    return {nom: lire_pubtator(dossier / fichier, nom) for nom, fichier in FICHIERS.items()}


def mentions_reference(documents, categories=CATEGORIES):
    """Ensemble de `tals.Mention` (doc, debut, fin, type) servant de référence au scoreur."""
    from tals import Mention
    return {
        Mention(d.document_id, m.debut, m.fin, m.type)
        for d in documents for m in d.mentions if m.type in categories
    }


# Découpage en phrases simple, avec positions dans le texte du document.
# Il sert à compter les phrases sans mention et à fenêtrer les textes pour la
# méthode apprise ; il peut couper après certaines abréviations (« i.v. »),
# sans conséquence sur les positions, qui restent celles du document.
_FIN_PHRASE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\[])")


def decouper_phrases(texte: str) -> list[tuple[int, int]]:
    bornes, debut = [], 0
    for m in _FIN_PHRASE.finditer(texte):
        bornes.append((debut, m.start()))
        debut = m.end()
    bornes.append((debut, len(texte)))
    return [(a, b) for a, b in bornes if b > a]


def sauvegarder_jsonl(documents, chemin: Path) -> None:
    with open(chemin, "w", encoding="utf-8") as f:
        for d in documents:
            ligne = {"document_id": d.document_id, "partition": d.partition, "texte": d.texte,
                     "longueur_titre": len(d.titre),
                     "mentions": [asdict(m) for m in d.mentions], "unite_positions": "caracteres"}
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")


def charger_jsonl(chemin: Path) -> list[DocumentCDR]:
    documents = []
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            o = json.loads(ligne)
            n = o["longueur_titre"]
            documents.append(DocumentCDR(
                o["document_id"], o["partition"], o["texte"][:n], o["texte"][n + 1:],
                [MentionCDR(**m) for m in o["mentions"]],
            ))
    return documents
