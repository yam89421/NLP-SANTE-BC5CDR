"""Détection de la négation par règles, à la manière de NegEx (section 2.5 du livret).

Démarche du cours (Qualification et normalisation, diapositives 6 à 9) :
  1. partir de la mention cible et de ses positions ;
  2. repérer d'abord les pseudo-déclencheurs (« no doubt », « not only »,
     « cannot be excluded »), qui neutralisent les mots qu'ils contiennent ;
  3. repérer les déclencheurs placés avant la mention (portée vers la droite)
     ou après elle (portée vers la gauche) ;
  4. limiter la portée par les terminaisons (« but », « however », « ; »…) et
     par une longueur maximale ; garder la règle et le fragment déclencheur.

Langue : anglais, comme le corpus BC5CDR. Les listes suivent les déclencheurs
usuels de NegEx (Chapman et al., 2001).

Les versions sont figées dans REGLES : « v0 » a été écrite avant la génération
des phrases fictives ; toute version suivante n'est modifiée qu'à partir des
erreurs observées sur le développement.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

REGLES = {
    "v0": {
        "pre": [  # déclencheurs avant la mention : portée vers la droite
            "no", "not", "without", "denies", "denied", "deny", "neither", "nor", "never", "none",
            "negative for", "free of", "absence of", "no evidence of", "no sign of", "no signs of",
            "rather than", "fails to reveal", "failed to reveal",
        ],
        "post": [  # déclencheurs après la mention : portée vers la gauche
            "was ruled out", "were ruled out", "is ruled out", "has been ruled out", "have been ruled out",
            "was excluded", "were excluded", "is excluded", "has been excluded",
            "is absent", "was absent", "were absent", "are absent", "absent",
            "was not observed", "were not observed", "was not seen", "were not seen",
            "was not detected", "were not detected", "was not found", "were not found",
            "was negative", "were negative", "did not occur", "does not occur",
        ],
        "pseudo": [  # expressions trompeuses : leurs mots ne déclenchent rien
            "no doubt", "without doubt", "not only", "no increase", "no change", "no significant change",
            "no further", "not necessarily", "not certain", "gram negative",
            "cannot be excluded", "can not be excluded", "could not be excluded", "may not be excluded",
            "cannot be ruled out", "can not be ruled out", "could not be ruled out", "not be ruled out",
            "not ruled out", "not excluded", "not been ruled out", "not been excluded",
        ],
        "terminaisons": [
            "but", "however", "although", "though", "yet", "except", "which", "who", "whereas",
            "while", "because", "since", "aside", "apart", "still", ";", ":", ".", "!", "?",
        ],
        "portee_max": 8,  # en tokens
    },
}

_TOKEN = re.compile(r"\w+|[^\w\s]")


@dataclass
class Decision:
    label: str                 # "nie" ou "non_nie"
    regle: str | None = None   # "pre", "post" ou None
    declencheur: str | None = None
    fragment: str | None = None


def _tokens(phrase: str):
    return [(m.group(0).lower(), m.start(), m.end()) for m in _TOKEN.finditer(phrase)]


def _occurrences(toks, expressions):
    """Positions (i, j) en tokens des expressions trouvées, les plus longues d'abord."""
    mots = [t for t, _, _ in toks]
    trouvees = []
    for expr in sorted(expressions, key=lambda e: -len(_TOKEN.findall(e))):
        cible = [t.lower() for t in _TOKEN.findall(expr)]
        n = len(cible)
        for i in range(len(mots) - n + 1):
            if mots[i:i + n] == cible:
                trouvees.append((i, i + n, expr))
    return trouvees


def detecter(phrase: str, debut: int, fin: int, version: str = "v0") -> Decision:
    """Statut de la mention `phrase[debut:fin]` : niée ou non niée."""
    r = REGLES[version]
    toks = _tokens(phrase)
    # tokens de la mention
    men = [k for k, (_, a, b) in enumerate(toks) if a >= debut and b <= fin]
    if not men:
        raise ValueError(f"Mention [{debut}, {fin}[ hors des frontières de tokens.")
    m0, m1 = men[0], men[-1] + 1

    bloques = set()
    for i, j, _ in _occurrences(toks, r["pseudo"]):
        bloques.update(range(i, j))
    termin = {k for k, (t, _, _) in enumerate(toks) if t in r["terminaisons"]}

    def libre(i, j):
        return not any(k in bloques for k in range(i, j)) and not any(m0 <= k < m1 for k in range(i, j))

    # Déclencheurs avant : portée de la fin du déclencheur jusqu'à une terminaison
    for i, j, expr in _occurrences(toks, r["pre"]):
        if not libre(i, j) or j > m0:
            continue
        stop = next((k for k in range(j, len(toks)) if k in termin), len(toks))
        if m0 < min(stop, j + r["portee_max"]):
            return Decision("nie", "pre", expr, phrase[toks[i][1]:toks[m1 - 1][2]])
    # Déclencheurs après : portée vers la gauche jusqu'à une terminaison
    for i, j, expr in _occurrences(toks, r["post"]):
        if not libre(i, j) or i < m1:
            continue
        stop = next((k for k in range(i - 1, -1, -1) if k in termin), -1)
        if m1 - 1 > max(stop, i - 1 - r["portee_max"]):
            return Decision("nie", "post", expr, phrase[toks[m0][1]:toks[j - 1][2]])
    return Decision("non_nie")
