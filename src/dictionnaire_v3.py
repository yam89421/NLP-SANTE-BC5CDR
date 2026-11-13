"""Méthode par dictionnaire et règles, version figée DIC-v3 (section 2.3 du livret).

Regroupée dans une classe pour être réutilisée (rapport, application Streamlit) : tout est appris sur TRAIN,
puis appliqué à n'importe quel texte. Configuration figée : casse insensible, seuil 0,3, regex, ajouts A (filtre
corrigé), B (variantes), C (extension à droite) et D (propagation).

Ordre des règles : suffixes, modificateurs à gauche, extension à droite, « X-induced », sigles, préfixe anti-,
propagation.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from types import SimpleNamespace

from tals import Mention, cle_normalisee
from tals.spans import tokeniser_avec_offsets

from .cdr import CATEGORIES
from .dictionnaire import ConfigDictionnaire, DictionnaireCDR

CONFIG_V3 = ConfigDictionnaire("insensible", 0.3, True)

EXCLUS_INDUIT = {"drug", "drugs", "stress", "therapy", "anesthesia", "handling", "blockade", "stimulus", "contrast",
                 "acid", "exercise", "surgery", "treatment", "injury", "ischemia", "hypoxia", "radiation", "diet",
                 "agonist", "antagonist", "neuroleptic", "analgesic", "psychostimulant", "the", "both", "rapid",
                 "maximal", "single", "combined", "chronic", "saline"}
ADJECTIF = re.compile(r".*(?:al|ic|ive|ous|ed|ing|ar)")


def mot_avant(texte, pos):
    """Mot qui précède immédiatement la position `pos` : (mot en minuscules, début) ou None."""
    debut = max(0, pos - 40)
    r = re.search(r"([A-Za-z][\w']*)\s+$", texte[debut:pos])
    return (r.group(1).lower(), debut + r.start(1)) if r else None


def libre(m, P):
    """Vrai si la mention ne chevauche aucune mention de P (P : mentions d'un même document)."""
    return all(m.fin <= x.debut or x.fin <= m.debut for x in P)


def variante(mot):
    """Variante singulier / pluriel du dernier mot d'une entrée (ajout B)."""
    if not mot.isalpha() or len(mot) < 4:
        return None
    if mot.endswith("ies"):
        return mot[:-3] + "y"
    if mot.endswith(("ses", "xes", "ches", "shes")):
        return mot[:-2]
    if mot.endswith("s") and not mot.endswith(("ss", "us", "is")):
        return mot[:-1]
    if mot.endswith("y") and mot[-2] not in "aeiou":
        return mot[:-1] + "ies"
    if mot.endswith(("s", "x", "ch", "sh")):
        return mot + "es"
    return mot + "s"


class DictionnaireCorrige(DictionnaireCDR):
    """Ajout A : une occurrence incluse dans une mention plus longue ne compte plus comme « non annotée »."""

    def construire(self, documents_train):
        super().construire(documents_train)          # entrées et types, comme au 2.3
        types = defaultdict(Counter)
        for d in documents_train:
            for m in d.mentions:
                types[self._cle(m.texte)][m.type] += 1
        self.entrees = {cle: c.most_common(1)[0][0] for cle, c in types.items() if cle}
        self.longueur_max = max(len(k) for k in self.entrees)
        trouvees, annotees = Counter(), Counter()
        for d in documents_train:
            ref = {(m.debut, m.fin, m.type) for m in d.mentions}
            spans = [(m.debut, m.fin) for m in d.mentions]
            for cle, debut, fin, type_ in self._correspondances(d.texte):
                if (debut, fin, type_) not in ref and any(x <= debut and fin <= y and (x, y) != (debut, fin) for x, y in spans):
                    continue                          # occurrence incluse dans une mention plus longue : ignorée
                trouvees[cle] += 1
                annotees[cle] += (debut, fin, type_) in ref
        for cle in self.entrees:
            self.stats[cle]["taux"] = annotees[cle] / trouvees[cle] if trouvees[cle] else 0.0
        self.entrees = {c: t for c, t in self.entrees.items() if self.stats[c]["taux"] >= self.config.seuil_annotation}
        self.longueur_max = max(len(k) for k in self.entrees)
        return self


REGLES_V2 = ("suffixes", "modificateurs", "induit", "sigles", "anti")   # les cinq règles de DIC-v2


class DictionnaireV3:
    """DIC-v3 : dictionnaire A + B appris sur TRAIN, puis les sept règles. `construire(train)` avant `extraire`.

    Les options (toutes actives par défaut = DIC-v3) permettent de retrouver les versions précédentes et de mesurer
    chaque ajout seul : DIC-v1 = `DictionnaireV3(False, False, False, False, regles=())` ; DIC-v2 =
    `DictionnaireV3(False, False, False, False)` ; `regles` choisit parmi les cinq règles de DIC-v2.
    """

    def __init__(self, filtre_corrige=True, variantes=True, extension=True, propagation=True, regles=REGLES_V2):
        self.options = {"filtre_corrige": filtre_corrige, "variantes": variantes, "extension": extension,
                        "propagation": propagation}
        self.regles = tuple(regles)

    def construire(self, train) -> "DictionnaireV3":
        dic_v2 = DictionnaireCDR(CONFIG_V3).construire(train)   # base des règles apprises (comme au 2.3)

        # Règle des suffixes
        compte = defaultdict(Counter)
        for d in train:
            types = {(m.debut, m.fin): m.type for m in d.mentions}
            for r in re.finditer(r"\b[a-z]{7,}\b", d.texte):
                for n in (4, 5, 6):
                    compte[r.group()[-n:]][types.get(r.span(), "O")] += 1
        suffixes = {}
        for suffixe, c in compte.items():
            type_, k = max(((t, c[t]) for t in CATEGORIES), key=lambda x: x[1])
            if sum(c.values()) >= 8 and k / sum(c.values()) >= 0.8:
                suffixes[suffixe] = type_
        suffixes = {s: t for s, t in suffixes.items()
                    if not any(o != s and s.endswith(o) and suffixes[o] == t for o in suffixes)}
        self.regex_suffixes = {t: re.compile(r"\b[A-Za-z][a-z]{3,}(?:" + "|".join(
            sorted((s for s, u in suffixes.items() if u == t), key=len, reverse=True)) + r")\b") for t in CATEGORIES}

        # Règle des modificateurs à gauche
        inclus, exclus = Counter(), Counter()
        for d in train:
            maladies = {(m.debut, m.fin) for m in d.mentions if m.type == "Disease"}
            for _, a, b, type_ in dic_v2._correspondances(d.texte):
                mot = mot_avant(d.texte, a) if type_ == "Disease" else None
                if mot is None:
                    continue
                if any(x <= mot[1] and y >= b for x, y in maladies):
                    inclus[mot[0]] += 1
                elif (a, b) in maladies:
                    exclus[mot[0]] += 1
        self.modificateurs = {w for w in inclus if inclus[w] >= 3 and inclus[w] / (inclus[w] + exclus[w]) >= 0.7}

        # Ajout C : suites apprises pour l'extension à droite
        inclus_d, exclus_d = Counter(), Counter()
        for d in train:
            toks = tokeniser_avec_offsets(d.texte)
            fin_tok = {b: j for j, (_, _, b) in enumerate(toks)}
            gold = {(m.debut, m.fin, m.type) for m in d.mentions}
            for _, a, b, type_ in dic_v2._correspondances(d.texte):
                j = fin_tok.get(b)
                if j is None:
                    continue
                for k in (1, 2, 3):
                    if j + k >= len(toks):
                        break
                    suite = (type_, tuple(cle_normalisee(t[0]) for t in toks[j + 1:j + k + 1]))
                    fin = toks[j + k][2]
                    if any(x <= a and y == fin and t == type_ for x, y, t in gold):
                        inclus_d[suite] += 1
                    elif (a, b, type_) in gold:
                        exclus_d[suite] += 1
        self.suites = {s for s in inclus_d if inclus_d[s] >= 3 and inclus_d[s] / (inclus_d[s] + exclus_d[s]) >= 0.7}

        # Ajouts A et B : dictionnaire corrigé + variantes jamais vues dans TRAIN
        ngrammes_train = set()
        for d in train:
            cles = [cle_normalisee(s) for s, _, _ in tokeniser_avec_offsets(d.texte)]
            for n in range(1, dic_v2.longueur_max + 1):
                ngrammes_train.update(tuple(cles[i:i + n]) for i in range(len(cles) - n + 1))
        self.dic = (DictionnaireCorrige if self.options["filtre_corrige"] else DictionnaireCDR)(CONFIG_V3).construire(train)
        ajouts = {}
        for cle, type_ in (self.dic.entrees.items() if self.options["variantes"] else []):
            v = variante(cle[-1])
            if v:
                cle_v = cle[:-1] + (v,)
                if cle_v not in self.dic.entrees and cle_v not in ngrammes_train:
                    ajouts[cle_v] = type_
        self.dic.entrees.update(ajouts)
        self.dic.longueur_max = max(len(k) for k in self.dic.entrees)
        self.variantes_ajoutees = len(ajouts)
        return self

    # --- Règles ---
    def r_suffixes(self, d, P):
        P = set(P)
        for type_, motif in self.regex_suffixes.items():
            for r in motif.finditer(d.texte):
                m = Mention(d.document_id, r.start(), r.end(), type_)
                if libre(m, P):
                    P.add(m)
        return P

    def r_modificateurs(self, d, P):
        P = set(P)
        for m in sorted((m for m in P if m.type == "Disease"), key=lambda m: -m.debut):
            mot = mot_avant(d.texte, m.debut)
            if mot and mot[0] in self.modificateurs:
                etendue = Mention(m.doc, mot[1], m.fin, "Disease")
                if libre(etendue, P - {m}):
                    P = (P - {m}) | {etendue}
        return P

    def r_extension_droite(self, d, P):
        P = set(P)
        toks = tokeniser_avec_offsets(d.texte)
        fin_tok = {b: j for j, (_, _, b) in enumerate(toks)}
        for m in sorted(P, key=lambda m: m.debut):
            j = fin_tok.get(m.fin)
            if j is None or m not in P:
                continue
            for k in (3, 2, 1):
                if j + k < len(toks) and (m.type, tuple(cle_normalisee(t[0]) for t in toks[j + 1:j + k + 1])) in self.suites:
                    etendue = Mention(m.doc, m.debut, toks[j + k][2], m.type)
                    if libre(etendue, P - {m}):
                        P = (P - {m}) | {etendue}
                    break
        return P

    def r_induit(self, d, P):
        P = set(P)
        for motif in (r"(?<![\w-])([A-Za-z][A-Za-z0-9]{3,})-induced\b", r"\binduced by (?:the |a )?([A-Za-z][A-Za-z0-9-]{3,})\b"):
            for r in re.finditer(motif, d.texte):
                mot = r.group(1).lower()
                if mot in EXCLUS_INDUIT or ADJECTIF.fullmatch(mot):
                    continue
                m = Mention(d.document_id, *r.span(1), "Chemical")
                if libre(m, P):
                    P.add(m)
        return P

    def r_sigles(self, d, P):
        t, P = d.texte, set(P)
        for r in re.finditer(r"\s\(([A-Za-z0-9][A-Za-z0-9-]{0,9})\)", t):
            sigle = r.group(1)
            if not re.search(r"[A-Z]", sigle):
                continue
            longues = [m for m in P if m.fin == r.start()]
            occurrences = [(x.start(), x.end()) for x in re.finditer(r"(?<![\w-])" + re.escape(sigle) + r"(?![\w-])", t)]
            if longues:
                type_ = longues[0].type
                P = {m for m in P if not ((m.debut, m.fin) in occurrences and m.type != type_)}
                for a, b in occurrences:
                    m = Mention(d.document_id, a, b, type_)
                    if libre(m, P):
                        P.add(m)
            elif self.dic._cle(sigle) not in self.dic.entrees:
                P = {m for m in P if (m.debut, m.fin) not in occurrences}
        return P

    def r_anti(self, d, P):
        return {m for m in P if not d.texte[m.debut:m.fin].lower().startswith("anti")}

    def r_propagation(self, d, P):
        P = set(P)
        for forme, type_ in {(d.texte[m.debut:m.fin], m.type) for m in P}:
            for r in re.finditer(r"(?<![\w-])" + re.escape(forme) + r"(?![\w-])", d.texte):
                m = Mention(d.document_id, r.start(), r.end(), type_)
                if libre(m, P):
                    P.add(m)
        return P

    def _document(self, d) -> set[Mention]:
        P = self.dic.extraire(d.texte, doc=d.document_id)
        for regle in self._ordre():
            P = regle(d, P)
        return P

    def _ordre(self):
        """Règles actives, dans l'ordre de DIC-v3."""
        ordre = [("suffixes", self.r_suffixes), ("modificateurs", self.r_modificateurs),
                 ("extension", self.r_extension_droite), ("induit", self.r_induit), ("sigles", self.r_sigles),
                 ("anti", self.r_anti), ("propagation", self.r_propagation)]
        return [f for nom, f in ordre if nom in self.regles or self.options.get(nom)]

    def extraire(self, texte: str, doc: str = "doc") -> set[Mention]:
        return self._document(SimpleNamespace(document_id=doc, texte=texte))

    def extraire_corpus(self, documents) -> set[Mention]:
        sortie = set()
        for d in documents:
            sortie |= self._document(d)
        return sortie
