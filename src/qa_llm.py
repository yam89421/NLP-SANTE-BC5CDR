"""Génération Q1/Q2 avec un LLM OpenAI (section 4.2 du livret, annexe C du guide).

Choix reproductibles : version datée du modèle, température 0, graine fixe ; chaque requête est mise en
cache (empreinte SHA-256 de la requête complète), comme dans le TD RAG : une requête identique n'est jamais
renvoyée au fournisseur et sa sortie reste stable. Le cache ne contient ni la clé ni d'en-têtes.

La clé est lue dans la variable d'environnement OPENAI_API_KEY (fichier `.env` à la racine, ignoré par git).
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

CITATION = re.compile(r"DOC\d{3}_P\d{3}")
ABSTENTION = "Information insuffisante dans les documents fournis"


def formater_passages(passages: list[dict], titres: dict[str, str] | None = None) -> str:
    """Bloc de contexte, dans l'ordre du classement (même bloc pour Q1 et Q2).

    Contexte c1 (`titres=None`) : « [identifiant] texte ».
    Contexte c2 (`titres` = document_id → titre) : l'identifiant est suivi du titre du document et de la
    section d'origine, pour situer le passage (traitement, effet) ; le texte du passage est inchangé.
    """
    blocs = []
    for p in passages:
        if titres is None:
            blocs.append(f"[{p['passage_id']}] {p['texte']}")
        else:
            blocs.append(f"[{p['passage_id']}] Document : {titres[p['document_id']]} — Section : "
                         f"{p['localisation']['section']}\n{p['texte']}")
    return "\n\n".join(blocs)


def empreinte(objet) -> str:
    return hashlib.sha256(json.dumps(objet, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


class ClientLLM:
    """Appels OpenAI Chat Completions avec cache disque des succès."""

    def __init__(self, modele: str, temperature: float, seed: int, max_tokens: int, chemin_cache: Path):
        self.parametres = {"model": modele, "temperature": temperature, "seed": seed, "max_tokens": max_tokens}
        self.chemin_cache = Path(chemin_cache)
        self.cache = (json.loads(self.chemin_cache.read_text(encoding="utf-8"))
                      if self.chemin_cache.exists() else {})
        self._client = None

    def _openai(self):
        if self._client is None:
            from dotenv import load_dotenv
            from openai import OpenAI
            load_dotenv(self.chemin_cache.parents[2] / ".env")
            self._client = OpenAI()
        return self._client

    def generer(self, prompt: str) -> dict:
        """Réponse brute + métadonnées ; `origine` vaut « api » ou « cache » ; un échec est renvoyé, pas levé."""
        requete = {**self.parametres, "messages": [{"role": "user", "content": prompt}]}
        cle = empreinte(requete)
        if cle in self.cache:
            return {**self.cache[cle], "origine": "cache", "cache_id": cle}
        debut = time.perf_counter()
        try:
            r = self._openai().chat.completions.create(**requete)
        except Exception as erreur:   # échec explicite, conservé dans les prédictions
            return {"texte": "", "echec": f"{type(erreur).__name__}: {erreur}"[:300], "origine": "api",
                    "cache_id": cle, "duree_secondes": round(time.perf_counter() - debut, 3)}
        sortie = {
            "texte": r.choices[0].message.content or "",
            "echec": None,
            "modele_reponse": r.model,
            "system_fingerprint": r.system_fingerprint,
            "fin": r.choices[0].finish_reason,
            "tokens_prompt": r.usage.prompt_tokens,
            "tokens_reponse": r.usage.completion_tokens,
            "duree_secondes": round(time.perf_counter() - debut, 3),
        }
        self.cache[cle] = sortie
        self.chemin_cache.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1), encoding="utf-8")
        return {**sortie, "origine": "api", "cache_id": cle}


def diagnostiquer(reponse: str, transmis: list[str]) -> dict:
    """Contrôles automatiques d'une réponse (aide à la lecture, pas la grille manuelle du guide)."""
    cites = CITATION.findall(reponse)
    return {
        "abstention": ABSTENTION.lower() in reponse.lower(),
        "citations": len(cites),
        "citations_inventees": sorted(set(c for c in cites if c not in transmis)),
        "mots": len(reponse.split()),
    }
