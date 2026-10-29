# RAPPORT — historique des configurations et des résultats

Ce fichier centralise **chaque version** des méthodes (configuration, scores, fichiers produits) pour pouvoir
restituer à la fin des résultats comparatifs. Il est mis à jour à chaque modification d'une méthode.

**Conventions**
- Chaque version a un identifiant (`DIC-v1`, `APP-v1`…) qui ne change plus une fois écrit ; une modification crée une nouvelle version.
- Scores = micro-moyenne sur les mentions (correspondance exacte des bornes et du type), calculés par `src/extraction.py`.
- Les réglages se font sur **VALIDATION** ; **TEST** n'est évalué qu'une fois, sur les versions figées, dans `5_evaluation.ipynb`.
- Temps : extraction (+ post-traitement) sur une partition de 500 documents.

---

## 1. Tableau comparatif (extraction Chemical / Disease)

| Version | Méthode | Date | P val | R val | F1 val | F1 Chemical val | F1 Disease val | Temps val | F1 TEST | Statut |
|---|---|---|---|---|---|---|---|---|---|---|
| DIC-v1 | Dictionnaire TRAIN + regex manuelles | ≤ 2026-10-11 | 0,8835 | 0,6438 | 0,7449 | 0,7715 | 0,7127 | 1,4 s | — | remplacée |
| DIC-v2 | DIC-v1 + 5 règles de post-traitement | 2026-10-16 | 0,8889 | 0,7128 | **0,7912** | 0,8289 | 0,7434 | 1,2 s | à calculer | **figée (actuelle)** |
| APP-v1 | BioBERT fine-tuné (BIO) | ≤ 2026-10-11 | 0,8533 | 0,8558 | **0,8546** | 0,9128 | 0,7813 | 18,0 s (GPU T4) | à calculer | figée |

> `resultats/extraction/comparaison_validation.csv` recalculé le 2026-10-23 avec DIC-v2 et APP-v1 (prédictions sauvegardées, sans réentraîner BioBERT). Les sorties affichées dans le notebook 2.4 montrent encore DIC-v1.

**Erreurs sur VALIDATION (9 591 mentions de référence)**

| Version | Correctes | Frontière | Type | Manquées | Parasites |
|---|---|---|---|---|---|
| DIC-v2 | 6 836 | 576 | 8 | 2 171 | 270 |
| APP-v1 | 8 208 | 631 | 11 | 741 | 769 |

**Complémentarité DIC-v2 / APP-v1** : 6 215 mentions trouvées par les deux, 1 993 par BioBERT seul, 621 par le dictionnaire seul (*toxicity, oxygen, sodium, calcium, tumor, 5-HT, Na, K…*), 762 par aucune. Rappel de l'union : 0,921 (contre 0,856 pour BioBERT seul).

---

## 2. Données

Corpus **BC5CDR** (PubTator, `CDR_Data/CDR.Corpus.v010516`), catégories Chemical et Disease, partitions officielles.

| Partition | Documents | Chemical | Disease | Mentions | Formes distinctes | Composites | Phrases | Phrases sans mention |
|---|---|---|---|---|---|---|---|---|
| train | 500 | 5 203 | 4 182 | 9 385 | 2 391 | 107 | 4 580 | 773 |
| validation | 500 | 5 347 | 4 244 | 9 591 | 2 239 | 89 | 4 592 | 787 |
| test | 500 | 5 385 | 4 424 | 9 809 | 2 355 | 57 | 4 821 | 837 |

Conversion BIO (`resultats/extraction/bilan_bio.csv`) : 10 mentions perdues à l'aller-retour en VALIDATION et 5 en TEST (bornes hors frontière de token), 0 en TRAIN.

**Exports lisibles (2026-10-16)**
- `data/corpus_extraction.csv` : une ligne par mention (document, partition, titre/résumé, type, mention, contexte ±50 caractères avec la mention entre `[ ]`, positions, identifiants MeSH, composite).
- `data/bio_extraction.csv` : une ligne par token (document, partition, position, token, étiquette BIO, positions).

---

## 3. Méthode par dictionnaire et règles (notebook `2.3_dictionnaire_regles.ipynb`)

### DIC-v1 — dictionnaire seul

- Dictionnaire construit sur les mentions de TRAIN (une forme → son type majoritaire), plus longue correspondance, sans chevauchement.
- **Réglage sur VALIDATION** (16 combinaisons, `dictionnaire_reglage_validation.csv`) :
  - casse : `exacte` / `insensible` ;
  - seuil de **taux d'annotation** (part des occurrences d'une forme dans TRAIN qui sont annotées) : 0 / 0,3 / 0,5 / 0,7 ;
  - regex de suffixes écrites à la main (Chemical : *-mycin, -olol, -pril…* ; Disease : *-itis, -emia, -pathy…*) : oui / non.
- **Configuration retenue** : casse insensible, seuil 0,3, regex oui → 2 348 entrées.

| Casse | Seuil | Regex | F1 val |
|---|---|---|---|
| insensible | 0,3 | oui | **0,7449** |
| insensible | 0,5 | oui | 0,7397 |
| exacte | 0 | oui | 0,7335 |
| insensible | 0 | oui | 0,6969 |
| insensible | 0 | non | 0,6802 |

Erreurs sur VALIDATION : 6 175 correctes, 578 erreurs de frontière, 13 de type, 2 825 manquées (2 808 absentes du dictionnaire), 223 fausses détections.

### Analyse du taux d'annotation (2026-10-16)

- Le filtre retire 42 entrées, évite 1 388 fausses détections et perd 128 bonnes détections (+4,8 points de F1 en casse insensible, aucun gain en casse exacte).
- **Il corrige surtout l'insensibilité à la casse** : 5 formes courtes (`mg`, `be`, `all`, `can`, `h`, c.-à-d. Mg, Be, ALL…) expliquent 85 % du gain. Un seuil de 0,05 suffit pour 0,738.
- **Biais de calcul** : une forme contenue dans une mention plus longue (« infarction » dans « myocardial infarction ») est comptée comme non annotée. 190 formes concernées ; 27 entrées sont retirées à tort au seuil 0,3 (infarction, cancer, neuropathy, edema…).
- Pistes testées, **non intégrées** (à arbitrer) :

| Variante (avec regex manuelles) | F1 val |
|---|---|
| Taux actuel, seuil 0,3 (DIC-v1) | 0,7449 |
| Taux corrigé (sans les occurrences imbriquées), seuil 0,3 | 0,7485 |
| Casse exacte pour les tokens ≤ 3 caractères, insensible sinon, sans filtre | 0,7470 |
| Seuil appliqué seulement aux formes vues ≥ 5 fois | 0,7459 |

### DIC-v2 — dictionnaire + règles de post-traitement (2026-10-16)

Cinq règles appliquées après DIC-v1, dans cet ordre (code dans le notebook, `src/` inchangé) :

| # | Règle | Construction | F1 val (règle seule) |
|---|---|---|---|
| — | aucune (DIC-v1) | — | 0,7449 |
| 1 | **Suffixes appris** : 81 suffixes Chemical (*-dipine, -anyl, -olam…*), 27 Disease (*-lemia, -bosis, -zure…*) | TRAIN : ≥ 8 occurrences, ≥ 80 % annotées du même type | 0,7610 |
| 2 | **Modificateurs à gauche** : 49 mots (*muscle, tardive, myocardial, postoperative…*) qui étendent une maladie vers la gauche | TRAIN : ≥ 3 fois et ≥ 70 % inclus dans l'annotation | 0,7504 |
| 3 | **« X-induced » / « induced by X »** → X Chemical, sauf mots génériques et adjectifs | TRAIN (82 % de Chemical) ; liste d'exclusion ajustée sur VALIDATION | 0,7479 |
| 4 | **Sigles définis** « forme longue (SIGLE) » : le sigle prend le type de la forme longue dans le document ; sinon il est retiré (sauf s'il est dans le dictionnaire) | Schwartz & Hearst (2003) ; condition de retrait ajustée sur VALIDATION | 0,7653 |
| 5 | **Préfixe anti-** : retrait des prédictions commençant par « anti » | TRAIN : mots en *anti-* presque jamais annotés | 0,7456 |
| | **Toutes, dans l'ordre** | | **0,7912** |

- Erreurs VALIDATION après règles : 6 836 correctes (+661), 576 frontière, 8 type, 2 171 manquées (−654), 270 fausses détections (+47).
- Le score VALIDATION est **légèrement optimiste** (deux réglages ajustés en regardant VALIDATION) : seul TEST juge.
- Erreurs restantes : médicaments sans suffixe reconnaissable (*lead, ammonia*), sigles jamais définis, maladies de plusieurs mots inconnues.

**Idées testées et abandonnées**

| Idée | Résultat |
|---|---|
| Regex générique pour les sigles en capitales `[A-Z]{2,6}` | 36 % de précision sur TRAIN (II, CI, HIV, DNA…) |
| Deux lettres « Xx » hors début de phrase | 29 % de précision sur TRAIN (To, We, In, Hg de « mm Hg ») |
| Liste de symboles chimiques (Na, K, Ca, Li, Mg…) | aucun gain : déjà dans le dictionnaire |

**Fichiers (version figée DIC-v2)** — `resultats/extraction/` : `dictionnaire_config_gelee.json` (configuration, règles apprises, temps), `dictionnaire.tsv`, `regles_effet_validation.csv`, `scores_dictionnaire_validation.csv`, `predictions_dictionnaire_validation.jsonl`, `predictions_dictionnaire_test.jsonl` (7 995 prédictions).

---

## 4. Méthode apprise (notebook `2.4_methode_apprise.ipynb`)

### APP-v1 — BioBERT

- Modèle `dmis-lab/biobert-base-cased-v1.1`, étiquetage BIO, premier sous-mot supervisé, fenêtres = phrases entières, décodage « réparer », seed 42, GPU Tesla T4.
- Paramètres du TD : lr 2e-5, batch 8, weight decay 0,01, max_length 512.
- **Réglage sur VALIDATION** (`apprise_reglage_validation.csv`) :

| Poids des entités | Époques | P | R | F1 val |
|---|---|---|---|---|
| 1 | 2 | 0,8533 | 0,8558 | **0,8546** |
| 1 | 3 | 0,8263 | 0,8826 | 0,8535 |
| 10 | 2 | 0,7182 | 0,8956 | 0,7971 |
| 1 | 1 | 0,6849 | 0,8004 | 0,7382 |

- **Configuration retenue** : poids 1, 2 époques. Entraînement 84,6 s, prédiction 18 s par partition.
- Fichiers : `apprise_config_gelee.json`, `scores_apprise_validation.csv`, `predictions_apprise_validation.jsonl`, `predictions_apprise_test.jsonl`.

---

## 5. Négation (notebook `2.5_negation.ipynb`)

### NEG-v0 — règles de négation (`resultats/negation/regles_v0.json`)

- 20 phrases générées (Claude, 07/10/2026) en 10 familles (négation simple, coordination, « cannot be excluded », pseudo-négation, double négation…), réparties dev / test par famille.
- Score TEST **provisoire** (référence = labels de génération, double annotation en cours) : F1 « nié » 0,80, F1 « non nié » 0,80, moyenne 0,80 (matrice 4/1/1/4).
- À faire : compléter `annotation_AMARA.csv` / `annotation_TOMAS.csv`, calculer le kappa et remplacer le score provisoire.

---

## 6. Question-réponse (notebooks 3, 4.1, 4.2)

Cadrage : effets indésirables de la chimiothérapie / soins de support, documents INCa (`rapport/cadrage_qa.md`). Objectif : 20 questions DEV et 10 TEST. Notebooks 4.1 et 4.2 pas encore exécutés : aucun résultat.

**Corpus documentaire (2026-10-23) : 3 → 10 documents INCa** (`data/corpus.csv`, fichiers dans `data/sources_qa/`)

| ID | Document | Mise à jour | Mots (≈) |
|---|---|---|---|
| DOC001 | Comprendre la chimiothérapie (guide PDF) | 2011-09 | — |
| DOC002 | Cancers et soins de support (fiche PDF) | 2024-11 | — |
| DOC003 | Les effets indésirables généraux de la chimiothérapie | 2019-04-28 | — |
| DOC004 | Pourquoi les traitements font tomber les cheveux et les poils ? | 2024-07-01 | 1 000 |
| DOC005 | Douleurs et traitements | 2015-05-26 | 1 500 |
| DOC006 | La prise en charge de la fatigue | 2024-03-08 | 1 250 |
| DOC007 | Nausées, vomissements, diarrhées | 2024-12-01 | 800 |
| DOC008 | Nutrition | 2024-12-01 | 2 900 |
| DOC009 | Problèmes de bouche | 2015-04-08 | 500 |
| DOC010 | Problèmes de peau | 2024-07-01 | 700 |

- DOC004 à DOC010 : pages de la rubrique « Effets indésirables » de cancer.fr. Le site étant **en maintenance le 23/10/2026** (et l'URL de DOC003 renvoyant 404), elles ont été récupérées depuis la **Wayback Machine** (copie brute `id_`, capture datée indiquée dans `acces`).
- Écartées : les pages d'accueil de rubrique (alopécie, douleurs, fatigue : moins de 200 mots, sommaires), « Conseils chute des cheveux » (150 mots), « La fatigue liée aux traitements par médicaments » (gardée en réserve : recoupe DOC006).
- Recouvrements thématiques avec DOC001/DOC003 (cheveux, nausées, poids) : ce ne sont pas des doublons, mais une question peut avoir des preuves dans plusieurs documents ; à prendre en compte dans l'annotation.

### PAS-v1 — extraction du texte et découpage en passages (2026-10-23, notebook `3_corpus_qa.ipynb`, code `src/qa_corpus.py`)

- **PDF** (PyMuPDF, méthode du TD RAG) : chaque page est une planche de deux pages imprimées en 1-2 colonnes avec encadrés → blocs triés par page imprimée, flux (texte courant puis encadrés), colonne, position ; lettrines recollées ; en-têtes, pieds de page, notes de marge, légendes de schémas, champs et pointillés de formulaires, renvois vers d'autres brochures retirés ; phrases coupées par une colonne/page recollées ; césures et traits d'union résiduels (« médi-ca-ments ») recollés seulement si le mot entier est attesté dans le document (22 cas). Pages : DOC001 p. 3, 5-39, 41-58 ; DOC002 p. 2-9 (jusqu'aux « Sources de référence »).
- **HTML** (BeautifulSoup) : chapô + blocs `wysiwyg` ; navigation, « À lire aussi », vignettes de publications, crédits photo, liens seuls retirés.
- **Découpage** : paragraphes d'une même section regroupés jusqu'à **800 caractères** (TD : 650), jamais à cheval sur deux sections ; paragraphe trop long coupé aux frontières de phrases. Titres gardés dans `localisation.section` (pas dans le texte) ; localisation = section, n° de paragraphes, pages imprimées (PDF).

| Document | Passages | Car. min / méd. / max | Mots |
|---|---|---|---|
| DOC001 | 260 | 74 / 548 / 795 | 20 722 |
| DOC002 | 42 | 158 / 573 / 781 | 3 493 |
| DOC003–DOC010 | 111 | 94 / — / 800 | 8 467 |
| **Total** | **413** | | **32 682** |

- **Contrôle de 10 passages** (le plus court, le plus long, 8 tirés graine 42) : ordre, nombres/unités et négations conformes (`resultats/qa/controle_passages.csv`). Limites relevées : regroupement glouton → petits passages de fin de section (74 car.) et listes coupées entre deux passages (contexte partiel).
- **Contrôle automatique** : 2 049 phrases recherchées dans le texte brut de la source ; 37 non retrouvées telles quelles (1,8 %, DOC001/DOC002), vérifiées par sondage : artefacts du texte brut (phrase coupée par un saut de colonne, mots collés), pas d'erreur d'ordre.
- Limites restantes : tableaux de la fiche 4 de DOC001 (traitements ciblés) aplatis ; quelques légendes longues conservées (« Cathéter simple ou cathéter veineux central »).

**Preuves des questions** : annotées par **extrait verbatim** (`preuves_extraits`) ; identifiants recalculés à chaque découpage (`resoudre_preuves`). Passages donnant la même information dans un autre document : `equivalents_by_element`, hors du calcul du Rappel@5. Correspondance avec les preuves provisoires du jalon E : DOC001_P01 → DOC001_P084 + P085 (Q002 devient une question à deux passages), DOC001_P02 → DOC001_P105, DOC002_P01 → DOC002_P003, DOC002_P02 → DOC002_P009 + P010 (Q004 à deux passages), DOC003_P01 → DOC003_P008 (équivalent DOC001_P142). Justification de Q005 (sans réponse) mise à jour pour les 10 documents.

**Sources divergentes (décision du 2026-10-23)** : DOC001 (2011) indique que les cheveux « recommencent à pousser environ 6 à 8 semaines » après la fin du traitement, DOC004 (2024) qu'ils « repoussent en général dans les 3 à 6 mois ». Q001 est réannotée sur DEV (avant tout réglage) : la référence donne les deux délais avec leur source, un élément attendu par source (preuves DOC001_P105 et DOC004_P002), champs `sources_divergentes: true` et `note_annotation`.
- **Règle de rédaction** (règle 2.3 de `rapport/guide_redaction_qa.md`) : quand deux documents donnent des informations différentes, la référence les cite toutes avec leur source et leur date, sans trancher ; chaque version est un élément attendu.
- **Références reformulées (2026-10-23)** : celles de Q001, Q002 et Q004 recopiaient les passages (segments de 11 à 16 mots), ce qui avantagerait dans BLEU/ROUGE les sorties qui recopient (Q0). Elles sont réécrites de façon concise, chiffres exacts : segment recopié le plus long de 3 à 9 mots, Q001 passe de 80 à 55 mots. Règles 1.1 (questions) et 2.1 (références) du guide ; le notebook 3 signale toute question ou référence qui recopie plus de 10 mots d'une preuve.
- **Conséquences pour la suite** : le prompt Q2 doit demander de signaler les informations divergentes entre passages ; la grille manuelle jugera si la réponse mentionne les deux délais (complétude) et ne présente pas un seul délai comme certain (exactitude). Prévoir au moins une question TEST de ce type.

### Questions DEV (2026-10-23) — 20/20

| ID | Sujet (document) | Type |
|---|---|---|
| Q001 | Chute et repousse des cheveux (DOC001, DOC004) | 2 documents, sources divergentes |
| Q002 | Durée des nausées et vomissements (DOC001 ; équivalent DOC007) | 2 passages |
| Q003 | Variation de poids et diététique remboursée (DOC003, DOC002) | 2 documents |
| Q004 | Bilans de soins de support après cancer (DOC002) | 2 passages |
| Q005 | Dépistage du déficit en DPD | sans réponse |
| Q006 | Aliments à éviter en cas d'aphtes (DOC009 ; équivalent DOC001) | 1 passage, vocabulaire patient |
| Q007 / Q008 | Seuils de dénutrition (DOC008) | 1 passage ; Q008 = reformulation à prémisse inexacte (kilos) |
| Q009 | Précautions quand les plaquettes baissent (DOC001) | 1 passage |
| Q010 | Diarrhée : alimentation, boissons, alerte (DOC007 ; équivalent DOC001) | 2 passages |
| Q011 | Chimiothérapies toxiques pour les nerfs (DOC005) | 1 passage |
| Q012 | Nutrition par sonde à domicile (DOC008) | 2 passages |
| Q013 | Pamplemousse, millepertuis et anticancéreux (DOC008) | 1 passage |
| Q014 | Délai d'apparition des douleurs de chimiothérapie (DOC005) | 1 passage |
| Q015 | Mesurer sa fatigue (DOC006) | 2 passages |
| Q016 | Signes d'infection quand les globules blancs sont bas (DOC001) | 1 passage (+ équivalent « À retenir ») |
| Q017 | Remboursement de la perruque (DOC001, montant 2011) | 1 passage, information datée |
| Q018 | Remboursement du casque réfrigérant | sans réponse (sujet proche très présent) |
| Q019 | Vernis à ongles | sans réponse |
| Q020 | Conduire juste après une séance | sans réponse (DOC010 parle de conduite pour la peau des mains) |

- Bilan : 16 avec réponse dont 7 à deux passages ou plus (≥ 4 demandées), 4 sans réponse ; les 10 documents sont utilisés. Aucune question ni référence ne recopie plus de 10 mots d'une preuve (max. 9).
- Q006-Q020 rédigées avec l'aide de Claude, **à relire par le binôme** (`statut_relecture: a_relire`, guide § 5).
- Q002 : ajout de l'équivalent DOC007_P004 (nausées ≤ 3 jours, vomissements ≤ 48 h).
- **Sujets réservés à TEST** (non utilisés en DEV, pour ne pas partager de famille) : casque réfrigérant, pose et durée (DOC001 fiche 2 + DOC004, 2 documents) ; remboursement du psychologue (DOC006 « seules les consultations des psychiatres sont remboursées » vs DOC002 « Mon soutien psy », **sources divergentes**) ; syndrome main-pied (DOC005 + DOC010) ; vaccinations pendant la chimiothérapie (DOC001_P039) ; nausées anticipatoires (DOC007, DOC001) ; compléments nutritionnels oraux (DOC008) ; activité physique (DOC002) ; colorations après la repousse (DOC001, DOC004).

### Questions TEST (2026-10-23) — 10/10, mises de côté jusqu'au gel du 06/11

| ID | Sujet (document) | Type |
|---|---|---|
| Q021 | Casque réfrigérant : pose, changement, retrait (DOC001, DOC004) | 2 documents complémentaires |
| Q022 | Remboursement du psychologue (DOC006 vs DOC002) | 2 documents, **sources divergentes** |
| Q023 | Syndrome main-pied sous capécitabine (DOC005, DOC010) | 2 documents |
| Q024 | Vaccin contre la grippe pendant la chimiothérapie (DOC001) | 1 passage, question plus précise que le corpus (vaccinations en général) |
| Q025 | Nausées avant la perfusion (DOC007 ; équivalent DOC001) | 1 passage, vocabulaire patient |
| Q026 | Compléments nutritionnels oraux (DOC008) | 2 passages |
| Q027 | Activité d'endurance recommandée (DOC002) | 2 passages |
| Q028 | Ergothérapeute : rôle et remboursement (DOC006) | 2 passages |
| Q029 | Gingembre contre les nausées | sans réponse |
| Q030 | Remboursement de l'acupuncture | sans réponse (pratiques non conventionnelles citées, pas leur prise en charge) |

- 8 avec réponse dont 6 à deux passages ou plus (≥ 2 demandées), 2 sans réponse ; aucune famille partagée avec DEV (contrôle du notebook 3). Recopie maximale : 9 mots (référence), 3 mots (question).
- Mêmes cas difficiles qu'en DEV, sur d'autres sujets : sources divergentes (Q022 ↔ Q001), question plus précise que le corpus (Q024 ↔ Q008), absences proches de sujets traités (Q029-Q030 ↔ Q018-Q020).
- **Rédigées avec l'aide de Claude, à relire par le binôme** (`statut_relecture: a_relire`). Les questions TEST ne servent ni aux réglages ni d'exemples dans les prompts.

### REC-v1 — recherche lexicale BM25 et Q0 sur DEV (2026-10-28, notebook `4.1_recherche_lexicale_q0.ipynb`, code `src/qa_recherche.py`)

- BM25 **repris du TD RAG** sans modification : tokenisation `\w+` minuscules (accents, nombres, négations conservés, aucun mot vide retiré), IDF positive, k1 = 1,5, b = 0,75, top-5. Recherche des 20 questions : 0,04 s (CPU).
- Seul réglage comparé sur DEV : le texte indexé (le titre de section n'est ajouté que pour l'indexation ; Q0 et les LLM reçoivent le texte seul).

| Texte indexé (DEV, 16 questions avec réponse) | Hit@5 | Rappel@5 | Hit@5 avec équiv. | Rappel@5 avec équiv. | Couverture éléments@5 |
|---|---|---|---|---|---|
| texte | 0,688 | 0,625 | 0,750 | 0,688 | 0,677 |
| **section + texte (retenu)** | **0,750** | **0,688** | 0,812 | 0,719 | 0,719 |

- Hit@5 / Rappel@5 : formules B.3 du guide sur `evidence_ids` ; « avec équivalents » : une preuve compte si un passage équivalent du même élément est retrouvé ; couverture : part des éléments attendus disponibles dans le top-5.
- **Manques (DEV)** :
  - Q010 (diarrhée) : top-5 = passages DOC001 équivalents (P092, rang 1) ; preuves DOC007 au rang 23 → retrouvée avec équivalents.
  - Q012 (« nourri par sonde à la maison ») : le vocabulaire de la question ne recoupe pas « nutrition entérale à domicile » ; le casque réfrigérant (« posé », « perfusion ») passe devant ; preuve au rang 17.
  - Q014 (délai des douleurs de chimiothérapie) : les passages sur les douleurs de radiothérapie (DOC005_P017, « après la fin du traitement ») passent devant ; preuve au rang 10.
  - Q016 (signes d'infection) : la preuve (liste de symptômes, un seul « infection ») est au rang 17, derrière des passages répétant « globules blancs ».
  - Q001, Q015 : une preuve sur deux retrouvée (DOC004_P002 et DOC006_P003 hors top-5).
- **Q0** (premier passage tel quel) : 20 réponses DEV dans `resultats/qa/predictions_q0_dev.jsonl`. Exemple d'erreur typique : Q002 (nausées après chimiothérapie) reçoit le passage sur les nausées de **radiothérapie** (DOC007_P005).
- Pistes à tester sur DEV avant le gel (06/11) : paramètres k1/b, mots vides français, k > 5 pour les questions à deux passages ; toute modification crée REC-v2.

### REC-v2 — racinisation (2026-10-29, notebook `4.1_recherche_lexicale_q0.ipynb`)

- Prétraitement appliqué identiquement aux passages et aux questions, pour le calcul des scores seulement : **questions, références et textes transmis aux LLM inchangés**. Mots vides : liste française de NLTK **sans les négations** (ne, pas, sans, aucun, jamais, ni, rien, non, plus) ; racinisation : Snowball français ; nombres conservés.

| DEV, 16 questions avec réponse | Hit@5 | Rappel@5 | Rappel@5 avec équiv. | Couverture éléments@5 | Rappel@10 |
|---|---|---|---|---|---|
| texte, aucun | 0,688 | 0,625 | 0,688 | 0,677 | 0,781 |
| texte, mots vides | 0,750 | 0,688 | 0,750 | 0,740 | 0,781 |
| **texte, racines (REC-v2)** | **0,875** | **0,781** | **0,812** | **0,823** | 0,812 |
| texte, mots vides + racines | 0,875 | 0,781 | 0,812 | 0,823 | 0,812 |
| section + texte, aucun (REC-v1) | 0,750 | 0,688 | 0,719 | 0,719 | 0,781 |
| section + texte, mots vides | 0,750 | 0,719 | 0,750 | 0,740 | 0,781 |
| section + texte, racines | 0,812 | 0,781 | 0,781 | 0,792 | 0,844 |
| section + texte, mots vides + racines | 0,812 | 0,750 | 0,750 | 0,760 | 0,812 |

- **Choix** : texte + racinisation (meilleur Rappel@5, couverture et Hit@5 ; à égalité avec « mots vides + racines », la plus simple). Les mots vides n'apportent rien une fois la racinisation en place ; le titre de section n'aide plus.
- **Grille k1 × b** (k1 ∈ {0,6 … 2,4}, b ∈ {0,3 … 1,0}) : aucun réglage ne dépasse Rappel@5 = 0,781 ; les valeurs du TD (1,5 ; 0,75) sont sur ce plateau et sont conservées (pas de sur-ajustement sur 16 questions).
- **Effets par question** (rang de la 1re preuve, REC-v1 → REC-v2) : Q010 23 → 2 (« diarrhée/diarrhées »), Q014 10 → 5, Q017 4 → 2 ; Q001 et Q015 récupèrent leur 2e preuve ou la gardent. **Restent hors top-5** : Q012 (« nourri par sonde » vs « nutrition entérale », aucun mot commun, rang 22) et Q016 (signes d'infection, rang 140 : la liste de symptômes partage peu de mots avec la question) → relèvent d'une recherche sémantique (approfondissement C.1, dense/hybride).
- Q0 DEV régénéré avec REC-v2 (`resultats/qa/predictions_q0_dev.jsonl`). **Les réponses LLM-v1/v2 ont été produites avec les contextes REC-v1** : le notebook 4.2 doit être relancé (nouveaux appels) pour évaluer Q1/Q2 sur les contextes REC-v2.

### LLM-v1 — Q1 et Q2 sur DEV avec les prompts du guide (2026-10-28, notebook `4.2_llm_q1_q2.ipynb`, code `src/qa_llm.py`)

- Modèle `gpt-4.1-mini-2025-04-14` (API OpenAI), température 0, graine 42, 300 tokens max ; cache des requêtes. Contexte : les 5 passages BM25 de Q0 (REC-v1), même ordre, texte complet (≤ 3 500 caractères). Prompts Q1 v1 et Q2 v1 = annexe C du guide.
- Coût DEV : Q1 14 197 + 1 693 tokens, Q2 15 877 + 1 276 tokens ; 0 échec.

| DEV (20 questions) | Abstentions correctes (/4) | Abstentions sur questions avec réponse (/16) | Réponses sans citation | Citations inventées | Mots (médiane) |
|---|---|---|---|---|---|
| Q1 v1 | 0 | 0 | 1 | 0 | 54 |
| Q2 v1 | **4** | 2 (Q014, Q016) | 0 | 0 | 49 |

- **Lecture des réponses DEV** (contrôles automatiques + lecture, pas la grille officielle) :
  - Q1 ne s'abstient jamais : sur Q018-Q020 il complète avec des inférences non soutenues (« il serait prudent d'éviter de conduire », « la prudence est de mise » pour le vernis). Q2 s'abstient correctement sur les 4.
  - Q014 et Q016 : les preuves ne sont pas dans le top-5 (échec de recherche, REC-v1). Q2 s'abstient (prudent mais compté 0) ; Q1 répond à tort avec des passages sur d'autres douleurs (postopératoires, radiothérapie) → affirmations non soutenues.
  - Q010 (diarrhée) : Q1 et Q2 reprennent les conseils alimentaires **de la radiothérapie** (DOC005_P016 : « 1,5 litre », purées) comme conseils contre la diarrhée sous chimiothérapie : le titre de section, qui situait le passage, n'est pas transmis au LLM.
  - Q001 : aucune des deux ne signale la divergence sur la repousse (DOC004_P002 n'est pas retrouvé) ; Q008 : aucune ne corrige la prémisse « en kilos ».
  - Q012 : échec de recherche ; Q2 répond partiellement et signale que la durée « n'est pas précisée » (comportement attendu), Q1 répond à côté.

### LLM-v2 — contexte avec titres (c2) et prompt Q2 v2 (2026-10-28, DEV)

- **Contexte c2** (Q1 et Q2) : identifiant + titre du document + section d'origine avant chaque passage, texte inchangé. **Q2 v2** : prompt du guide + 4 consignes issues des erreurs v1 : passage portant sur la même situation que la question ; réponse partielle en signalant ce qui manque ; sources divergentes données avec leur document ; hypothèse de la question contredite par les passages signalée. Q1 garde le prompt du guide. Q2 v1 relancé en c2 pour séparer l'effet du contexte et celui des consignes.
- Coût des 60 nouveaux appels : 57 242 + 4 712 tokens ; 0 échec ; les 40 réponses v1 sont reproduites à l'identique par le cache.

| DEV (20 questions) | Abstentions correctes (/4) | Abstentions sur questions avec réponse (/16) | Réponses sans citation | Citations inventées | Mots (médiane) |
|---|---|---|---|---|---|
| Q1 v1 c1 | 0 | 0 | 1 | 0 | 54 |
| Q2 v1 c1 | 4 | 2 | 0 | 0 | 49 |
| Q1 v1 c2 | 0 | 0 | 1 | 0 | 54 |
| Q2 v1 c2 | 4 | 1 | 0 | 0 | 46 |
| Q2 v2 c2 | 4 | 2 | 0 | 0 | 48 |

- **Effet du contexte c2** (lecture) : Q1 devient plus prudent sur Q014 (« les passages ne mentionnent pas explicitement… ») au lieu d'attribuer à la chimiothérapie des douleurs postopératoires ; Q2 v1 complète Q009 (signes à surveiller). Mais Q1 reste sans abstention et continue d'inférer (Q019 « il vaut mieux éviter le vernis », Q020 « il serait prudent de ne pas conduire »).
- **Effet des consignes Q2 v2 : pas de gain net sur les erreurs visées.**
  - Q010 : les conseils de la radiothérapie (DOC005_P016, boissons gazeuses) sont encore cités, sans le « 1,5 litre » ; v2 ajoute que les documents ne précisent pas les aliments et cite à tort une recommandation générale (DOC003_P009, section poids) → la consigne « même situation » est partiellement suivie.
  - Q008 : la prémisse « en kilos » n'est corrigée par aucune configuration, malgré la consigne explicite de v2.
  - Q001 : divergence non signalée, mais la consigne ne peut pas agir : DOC004_P002 n'est pas dans le contexte (échec de recherche).
  - Q012, Q016, Q019 : v2 dit explicitement ce qui manque (« les documents ne précisent pas la durée du passage ni qui s'occupe du matériel ») ; sur Q016/Q019, la phrase d'abstention est précédée d'une explication.
- **Conclusion provisoire** : l'essentiel des erreurs restantes vient de la recherche (Q001, Q010, Q012, Q014, Q016 : preuve absente du top-5), pas de la génération. Contexte c2 à conserver ; choix entre Q2 v1 et Q2 v2 à faire au gel (06/11), après d'éventuels réglages de la recherche sur DEV (REC-v2), qui changeront les contextes transmis.

### LLM sur les contextes REC-v2 (2026-10-29, DEV)

- Mêmes 5 configurations (Q1 v1 c1, Q2 v1 c1, Q1 v1 c2, Q2 v1 c2, Q2 v2 c2), passages REC-v2 ; 100 appels, 0 échec, 105 479 + 7 877 tokens. Sorties REC-v1 archivées (`predictions_llm_dev_REC-v1.jsonl`, `llm_dev_controles_REC-v1.csv`).

| DEV (20 questions), contextes REC-v2 | Abstentions correctes (/4) | Phrase d'abstention sur questions avec réponse (/16) | Réponses sans citation | Citations inventées | Mots (médiane) |
|---|---|---|---|---|---|
| Q1 v1 c1 | 0 | 0 | 1 | 0 | 59,5 |
| Q2 v1 c1 | 4 | 2 | 0 | 0 | 43,5 |
| Q1 v1 c2 | 0 | 0 | 1 | 0 | 50,5 |
| Q2 v1 c2 | 4 | 2 | 0 | 0 | 44,5 |
| Q2 v2 c2 | 4 | 0 | 0 | 0 | 54,5 |

- Le contrôle automatique compte la phrase d'abstention même quand elle ne porte que sur une partie de la réponse : pour Q2 v1 c2, Q014 est une **réponse correcte** suivie d'une abstention partielle (« Information insuffisante… pour savoir si des douleurs persistent ») ; seule Q016 est une vraie abstention (preuve absente du top-5).
- **Ce que la meilleure recherche change** (lecture des réponses) :
  - Q014 : les trois configurations répondent juste (2-3 semaines, disparition à la fin), alors que Q1 répondait faux et Q2 s'abstenait avec REC-v1.
  - Q010 : les trois donnent les 2 litres et les signes d'alerte (DOC007_P009) ; les conseils de radiothérapie disparaissent. Les aliments restent absents (DOC007_P008 hors top-5). Q1 ajoute des conseils **contre les nausées** (DOC001_P088) et Q2 v2 une « alimentation équilibrée » tirée de la section poids (DOC003_P009) : affirmations sur une autre situation.
  - Q001 : DOC004_P002 est maintenant transmis. **Q2 v1 c2 donne les deux délais avec leur source** (6-8 semaines DOC001, 3-6 mois DOC004) ; Q2 v2 les fusionne (« ou plus généralement ») et Q1 n'en garde qu'un ; aucune ne dit explicitement que les sources divergent.
- **Erreurs restantes** :
  - Q012 : la recherche remonte la nutrition **parentérale** à domicile (DOC008_P031) ; les trois configurations s'en servent pour une question sur la sonde (entérale) → réponse sur une autre situation.
  - Q016 : preuve hors top-5 ; Q2 s'abstient, Q1 répond de façon générale.
  - Q008 : la prémisse « en kilos » n'est corrigée par aucune configuration.
  - Q1 invente davantage sur les questions sans réponse : Q020 « **il est déconseillé de prendre le volant** […] rendant la conduite dangereuse » ; Q019 « l'usage du vernis pourrait être déconseillé ».
- **Bilan pour le choix des prompts** : avec de meilleurs passages, **Q2 v1 (prompt du guide) en contexte c2 donne les réponses les plus sûres** (abstentions correctes, deux délais pour Q001, pas d'ajout hors situation) ; les consignes v2 n'apportent pas de gain et ajoutent des généralités. Proposition pour le gel : Q1 v1 + Q2 v1, contexte c2, REC-v2.

### APP-REC — approfondissement : recherche dense et hybride (2026-10-29, notebook `4.3_recherche_hybride.ipynb`, DEV)

- **Question** : une recherche sémantique retrouve-t-elle les preuves de Q012 et Q016 (mots différents de la question), sans dégrader les autres, et à quel coût ? Approfondissement C.1 du guide : le socle Q0/Q1/Q2 reste défini avec BM25.
- **Méthodes** (code du TD RAG) : dense `intfloat/multilingual-e5-small` (préfixes `passage:`/`query:`, cosinus), sur le texte seul ou sur titre de section + texte ; hybride RRF des 20 premiers BM25 REC-v2 et denses (1/(60 + rang)).

| DEV, 16 questions avec réponse | Hit@5 | Rappel@5 | Hit@5 équiv. | Rappel@5 équiv. | Couverture éléments@5 | Recherche 20 q. |
|---|---|---|---|---|---|---|
| BM25 REC-v2 | 0,875 | 0,781 | 0,875 | 0,812 | 0,823 | 0,05 s |
| dense (texte) | 0,812 | 0,719 | 0,812 | 0,750 | 0,760 | 0,55 s |
| **dense (section + texte)** | **0,938** | **0,875** | **1,000** | **0,969** | **0,979** | 0,55 s |
| hybride RRF (BM25 + dense texte) | 0,812 | 0,656 | 0,812 | 0,688 | 0,698 | 0,64 s |
| hybride RRF (BM25 + dense section + texte) | 0,875 | 0,781 | 0,875 | 0,781 | 0,802 | 0,60 s |

- **Coût** : encodage des 413 passages ≈ 35 s sur CPU (une fois, modèle de 118 M paramètres), aucun passage tronqué ; recherche ≈ 30 ms par question, contre 2-3 ms pour BM25. Aucun coût d'API.
- **Dense (section + texte)** retrouve les deux preuves visées : Q012 au rang 4 (BM25 : 22), Q016 au rang 4 (BM25 : 140), et Q014 au rang 1. Il recule sur Q006 (aphtes : rang 14, mais l'équivalent DOC001 est retrouvé, d'où Hit@5 équiv. = 1) et Q001 (rang 3).
- **Le titre de section aide la recherche dense** (0,719 → 0,875 de Rappel@5), alors qu'il n'aidait plus BM25 après racinisation : le modèle situe le passage (« Nutrition entérale à domicile », « Une diminution temporaire de certains globules blancs »).
- **La fusion RRF n'apporte rien** : elle mélange un BM25 qui rate Q012/Q016 et un dense qui rate Q006/Q009 ; à poids égaux, les erreurs de chaque méthode diluent les réussites de l'autre. Pas de pondération réglée (risque de sur-ajustement sur 16 questions).
- **Essais de fusion favorisant la recherche dense** (BM25 REC-v2 + dense section + texte ; `recherche_dev_fusion_essais.csv`) :

| DEV, 16 questions avec réponse | Hit@5 | Rappel@5 | Couverture éléments@5 | Paramètres réglés |
|---|---|---|---|---|
| BM25 REC-v2 | 0,875 | 0,781 | 0,823 | 0 |
| **dense (section + texte)** | **0,938** | **0,875** | **0,979** | 0 |
| RRF, poids dense × 1 | 0,875 | 0,781 | 0,802 | 0 |
| RRF, poids dense × 1,5 / × 2 / × 3 (identiques) | 0,938 | 0,812 | 0,844 | 1 |
| règle « grand écart » → dense (premier passage d'une méthode absent des 20 premiers de l'autre → dense seul, sinon RRF) | 0,875 | 0,781 | 0,885 | 1 |

  - La pondération récupère Q006 (aphtes, rang 14 → 3, bien vu par BM25) mais fait reculer Q012 (4 → 5) et Q016 (4 → 13), que seule la recherche dense trouvait ; au-delà de × 1,5, le poids ne change plus rien.
  - La règle « grand écart » bascule bien sur la recherche dense pour Q016 (rang 4), mais la fusion reprend la main sur Q012 (rang 7) et ne récupère pas Q006 (rang 14).
  - Ces règles ont été imaginées après avoir vu les échecs de DEV (résultat optimiste) et ajoutent un paramètre réglé sur 16 questions ; aucune ne dépasse la recherche dense seule, sans paramètre. **Retenu pour l'approfondissement : recherche dense sur titre de section + texte, sans fusion** ; BM25 REC-v2 reste le socle. À comparer une seule fois sur TEST après le gel, avec la qualité des réponses de Q2.
- **Limites** : 16 questions, 5 méthodes comparées sur le même DEV ; l'écart dense / BM25 (+0,094 de Rappel@5) repose sur 3 questions. À confirmer sur TEST après le gel, si l'approfondissement est retenu, en le rapportant à côté du socle BM25.
- **Incident d'environnement** : l'installation de `sentence-transformers` 6.2 a mis à jour `transformers` en 5.22 ; restauré en 4.57.1 (version de BioBERT) avec `sentence-transformers` 5.1.2, `pip check` sans conflit.

### APP-REC — qualité des réponses de Q2 avec la recherche dense (2026-10-29, DEV, notebook 4.2)

- Q2 v1, contexte c2, mêmes paramètres ; seule la source des 5 passages change (dense E5 section + texte au lieu de BM25 REC-v2). 20 appels, 17 694 + 1 674 tokens, 0 échec. Sorties : `resultats/qa/predictions_llm_dev_dense.jsonl`.
- Contrôles automatiques : 4/4 abstentions correctes dans les deux cas ; phrase d'abstention sur une question avec réponse : 2 (BM25 : Q014 partielle, Q016) → 1 (dense : Q014 partielle) ; 0 citation inventée ; réponses plus longues (médiane 55 mots contre 44,5).
- Lecture des 20 paires de réponses (5 identiques : Q004, Q005, Q018, Q020 et une partie de Q007/Q008/Q017 quasi identiques) :

| Question | Q2 avec BM25 REC-v2 | Q2 avec recherche dense |
|---|---|---|
| Q012 (sonde à domicile) | répond sur la nutrition **parentérale**, dit ne pas savoir comment installer le patient | **complète et juste** : position assise ou demi-assise à 30°, passage sur 18 h / 6 h couché, prestataire (DOC008_P027, P028) |
| Q016 (signes d'infection) | abstention (preuve absente) | **complète** : seuils 38 °C / 38,5 °C / 36,5 °C, autres signes, consulter immédiatement (DOC001_P118, P119) |
| Q010 (diarrhée) | boissons et alerte, **sans les aliments** | **complète** : alimentation pauvre en fibres, 2 litres, alerte (DOC001_P092-P093, DOC007_P008) |
| Q015 (mesurer sa fatigue) | échelle 0-20 seulement | échelle 0-20 **et** questionnaire quotidien (DOC006_P002, P003) |
| Q003 (poids et diététique remboursée) | complète | **régression** : DOC002_P003 (panier des 9 soins remboursés) absent ; Q2 dit honnêtement que le remboursement « n'est pas précisé ici » |
| Q001 (sources divergentes) | deux délais, deux phrases distinctes avec leur source | deux délais présentés comme **une seule histoire cohérente** (« repoussent en 3 à 6 mois, avec un début de repousse vers 6 à 8 semaines ») : la divergence entre documents n'est pas signalée |
| Q019 (vernis, sans réponse) | abstention seule | explication sur la fragilité des ongles, puis abstention (correct) |

- **Bilan** : avec la recherche dense, Q2 répond correctement à Q012 et Q016, que la configuration du socle ratait, et complète Q010 et Q015 ; une régression (Q003, élément « remboursement » manquant, sans affirmation fausse). L'erreur de Q008 (prémisse en kilos) reste la seule erreur imputable au LLM sur DEV, avec la façon de présenter la divergence de Q001.
- À reproduire sur TEST après le gel (comparaison BM25 REC-v2 / dense pour Q2), en rappelant que DEV a servi à choisir la méthode dense (résultat DEV optimiste).

---

## 7. Journal

| Date | Changement |
|---|---|
| ≤ 2026-10-11 | DIC-v1 et APP-v1 figées ; NEG-v0 ; corpus QA (commit `fd3fc0d`). |
| 2026-10-16 | Analyse du taux d'annotation (biais d'imbrication, rôle de la casse) — non intégrée. |
| 2026-10-16 | Exports `data/corpus_extraction.csv` et `data/bio_extraction.csv`. |
| 2026-10-16 | DIC-v2 : 5 règles de post-traitement dans le notebook 2.3 (F1 val 0,7449 → 0,7912) ; prédictions VALIDATION et TEST régénérées. |
| 2026-10-23 | Corpus QA : 7 pages INCa ajoutées (DOC004–DOC010, via Wayback Machine), catalogue `data/corpus.csv` à 10 documents. |
| 2026-10-23 | Notebook 2.3 réexécuté (résultats DIC-v2 identiques) ; `comparaison_validation.csv` recalculé avec DIC-v2. |
| 2026-10-23 | PAS-v1 : extraction (PyMuPDF / BeautifulSoup) et découpage des 10 documents en 413 passages ; preuves annotées par extrait verbatim, Q001–Q005 remappées ; contrôle de 10 passages. |
| 2026-10-23 | Q001 réannotée (sources divergentes DOC001/DOC004 sur la repousse des cheveux) ; règle de rédaction pour les sources divergentes. |
| 2026-10-23 | Guide de rédaction QA (`rapport/guide_redaction_qa.md`) ; références de Q001, Q002, Q004 reformulées ; contrôle de recopie dans le notebook 3. |
| 2026-10-23 | Questions DEV Q006–Q020 rédigées (aide Claude, à relire) : DEV complet 20/20 ; équivalent DOC007 pour Q002 ; règles 1.5 (prémisse inexacte), 1.6 (information datée) et § 5 (aide LLM) du guide. |
| 2026-10-23 | Questions TEST Q021–Q030 rédigées (aide Claude, à relire) : TEST complet 10/10, dont une question à sources divergentes (Q022). |
| 2026-10-28 | Relecture des 30 questions QA par AMARA Yanis, sans modification (`statut_relecture: relue_AMARA`). |
| 2026-10-28 | REC-v1 : BM25 du TD (section + texte indexés), DEV Hit@5 = 0,750, Rappel@5 = 0,688 ; Q0 DEV produit. |
| 2026-10-28 | LLM-v1 : Q1/Q2 (prompts du guide) sur DEV avec gpt-4.1-mini-2025-04-14 ; Q2 : 4/4 abstentions correctes, 2 abstentions dues à la recherche. |
| 2026-10-28 | LLM-v2 : contexte c2 (titres) et prompt Q2 v2 sur DEV ; pas de gain net des nouvelles consignes, erreurs restantes dominées par la recherche. |
| 2026-10-29 | REC-v2 : BM25 + racinisation Snowball, DEV Hit@5 = 0,875, Rappel@5 = 0,781 (REC-v1 : 0,750 / 0,688) ; k1/b du TD conservés ; Q0 DEV régénéré. |
| 2026-10-29 | Q1/Q2 relancés sur les contextes REC-v2 : Q014 et Q010 corrigés par la recherche ; Q2 v1 c2 meilleure configuration sur DEV ; v2 sans gain. |
| 2026-10-29 | APP-REC (approfondissement) : dense E5 section + texte, DEV Hit@5 = 0,938, Rappel@5 = 0,875 ; Q012 et Q016 retrouvées ; hybride RRF sans gain. |
| 2026-10-29 | APP-REC : essais de fusion pondérée (× 1,5 à × 3) et de règle « grand écart » sur DEV, sans gain sur la recherche dense seule (Rappel@5 0,812 / 0,781 contre 0,875) ; dense sans fusion retenu pour l'approfondissement. |
| 2026-10-29 | APP-REC : Q2 v1 c2 avec passages denses sur DEV ; Q012 et Q016 désormais justes, Q010 et Q015 complétées, régression sur Q003. |
| 2026-10-29 | Synthèse du jalon QA1 rédigée (`rapport/synthese_QA1.md`). |
