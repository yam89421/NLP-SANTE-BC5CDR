# Synthèse du jalon QA1 — documents, questions et recherche de passages

AMARA Yanis, TOMAS Alban · E5-BIO, Traitement automatique du langage naturel en santé · 2026/2027

**Usage visé** : « Cet outil aide les patients traités par chimiothérapie et leurs proches à retrouver les effets
indésirables possibles et leur prise en charge dans les documents d'information de l'Institut national du cancer. »

## 1. Documents

Le corpus compte **10 documents de l'Institut national du cancer (INCa)**, en français, destinés aux patients,
réutilisables sous la licence ouverte INCa (mention de la source et de la date) ; le catalogue (`data/corpus.csv`)
donne pour chacun l'URL, la version et la date de récupération.

| ID | Document | Format, version |
|---|---|---|
| DOC001 | Comprendre la chimiothérapie (guide patients) | PDF, 2011 |
| DOC002 | Cancers et soins de support (fiche Cancer info) | PDF, 2024 |
| DOC003 | Les effets indésirables généraux de la chimiothérapie | web, 2019 |
| DOC004 à DOC010 | Chute des cheveux, douleurs et traitements, prise en charge de la fatigue, nausées-vomissements-diarrhées, nutrition, problèmes de bouche, problèmes de peau | web, 2015 à 2024 |

Les sept pages ajoutées pour QA1 proviennent de la rubrique « Effets indésirables » de cancer.fr. Le site étant en
maintenance le 23/10/2026, elles ont été récupérées depuis la Wayback Machine (copie brute, date de capture
indiquée dans le catalogue). Deux documents datent de 2015 et le guide de 2011 : certaines informations sont
anciennes (forfait perruque) et deux sources divergent sur la repousse des cheveux, ce que nos questions exploitent.

## 2. Passages

**Extraction** (`src/qa_corpus.py`, notebook 3). Les deux PDF sont des planches de deux pages imprimées en une ou
deux colonnes, avec encadrés : l'ordre brut du texte n'est pas l'ordre de lecture. Les blocs sont triés par page
imprimée, flux (texte courant puis encadrés), colonne et position ; en-têtes, pieds de page, notes de marge,
légendes de schémas, formulaires et renvois vers d'autres brochures sont retirés ; les phrases coupées par une
colonne ou une page et les césures sont recollées. Les pages web gardent le chapô et le corps de l'article.

**Découpage.** Les paragraphes d'une même section sont regroupés jusqu'à **800 caractères** (650 dans le TD), sans
franchir une frontière de section ; un paragraphe plus long est coupé entre deux phrases. Chaque passage garde sa
localisation : section, numéros de paragraphes, pages imprimées.

| | DOC001 | DOC002 | DOC003-DOC010 | Total |
|---|---|---|---|---|
| Passages | 260 | 42 | 111 | **413** |
| Mots | 20 722 | 3 493 | 8 467 | 32 682 |

**Contrôle.** Dix passages (le plus court, le plus long, huit tirés au hasard) ont été comparés à la source : ordre,
nombres, unités et négations conformes (`resultats/qa/controle_passages.csv`). Un contrôle automatique retrouve
98,2 % des 2 049 phrases telles quelles dans le texte brut des sources ; les 37 restantes sont des artefacts du texte
brut (phrase coupée par un saut de colonne, mots collés). Limites : regroupement glouton (quelques passages courts en
fin de section, listes coupées entre deux passages), tableaux d'une fiche aplatis.

## 3. Questions

| | Questions | Avec réponse | dont à 2 passages ou plus | Sans réponse | Éléments attendus |
|---|---|---|---|---|---|
| DEV (`questions_dev.jsonl`) | 20 | 16 | 7 (≥ 4 demandées) | 4 | 46 |
| TEST (`questions_test.jsonl`) | 10 | 8 | 6 (≥ 2 demandées) | 2 | 24 |

Les dix documents sont utilisés. Aucune famille de reformulations n'est partagée entre DEV et TEST.

**Annotation.** Chaque question avec réponse a une référence, des éléments attendus et, pour chaque élément, ses
preuves. Les preuves sont notées par un **extrait verbatim** du document : leurs identifiants sont recalculés à
chaque redécoupage, sans toucher aux questions. Un passage d'un autre document qui donne la même information est
indiqué comme **équivalent**, hors du calcul du rappel. Chaque question sans réponse a une justification qui cite
les passages proches et dit pourquoi ils ne répondent pas.

**Règles de rédaction** (`rapport/guide_redaction_qa.md`) :
- questions dans les mots d'un patient, sans recopier le passage (« J'ai des aphtes depuis que je suis sous chimio… ») ;
- références concises et reformulées, nombres et négations exacts : aucune ne recopie plus de 9 mots d'une preuve,
  pour ne pas avantager dans BLEU/ROUGE les réponses qui recopient le corpus ;
- cas difficiles volontaires, présents en DEV et en TEST sur des sujets différents : **sources divergentes**
  (repousse des cheveux en 6-8 semaines selon le guide de 2011, en 3-6 mois selon la page de 2024 ; remboursement du
  psychologue), **prémisse inexacte** (seuil de dénutrition demandé en kilos, donné en % du poids), **questions sans
  réponse proches d'un sujet traité** (remboursement du casque réfrigérant, vernis à ongles, gingembre).

Les questions Q006 à Q030 ont été rédigées avec l'aide d'un LLM (Claude), à partir des passages ; chaque preuve est
vérifiée automatiquement et chaque absence recherchée dans les dix documents. Les 30 questions ont été relues par
AMARA Yanis le 28/10/2026, sans modification. TEST est mis de côté jusqu'au gel du 06/11.

## 4. Recherche de passages sur DEV

**Méthode** (`src/qa_recherche.py`, notebook 4.1) : BM25 du TD RAG (k1 = 1,5, b = 0,75), top-5. Mesures sur les
16 questions DEV avec réponse : Hit@5 (au moins une preuve dans les 5 premiers), Rappel@5 (part des preuves
retrouvées), couverture des éléments@5 (part des éléments attendus disponibles, preuves ou équivalents).

| Configuration (DEV) | Hit@5 | Rappel@5 | Couverture éléments@5 |
|---|---|---|---|
| texte seul, sans prétraitement | 0,688 | 0,625 | 0,677 |
| REC-v1 : titre de section + texte | 0,750 | 0,688 | 0,719 |
| **REC-v2 : texte + racinisation Snowball français (retenu)** | **0,875** | **0,781** | **0,823** |

Huit variantes ont été comparées (texte indexé, mots vides, racinisation) puis une grille k1 × b. La racinisation
apporte l'essentiel du gain (« diarrhée » / « diarrhées ») ; les mots vides (liste NLTK sans les négations)
n'ajoutent rien ensuite ; aucune valeur de k1 ou b ne dépasse celles du TD, qui sont conservées. Le prétraitement ne
modifie ni les questions ni le texte transmis aux modèles.

**Échecs restants** : Q012 (« nourri par sonde » contre « nutrition entérale » : aucun mot commun, preuve au rang 22)
et Q016 (signes d'infection : la liste de symptômes partage peu de mots avec la question, rang 140). Ce sont des
limites d'une recherche par mots, pas de réglage.

**Q0** (premier passage renvoyé tel quel) est produit pour les 20 questions DEV
(`resultats/qa/predictions_q0_dev.jsonl`). Exemple d'erreur : pour la durée des nausées après une chimiothérapie,
le premier passage traite des nausées de radiothérapie ; et Q0 renvoie aussi un passage aux questions sans réponse,
faute de mécanisme d'abstention.

**Approfondissement : recherche dense** (notebook 4.3, guide C.1). Avec le modèle du TD
`multilingual-e5-small` (titre de section + texte encodés, environ 35 s sur CPU, sans coût d'API), la recherche
dense atteint sur DEV **Hit@5 = 0,938, Rappel@5 = 0,875, couverture = 0,979** et retrouve Q012 et Q016 (rang 4).
La fusion des rangs BM25 + dense (RRF), y compris pondérée en faveur du dense, ne dépasse pas la recherche dense
seule. Ce résultat repose sur trois questions et sur un choix fait avec DEV : il reste à confirmer sur TEST, où le
socle restera BM25 REC-v2.

## 5. Suite

- **Premiers essais Q1/Q2 sur DEV** (notebook 4.2, `gpt-4.1-mini-2025-04-14`, température 0, mêmes 5 passages pour
  Q1 et Q2) : Q2 (prompt structuré du guide) s'abstient correctement sur les 4 questions sans réponse, alors que Q1
  invente des conseils absents du corpus (« il serait prudent d'éviter de conduire »). Ajouter des consignes à Q2 n'a
  pas corrigé les erreurs, qui venaient surtout de la recherche ; avec de meilleurs passages, les réponses
  s'améliorent. Les erreurs propres au LLM sur DEV : prémisse en kilos jamais corrigée, sources divergentes fondues
  en une seule réponse.
- **Gel du 06/11** : recherche (BM25 REC-v2 pour le socle, recherche dense pour l'approfondissement), modèle,
  prompts (proposition : Q1 et Q2 du guide, passages précédés de leur titre de section) et paramètres.
- **QA2 (13/11)** : exécution unique sur TEST, BLEU et ROUGE, grille manuelle des 30 réponses par les deux membres,
  analyse des erreurs.

Le détail des versions, des configurations et des scores est dans `RAPPORT.md` ; les sorties dans `resultats/qa/`.
