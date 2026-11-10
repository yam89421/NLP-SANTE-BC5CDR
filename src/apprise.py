"""Méthode apprise : BioBERT ajusté en classification de tokens BIO (section 2.4 du livret).

Repris du TD NER du cours (`Extraction/BERT/TD/Tuto1_NER/Partie3_Entrainement_et_Eval`) :
même modèle (`dmis-lab/biobert-base-cased-v1.1`), mêmes hyperparamètres de départ et même perte pondérée
(`WeightedLossTrainer`). Modifications pour BC5CDR :
  - les étiquettes viennent de `data/bio_extraction.jsonl` (convention de la section 2.2) ;
  - les résumés sont découpés en fenêtres de phrases entières qui tiennent dans la longueur maximale,
    au lieu d'être tronqués ; chaque mot garde sa position dans le document ;
  - l'alignement sur les sous-mots utilise `tals.aligner_sous_mots` (premier sous-mot supervisé) ;
  - les mentions sont reconstruites au niveau du document, en intervalles de caractères, avec
    `tals.bio_vers_mentions` et la politique « reparer » annoncée avant le test : un `I-X` sans début
    compatible ouvre une nouvelle mention de type X.
"""
from __future__ import annotations

from collections import Counter

import torch
from torch.nn import CrossEntropyLoss
from transformers import Trainer

from tals import IGNORE, aligner_sous_mots, bio_vers_mentions

from .cdr import decouper_phrases

LABELS = ["O", "B-Chemical", "I-Chemical", "B-Disease", "I-Disease"]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
POLITIQUE_DECODAGE = "reparer"


def construire_fenetres(bio_docs, textes, tokenizer, max_length):
    """Découpe chaque document en fenêtres de phrases entières (au plus max_length sous-mots avec [CLS]/[SEP]).

    Une phrase trop longue à elle seule est coupée entre deux mots. Renvoie des dicts
    {document_id, mots (indices dans le document)}.
    """
    budget = max_length - 2
    fenetres = []
    for d in bio_docs:
        mots = d["tokens"]
        if not mots:
            continue
        ids = tokenizer(mots, is_split_into_words=True, add_special_tokens=False).word_ids()
        n_sous = Counter(i for i in ids if i is not None)
        phrases = decouper_phrases(textes[d["document_id"]])
        groupes, k = [], 0
        for a, b in phrases:
            groupe = []
            while k < len(mots) and d["offsets"][k][0] < b:
                groupe.append(k)
                k += 1
            if groupe:
                groupes.append(groupe)
        if k < len(mots):
            groupes.append(list(range(k, len(mots))))

        courant, longueur = [], 0
        for groupe in groupes:
            l_groupe = sum(max(n_sous[i], 1) for i in groupe)
            if l_groupe > budget:  # phrase trop longue : coupée entre deux mots
                if courant:
                    fenetres.append({"document_id": d["document_id"], "mots": courant})
                    courant, longueur = [], 0
                for i in groupe:
                    if courant and longueur + max(n_sous[i], 1) > budget:
                        fenetres.append({"document_id": d["document_id"], "mots": courant})
                        courant, longueur = [], 0
                    courant.append(i)
                    longueur += max(n_sous[i], 1)
                continue
            if courant and longueur + l_groupe > budget:
                fenetres.append({"document_id": d["document_id"], "mots": courant})
                courant, longueur = [], 0
            courant += groupe
            longueur += l_groupe
        if courant:
            fenetres.append({"document_id": d["document_id"], "mots": courant})
    return fenetres


def encoder(fenetres, bio_par_doc, tokenizer, max_length):
    """Exemples d'entraînement : input_ids, attention_mask, labels alignés (IGNORE hors premier sous-mot)."""
    exemples, tronques = [], 0
    for f in fenetres:
        d = bio_par_doc[f["document_id"]]
        mots = [d["tokens"][i] for i in f["mots"]]
        tags = [d["tags"][i] for i in f["mots"]]
        enc = tokenizer(mots, is_split_into_words=True, truncation=True, max_length=max_length)
        word_ids = enc.word_ids()
        if len({i for i in word_ids if i is not None}) < len(mots):
            tronques += 1
        cibles = aligner_sous_mots(word_ids, tags, strategie="premier")
        enc["labels"] = [c if c == IGNORE else LABEL2ID[c] for c in cibles]
        exemples.append(dict(enc))
    return exemples, tronques


@torch.no_grad()
def predire(model, tokenizer, fenetres, bio_par_doc, max_length, batch_size=16):
    """Prédit les étiquettes BIO de chaque mot puis reconstruit les mentions par document."""
    model.eval()
    device = next(model.parameters()).device
    tags_doc = {doc: ["O"] * len(d["tokens"]) for doc, d in bio_par_doc.items()}
    for k in range(0, len(fenetres), batch_size):
        lot = fenetres[k:k + batch_size]
        mots = [[bio_par_doc[f["document_id"]]["tokens"][i] for i in f["mots"]] for f in lot]
        enc = tokenizer(mots, is_split_into_words=True, truncation=True, max_length=max_length,
                        padding=True, return_tensors="pt")
        logits = model(**{c: v.to(device) for c, v in enc.items()}).logits
        pred = logits.argmax(-1).cpu().tolist()
        for b, f in enumerate(lot):
            vus = set()
            for pos, w in enumerate(enc.word_ids(batch_index=b)):
                if w is None or w in vus:
                    continue
                vus.add(w)
                tags_doc[f["document_id"]][f["mots"][w]] = model.config.id2label[pred[b][pos]]
    mentions = set()
    for doc in {f["document_id"] for f in fenetres}:
        mentions |= bio_vers_mentions(tags_doc[doc], bio_par_doc[doc]["offsets"], doc, politique=POLITIQUE_DECODAGE)
    return mentions


class WeightedLossTrainer(Trainer):
    """Perte d'entropie croisée pondérée (poids `entity_weight` sur les étiquettes B/I), reprise du TD."""

    def __init__(self, *args, entity_weight=10.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_weight = entity_weight
        self.model_accepts_loss_kwargs = False

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs["labels"]
        outputs = model(**{k: v for k, v in inputs.items() if k != "labels"})
        logits = outputs.logits
        poids = logits.new_tensor([1.0 if model.config.id2label[i] == "O" else self.entity_weight
                                   for i in range(model.config.num_labels)])
        loss = CrossEntropyLoss(weight=poids, ignore_index=IGNORE)(
            logits.reshape(-1, model.config.num_labels), labels.reshape(-1))
        return (loss, outputs) if return_outputs else loss


def entrainer(nom_modele, donnees_train, tokenizer, dossier, *, taux, epoques, graine, poids=1.0, warmup=0.1,
              batch_size=8, weight_decay=0.01):
    """Ajuste un BERT pré-entraîné sur TRAIN (recette d'APP-v2 / APP-v3, notebooks 2.4b et 2.4c).

    Sauvegarde le modèle à la fin de chaque époque dans `dossier` et renvoie (points de sauvegarde, durée en s).
    Prévu pour un GPU (Google Colab) : environ 3 à 4 min pour 10 époques sur une T4.
    """
    import math
    import time
    from pathlib import Path
    from transformers import (BertForTokenClassification, DataCollatorForTokenClassification, TrainingArguments,
                              set_seed)

    set_seed(graine)
    modele = BertForTokenClassification.from_pretrained(
        nom_modele, num_labels=len(LABELS), id2label=dict(enumerate(LABELS)), label2id=LABEL2ID)
    etapes = math.ceil(len(donnees_train) / batch_size) * epoques
    args = TrainingArguments(
        output_dir=str(dossier), save_strategy="epoch", save_only_model=True, eval_strategy="no",
        logging_strategy="epoch", learning_rate=taux, per_device_train_batch_size=batch_size,
        num_train_epochs=epoques, weight_decay=weight_decay, lr_scheduler_type="linear",
        warmup_steps=int(warmup * etapes), fp16=torch.cuda.is_available(), report_to="none",
        seed=graine, data_seed=graine, save_total_limit=None)
    trainer = WeightedLossTrainer(model=modele, args=args, entity_weight=poids, train_dataset=donnees_train,
                                  processing_class=tokenizer, data_collator=DataCollatorForTokenClassification(tokenizer))
    debut = time.perf_counter()
    trainer.train()
    points = sorted(Path(dossier).glob("checkpoint-*"), key=lambda c: int(c.name.split("-")[1]))
    return points, time.perf_counter() - debut
