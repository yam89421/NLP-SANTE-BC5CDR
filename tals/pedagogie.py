"""Auto-vérification des exercices et figures d'appui.

`verifier` répond « juste » ou « faux », avec un indice, **sans** afficher la
solution. Dans la version précédente des notebooks, le corrigé occupait la
cellule suivant immédiatement l'exercice : il n'y avait aucune friction, donc
aucune raison de chercher.
"""
from __future__ import annotations

__all__ = ["verifier", "attendus", "figure_perte", "figure_attention", "figure_erreurs"]

#: Réponses attendues, repérées par un identifiant court cité dans l'énoncé.
attendus: dict[str, dict] = {}


def enregistrer(nom: str, valeur, indice: str = "") -> None:
    """Déclare la réponse attendue d'un exercice (à faire dans une cellule masquée)."""
    attendus[nom] = {"valeur": valeur, "indice": indice}


def _normaliser(x):
    if isinstance(x, (list, tuple)):
        return [_normaliser(v) for v in x]
    if isinstance(x, set):
        return sorted(_normaliser(v) for v in x)
    if isinstance(x, float):
        return round(x, 6)
    return x


def verifier(nom: str, valeur) -> bool:
    """Compare une réponse à l'attendu et affiche un retour, sans révéler la solution."""
    if nom not in attendus:
        print(f"Exercice inconnu : {nom!r}. Disponibles : {sorted(attendus)}.")
        return False
    attendu = attendus[nom]
    if _normaliser(valeur) == _normaliser(attendu["valeur"]):
        print(f"[{nom}] Juste.")
        return True
    print(f"[{nom}] Pas encore.")
    if attendu["indice"]:
        print(f"        Indice : {attendu['indice']}")
    print("        Relire l'énoncé, puis relancer cette cellule.")
    return False


# --------------------------------------------------------------- figures

def figure_perte(historique, titre="Perte d'apprentissage"):
    """Courbe de perte. La baisse mesure l'ajustement, pas la généralisation."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(historique, color="#1f4e79")
    ax.set_xlabel("époque")
    ax.set_ylabel("perte moyenne")
    ax.set_title(titre)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def figure_attention(A, etiquettes=None, titre="Coefficients d'attention"):
    """Carte d'attention : une ligne répond à « que combine cette position ? ».

    La carte montre ce qui est combiné dans une tête et à une couche. Elle ne
    démontre pas à elle seule la cause d'une prédiction finale.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    A = np.asarray(A)
    n = A.shape[0]
    etiquettes = etiquettes or [f"pos {i + 1}" for i in range(n)]
    fig, ax = plt.subplots(figsize=(4.6, 4))
    ax.imshow(A, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(n), etiquettes, rotation=45, ha="right")
    ax.set_yticks(range(n), etiquettes)
    ax.set_xlabel("clés"), ax.set_ylabel("requêtes")
    ax.set_title(titre)
    for i in range(n):
        for j in range(A.shape[1]):
            ax.text(j, i, f"{A[i, j]:.3f}", ha="center", va="center",
                    fontsize=8, color="white" if A[i, j] > 0.5 else "black")
    fig.tight_layout()
    return fig


def figure_erreurs(decomposition, titre="Catégories d'erreurs"):
    """Barres des catégories d'erreurs, pour hiérarchiser les modifications."""
    import matplotlib.pyplot as plt

    cles = ["correcte", "frontiere", "type", "manquee", "parasite"]
    valeurs = [len(decomposition.get(c, [])) for c in cles]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    couleurs = ["#2e7d32", "#ef6c00", "#c62828", "#6a1b9a", "#455a64"]
    ax.bar(cles, valeurs, color=couleurs)
    ax.set_ylabel("nombre de mentions")
    ax.set_title(titre)
    for i, v in enumerate(valeurs):
        ax.text(i, v, str(v), ha="center", va="bottom")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    return fig
