"""Boîte à outils du cours « Extraction d'information en santé ».

Un seul endroit pour le code partagé par les trois modules : les notebooks
importent ces fonctions au lieu d'en recopier des variantes divergentes.

    import sys; sys.path.insert(0, "../../Commun")
    from tals import Mention, charger, scores

Les textes manipulés sont fictifs et servent l'enseignement, pas la mesure
d'une performance clinique.
"""
from .spans import Mention, tokeniser_avec_offsets, verifier_offsets, cle_normalisee
from .bio import bio_vers_mentions, mentions_vers_bio, aligner_sous_mots, IGNORE
from .evaluation import Scores, scores, scores_par_type, erreurs, tableau_comparatif
from .donnees import charger, partition, textes, mentions_de, resume

__version__ = "1.0.0"

__all__ = [
    "Mention", "tokeniser_avec_offsets", "verifier_offsets", "cle_normalisee",
    "bio_vers_mentions", "mentions_vers_bio", "aligner_sous_mots", "IGNORE",
    "Scores", "scores", "scores_par_type", "erreurs", "tableau_comparatif",
    "charger", "partition", "textes", "mentions_de", "resume",
]
