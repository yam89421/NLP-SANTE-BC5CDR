"""Lexique MeSH (NLM) pour la méthode par dictionnaire, version DIC-v4.

MeSH 2026, fichiers XML officiels de la NLM, téléchargés dans `data/mesh/` (non versionnés) :
  - descripteurs (`desc2026.gz`) : catégorie donnée par l'arbre MeSH, C (maladies) ou F03 (troubles mentaux)
    → Disease, D (produits chimiques et médicaments) → Chemical ;
  - concepts supplémentaires (`supp2026.zip`) : classe 1 (substances) → Chemical, classe 3 (maladies rares)
    → Disease ; les autres classes (protocoles, organismes) sont ignorées.
Tous les termes d'un enregistrement sont repris (nom principal et synonymes). MeSH écrit souvent les termes à
l'envers (« Infarction, Myocardial ») : la forme remise à l'endroit (« Myocardial Infarction ») est ajoutée.

Le lexique extrait est mis en cache dans `data/mesh/lexique_mesh_2026.tsv.gz` (terme, catégorie, source, branches).
"""
from __future__ import annotations

import gzip
import re
import urllib.request
import zipfile
from pathlib import Path
from xml.etree.ElementTree import iterparse

URL = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/"
FICHIERS = ("desc2026.gz", "supp2026.zip")
INVERSE = re.compile(r"^([A-Za-z][A-Za-z -]*), ([A-Za-z][A-Za-z -]*)$")   # « Infarction, Myocardial »


def telecharger(dossier: Path) -> None:
    """Télécharge les deux fichiers MeSH s'ils sont absents (≈ 64 Mo)."""
    dossier.mkdir(parents=True, exist_ok=True)
    for nom in FICHIERS:
        if not (dossier / nom).exists():
            urllib.request.urlretrieve(URL + nom, dossier / nom)


def formes(terme: str) -> list[str]:
    """Le terme et, s'il est écrit à l'envers, sa forme à l'endroit."""
    r = INVERSE.match(terme)
    return [terme, f"{r.group(2)} {r.group(1)}"] if r else [terme]


def categorie_descripteur(arbres: list[str]) -> str | None:
    if any(a.startswith(("C", "F03")) for a in arbres):
        return "Disease"
    if any(a.startswith("D") for a in arbres):
        return "Chemical"
    return None


def _enregistrements(flux, balise):
    """Parcourt un fichier XML MeSH enregistrement par enregistrement, sans tout charger en mémoire."""
    for _, elem in iterparse(flux, events=("end",)):
        if elem.tag == balise:
            yield elem
            elem.clear()


def _termes(elem) -> set[str]:
    return {s.text.strip() for s in elem.iterfind("ConceptList/Concept/TermList/Term/String") if s.text}


def lire_mesh(dossier: Path) -> list[tuple[str, str, str, str]]:
    """Lexique (terme, catégorie, source, branches) ; source = « descripteur » ou « supplementaire » ;
    branches = numéros d'arbre MeSH coupés au 2e niveau (« D12.776 » protéines, « C10.228 »…), séparés par des
    virgules. Un concept
    supplémentaire prend les branches des descripteurs auxquels MeSH le rattache."""
    lexique, arbres = [], {}
    with gzip.open(dossier / "desc2026.gz") as f:
        for e in _enregistrements(f, "DescriptorRecord"):
            numeros = [t.text for t in e.iterfind("TreeNumberList/TreeNumber")]
            arbres[e.findtext("DescriptorUI")] = numeros
            categorie = categorie_descripteur(numeros)
            if categorie:
                lexique += [(x, categorie, "descripteur", _branches(numeros)) for t in _termes(e) for x in formes(t)]
    classes = {"1": "Chemical", "3": "Disease"}
    with zipfile.ZipFile(dossier / "supp2026.zip") as z, z.open("supp2026.xml") as f:
        for e in _enregistrements(f, "SupplementalRecord"):
            categorie = classes.get(e.get("SCRClass"))
            if categorie:
                numeros = [n for ui in e.iterfind("HeadingMappedToList/HeadingMappedTo/DescriptorReferredTo/DescriptorUI")
                           for n in arbres.get(ui.text.lstrip("*"), [])]
                lexique += [(x, categorie, "supplementaire", _branches(numeros)) for t in _termes(e) for x in formes(t)]
    return lexique


def _branches(numeros: list[str]) -> str:
    return ",".join(sorted({n[:7] for n in numeros}))


def charger_lexique(dossier: Path) -> list[tuple[str, str, str, str]]:
    """Lexique MeSH depuis le cache, ou construit (téléchargement + lecture, ≈ 2 min) puis mis en cache."""
    cache = dossier / "lexique_mesh_2026.tsv.gz"
    if not cache.exists():
        telecharger(dossier)
        lexique = sorted(set(lire_mesh(dossier)))
        with gzip.open(cache, "wt", encoding="utf-8") as f:
            f.writelines("\t".join(ligne) + "\n" for ligne in lexique if "\t" not in ligne[0])
    with gzip.open(cache, "rt", encoding="utf-8") as f:
        return [tuple(ligne.rstrip("\n").split("\t")) for ligne in f]
