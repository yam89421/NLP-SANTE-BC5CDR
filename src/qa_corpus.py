"""Extraction du texte des documents QA et découpage en passages (section 3.2 du livret).

Démarche (reprise du TD RAG du cours, lecture des PDF avec PyMuPDF) :
  1. extraire le texte en gardant sa provenance (page imprimée, section) ;
  2. retirer les en-têtes, pieds de page, notes de marge et éléments de navigation ;
  3. reconstituer des paragraphes, puis les regrouper en passages à l'intérieur
     d'une même section, jusqu'à une taille maximale en caractères.

Particularités des sources (INCa) :
  - PDF : chaque page PDF est une planche de deux pages imprimées, chacune en une
    ou deux colonnes, avec des encadrés. L'ordre brut du texte n'est pas l'ordre
    de lecture : on trie les blocs par page imprimée, flux (texte courant puis
    encadrés), colonne et position verticale ;
  - HTML : pages cancer.fr, contenu dans le chapô et les blocs « wysiwyg ».

Le texte n'est pas réécrit : seuls les césures de fin de ligne, les puces et les
espaces sont normalisés. Les titres ne sont pas copiés dans le texte du passage,
ils sont conservés dans `localisation.section`.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

TAILLE_MAX = 800   # caractères par passage (le TD RAG utilise 650)

_FIN_PHRASE = re.compile(r"[.!?:;»)…]$")
_PUCE = re.compile(r"^\s*(?:[●•▪n](?:\s*[●•▪])?)\s+|^\s*[●•▪]{1,2}(?=\S)")
_GARDER_TIRET = {"ci", "là", "t", "il", "elle", "ils", "elles", "on", "même", "mêmes", "y"}


@dataclass
class Paragraphe:
    texte: str
    section: str
    pages: list[int] = field(default_factory=list)   # pages imprimées (PDF), vide pour le HTML


def normaliser(texte: str) -> str:
    """NFC, espaces insécables et tabulations remplacés par des espaces simples."""
    texte = unicodedata.normalize("NFC", texte)
    texte = texte.replace(" ", " ").replace("\xa0", " ").replace("\t", " ").replace("­", "")
    return re.sub(r"\s+", " ", texte).strip()


def joindre_lignes(lignes: list[str]) -> str:
    """Recolle les lignes d'un bloc en retirant les césures (« chimio- / thérapie »)."""
    texte = ""
    puce_seule = False
    for ligne in lignes:
        ligne = normaliser(ligne)
        if not ligne:
            continue
        if re.fullmatch(r"[●•▪]+", ligne):      # puce typographiée sur une ligne à part
            puce_seule = True
            continue
        puce = _PUCE.match(ligne)
        if puce or puce_seule:
            ligne = "• " + (ligne[puce.end():] if puce else ligne).lstrip()
            puce_seule = False
            texte = (texte + " " if texte else "") + ligne
            continue
        if texte.endswith(("-", "‑")) and ligne[:1].islower():
            suite = re.match(r"[\w’']+", ligne)
            mot = suite.group(0).lower() if suite else ""
            texte = texte[:-1] + ("-" if mot in _GARDER_TIRET else "") + ligne
        else:
            texte = (texte + " " if texte else "") + ligne
    return texte.strip()


# --------------------------------------------------------------------------- PDF

@dataclass
class ReglagePDF:
    pages: list[int]                     # pages PDF utiles (numérotation physique, à partir de 1)
    taille_titre: float = 11.5           # une ligne en police ≥ ce corps est un titre
    taille_chapitre: float = 18.0        # titre de niveau 1 (chapitre, fiche, « À retenir »)
    taille_encadre: float | None = None  # texte en corps < ce seuil = encadré, lu après le texte courant
    taille_min: float = 7.5              # notes minuscules : retirées
    taille_corps: float = 11.0           # corps du texte courant ; en dessous, les blocs courts sont des légendes
    marge_gauche: float = 0.0            # blocs entièrement à gauche de cette abscisse (notes de marge) : retirés
    marge_droite: float = 1e9            # blocs commençant à droite de cette abscisse : retirés
    haut: float = 60.0                   # en-têtes courants (titre du guide, de la fiche) au-dessus
    bas: float = 555.0                   # pieds de page en dessous
    arret: str | None = None             # titre à partir duquel on arrête la lecture (crédits)
    exclure: list[str] = field(default_factory=list)   # motifs de blocs à retirer
    titres_encadres: list[str] = field(default_factory=list)   # titres qui ouvrent un encadré (« À retenir »)


def _corps(spans) -> float:
    """Corps dominant d'une ligne ou d'un bloc (pondéré par le nombre de caractères)."""
    poids: dict[float, int] = {}
    for s in spans:
        if s["text"].strip():
            poids[round(s["size"], 1)] = poids.get(round(s["size"], 1), 0) + len(s["text"].strip())
    return max(poids, key=poids.get) if poids else 0.0


def lire_pdf(chemin: Path, reglage: ReglagePDF) -> list[Paragraphe]:
    """Paragraphes d'un PDF INCa en planches de deux pages, dans l'ordre de lecture."""
    import pymupdf

    paragraphes: list[Paragraphe] = []
    chapitre, titre = "", ""
    titre_en_cours: list[str] = []
    niveau_en_cours = 0
    arrete = False

    def fermer_titre():
        nonlocal chapitre, titre, titre_en_cours, niveau_en_cours
        if titre_en_cours:
            groupes: list[list[str]] = []
            police_prec = None
            for txt, police in titre_en_cours:
                if police != police_prec:
                    groupes.append([])
                groupes[-1].append(txt)
                police_prec = police
            t = " > ".join(normaliser(" ".join(g)) for g in groupes)
            # Niveau 1 : chapitres numérotés, fiches, glossaire (« À retenir » reste un titre de section).
            if niveau_en_cours == 1 and re.match(r"(\d+\.|Fiche \d|Glossaire)", t):
                chapitre, titre = t, ""
            else:
                titre = t
        titre_en_cours, niveau_en_cours = [], 0

    with pymupdf.open(chemin) as pdf:
        for numero in reglage.pages:
            page = pdf[numero - 1]
            largeur = page.rect.width
            planche = largeur > 600
            blocs = []
            bruts = []
            for b in page.get_text("dict")["blocks"]:
                if b["type"] != 0:
                    continue
                if planche and b["bbox"][0] < largeur / 2 < b["bbox"][2]:
                    for cote in (0, 1):
                        lignes = [l for l in b["lines"]
                                  if ((l["bbox"][0] + l["bbox"][2]) / 2 > largeur / 2) == cote]
                        if lignes:
                            bruts.append({"lines": lignes, "bbox": (
                                min(l["bbox"][0] for l in lignes), min(l["bbox"][1] for l in lignes),
                                max(l["bbox"][2] for l in lignes), max(l["bbox"][3] for l in lignes))})
                else:
                    bruts.append(b)
            for b in bruts:
                x0, y0, x1, y1 = b["bbox"]
                spans = [s for l in b["lines"] for s in l["spans"]]
                texte = normaliser(" ".join(s["text"] for s in spans))
                if not texte or y1 < reglage.haut or y0 > reglage.bas:
                    continue
                if x1 < reglage.marge_gauche or x0 > reglage.marge_droite:
                    continue
                corps = _corps(spans)
                if corps < reglage.taille_min:
                    continue
                if any(re.search(m, texte) for m in reglage.exclure):
                    continue
                if "....." in texte:                    # pointillés : sommaire, formulaire à remplir
                    continue
                # Légendes de schémas, cellules de tableaux : courtes, sans ponctuation finale, en petit corps.
                if (corps < reglage.taille_corps and len(texte) < 40 and not _FIN_PHRASE.search(texte)
                        and re.match(r"[A-ZÀ-ÖØ-Þ\d*]", texte)):
                    continue
                moitie = int(planche and (x0 + x1) / 2 > largeur / 2)
                debut_moitie = moitie * largeur / 2
                largeur_moitie = largeur / 2 if planche else largeur
                colonne = int(x0 - debut_moitie >= 0.45 * largeur_moitie)
                if re.fullmatch(r"[\d\s]+", texte):     # numéros de schéma
                    continue
                encadre = int((reglage.taille_encadre is not None and corps < reglage.taille_encadre)
                              or texte in reglage.titres_encadres)
                blocs.append({"b": b, "moitie": moitie, "colonne": colonne, "encadre": encadre,
                              "y0": y0, "x0": x0, "corps": corps, "texte": texte})

            # Lettrine : bloc d'une seule majuscule en gros corps, recollée au bloc voisin à sa droite.
            lettrines = [d for d in blocs if len(d["texte"]) == 1 and d["texte"].isupper() and d["corps"] >= 18]
            for l in lettrines:
                voisins = [d for d in blocs if d is not l and d["moitie"] == l["moitie"]
                           and -5 <= d["x0"] - l["x0"] < 80 and abs(d["y0"] - l["y0"]) < 30]
                if voisins:
                    cible = min(voisins, key=lambda d: abs(d["y0"] - l["y0"]))
                    cible["lettrine"] = l["texte"]
                    blocs.remove(l)

            blocs.sort(key=lambda d: (d["moitie"], d["encadre"], d["colonne"], d["y0"], d["x0"]))
            contexte = None   # section du texte courant, rétablie après les encadrés
            for d in blocs:
                if d["encadre"] and contexte is None:
                    fermer_titre()
                    contexte = (chapitre, titre)
                elif not d["encadre"] and contexte is not None:
                    fermer_titre()
                    chapitre, titre = contexte
                    contexte = None
                page_imprimee = 2 * (numero - 1) + d["moitie"] if planche else numero
                corps_lignes: list[str] = []
                premiere = True
                for ligne in d["b"]["lines"]:
                    txt = "".join(s["text"] for s in ligne["spans"])
                    if not txt.strip():
                        continue
                    if premiere and d.get("lettrine"):
                        txt = d["lettrine"] + txt.lstrip()
                    premiere = False
                    corps = _corps(ligne["spans"])
                    niveau = 1 if corps >= reglage.taille_chapitre else 2 if corps >= reglage.taille_titre else 0
                    # Titre d'encadré : ligne en capitales (« PRESCRIPTION MÉDICALE… »).
                    lettres = re.sub(r"[^\w]|\d", "", txt)
                    if d["encadre"] and len(lettres) >= 10 and lettres.isupper():
                        niveau = 2
                    if niveau and re.fullmatch(r"[\d\s.]+", normaliser(txt)):
                        niveau = 0
                    if niveau:
                        if corps_lignes:
                            _ajouter(paragraphes, joindre_lignes(corps_lignes), chapitre, titre, page_imprimee)
                            corps_lignes = []
                        if niveau_en_cours and niveau != niveau_en_cours:
                            fermer_titre()
                        police = max(ligne["spans"], key=lambda sp: len(sp["text"].strip()))["font"]
                        titre_en_cours.append((txt, police))
                        niveau_en_cours = niveau
                        if reglage.arret and reglage.arret in normaliser(" ".join(t for t, _ in titre_en_cours)):
                            arrete = True
                            break
                    else:
                        fermer_titre()
                        corps_lignes.append(txt)
                if arrete:
                    break
                if corps_lignes:
                    _ajouter(paragraphes, joindre_lignes(corps_lignes), chapitre, titre, page_imprimee)
            if contexte is not None:
                fermer_titre()
                chapitre, titre = contexte
            if arrete:
                break
    return paragraphes


def _ajouter(paragraphes: list[Paragraphe], texte: str, chapitre: str, titre: str, page: int) -> None:
    """Ajoute un paragraphe, ou le recolle au précédent s'il en est la suite (coupure de colonne ou de page)."""
    if not texte or (len(texte) < 15 and not _FIN_PHRASE.search(texte)):   # fragment de tableau
        return
    section = " > ".join(t for t in (chapitre, titre) if t)
    # Suite d'une phrase coupée par une colonne ou une page : on la recolle au dernier paragraphe
    # inachevé de la même section, en sautant un encadré ou un renvoi intercalé.
    # Suite d'une liste à puces : on la recolle au paragraphe précédent de la même section.
    suite = texte[:1].islower() or texte[:1] in "(«,"
    if suite:
        precedent = next((p for p in reversed(paragraphes[-4:])
                          if p.section == section and not _FIN_PHRASE.search(p.texte)), None)
    else:
        precedent = paragraphes[-1] if paragraphes and paragraphes[-1].section == section else None
    if precedent and (suite or texte.startswith("•")):
        if precedent.texte.endswith(("-", "‑")) and texte[:1].islower():
            precedent.texte = precedent.texte[:-1] + texte
        else:
            precedent.texte += " " + texte
        if page not in precedent.pages:
            precedent.pages.append(page)
    else:
        paragraphes.append(Paragraphe(texte, section, [page]))


def recoller_coupures(paragraphes: list[Paragraphe]) -> int:
    """Retire les traits d'union résiduels d'une ancienne mise en page (« médi-ca-ments »).

    « a-b » devient « ab » seulement si « ab » apparaît ailleurs dans le document ;
    un vrai mot composé (« celui-ci », « anti-nauséeux ») est donc conservé.
    Renvoie le nombre de remplacements.
    """
    mots = {m.lower() for p in paragraphes for m in re.findall(r"[^\W\d_]+", p.texte)}
    motif = re.compile(r"\b([^\W\d_]+(?:[-‑][^\W\d_]+)+)\b")
    total = 0

    def remplacer(m):
        nonlocal total
        morceaux = re.split(r"[-‑]", m.group(1))
        colle = "".join(morceaux)
        if colle.lower() in mots and not any(x.lower() in _GARDER_TIRET | {"à", "dire"} for x in morceaux):
            total += 1
            return colle
        return m.group(1)

    for p in paragraphes:
        p.texte = motif.sub(remplacer, p.texte)
    return total


# -------------------------------------------------------------------------- HTML

def lire_html(chemin: Path) -> list[Paragraphe]:
    """Paragraphes d'une page cancer.fr : chapô et blocs « wysiwyg », sections h2 > h3 > h4."""
    from bs4 import BeautifulSoup

    soupe = BeautifulSoup(chemin.read_text(encoding="utf-8"), "html.parser")
    principal = soupe.find("main")
    # Vignettes de publications à télécharger, insérées dans le texte : pas du contenu de la page.
    for vignette in principal.select("div.embed-rich, div[class*=slider-pub]"):
        vignette.decompose()
    titres = {"h2": "", "h3": "", "h4": ""}
    paragraphes: list[Paragraphe] = []

    zones = principal.select("div.article-section-chapo, div.wysiwyg")
    for zone in zones:
        for el in zone.find_all(["h2", "h3", "h4", "p", "li"]):
            if el.name == "p" and el.find_parent("li"):
                continue
            texte = normaliser(el.get_text(" "))
            texte = re.sub(r"\s+([,.;:)])", r"\1", texte)
            if not texte:
                continue
            if el.name in titres:
                titres[el.name] = texte
                for plus_bas in ("h3", "h4")[("h2", "h3", "h4").index(el.name):]:
                    if plus_bas != el.name:
                        titres[plus_bas] = ""
                continue
            # Crédits photo, poids des fichiers à télécharger : pas du contenu.
            if ("©" in texte and len(texte) < 120) or re.fullmatch(r"PDF [\d,.]+ [kM]B", texte):
                continue
            # Liens seuls (« Fatigue », « Nutrition ») : navigation, pas du contenu.
            liens = " ".join(a.get_text(" ", strip=True) for a in el.find_all("a"))
            if liens and normaliser(liens) == texte and len(texte) < 60:
                continue
            section = " > ".join(t for t in titres.values() if t) or "Introduction"
            if el.name == "li":
                texte = "• " + texte
                precedent = paragraphes[-1] if paragraphes else None
                if precedent and precedent.section == section:
                    precedent.texte += " " + texte
                    continue
            paragraphes.append(Paragraphe(texte, section))
    return paragraphes


# --------------------------------------------------------------------- Passages

_PHRASE = re.compile(r"(?<=[.!?;:])\s+(?=[A-ZÀ-ÖØ-Þ«•])")


def _couper_long(texte: str, taille: int) -> list[str]:
    """Coupe un paragraphe trop long en morceaux équilibrés, aux frontières de phrases."""
    phrases = _PHRASE.split(texte)
    n = -(-len(texte) // taille)            # nombre de morceaux visé
    cible = len(texte) / n
    morceaux, courant = [], ""
    for phrase in phrases:
        if courant and len(courant) + 1 + len(phrase) > cible * 1.15 and len(morceaux) < n - 1:
            morceaux.append(courant)
            courant = phrase
        else:
            courant = f"{courant} {phrase}".strip()
    if courant:
        morceaux.append(courant)
    return morceaux


def decouper(document_id: str, paragraphes: list[Paragraphe], taille: int = TAILLE_MAX) -> list[dict]:
    """Regroupe les paragraphes voisins d'une même section jusqu'à `taille` caractères.

    Un passage ne franchit jamais une frontière de section ; un paragraphe plus long
    que `taille` est coupé aux frontières de phrases. La localisation garde la section,
    les numéros des paragraphes extraits (base 1) et, pour un PDF, les pages imprimées.
    """
    unites = []   # (texte, section, pages, index de paragraphe)
    for i, p in enumerate(paragraphes, start=1):
        for morceau in (_couper_long(p.texte, taille) if len(p.texte) > taille else [p.texte]):
            unites.append((morceau, p.section, p.pages, i))

    passages, groupe = [], []

    def fermer():
        if not groupe:
            return
        pages = sorted({pg for u in groupe for pg in u[2]})
        localisation = {"unite": "paragraphes", "section": groupe[0][1],
                        "paragraphes": sorted({u[3] for u in groupe})}
        if pages:
            localisation["pages_imprimees"] = f"{pages[0]}-{pages[-1]}" if len(pages) > 1 else str(pages[0])
        passages.append({
            "passage_id": f"{document_id}_P{len(passages) + 1:03d}",
            "document_id": document_id,
            "texte": " ".join(u[0] for u in groupe),
            "localisation": localisation,
        })
        groupe.clear()

    for unite in unites:
        longueur = sum(len(u[0]) + 1 for u in groupe) + len(unite[0])
        if groupe and (unite[1] != groupe[0][1] or longueur > taille):
            fermer()
        groupe.append(unite)
    fermer()
    return passages


# ---------------------------------------------------------------------- Preuves

def _cle(texte: str) -> str:
    """Forme de comparaison : minuscules, apostrophes unifiées, ponctuation et espaces réduits."""
    texte = normaliser(texte).lower().replace("’", "'")
    return re.sub(r"[^\w']+", " ", texte).strip()


def localiser_extrait(document_id: str, extrait: str, passages: list[dict]) -> str:
    """Identifiant du passage de `document_id` qui contient `extrait` (verbatim, à la ponctuation près).

    Les preuves sont annotées par un extrait du document source : leurs identifiants se
    recalculent ainsi après tout changement de découpage, sans toucher aux questions.
    Lève une erreur si l'extrait est absent ou coupé entre deux passages.
    """
    cle = _cle(extrait)
    trouves = [p["passage_id"] for p in passages
               if p["document_id"] == document_id and cle in _cle(p["texte"])]
    if len(trouves) != 1:
        raise ValueError(f"{document_id} : extrait trouvé dans {len(trouves)} passage(s) : {extrait!r}")
    return trouves[0]


def resoudre_preuves(question: dict, passages: list[dict]) -> dict:
    """Recalcule evidence_ids, evidence_by_element et equivalents_by_element depuis les extraits.

    `preuves_extraits` : pour chaque élément, la liste des {document_id, extrait} qui le justifient.
    `equivalents_extraits` : pour chaque élément, d'autres passages qui donnent la même information
    (indiqués comme équivalents, hors du calcul du rappel).
    """
    q = dict(question)
    par_element = [[localiser_extrait(e["document_id"], e["extrait"], passages) for e in element]
                   for element in q.get("preuves_extraits", [])]
    q["evidence_by_element"] = [list(dict.fromkeys(ids)) for ids in par_element]
    q["evidence_ids"] = list(dict.fromkeys(i for ids in par_element for i in ids))
    equivalents = [[localiser_extrait(e["document_id"], e["extrait"], passages) for e in element]
                   for element in q.get("equivalents_extraits", [[] for _ in par_element])]
    q["equivalents_by_element"] = [list(dict.fromkeys(ids)) for ids in equivalents]
    return q
