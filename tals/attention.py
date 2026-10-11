"""Attention, LayerNorm et bloc encodeur, en NumPy.

Correction importante par rapport à la première version du notebook : la
LayerNorm y était figée à gamma=1, beta=0, et une assertion exigeait une sortie
de moyenne nulle. C'est exactement la confusion que le polycopié dénonce
(« Après apprentissage de gamma et beta, il ne faut plus exiger de la sortie une
moyenne nulle et une variance exactement égale à 1 »). Les deux paramètres sont
donc de vrais arguments, et `bloc_encodeur` accepte une affine apprise.
"""
from __future__ import annotations

import numpy as np

__all__ = [
    "softmax",
    "attention",
    "masque_causal",
    "masque_padding",
    "attention_multi_tetes",
    "layernorm",
    "ffn",
    "bloc_encodeur",
    "tete_bio",
]


def softmax(x: np.ndarray) -> np.ndarray:
    """Softmax stable sur le dernier axe."""
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def masque_causal(n: int) -> np.ndarray:
    """Matrice booléenne des relations autorisées : pas d'accès au futur."""
    return np.tril(np.ones((n, n), dtype=bool))


def masque_padding(cles_valides) -> np.ndarray:
    """Interdit les clés de padding pour toutes les requêtes.

    Attention : masquer les *clés* de padding ne retire pas les *requêtes* de
    padding de la perte. Ces positions produisent encore une sortie numérique ;
    il faut les exclure explicitement des positions supervisées.
    """
    valides = np.asarray(cles_valides, dtype=bool)
    return np.broadcast_to(valides[None, :], (valides.size, valides.size))


def attention(Q, K, V, autorise=None):
    """Attention par produit scalaire redimensionné.

    Le masque est additif et appliqué **avant** le softmax : une relation
    interdite reçoit -inf, donc un poids nul, et le softmax renormalise les
    autres. Mettre un coefficient à zéro après le softmax, sans renormaliser,
    ne réalise pas le même calcul.
    """
    scores = Q @ K.swapaxes(-1, -2) / np.sqrt(Q.shape[-1])
    if autorise is not None:
        if not np.asarray(autorise).any(axis=-1).all():
            raise ValueError(
                "Une ligne entièrement interdite rend le softmax indéfini : "
                "chaque requête doit garder au moins une clé autorisée."
            )
        scores = np.where(autorise, scores, -np.inf)
    A = softmax(scores)
    return A @ V, A


def attention_multi_tetes(H, parametres, WO, autorise=None):
    """h têtes en parallèle, concaténation, puis projection de sortie WO.

    Chaque tête possède ses propres projections. Rien n'impose qu'une tête soit
    « la tête de négation » : une spécialisation peut s'observer, elle n'est pas
    garantie par la conception.
    """
    sorties, cartes = [], []
    for Wq, Wk, Wv in parametres:
        O, A = attention(H @ Wq, H @ Wk, H @ Wv, autorise)
        sorties.append(O)
        cartes.append(A)
    return np.concatenate(sorties, axis=-1) @ WO, cartes


def layernorm(H, gamma=None, beta=None, eps: float = 1e-5):
    """Normalise les coordonnées de chaque position, puis applique une affine.

    Moyenne et variance sont calculées sur les coordonnées d'un token,
    séparément pour chaque exemple — jamais sur les tokens du lot (ce serait
    BatchNorm).

    `gamma` et `beta` sont **appris** dans un vrai modèle. Les laisser à None
    donne la normalisation seule (gamma=1, beta=0) : c'est le cas du calcul
    illustratif du polycopié, pas le comportement d'un réseau entraîné.
    """
    centre = (H - H.mean(axis=-1, keepdims=True)) / np.sqrt(
        H.var(axis=-1, keepdims=True) + eps
    )
    if gamma is not None:
        centre = centre * gamma
    if beta is not None:
        centre = centre + beta
    return centre


def ffn(Z, W1, b1, W2, b2, activation=None):
    """MLP partagé entre positions : il ne mélange jamais les positions.

    Le mélange entre positions est le rôle de l'attention. La dimension interne
    d_ff est généralement supérieure à d, puis la seconde projection revient à d
    pour permettre l'addition résiduelle.
    """
    activation = activation if activation is not None else (lambda x: np.maximum(0, x))
    return activation(Z @ W1 + b1) @ W2 + b2


def bloc_encodeur(H, parametres_tetes, WO, W1, b1, W2, b2,
                  gamma1=None, beta1=None, gamma2=None, beta2=None,
                  autorise=None, pre_norm: bool = False):
    """Bloc encodeur complet, post-norm par défaut.

    post-norm : U = LN1(H + MHA(H)) ;  H' = LN2(U + FFN(U))
    pre-norm  : U = H + MHA(LN1(H)) ;  H' = U + FFN(LN2(U))

    Ces écritures ne sont pas interchangeables : elles décrivent des chemins de
    calcul différents. Le dropout est omis (évaluation).
    """
    if pre_norm:
        sortie_attention, cartes = attention_multi_tetes(
            layernorm(H, gamma1, beta1), parametres_tetes, WO, autorise
        )
        U = H + sortie_attention
        return U + ffn(layernorm(U, gamma2, beta2), W1, b1, W2, b2), cartes
    sortie_attention, cartes = attention_multi_tetes(H, parametres_tetes, WO, autorise)
    U = layernorm(H + sortie_attention, gamma1, beta1)
    return layernorm(U + ffn(U, W1, b1, W2, b2), gamma2, beta2), cartes


def tete_bio(H, Wc, bc):
    """Tête linéaire : d coordonnées -> C scores de classes BIO.

    Le softmax porte ici sur les **classes** ; dans l'attention il portait sur
    les **clés**. Même opération, deux rôles.
    """
    logits = H @ Wc + bc
    return logits, softmax(logits)
