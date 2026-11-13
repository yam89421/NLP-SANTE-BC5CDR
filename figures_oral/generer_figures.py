"""Figures pour les slides de l'oral (PNG 16:9 dans ce dossier).

Lancer depuis la racine du projet :
    ../Extraction/BERT/TD/bin/python figures_oral/generer_figures.py

Les chiffres sont ceux des notebooks du rapport (`rapport/`, versions figées) ; seules les figures 08
(exemple) et 14 (combinaisons dictionnaire + modèle, HYB-v2) sont recalculées
à partir des prédictions VALIDATION sauvegardées. Aucune méthode n'est relancée.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
SORTIE = Path(__file__).resolve().parent

# Palette (validée : contrastes et daltonisme). Une couleur = une méthode, sur toutes les figures.
ORANGE = "#eb6834"   # dictionnaire / BM25 (méthodes « à la main » ou lexicales)
BLEU = "#2a78d6"     # modèle appris / recherche dense
AQUA = "#1baf7a"     # Q1 ; Chemical
VIOLET = "#4a3aa7"   # Q2 ; Disease
ROUGE = "#e34948"    # erreurs
MAGENTA = "#d55181"
ORANGE_CLAIR = "#f4b496"  # version précédente du dictionnaire  # second LLM (Mistral)
GRIS = "#b4b2ab"     # références externes, versions anciennes
GRIS_FONCE = "#6f6e69"
ENCRE = "#0b0b0b"
ENCRE_2 = "#52514e"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 13, "axes.titlesize": 15, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.labelcolor": ENCRE_2, "xtick.color": ENCRE_2, "ytick.color": ENCRE_2,
    "axes.edgecolor": "#c9c8c2", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e8e7e3", "grid.linewidth": 0.8, "axes.axisbelow": True,
    "legend.frameon": False, "figure.dpi": 100,
})


def _formateur_fr(graduations):
    """Même nombre de décimales pour toutes les graduations d'un axe, virgule décimale, espace des milliers."""
    from matplotlib.ticker import FuncFormatter
    n = max((len(f"{v:.3f}".rstrip("0").split(".")[1]) for v in graduations), default=0)
    if n == 0:
        return FuncFormatter(lambda x, pos=None: f"{int(round(x)):,}".replace(",", "\u202f"))
    return FuncFormatter(lambda x, pos=None: f"{x:.{n}f}".replace(".", ","))


def sauver(fig, nom):
    from matplotlib.ticker import ScalarFormatter
    for ax in fig.axes:  # graduations numériques à la française
        for axe in (ax.xaxis, ax.yaxis):
            if isinstance(axe.get_major_formatter(), ScalarFormatter):
                bas, haut = sorted(axe.get_view_interval())
                axe.set_major_formatter(_formateur_fr([v for v in axe.get_majorticklocs() if bas - 1e-9 <= v <= haut + 1e-9]))
    fig.savefig(SORTIE / f"{nom}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("écrit", nom)


def fr(x, n=2):
    return f"{x:.{n}f}".replace(".", ",")


def carres(cible, items, **kw):
    """Légende à carrés colorés : items = [(libellé, couleur) ou (libellé, couleur, alpha)]."""
    from matplotlib.patches import Patch
    poignees = [Patch(facecolor=it[1], alpha=it[2] if len(it) > 2 else 1, label=it[0]) for it in items]
    return cible.legend(handles=poignees, handlelength=1.0, handleheight=1.0, handletextpad=0.5, **kw)


def barres_etiquetees(ax, x, valeurs, largeur, couleur, n=2, **kw):
    b = ax.bar(x, valeurs, largeur, color=couleur, edgecolor="white", linewidth=2, **kw)
    for xi, v in zip(x, valeurs):
        ax.text(xi, v + 0.01 * ax.get_ylim()[1], fr(v, n), ha="center", va="bottom", fontsize=11, color=ENCRE)
    return b


# ---------------------------------------------------------------- extraction
VERSIONS = [  # rapport/1_extraction.ipynb, VALIDATION
    ("DIC-v1", 0.8835, 0.6438, 0.7449), ("DIC-v2", 0.8889, 0.7128, 0.7912), ("DIC-v3", 0.8811, 0.7314, 0.7993),
    ("DIC-v4", 0.9032, 0.8669, 0.8847),
    ("APP-v1", 0.8533, 0.8558, 0.8546), ("APP-v2", 0.8886, 0.8973, 0.8929), ("APP-v3", 0.9042, 0.9197, 0.9119),
]


def fig01_precision_rappel():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    p = np.linspace(0.5, 1, 300)
    for f in (0.75, 0.80, 0.85, 0.90):
        r = f * p / (2 * p - f)
        ok = (r > 0) & (r <= 1)
        ax.plot(p[ok], r[ok], ls=":", color=GRIS, lw=1.2)
        ax.text(0.975, f * 0.975 / (2 * 0.975 - f), f"F1 = {fr(f)}", color=GRIS_FONCE, fontsize=10,
                ha="right", va="center", bbox=dict(fc="white", ec="none", pad=1.5))
    for famille, couleur in (("DIC", ORANGE), ("APP", BLEU)):
        pts = [v for v in VERSIONS if v[0].startswith(famille)]
        ax.plot([v[1] for v in pts], [v[2] for v in pts], color=couleur, lw=2, zorder=2)
        for i, (nom, pr, rp, f1) in enumerate(pts):
            derniere = i == len(pts) - 1
            ax.scatter(pr, rp, s=90 if derniere else 55, color=couleur, edgecolor="white", linewidth=2, zorder=3)
            ax.annotate(f"{nom}  (F1 {fr(f1, 3)})", (pr, rp), xytext=(10, -4), textcoords="offset points",
                        fontsize=11, fontweight="bold" if derniere else "normal", color=ENCRE,
                        bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.8))
    ax.set_xlim(0.84, 0.98); ax.set_ylim(0.60, 0.95)
    ax.set_xlabel("Précision"); ax.set_ylabel("Rappel")
    carres(ax, [("Dictionnaire + règles", ORANGE), ("Modèle appris", BLEU)], loc="upper left")
    sauver(fig, "01_precision_rappel_versions")


TEST = {  # scores_test.csv
    "DIC-v4": {"Chemical": (0.9260, 0.9203, 0.9232), "Disease": (0.8692, 0.8248, 0.8464), "Global": (0.9010, 0.8773, 0.8890)},
    "APP-v3": {"Chemical": (0.9128, 0.9443, 0.9283), "Disease": (0.8369, 0.8687, 0.8525), "Global": (0.8785, 0.9102, 0.8941)},
}


def fig02_test_par_categorie():
    fig, axes = plt.subplots(1, 3, figsize=(13, 5.2), sharey=True)
    cats = ["Chemical", "Disease", "Global"]
    x = np.arange(len(cats)); w = 0.36
    for k, (ax, mesure) in enumerate(zip(axes, ["Précision", "Rappel", "F1"])):
        ax.set_ylim(0, 1.05)
        for j, (meth, coul) in enumerate((("DIC-v4", ORANGE), ("APP-v3", BLEU))):
            barres_etiquetees(ax, x + (j - 0.5) * w, [TEST[meth][c][k] for c in cats], w, coul, n=3, label=meth)
        ax.set_xticks(x, cats); ax.set_title(mesure); ax.grid(axis="x", visible=False)
    fig.tight_layout()
    carres(fig, [("DIC-v4", ORANGE), ("APP-v3", BLEU)], loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.07))
    sauver(fig, "02_test_dic_vs_app_par_categorie")


def fig03_types_erreurs():
    # rapport/1_extraction.ipynb, VALIDATION (9 591 entités de référence) : bornes fausses, type, manquées, fausses détections
    lignes = [("DIC-v1", 578, 13, 2825, 223), ("DIC-v2", 576, 8, 2171, 270), ("DIC-v3", 627, 8, 1941, 312),
              ("DIC-v4", 437, 8, 832, 446),
              ("APP-v1", 631, 11, 741, 769), ("APP-v2", 489, 14, 482, 576), ("APP-v3", 432, 4, 334, 499)][::-1]
    panneaux = [("Entités manquées", 2), ("Bornes fausses", 0), ("Fausses détections", 3)]
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.8), sharey=True)
    y = np.arange(len(lignes))
    couleurs = [BLEU if l[0].startswith("APP") else ORANGE for l in lignes]
    for ax, (titre, k) in zip(axes, panneaux):
        vals = [l[1 + k] for l in lignes]
        ax.barh(y, vals, color=couleurs, height=0.62, edgecolor="white", linewidth=2)
        ax.set_xlim(0, 3000)
        for yi, v in zip(y, vals):
            ax.text(v + 40, yi, f"{v:,}".replace(",", " "), va="center", fontsize=11, color=ENCRE)
        ax.set_title(titre, fontsize=13.5)
        ax.grid(axis="y", visible=False); ax.set_xticks([0, 1000, 2000, 3000])
    axes[0].set_yticks(y, [l[0] for l in lignes])
    fig.tight_layout()
    carres(fig, [("Dictionnaire + règles", ORANGE), ("Modèle appris", BLEU)], loc="lower center", ncol=2,
           bbox_to_anchor=(0.5, -0.08))
    sauver(fig, "03_types_erreurs")


def fig04_etat_art():
    # rapport/1_extraction.ipynb, comparaison avec l'état de l'art : (nom, Chemical, Disease, genre)
    sys_ = [
        ("DIC-v3", 82.77, 76.20, "ancien_dic"), ("DIC-v4 (+ MeSH)", 92.32, 84.64, "nous_dic"),
        ("tmChem + DNorm", 92.20, 80.24, "mesure"),
        ("BERT-base", 89.25, 81.44, "publie"), ("SciBERT", 92.49, 84.54, "publie"),
        ("BioBERT", 92.85, 84.70, "publie"), ("PubMedBERT (publié)", 93.33, 85.62, "publie"),
        ("BioLinkBERT-base", 93.75, 86.10, "publie"), ("APP-v3 (PubMedBERT)", 92.83, 85.25, "nous_app"),
    ]
    couleur = {"ancien_dic": ORANGE_CLAIR, "nous_dic": ORANGE, "nous_app": BLEU, "mesure": GRIS_FONCE, "publie": GRIS}
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6))
    for k, (ax, cat) in enumerate(zip(axes, ["Chemical", "Disease"])):
        ordre = sorted(sys_, key=lambda s: s[1 + k])
        y = np.arange(len(ordre))
        ax.hlines(y, 74, 96, color="#ecebe7", lw=1, zorder=0)
        ax.scatter([s[1 + k] for s in ordre], y, s=[150 if s[3].startswith("nous") else 90 for s in ordre],
                   color=[couleur[s[3]] for s in ordre], edgecolor="white", linewidth=1.5, zorder=3)
        for yi, s in zip(y, ordre):
            ax.text(s[1 + k] + 0.45, yi, fr(s[1 + k], 1), va="center", fontsize=11,
                    fontweight="bold" if s[3].startswith("nous") else "normal")
        ax.set_yticks(y, [s[0] for s in ordre]); ax.set_xlim(74, 96); ax.set_title(cat)
        ax.set_xlabel("F1 TEST (%)"); ax.grid(axis="y", visible=False)
        for etiquette, s in zip(ax.get_yticklabels(), ordre):
            if s[3].startswith("nous"):
                etiquette.set_fontweight("bold"); etiquette.set_color(ENCRE)
    fig.tight_layout()
    carres(fig, [("DIC-v3", ORANGE_CLAIR), ("DIC-v4", ORANGE), ("APP-v3", BLEU), ("Outils officiels (mesurés)", GRIS_FONCE),
                 ("Modèles publiés", GRIS)], loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.08))
    sauver(fig, "04_etat_de_l_art")


def fig05_epoques():
    ep = np.arange(1, 11)
    courbes = [  # rapport/1_extraction.ipynb (F1 VALIDATION moyen sur 2 graines)
        ("BioBERT, taux 3e-5", [0.747, 0.867, 0.878, 0.881, 0.884, 0.882, 0.887, 0.885, 0.889, 0.887], None, GRIS, "--"),
        ("BioBERT, taux 5e-5 (APP-v2)", [0.835, 0.879, 0.883, 0.892, 0.892, 0.890, 0.893, 0.895, 0.895, 0.896], 4, GRIS_FONCE, "-"),
        ("BioLinkBERT-base", [0.793, 0.881, 0.894, 0.901, 0.906, 0.906, 0.902, 0.908, 0.906, 0.907], 5, VIOLET, "-"),
        ("PubMedBERT (APP-v3)", [0.795, 0.875, 0.892, 0.898, 0.902, 0.905, 0.911, 0.908, 0.909, 0.910], 7, BLEU, "-"),
    ]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for nom, v, retenue, coul, ls in courbes:
        ax.plot(ep, v, color=coul, lw=2.2 if "APP-v3" in nom else 1.8, ls=ls, label=nom)
        if retenue:
            ax.scatter(retenue, v[retenue - 1], s=110, color=coul, edgecolor="white", linewidth=2, zorder=3)
            ax.annotate(f"{retenue} ép.", (retenue, v[retenue - 1]), xytext=(16, -16) if retenue == 4 else (0, 10),
                        textcoords="offset points", ha="center", fontsize=10, color=ENCRE,
                        bbox=dict(fc="white", ec="none", pad=1))
    ax.scatter(2, 0.8546, marker="X", s=130, color=ROUGE, zorder=4)
    ax.annotate("APP-v1", (2, 0.8546), xytext=(14, -18), textcoords="offset points",
                fontsize=10.5, color=ENCRE)
    ax.set_xticks(ep); ax.set_ylim(0.73, 0.93)
    ax.set_xlabel("Époques"); ax.set_ylabel("F1 VALIDATION")
    carres(ax, [(nom, coul) for nom, _, _, coul, _ in courbes], loc="lower right")
    sauver(fig, "05_courbes_epoques")


def fig06_regles():
    groupes = [
        ("DIC-v1 → DIC-v2", 0.7449, [("Suffixes appris", 0.7610), ("Modificateurs à gauche", 0.7504),
                                     ("« X-induced »", 0.7479), ("Sigles définis", 0.7653), ("Préfixe anti-", 0.7456),
                                     ("Toutes ensemble", 0.7912)]),
        ("DIC-v2 → DIC-v3", 0.7912, [("Filtre corrigé", 0.7945), ("Singulier / pluriel", 0.7941),
                                     ("Extension à droite", 0.7914), ("Propagation", 0.7931), ("Tous ensemble", 0.7993)]),
    ]
    fig, ax = plt.subplots(figsize=(11, 6.6))
    y, noms, ticks = 0, [], []
    for titre, base, items in groupes:
        ax.text(-0.05, y, titre, fontsize=13, fontweight="bold", va="center", ha="right",
                transform=ax.get_yaxis_transform())
        y -= 1
        for i, (nom, f) in enumerate(items):
            total = i == len(items) - 1
            g = (f - base) * 100
            ax.barh(y, g, height=0.68, color="#a8461f" if total else ORANGE, edgecolor="white", linewidth=2)
            ax.text(g + 0.06, y, f"+{fr(g, 1)}", va="center", fontsize=11, fontweight="bold" if total else "normal")
            ticks.append(y); noms.append(nom); y -= 1
        y -= 0.6
    ax.set_yticks(ticks, noms); ax.set_ylim(y + 0.4, 0.6); ax.set_xlim(0, 5.2)
    ax.grid(axis="y", visible=False); ax.set_xlabel("Gain de F1 VALIDATION (points)")
    for etiquette in ax.get_yticklabels():
        if "ensemble" in etiquette.get_text():
            etiquette.set_fontweight("bold"); etiquette.set_color(ENCRE)
    sauver(fig, "06_effet_regles_dictionnaire")


def fig07_validation_test():
    fig, ax = plt.subplots(figsize=(7, 5.6))
    # (nom, VALIDATION, TEST, couleur, décalage vertical de l'étiquette TEST pour éviter les chevauchements)
    for nom, v, t, coul, dy in (("DIC-v3", 0.7993, 0.7978, ORANGE_CLAIR, 0), ("DIC-v4", 0.8847, 0.8890, ORANGE, -0.004),
                                ("APP-v3", 0.9119, 0.8941, BLEU, 0.004)):
        ax.plot([0, 1], [v, t], color=coul, lw=2.5, marker="o", ms=10, markeredgecolor="white", markeredgewidth=2)
        ax.text(-0.06, v, f"{nom}  {fr(v, 3)}", ha="right", va="center", fontsize=12)
        ax.text(1.06, t + dy, f"{fr(t, 3)}  ({'+' if t >= v else '−'}{fr(abs(t - v) * 100, 1)} pt)", ha="left",
                va="center", fontsize=12)
    ax.set_xticks([0, 1], ["VALIDATION", "TEST"]); ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0.77, 0.93); ax.set_ylabel("F1 global"); ax.grid(axis="x", visible=False)
    sauver(fig, "07_validation_vs_test")


def fig08_exemple():
    from matplotlib.patches import Rectangle
    from src.cdr import charger_cdr
    from src.extraction import lire_predictions
    doc = next(d for d in charger_cdr(RACINE / "CDR_Data/CDR.Corpus.v010516")["validation"] if d.document_id == "6794356")
    texte = doc.texte[:doc.texte.index("described.") + len("described.")]
    ref = {(m.debut, m.fin, m.type) for m in doc.mentions if m.fin <= len(texte)}
    lignes = {"Référence": ref}
    for nom, f in (("DIC-v3", "predictions_dictionnaire_v3_validation.jsonl"),
                   ("DIC-v4", "predictions_dictionnaire_v4_validation.jsonl"),
                   ("APP-v3", "predictions_apprise_v3_validation.jsonl")):
        lignes[nom] = {(m.debut, m.fin, m.type) for m in lire_predictions(RACINE / "resultats/extraction" / f)
                       if m.doc == "6794356" and m.fin <= len(texte)}
    fond = {"Chemical": "#bfe9d9", "Disease": "#d6d2f0"}
    coupure = texte.index(" A newborn") + 1
    fig = plt.figure(figsize=(14, 8.6)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    rendu = fig.canvas.get_renderer()
    toutes_bornes = sorted({0, coupure, len(texte)} | {b for ms in lignes.values() for m in ms for b in m[:2]})
    haut = 0.037  # hauteur d'un cadre

    def cadre(x0, x1, y, **kw):
        ax.add_patch(Rectangle((x0 - 0.002, y - haut / 2), x1 - x0 + 0.004, haut, **kw))

    y0 = 0.92
    for nom, mentions in lignes.items():
        ax.text(0.015, y0, nom, fontsize=14, fontweight="bold", va="center",
                color={"DIC-v3": ORANGE_CLAIR, "DIC-v4": ORANGE, "APP-v3": BLEU}.get(nom, ENCRE))
        pos = {}  # borne de caractère -> (x, y)
        x, y = 0.13, y0
        for a, b in zip(toutes_bornes, toutes_bornes[1:]):
            if a == coupure:
                x, y = 0.13, y - 0.08
            pos.setdefault(a, (x, y))
            t = ax.text(x, y, texte[a:b], fontsize=13, va="center", color=ENCRE, zorder=3)
            x = t.get_window_extent(rendu).transformed(ax.transData.inverted()).x1
            pos[("fin", b)] = (x, y)
        for m in mentions:
            (xa, ya), (xb, _) = pos[m[0]], pos[("fin", m[1])]
            juste = m in ref
            cadre(xa, xb, ya, fc=fond[m[2]], ec="none" if juste else ROUGE, lw=0 if juste else 2.5, zorder=1)
            if not juste:
                ax.text((xa + xb) / 2, ya - 0.035, "bornes fausses", ha="center", va="top", fontsize=10.5,
                        color=ROUGE, fontweight="bold")
        if nom != "Référence":
            for r in ref:
                if not any(m[0] < r[1] and r[0] < m[1] for m in mentions):
                    (xa, ya), (xb, _) = pos[r[0]], pos[("fin", r[1])]
                    cadre(xa, xb, ya, fc="none", ec=ROUGE, lw=2, ls="--", zorder=2)
                    ax.text((xa + xb) / 2, ya - 0.035, "manquée", ha="center", va="top", fontsize=10.5,
                            color=ROUGE, fontweight="bold")
        y0 -= 0.22
    # légende dessinée avec de vrais échantillons
    x, y = 0.13, 0.05
    for etiquette, kw in (("Chemical", dict(fc=fond["Chemical"], ec="none")), ("Disease", dict(fc=fond["Disease"], ec="none")),
                          ("bornes fausses", dict(fc=fond["Disease"], ec=ROUGE, lw=2.5)),
                          ("manquée", dict(fc="none", ec=ROUGE, lw=2, ls="--"))):
        cadre(x, x + 0.035, y, **kw)
        t = ax.text(x + 0.045, y, etiquette, fontsize=11.5, color=ENCRE_2, va="center")
        x = t.get_window_extent(rendu).transformed(ax.transData.inverted()).x1 + 0.035
    sauver(fig, "08_exemple_phrase_annotee")


# ---------------------------------------------------------------- négation
def fig09_negation():
    m = np.array([[4, 1], [1, 4]])
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    from matplotlib.colors import ListedColormap
    ax.imshow(np.eye(2), cmap=ListedColormap(["#cde2fb", BLEU])); ax.grid(False)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, m[i, j], ha="center", va="center", fontsize=26, color="white" if m[i, j] > 3 else ENCRE)
    ax.set_xticks([0, 1], ["nié", "non nié"]); ax.set_yticks([0, 1], ["nié", "non nié"])
    ax.set_xlabel("Prédiction"); ax.set_ylabel("Référence")
    for s in ax.spines.values():
        s.set_visible(False)
    sauver(fig, "09_negation_matrice")


# ---------------------------------------------------------------- QA
def fig10_recherche():
    mesures = ["Hit@5", "Rappel@5", "Couverture\néléments@5"]
    dev = [("BM25", [0.750, 0.688, 0.719], GRIS), ("BM25 + racinisation", [0.875, 0.781, 0.823], ORANGE),
           ("Recherche dense", [0.938, 0.875, 0.979], BLEU)]
    test = [("BM25 + racinisation", [0.875, 0.771, 0.792], ORANGE), ("Recherche dense", [1.000, 0.771, 0.792], BLEU)]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), sharey=True, gridspec_kw={"width_ratios": [3, 2.3]})
    for ax, series, titre in ((axes[0], dev, "DEV"), (axes[1], test, "TEST")):
        x = np.arange(len(mesures)); w = 0.8 / len(series); ax.set_ylim(0, 1.12)
        for j, (nom, v, c) in enumerate(series):
            barres_etiquetees(ax, x + (j - (len(series) - 1) / 2) * w, v, w, c, label=nom)
        ax.set_xticks(x, mesures); ax.set_title(titre, fontsize=13); ax.grid(axis="x", visible=False)
    fig.tight_layout()
    carres(fig, [(nom, c) for nom, _, c in dev], loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.08))
    sauver(fig, "10_recherche_passages")


def fig11_reponses():
    confs = ["Q0", "Q1", "Q2", "Q2\n+ dense"]
    coul = [GRIS, AQUA, VIOLET, BLEU]
    panneaux = [
        ("ROUGE-L", [0.210, 0.315, 0.325, 0.354], 0.45, 3),
        ("BLEU", [5.44, 9.96, 10.10, 13.99], 17, 1),
        ("Exactitude (/ 2)", [1.4, 1.4, 1.7, None], 2.1, 1),
        ("Complétude (/ 1)", [0.42, 0.83, 0.76, None], 1.05, 2),
        ("Abstentions justes (/ 2)", [0, 1, 2, None], 2.3, 0),
    ]
    fig, axes = plt.subplots(1, 5, figsize=(16, 5))
    for ax, (titre, vals, ymax, n) in zip(axes, panneaux):
        idx = [i for i, v in enumerate(vals) if v is not None]
        ax.set_ylim(0, ymax)
        for i in idx:
            ax.bar(i, vals[i], color=coul[i], width=0.7, edgecolor="white", linewidth=2)
            ax.text(i, vals[i] + ymax * 0.015, fr(vals[i], n) if n else str(vals[i]), ha="center", va="bottom", fontsize=11)
        ax.set_xticks(idx, [confs[i] for i in idx], fontsize=10); ax.set_title(titre, fontsize=12.5)
        if titre.startswith("Abstentions"):
            ax.set_yticks([0, 1, 2])
        elif titre.startswith("Exactitude"):
            ax.set_yticks([0, 0.5, 1, 1.5, 2])
        ax.grid(axis="x", visible=False)
    fig.tight_layout()
    sauver(fig, "11_qualite_reponses_q0_q1_q2")


def fig12_mistral():
    confs = ["Q1", "Q2", "Q2 + dense"]
    donnees = {"DEV": ([0.336, 0.360, 0.377], [0.394, 0.374, 0.377]), "TEST": ([0.315, 0.325, 0.354], [0.343, 0.359, 0.380])}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, (part, (o, m)) in zip(axes, donnees.items()):
        x = np.arange(3); ax.set_ylim(0, 0.47)
        barres_etiquetees(ax, x - 0.19, o, 0.38, GRIS_FONCE, n=3)
        barres_etiquetees(ax, x + 0.19, m, 0.38, MAGENTA, n=3)
        ax.set_xticks(x, confs); ax.set_title(part, fontsize=13); ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("ROUGE-L")
    carres(axes[0], [("gpt-4.1-mini", GRIS_FONCE), ("mistral-medium", MAGENTA)], loc="upper left", ncol=2)
    fig.tight_layout()
    sauver(fig, "12_openai_vs_mistral")


def fig13_nb_passages():
    k = [3, 5, 10]
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.plot(k, [0.625, 0.781, 0.812], color=ORANGE, lw=2.2, marker="o", ms=9)
    ax.plot(k, [0.314, 0.360, 0.367], color=VIOLET, lw=2.2, marker="o", ms=9)
    for xi, a in zip(k, [3, 2, 2]):
        ax.text(xi, 0.20, f"{a} abstention{'s' if a > 1 else ''}\nà tort", ha="center", fontsize=10.5, color=ROUGE)
    ax.text(10, 0.86, "+ 1 réponse non soutenue", ha="center", fontsize=10, color=ROUGE)
    ax.axvspan(4.4, 5.6, color="#e8e7e3", zorder=0); ax.text(5, 0.93, "retenu", ha="center", fontsize=11)
    ax.set_xticks(k); ax.set_ylim(0.15, 0.97); ax.set_xlabel("Passages transmis au LLM (k)")
    carres(ax, [("Rappel des passages", ORANGE), ("ROUGE-L de Q2", VIOLET)], loc="center right")
    sauver(fig, "13_nombre_de_passages")


# ---------------------------------------------------------------- pas d'hybride
def fig14_hybride_extraction():
    from tals import scores_par_type
    from src.cdr import charger_cdr, mentions_reference
    from src.extraction import lire_predictions
    ref = mentions_reference(charger_cdr(RACINE / "CDR_Data/CDR.Corpus.v010516")["validation"])
    R = RACINE / "resultats/extraction"
    dic = lire_predictions(R / "predictions_dictionnaire_v4_validation.jsonl")
    app = lire_predictions(R / "predictions_apprise_v3_validation.jsonl")
    par_doc = defaultdict(list)
    for m in app:
        par_doc[m.doc].append(m)
    ajouts = {m for m in dic if not any(o.debut < m.fin and m.debut < o.fin for o in par_doc[m.doc])}
    combis = [("DIC-v4", dic, ORANGE), ("APP-v3", app, BLEU), ("Intersection", dic & app, GRIS),
              ("Union", dic | app, GRIS), ("APP-v3 + DIC\n(sans chevauchement)", app | ajouts, GRIS)]
    scores = [scores_par_type(ref, p)["micro"] for _, p, _ in combis]
    for (nom, _, _), s in zip(combis, scores):
        print(" ", nom.replace("\n", " "), s)
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [3.2, 2]})
    ax = axes[0]; x = np.arange(len(combis)); w = 0.26; ax.set_ylim(0, 1.08)
    for j, (attr, nom, alpha) in enumerate((("precision", "P", 0.45), ("rappel", "R", 0.7), ("F1", "F1", 1.0))):
        vals = [getattr(s, attr) for s in scores]
        for xi, v, (_, _, c) in zip(x + (j - 1) * w, vals, combis):
            ax.bar(xi, v, w, color=c, alpha=alpha, edgecolor="white", linewidth=1.5)
            ax.text(xi, v + 0.01, fr(v), ha="center", va="bottom", fontsize=9, zorder=4,
                    bbox=dict(fc="white", ec="none", pad=0.6))
    ax.axhline(scores[1].F1, color=BLEU, ls="--", lw=1.2)
    ax.set_xticks(x, [n for n, _, _ in combis], fontsize=10); ax.grid(axis="x", visible=False)
    ax.set_title("Combinaisons (VALIDATION)", fontsize=13)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=GRIS_FONCE, alpha=a, label=l) for l, a in (("Précision", 0.45), ("Rappel", 0.7), ("F1", 1.0))]
              + [Line2D([], [], color=BLEU, ls="--", label="F1 APP-v3")], handlelength=1.0, handleheight=1.0,
              loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.25))
    # complémentarité
    ax = axes[1]
    parts = [("Trouvées par\nles deux", len(ref & dic & app), GRIS_FONCE), ("Par APP-v3\nseulement", len((ref & app) - dic), BLEU),
             ("Par DIC-v4\nseulement", len((ref & dic) - app), ORANGE), ("Par aucune", len(ref - dic - app), ROUGE)]
    y = np.arange(len(parts))[::-1]
    ax.barh(y, [p[1] for p in parts], color=[p[2] for p in parts], height=0.62, edgecolor="white", linewidth=2)
    for yi, (_, v, _) in zip(y, parts):
        ax.text(v + 80, yi, f"{v:,}".replace(",", " ") + f"  ({fr(100 * v / len(ref), 1)} %)", va="center", fontsize=11)
    ax.set_yticks(y, [p[0] for p in parts]); ax.set_xlim(0, 9500); ax.grid(axis="y", visible=False)
    ax.set_title(f"Entités de référence ({len(ref):,})".replace(",", " "), fontsize=13)
    fig.tight_layout()
    sauver(fig, "14_pourquoi_pas_hybride_extraction")


def fig15_hybride_qa():
    lignes = [  # rapport/3_question_reponse.ipynb, recherche hybride (DEV, 16 questions avec réponse) : rappel@5, couverture@5, temps / question
        ("BM25 + racinisation", 0.781, 0.823, "< 0,01 s", ORANGE),
        ("Recherche dense", 0.875, 0.979, "0,04 s", BLEU),
        ("Hybride RRF, poids égaux", 0.781, 0.802, "", GRIS),
        ("Hybride RRF, dense × 1,5 à × 3", 0.812, 0.844, "", GRIS),
        ("Hybride « grand écart »", 0.781, 0.885, "", GRIS),
        ("Union BM25 + dense\nreclassée (cross-encoder)", 0.875, 0.958, "3,5 s", GRIS),
    ]
    fig, ax = plt.subplots(figsize=(13, 5.8))
    y = np.arange(len(lignes))[::-1]; h = 0.36
    for yi, (nom, r, c, t, coul) in zip(y, lignes):
        ax.barh(yi + h / 2, r, h, color=coul, edgecolor="white", linewidth=1.5)
        ax.barh(yi - h / 2, c, h, color=coul, alpha=0.5, edgecolor="white", linewidth=1.5)
        ax.text(r + 0.005, yi + h / 2, fr(r, 3), va="center", fontsize=10)
        ax.text(c + 0.005, yi - h / 2, fr(c, 3) + (f"   ({t} / question)" if t else ""), va="center", fontsize=10)
    ax.set_yticks(y, [l[0] for l in lignes]); ax.set_xlim(0, 1.22); ax.set_xticks(np.arange(0, 1.01, 0.2))
    ax.grid(axis="y", visible=False)
    ax.axvline(0.875, color=BLEU, ls="--", lw=1.1)
    ax.set_xlabel("DEV")
    carres(ax, [("Rappel@5", GRIS_FONCE), ("Couverture des éléments@5", GRIS_FONCE, 0.5)], loc="upper center",
           ncol=2, bbox_to_anchor=(0.5, -0.14))
    sauver(fig, "15_pourquoi_pas_hybride_qa")


def fig16_construction_dic_v4():
    etapes = [  # rapport/1_extraction.ipynb, DIC-v4 : variantes comparées sur VALIDATION (cumulatives)
        ("DIC-v3", 0.8811, 0.7314, 0.7993), ("+ MeSH\nsans filtre", 0.7733, 0.8598, 0.8142),
        ("+ filtre\npar terme", 0.8580, 0.8633, 0.8607), ("+ filtre par\nbranche (niv. 1)", 0.8823, 0.8627, 0.8724),
        ("+ filtre par\nbranche (niv. 2)\n= DIC-v4", 0.9032, 0.8669, 0.8847),
    ]
    x = np.arange(len(etapes))
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.axhline(0.9119, color=BLEU, ls="--", lw=1.3, zorder=1)
    ax.text(len(etapes) - 0.6, 0.9119 + 0.004, "F1 APP-v3", color=BLEU, fontsize=10.5, ha="right", va="bottom")
    for k, (nom, coul, lw) in enumerate((("Précision", AQUA, 2), ("Rappel", VIOLET, 2), ("F1", ORANGE, 3.2))):
        v = [e[1 + k] for e in etapes]
        ax.plot(x, v, color=coul, lw=lw, marker="o", ms=9 if k == 2 else 7, markeredgecolor="white",
                markeredgewidth=1.5, zorder=3)
        for xi, vi in zip(x, v):
            if k < 2 and xi in (2, 3):  # précision et rappel étiquetés seulement aux étapes clés (lisibilité)
                continue
            decal = {0: 9, 1: -16, 2: 9}[k]
            ax.annotate(fr(vi, 3 if k == 2 else 2), (xi, vi), xytext=(0, decal), textcoords="offset points", ha="center", fontsize=10,
                        fontweight="bold" if k == 2 else "normal", color=ENCRE,
                        bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xticks(x, [e[0] for e in etapes], fontsize=11); ax.set_ylim(0.70, 0.95)
    ax.grid(axis="x", visible=False); ax.set_ylabel("VALIDATION")
    carres(ax, [("Précision", AQUA), ("Rappel", VIOLET), ("F1", ORANGE)], loc="lower right", ncol=3)
    sauver(fig, "16_construction_dic_v4")


if __name__ == "__main__":
    for f in (fig01_precision_rappel, fig02_test_par_categorie, fig03_types_erreurs, fig04_etat_art, fig05_epoques,
              fig06_regles, fig07_validation_test, fig08_exemple, fig09_negation, fig10_recherche, fig11_reponses,
              fig12_mistral, fig13_nb_passages, fig14_hybride_extraction, fig15_hybride_qa,
              fig16_construction_dic_v4):
        f()
