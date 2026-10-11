"""Chargement du mini-corpus fictif partagé par les trois modules.

Un seul corpus pour les trois modules : c'est ce qui rend possible la
comparaison demandée par le chapitre évaluation (« comparer des chaînes
complètes sur les mêmes sorties »). Tant que chaque notebook gardait ses
propres données jouets, aucune comparaison n'était possible.

Les textes sont **fictifs**, écrits pour l'enseignement. Les partitions sont
déclarées dans le fichier : TRAIN pour apprendre, VALIDATION pour choisir,
TEST pour mesurer une fois les choix figés.
"""
from __future__ import annotations

import json
from pathlib import Path

from .spans import Mention

__all__ = ["CHEMIN_CORPUS", "charger", "partition", "textes", "mentions_de", "resume"]

CHEMIN_CORPUS = Path(__file__).resolve().parent.parent / "donnees" / "mini_corpus.jsonl"


def charger(chemin: Path | str | None = None) -> list[dict]:
    """Charge les documents et vérifie que chaque offset redonne sa surface."""
    chemin = Path(chemin) if chemin is not None else CHEMIN_CORPUS
    documents = []
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue
            d = json.loads(ligne)
            for m in d["mentions"]:
                obtenu = d["texte"][m["debut"]:m["fin"]]
                if obtenu != m["surface"]:
                    raise ValueError(
                        f"{d['doc']} : offsets désalignés, {obtenu!r} != {m['surface']!r}"
                    )
            documents.append(d)
    return documents


def partition(nom: str, documents=None) -> list[dict]:
    """Documents d'une partition : 'train', 'validation' ou 'test'."""
    documents = documents if documents is not None else charger()
    connues = {d["partition"] for d in documents}
    if nom not in connues:
        raise ValueError(f"Partition inconnue : {nom!r}. Disponibles : {sorted(connues)}.")
    return [d for d in documents if d["partition"] == nom]


def textes(documents) -> dict[str, str]:
    """Table doc -> texte original, celui qui porte les offsets."""
    return {d["doc"]: d["texte"] for d in documents}


def mentions_de(documents) -> set[Mention]:
    """Mentions de référence, prêtes pour l'évaluation stricte."""
    return {
        Mention(d["doc"], m["debut"], m["fin"], m["type"])
        for d in documents
        for m in d["mentions"]
    }


def resume(documents=None) -> str:
    """Description courte du corpus, à citer dans un rapport."""
    from collections import Counter

    documents = documents if documents is not None else charger()
    parts = Counter(d["partition"] for d in documents)
    types = Counter(m["type"] for d in documents for m in d["mentions"])
    lignes = [
        f"{len(documents)} documents fictifs, {sum(types.values())} mentions.",
        "  partitions : " + ", ".join(f"{k}={v}" for k, v in sorted(parts.items())),
        "  types      : " + ", ".join(f"{k}={v}" for k, v in sorted(types.items())),
    ]
    return "\n".join(lignes)
