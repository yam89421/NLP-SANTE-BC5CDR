"""BLEU et ROUGE des réponses QA (section 5 du livret, annexe B.4 du guide).

Conventions B.4 :
  - questions avec réponse seulement, une référence par question ; une abstention (phrase imposée de Q2) sur
    ces questions compte comme une réponse vide ;
  - marqueurs de citation valides retirés (identifiants présents parmi les passages transmis) ; une citation
    inventée reste dans le texte ;
  - Unicode NFC, minuscules, même tokenisation pour BLEU et ROUGE : mots `\\w+` (accents, nombres et
    négations conservés ; « 38,5 » → « 38 5 », « l'installe » → « l installe ») ;
  - BLEU de corpus 0-100 (sacrebleu : n-grammes 1 à 4, pénalité de brièveté, lissage exponentiel,
    tokenisation externe `none`, ordre effectif désactivé) ; ROUGE-1/2/L = F1 moyenné par question, 0-1
    (rouge-score, avec notre tokeniseur : le sien supprime les lettres accentuées).
Les réponses brutes ne sont jamais modifiées : la préparation se fait à la volée.
"""
from __future__ import annotations

import re
import statistics
import unicodedata

from src.qa_llm import ABSTENTION, CITATION

MOT = re.compile(r"\w+")


def tokeniser(texte: str) -> list[str]:
    return MOT.findall(unicodedata.normalize("NFC", texte).lower())


def preparer(reponse: str, transmis: list[str]) -> str:
    """Texte évalué : sans citations valides ni phrase d'abstention, normalisé et retokenisé."""
    texte = CITATION.sub(lambda m: " " if m.group() in transmis else m.group(), reponse)
    texte = re.sub(re.escape(ABSTENTION), " ", texte, flags=re.IGNORECASE)
    return " ".join(tokeniser(texte))


class _Tokeniseur:   # interface attendue par rouge-score
    def tokenize(self, texte: str) -> list[str]:
        return tokeniser(texte)


def scores_reponses(lignes: list[dict], questions: dict[str, dict]) -> dict:
    """BLEU (corpus) et ROUGE moyens d'une configuration ; `questions` : question_id → question annotée."""
    import sacrebleu
    from rouge_score import rouge_scorer

    lignes = [l for l in lignes if questions[l["question_id"]]["answerable"]]
    hyp = [preparer(l["reponse"], l["passages_transmis"]) for l in lignes]
    ref = [" ".join(tokeniser(questions[l["question_id"]]["reference"])) for l in lignes]

    bleu = sacrebleu.metrics.BLEU(tokenize="none", smooth_method="exp", effective_order=False)
    rouge = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], tokenizer=_Tokeniseur())
    par_question = [rouge.score(r, h) for r, h in zip(ref, hyp)]
    return {
        "questions": len(lignes),
        "BLEU": round(bleu.corpus_score(hyp, [ref]).score, 2),
        **{f"ROUGE-{n[5:].upper()}": round(sum(s[n].fmeasure for s in par_question) / len(lignes), 3)
           for n in ("rouge1", "rouge2", "rougeL")},
        "réponses vides": sum(not h for h in hyp),
        "mots (médiane)": statistics.median(len(h.split()) for h in hyp),
        "signature BLEU": str(bleu.get_signature()),
    }
