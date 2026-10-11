"""Codage BIO, politiques de décodage et alignement sous-mots.

Le module 3 insiste sur un point que le code doit rendre explicite : une tête
de classification indépendante peut produire des séquences BIO invalides
(`I-X` après `O`, ou après un `B-Y` d'un autre type). Il n'existe pas de
réponse universelle ; il faut *annoncer une politique* et la fixer avant le
test. Les trois politiques implémentées ici sont celles du polycopié.
"""
from __future__ import annotations

from .spans import Mention

__all__ = [
    "POLITIQUES",
    "bio_vers_mentions",
    "mentions_vers_bio",
    "aligner_sous_mots",
    "IGNORE",
]

#: Indice ignoré par la perte de PyTorch. Ce n'est **pas** une classe BIO.
IGNORE = -100

POLITIQUES = ("stricte", "reparer", "ignorer")


def _verifier_politique(politique: str) -> None:
    if politique not in POLITIQUES:
        raise ValueError(f"Politique inconnue : {politique!r}. Attendu : {POLITIQUES}.")


def bio_vers_mentions(tags, offsets, doc: str = "doc", politique: str = "stricte") -> set[Mention]:
    """Fusionne des étiquettes BIO en mentions localisées.

    politique :
      - "stricte"  : un `I-X` sans début compatible lève une erreur. À utiliser
                     sur des annotations de référence, où l'invalidité est un bug.
      - "reparer"  : un `I-X` incompatible ouvre une nouvelle mention de type X.
      - "ignorer"  : un `I-X` incompatible est traité comme `O`.

    Les deux dernières changent les mentions produites, donc le score : le
    choix doit être déclaré dans le protocole, pas laissé à la bibliothèque.
    """
    _verifier_politique(politique)
    if len(tags) != len(offsets):
        raise ValueError(
            f"Un label par token est nécessaire : {len(tags)} tags, {len(offsets)} offsets."
        )

    mentions: set[Mention] = set()
    actif: list | None = None

    def fermer() -> None:
        nonlocal actif
        if actif is not None:
            mentions.add(Mention(doc, actif[0], actif[1], actif[2]))
            actif = None

    for tag, (debut, fin) in zip(tags, offsets):
        if tag == "O":
            fermer()
        elif tag.startswith("B-"):
            fermer()
            actif = [debut, fin, tag[2:]]
        elif tag.startswith("I-"):
            type_entite = tag[2:]
            compatible = actif is not None and actif[2] == type_entite
            if compatible:
                actif[1] = fin
            elif politique == "stricte":
                raise ValueError(f"Séquence BIO invalide : {tag} sans début compatible.")
            elif politique == "reparer":
                fermer()
                actif = [debut, fin, type_entite]
            else:  # "ignorer"
                fermer()
        else:
            raise ValueError(f"Étiquette inconnue : {tag!r}.")
    fermer()
    return mentions


def mentions_vers_bio(mentions, offsets, doc: str | None = None) -> list[str]:
    """Projette des mentions sur une séquence de tokens (opération inverse).

    Sert à fabriquer des cibles d'entraînement à partir de spans de caractères,
    et à vérifier qu'un aller-retour BIO conserve bien les mentions.
    """
    tags = ["O"] * len(offsets)
    for mention in sorted(mentions):
        if doc is not None and mention.doc != doc:
            continue
        premier = True
        for i, (debut, fin) in enumerate(offsets):
            if debut >= mention.debut and fin <= mention.fin:
                tags[i] = ("B-" if premier else "I-") + mention.type
                premier = False
    return tags


def aligner_sous_mots(ids_mots, tags_mots, strategie: str = "premier"):
    """Aligne des étiquettes définies par mot sur une séquence de sous-mots.

    `ids_mots` est la liste renvoyée par un tokenizer sous la forme `word_ids()` :
    un indice de mot par sous-mot, et `None` pour les tokens spéciaux.

    strategie :
      - "premier" : seul le premier sous-mot d'un mot est supervisé ; les autres
                    reçoivent IGNORE. Convention usuelle de Hugging Face.
      - "toutes"  : toutes les pièces sont supervisées ; un mot qui commence une
                    entité donne `B-TYPE` puis `I-TYPE` sur ses pièces suivantes.
                    Répéter `B` créerait plusieurs débuts artificiels.

    Retourne une liste de la longueur de `ids_mots`, contenant des étiquettes
    BIO ou IGNORE. IGNORE n'est pas une classe : c'est un indice exclu de la perte.
    """
    if strategie not in ("premier", "toutes"):
        raise ValueError(f"Stratégie inconnue : {strategie!r}.")

    cibles: list = []
    precedent = None
    for id_mot in ids_mots:
        if id_mot is None:
            cibles.append(IGNORE)
        elif id_mot != precedent:
            cibles.append(tags_mots[id_mot])
        elif strategie == "premier":
            cibles.append(IGNORE)
        else:
            tag = tags_mots[id_mot]
            cibles.append(("I-" + tag[2:]) if tag.startswith("B-") else tag)
        precedent = id_mot
    return cibles
