"""Skip-gram avec softmax complet.

Correction importante par rapport à la première version du notebook : le
vocabulaire est un **attribut de l'objet**, plus une variable globale. Dans la
version précédente, `entrainer(corpus)` acceptait un corpus en argument mais
lisait `vocabulaire` et `vers_id` du module ; entraîner sur un autre corpus
levait un `KeyError` ou, pire, apprenait sur le mauvais vocabulaire.

Le softmax complet est conservé pour garder le calcul lisible. Le negative
sampling est un **autre objectif** (`perte_negative_sampling`), pas un softmax
calculé plus vite.
"""
from __future__ import annotations

import numpy as np

__all__ = ["softmax", "paires_skipgram", "SkipGram", "perte_negative_sampling", "cosinus"]


def softmax(scores: np.ndarray) -> np.ndarray:
    """Softmax stable sur le dernier axe (on retire le maximum avant l'exponentielle)."""
    z = scores - np.max(scores, axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def cosinus(u: np.ndarray, v: np.ndarray) -> float:
    """Similarité cosinus. Compare des directions, pas des amplitudes."""
    denominateur = np.linalg.norm(u) * np.linalg.norm(v)
    return float(u @ v / denominateur) if denominateur else 0.0


def paires_skipgram(corpus, rayon: int = 1) -> list[tuple[str, str]]:
    """Paires (centre, voisin) dans une fenêtre de rayon donné.

    Les cibles sont construites à partir du texte : c'est de l'auto-supervision,
    aucune annotation d'entité n'intervient.
    """
    return [
        (phrase[i], phrase[j])
        for phrase in corpus
        for i in range(len(phrase))
        for j in range(max(0, i - rayon), min(len(phrase), i + rayon + 1))
        if i != j
    ]


class SkipGram:
    """Skip-gram, softmax complet, descente de gradient stochastique.

    Deux tables sont apprises : `E` pour les vecteurs de centre, `U` pour les
    vecteurs de contexte. Elles partagent le vocabulaire mais pas leurs
    paramètres.
    """

    def __init__(self, dimension: int = 12, rayon: int = 1, taux: float = 0.05, graine: int = 7):
        self.dimension = dimension
        self.rayon = rayon
        self.taux = taux
        self.graine = graine
        self.vocabulaire: list[str] = []
        self.vers_id: dict[str, int] = {}
        self.E: np.ndarray | None = None
        self.U: np.ndarray | None = None
        self.E_initial: np.ndarray | None = None
        self.historique: list[float] = []

    def _construire_vocabulaire(self, corpus) -> None:
        self.vocabulaire = sorted({mot for phrase in corpus for mot in phrase})
        self.vers_id = {mot: i for i, mot in enumerate(self.vocabulaire)}

    def perte_moyenne(self, paires: np.ndarray) -> float:
        probabilites = softmax(self.E[paires[:, 0]] @ self.U.T)
        return float(-np.log(probabilites[np.arange(len(paires)), paires[:, 1]]).mean())

    def ajuster(self, corpus, epoques: int = 100) -> "SkipGram":
        self._construire_vocabulaire(corpus)
        couples = paires_skipgram(corpus, self.rayon)
        if not couples:
            raise ValueError("Corpus trop court : aucune paire centre-voisin.")
        paires = np.array([(self.vers_id[c], self.vers_id[o]) for c, o in couples])

        rng = np.random.default_rng(self.graine)
        taille = len(self.vocabulaire)
        self.E = rng.normal(0, 0.1, (taille, self.dimension))
        self.U = rng.normal(0, 0.1, (taille, self.dimension))
        self.E_initial = self.E.copy()
        self.historique = [self.perte_moyenne(paires)]

        for _ in range(epoques):
            for c, o in paires[rng.permutation(len(paires))]:
                v = self.E[c].copy()          # paramètres AVANT mise à jour
                p = softmax(self.U @ v)
                gradient_scores = p.copy()
                gradient_scores[o] -= 1        # softmax + entropie croisée : p - cible
                self.E[c] -= self.taux * (gradient_scores @ self.U)
                self.U -= self.taux * np.outer(gradient_scores, v)
            self.historique.append(self.perte_moyenne(paires))
        return self

    def vecteur(self, mot: str) -> np.ndarray:
        if mot not in self.vers_id:
            raise KeyError(
                f"{mot!r} est hors vocabulaire. Word2Vec est statique : une forme "
                "absente du corpus d'apprentissage n'a pas de vecteur."
            )
        return self.E[self.vers_id[mot]]

    def voisins(self, mot: str, nombre: int = 4, matrice: np.ndarray | None = None):
        """Plus proches voisins au cosinus. Proximité d'usage, pas synonymie."""
        matrice = self.E if matrice is None else matrice
        normes = np.linalg.norm(matrice, axis=1, keepdims=True)
        normalisee = matrice / np.maximum(normes, 1e-12)
        scores = normalisee @ normalisee[self.vers_id[mot]]
        ordre = np.argsort(-scores)
        return [
            (self.vocabulaire[i], round(float(scores[i]), 3))
            for i in ordre
            if i != self.vers_id[mot]
        ][:nombre]


def perte_negative_sampling(v_c: np.ndarray, u_o: np.ndarray, u_negatifs: np.ndarray) -> float:
    """Objectif contrastif binaire sur une paire observée et k paires tirées.

    Un « négatif » est un tirage selon une distribution de bruit ; ce n'est ni un
    antonyme ni une négation clinique. Les scores obtenus ne forment pas une
    distribution normalisée sur le vocabulaire.
    """
    sigma = lambda z: 1.0 / (1.0 + np.exp(-z))
    return float(
        -np.log(sigma(v_c @ u_o)) - np.sum(np.log(sigma(-(u_negatifs @ v_c))))
    )
