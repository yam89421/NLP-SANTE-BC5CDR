"""Recherche lexicale BM25 et mesures de recherche (section 4.1 du livret, annexe B.3 du guide).

BM25 est repris sans modification du TD RAG du cours (question_answering/TD_RAG_HAS) :
  - tokenisation `\\w+` en minuscules, accents, nombres et négations conservés ;
  - IDF positive log(1 + (N - df + 0.5) / (df + 0.5)), k1 = 1.5, b = 0.75 ;
  - chaque mot de la question compté une fois ; ex æquo dans l'ordre du corpus.
Ajouts réglés sur DEV (REC-v2), désactivés par défaut : racinisation Snowball français et mots vides
(liste NLTK sans les négations), appliqués de la même façon aux passages et aux questions.

Mesures, sur les seules questions avec réponse :
  - Hit@k et Rappel@k sur les preuves annotées `evidence_ids` (formules B.3 du guide) ;
  - variante « avec équivalents » : une preuve compte comme retrouvée si elle-même ou un passage
    équivalent du même élément (`equivalents_by_element`) est dans le top-k ;
  - couverture des éléments@k : part des éléments attendus dont au moins une preuve ou un
    équivalent est dans le top-k (vérifie qu'une réponse complexe dispose de tous ses éléments).
"""
from __future__ import annotations

import re
from collections import Counter

import numpy as np

K1, B = 1.5, 0.75


# Mots vides : liste française de NLTK (stopwords « french », 157 mots), recopiée pour rester reproductible
# hors ligne, **sans les négations** (« ne », « pas », « n ») : le guide demande de les conserver.
_MOTS_VIDES_NLTK = """au aux avec ce ces dans de des du elle en et eux il ils je la le les leur lui ma mais me même
mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se ses son sur ta te tes toi ton tu un une vos votre
vous c d j l à m n s t y été étée étées étés étant étante étants étantes suis es est sommes êtes sont serai seras
sera serons serez seront serais serait serions seriez seraient étais était étions étiez étaient fus fut fûmes
fûtes furent sois soit soyons soyez soient fusse fusses fût fussions fussiez fussent ayant ayante ayantes ayants
eu eue eues eus ai as avons avez ont aurai auras aura aurons aurez auront aurais aurait aurions auriez auraient
avais avait avions aviez avaient eut eûmes eûtes eurent aie aies ait ayons ayez aient eusse eusses eût eussions
eussiez eussent""".split()
NEGATIONS = {"ne", "n", "pas", "sans", "aucun", "aucune", "jamais", "ni", "rien", "non", "plus"}
MOTS_VIDES = frozenset(_MOTS_VIDES_NLTK) - NEGATIONS


def tokeniser(texte: str, mots_vides: bool = False, racines: bool = False) -> list[str]:
    """Mots et nombres en minuscules ; la ponctuation sépare les unités (TD RAG).

    Options (réglage REC-v2, testées sur DEV) : retrait des mots vides français (négations et nombres
    conservés) ; racinisation Snowball français (« infections » → « infect »). Les nombres ne sont pas racinisés.
    """
    mots = re.findall(r"\w+", texte.lower())
    if mots_vides:
        mots = [m for m in mots if m not in MOTS_VIDES]
    if racines:
        mots = [m if m.isdigit() else r for m, r in zip(mots, _raciniseur().stemWords(mots))]
    return mots


_RACINISEUR = None


def _raciniseur():
    global _RACINISEUR
    if _RACINISEUR is None:
        import snowballstemmer
        _RACINISEUR = snowballstemmer.stemmer("french")
    return _RACINISEUR


def construire_bm25(textes: list[str], mots_vides: bool = False, racines: bool = False) -> dict:
    """Statistiques du corpus pour BM25 : compteurs de termes, longueurs, longueur moyenne, df.

    Le prétraitement choisi est gardé dans l'index et appliqué de la même façon aux questions.
    """
    pretraitement = {"mots_vides": mots_vides, "racines": racines}
    compteurs = [Counter(tokeniser(t, **pretraitement)) for t in textes]
    longueurs = np.array([sum(c.values()) for c in compteurs], dtype=float)
    if not len(longueurs) or longueurs.mean() == 0:
        raise ValueError("Le corpus ne contient aucun terme indexable.")
    df = Counter()
    for c in compteurs:
        df.update(c.keys())
    return {"compteurs": compteurs, "longueurs": longueurs, "moyenne": longueurs.mean(), "df": df,
            "pretraitement": pretraitement}


def scores_bm25(question: str, index: dict, k1: float = K1, b: float = B) -> np.ndarray:
    """Un score BM25 par passage, dans l'ordre de l'index."""
    n = len(index["compteurs"])
    scores = np.zeros(n)
    correction = k1 * (1 - b + b * index["longueurs"] / index["moyenne"])
    for terme in set(tokeniser(question, **index.get("pretraitement", {}))):
        df = index["df"].get(terme, 0)
        idf = np.log(1 + (n - df + 0.5) / (df + 0.5))
        tf = np.array([c.get(terme, 0) for c in index["compteurs"]], dtype=float)
        scores += idf * tf * (k1 + 1) / (tf + correction)
    return scores


def premiers(scores: np.ndarray, k: int = 5) -> list[tuple[int, float]]:
    """(indice, score) des k meilleurs passages ; tri stable, les ex æquo gardent l'ordre du corpus."""
    indices = np.argsort(-np.asarray(scores), kind="stable")[:k]
    return [(int(i), float(scores[i])) for i in indices]


def mesures_question(question: dict, retrouves: list[str], k: int = 5) -> dict:
    """Hit@k, Rappel@k (stricts et avec équivalents) et couverture des éléments pour une question."""
    top = set(retrouves[:k])
    preuves = question["evidence_ids"]
    par_element = question["evidence_by_element"]
    equivalents = question.get("equivalents_by_element") or [[] for _ in par_element]

    # Équivalents d'une preuve : ceux des éléments qu'elle justifie.
    equiv_preuve = {p: set() for p in preuves}
    for ids, eqs in zip(par_element, equivalents):
        for p in ids:
            equiv_preuve[p].update(eqs)

    trouvees = [p in top for p in preuves]
    trouvees_eq = [p in top or bool(equiv_preuve[p] & top) for p in preuves]
    elements = [bool((set(ids) | set(eqs)) & top) for ids, eqs in zip(par_element, equivalents)]
    return {
        f"hit@{k}": int(any(trouvees)),
        f"rappel@{k}": sum(trouvees) / len(preuves),
        f"hit@{k}_equiv": int(any(trouvees_eq)),
        f"rappel@{k}_equiv": sum(trouvees_eq) / len(preuves),
        f"couverture_elements@{k}": sum(elements) / len(elements),
        "rang_premiere_preuve": next((r for r, p in enumerate(retrouves, start=1) if p in preuves), None),
    }


# ------------------------------------------------- Approfondissement : recherche dense et hybride (guide C.1)

MODELE_DENSE = "intfloat/multilingual-e5-small"   # modèle du TD RAG


class IndexDense:
    """Recherche sémantique (TD RAG) : vecteurs E5 normalisés, préfixes « passage: » / « query: », cosinus."""

    def __init__(self, textes: list[str], modele: str = MODELE_DENSE, appareil: str = "cpu"):
        from sentence_transformers import SentenceTransformer
        self.encodeur = SentenceTransformer(modele, device=appareil)
        self.tronques = sum(len(self.encodeur.tokenizer("passage: " + t)["input_ids"]) > self.encodeur.max_seq_length
                            for t in textes)
        self.vecteurs = self.encodeur.encode(["passage: " + t for t in textes], normalize_embeddings=True,
                                             batch_size=16, convert_to_numpy=True)

    def scores(self, question: str) -> np.ndarray:
        requete = self.encodeur.encode("query: " + question, normalize_embeddings=True, convert_to_numpy=True)
        return self.vecteurs @ requete


def fusion_rrf(classements: list[list[int]], k: int = 5, candidats: int = 20, constante: int = 60,
               poids: list[float] | None = None) -> list[tuple[int, float]]:
    """Reciprocal Rank Fusion (TD RAG) : somme de poids / (constante + rang) sur les `candidats` premiers de chaque
    classement ; les scores bruts (BM25, cosinus) ne sont jamais additionnés. Ex æquo : ordre du corpus.
    `poids` (essai sur DEV) : un poids par classement, 1 par défaut (RRF du TD)."""
    poids = poids or [1.0] * len(classements)
    scores = Counter()
    for classement, w in zip(classements, poids):
        for rang, i in enumerate(classement[:candidats], start=1):
            scores[i] += w / (constante + rang)
    ordre = sorted(scores, key=lambda i: (-scores[i], i))
    return [(i, scores[i]) for i in ordre[:k]]


MODELE_RECLASSEUR = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"   # multilingue, 118 M paramètres


class Reclasseur:
    """Reclassement (cross-encoder) : le modèle lit la question et le passage ensemble et donne un score de
    pertinence ; plus précis qu'un cosinus entre deux vecteurs, mais un calcul par paire (question, passage)."""

    def __init__(self, modele: str = MODELE_RECLASSEUR, appareil: str = "cpu"):
        from sentence_transformers import CrossEncoder
        self.modele = CrossEncoder(modele, device=appareil, max_length=512)

    def reclasser(self, question: str, candidats: list[int], textes: list[str]) -> list[int]:
        """Candidats triés par score décroissant ; ex æquo : ordre du corpus."""
        scores = self.modele.predict([(question, textes[i]) for i in candidats], batch_size=16)
        return [i for _, i in sorted(zip(-scores, candidats))]
