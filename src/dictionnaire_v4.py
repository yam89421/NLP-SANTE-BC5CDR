"""Méthode par dictionnaire et règles, version DIC-v4 : DIC-v3 + lexique MeSH.

DIC-v3 est construite sans changement (dictionnaire, variantes et règles appris sur TRAIN). On ajoute ensuite au
dictionnaire les termes MeSH (`src/mesh.py`) :
  - priorité à TRAIN : un terme dont la forme a été annotée dans TRAIN garde le type et la décision de TRAIN
    (y compris quand le filtre l'a retirée) ;
  - un terme MeSH classé à la fois Chemical et Disease est ignoré ;
  - termes plus longs que la plus longue entrée de DIC-v3 ou de moins de `longueur_min` caractères ignorés ;
  - filtre par branche MeSH : une branche dont les termes, cherchés dans les textes de TRAIN, sont annotés moins de
    30 % du temps (protéines, enzymes, classes de médicaments…) est écartée entièrement, ainsi que tout terme qui
    en fait partie ;
  - filtre par terme, comme pour DIC-v3 (seuil 0,3) : un terme MeSH trouvé dans les textes de TRAIN mais rarement
    annoté (*lead, water…*) est retiré ; un terme jamais rencontré dans TRAIN est gardé.
Les taux sont calculés comme l'ajout A de DIC-v3 (occurrences incluses dans une mention plus longue ignorées).
Les règles de DIC-v3 s'appliquent ensuite sur ce dictionnaire élargi, dans le même ordre.
`sauver_ajouts` écrit les termes MeSH retenus ; `DictionnaireV4Fige` reconstruit DIC-v4 à partir
de ce fichier (application Streamlit) et `verifier_dic_v4()` contrôle qu'on retrouve les prédictions TEST.
"""
from __future__ import annotations

import gzip
from collections import Counter, defaultdict

from .dictionnaire import DictionnaireCDR
from .dictionnaire_v3 import CONFIG_V3, DictionnaireV3


def taux_train(dic, train):
    """Occurrences trouvées et annotées de chaque entrée de `dic` dans les textes de TRAIN (calcul de l'ajout A)."""
    trouvees, annotees = Counter(), Counter()
    for d in train:
        ref = {(m.debut, m.fin, m.type) for m in d.mentions}
        spans = [(m.debut, m.fin) for m in d.mentions]
        for cle, debut, fin, type_ in dic._correspondances(d.texte):
            if (debut, fin, type_) not in ref and any(x <= debut and fin <= y and (x, y) != (debut, fin) for x, y in spans):
                continue                              # occurrence incluse dans une mention plus longue : ignorée
            trouvees[cle] += 1
            annotees[cle] += (debut, fin, type_) in ref
    return trouvees, annotees


class DictionnaireV4(DictionnaireV3):
    """DIC-v4 : `DictionnaireV4(lexique).construire(train)` puis `extraire` / `extraire_corpus` comme DIC-v3.

    `lexique` : liste (terme, catégorie, source, branches) de `src.mesh.charger_lexique` ; `sources` choisit les
    parties de MeSH utilisées (« descripteur », « supplementaire ») ; `niveau_branches` : 0 = pas de filtre par
    branche, 1 = branches « D12 », 2 = branches « D12.776 » ; `filtre_termes=False` garde tous les termes.
    """

    def __init__(self, lexique, sources=("descripteur", "supplementaire"), niveau_branches=2, filtre_termes=True,
                 longueur_min=3, occurrences_min=5, **options):
        super().__init__(**options)
        self.lexique = lexique
        self.sources = tuple(sources)
        self.niveau_branches = niveau_branches
        self.filtre_termes = filtre_termes
        self.longueur_min = longueur_min
        self.occurrences_min = occurrences_min   # une branche n'est jugée que sur assez d'occurrences dans TRAIN

    def construire(self, train) -> "DictionnaireV4":
        super().construire(train)                              # DIC-v3
        dic, seuil = self.dic, CONFIG_V3.seuil_annotation

        # Termes MeSH (tous, y compris ceux déjà annotés dans TRAIN) avec leur catégorie et leurs branches
        types, branches = defaultdict(set), defaultdict(set)
        coupe = {1: 3, 2: 7}.get(self.niveau_branches, 0)
        for terme, categorie, source, br in self.lexique:
            if source in self.sources and len(terme) >= self.longueur_min:
                cle = dic._cle(terme)
                if cle and len(cle) <= dic.longueur_max:
                    types[cle].add(categorie)
                    branches[cle].update(b[:coupe] for b in br.split(",") if b)
        tous = {cle: t.pop() for cle, t in types.items() if len(t) == 1}   # catégorie ambiguë : ignoré
        self.mesh_ambigus = len(types) - len(tous)

        # Filtre par branche : taux d'annotation de tous les termes de la branche dans TRAIN
        self.branches_ecartees, self.branches_stats = set(), {}
        if coupe:
            seul = DictionnaireCDR(CONFIG_V3)
            seul.entrees, seul.longueur_max = tous, dic.longueur_max
            trouvees, annotees = taux_train(seul, train)
            t_b, a_b = Counter(), Counter()
            for cle in trouvees:
                for b in branches[cle]:
                    t_b[b] += trouvees[cle]
                    a_b[b] += annotees[cle]
            self.branches_stats = {b: (t_b[b], a_b[b]) for b in t_b}
            self.branches_ecartees = {b for b in t_b if t_b[b] >= self.occurrences_min and a_b[b] / t_b[b] < seuil}

        # Ajout au dictionnaire : priorité à TRAIN, branches écartées exclues
        vus_train = set(dic.stats) | set(dic.entrees)          # formes annotées dans TRAIN (+ variantes B)
        mesh = {cle: t for cle, t in tous.items()
                if cle not in vus_train and not branches[cle] & self.branches_ecartees}
        dic.entrees.update(mesh)

        # Filtre par terme sur TRAIN
        trouvees, annotees = taux_train(dic, train)
        self.mesh_stats = {cle: (trouvees[cle], annotees[cle]) for cle in trouvees if cle in mesh}
        self.mesh_retirees = {cle for cle, (t, a) in self.mesh_stats.items() if a / t < seuil} \
            if self.filtre_termes else set()
        for cle in self.mesh_retirees:
            del dic.entrees[cle]
        self.mesh_ajoutees = {cle: t for cle, t in mesh.items() if cle not in self.mesh_retirees}
        self.mesh_branches = {cle: branches[cle] for cle in self.mesh_ajoutees}
        return self

    def sauver_ajouts(self, chemin) -> None:
        """Écrit les termes MeSH retenus (type, clé) : DIC-v4 = DIC-v3 + ces termes, sans relire MeSH."""
        with gzip.open(chemin, "wt", encoding="utf-8") as f:
            f.writelines(f"{t}\t{SEP.join(cle)}\n" for cle, t in sorted(self.mesh_ajoutees.items()))


SEP = "\x1f"   # séparateur des tokens d'une clé (n'apparaît dans aucun token)


class DictionnaireV4Fige(DictionnaireV3):
    """DIC-v4 figée, pour l'application : DIC-v3 construite sur TRAIN + termes MeSH retenus
    (`resultats/extraction/dictionnaire_v4_termes_mesh.tsv.gz`). Même dictionnaire que `DictionnaireV4`, sans
    télécharger ni filtrer MeSH (≈ 64 Mo et ≈ 1,3 Go de mémoire évités)."""

    def __init__(self, chemin_ajouts, **options):
        super().__init__(**options)
        self.chemin_ajouts = chemin_ajouts

    def construire(self, train) -> "DictionnaireV4Fige":
        super().construire(train)                              # DIC-v3
        with gzip.open(self.chemin_ajouts, "rt", encoding="utf-8") as f:
            for ligne in f:
                t, cle = ligne.rstrip("\n").split("\t")
                self.dic.entrees[tuple(cle.split(SEP))] = t
        return self


def verifier_dic_v4(racine) -> int:
    """Reconstruit DIC-v4 comme l'application et vérifie qu'on retrouve les prédictions TEST sauvegardées."""
    from .cdr import charger_jsonl
    from .extraction import lire_predictions
    documents = charger_jsonl(racine / "data" / "corpus_extraction.jsonl")
    train = [d for d in documents if d.partition == "train"]
    test = [d for d in documents if d.partition == "test"]
    dic = DictionnaireV4Fige(racine / "resultats" / "extraction" / "dictionnaire_v4_termes_mesh.tsv.gz").construire(train)
    pred = dic.extraire_corpus(test)
    attendu = lire_predictions(racine / "resultats" / "extraction" / "predictions_dictionnaire_v4_test.jsonl")
    assert pred == attendu, f"DIC-v4 non reproduite : {len(pred ^ attendu)} différences"
    return len(pred)
