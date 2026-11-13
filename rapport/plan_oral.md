# Plan de l'oral — projet TALS (AMARA / TOMAS)

21 slides, environ 21 minutes. Figures : `figures_oral/NN_*.png` (régénérées par
`figures_oral/generer_figures.py`). Pour chaque slide : ce qu'on met **sur la slide**, ce qu'on **dit**,
comment **lire la figure**, un **exemple**, les **questions possibles** du jury.

Mise à jour du 11/11/2026 : **DIC-v4** (dictionnaire + lexique MeSH) remplace DIC-v3 comme version figée.
Le message de la partie extraction change : le dictionnaire arrive à 0,5 point du modèle appris sur TEST
(0,889 contre 0,894).

Version courte (≈ 13 min) : passer en annexe les slides 4, 6, 12 et 19.

| # | Slide | Figure | Durée |
|---|---|---|---|
| 1 | Titre | — | 0:15 |
| 2 | Les deux tâches et la méthode | — | 1:00 |
| 3 | La tâche d'extraction sur un exemple | 08 | 1:00 |
| 4 | Méthode 1 : dictionnaire et règles | 06 | 1:00 |
| 5 | Méthode 1 (suite) : ajout du lexique MeSH (DIC-v4) | 16 | 1:30 |
| 6 | Méthode 2 : modèle appris | 05 | 1:00 |
| 7 | L'évolution des versions | 01 | 0:45 |
| 8 | Où sont les erreurs | 03 | 0:45 |
| 9 | Erreurs commentées (extraction) | tableau | 1:15 |
| 10 | Pourquoi ne pas combiner les deux méthodes | 14 | 1:00 |
| 11 | Résultats TEST | 02 + 07 | 1:15 |
| 12 | Comparaison avec l'état de l'art | 04 | 0:45 |
| 13 | Négation + erreurs commentées | 09 + tableau | 1:30 |
| 14 | Corpus et questions QA | — | 0:45 |
| 15 | Retrouver les bons passages | 10 | 1:00 |
| 16 | Pourquoi pas de recherche hybride | 15 | 0:45 |
| 17 | Q0 / Q1 / Q2 : les scores | 11 | 1:00 |
| 18 | Q0 / Q1 / Q2 : exemples de réponses | encadrés | 1:30 |
| 19 | Robustesse des choix | 13 + 12 | 0:45 |
| 20 | Bilan et limites | — | 1:00 |
| 21 | Merci / questions (+ annexes) | — | — |

---

## Introduction

### 1. Titre
- **Sur la slide :** titre du projet, binôme, ESIEE E5-BIO, date.
- **À dire :** « Deux tâches de traitement du langage en santé : repérer automatiquement médicaments et
  maladies dans des articles scientifiques, puis répondre à des questions de patients à partir de documents fiables. »

### 2. Les deux tâches et la méthode
- **Sur la slide :** deux colonnes.
  - **Extraction** : BC5CDR, 1 500 résumés PubMed (500 TRAIN / 500 VALIDATION / 500 TEST), entités Chemical et Disease ;
    deux méthodes comparées : dictionnaire + règles (puis + lexique MeSH) et modèle appris (BERT biomédical).
  - **Question-réponse** : 10 documents INCa sur les effets indésirables de la chimiothérapie, public patients et proches.
  - En bas : « Réglages sur VALIDATION / DEV — TEST évalué une seule fois ».
- **À dire :**
  - Tous les choix (seuils, règles, époques, consignes) sont faits sur VALIDATION ou DEV.
  - TEST n'est utilisé qu'une fois, à la fin, sur des versions figées.
  - Chaque version et ses scores sont tracés dans un historique (`RAPPORT.md`).
- **Pourquoi c'est important :** un score réglé sur TEST est trop optimiste. Le jury le vérifie presque toujours.

---

## Partie 1 — Extraction d'entités

### 3. La tâche, sur un exemple (figure 08)
- **Sur la slide :** la figure, et une phrase : « trouver chaque entité avec ses bornes exactes et sa catégorie ».
- **Lire la figure :**
  - Ligne 1 = référence des experts (vert = Chemical, violet = Disease).
  - Puis DIC-v3 (dictionnaire sans lexique externe), DIC-v4 (avec MeSH), APP-v3 (modèle appris).
  - Cadre rouge plein = bornes fausses ; cadre pointillé = entité manquée.
- **À dire :**
  - DIC-v3 trouve « valve regurgitation » mais oublie « Tricuspid », et rate « tricuspid regurgitation » :
    ces formes n'apparaissent pas dans TRAIN.
  - DIC-v4 les trouve : elles sont dans MeSH, le grand vocabulaire médical que nous avons ajouté.
  - Le modèle appris les trouve aussi, sans lexique : grâce au contexte.
  - L'évaluation est stricte : une entité mal découpée compte comme une erreur.
- **Question possible :** « Pourquoi une évaluation aussi stricte ? » → C'est le standard de BC5CDR ; elle permet
  la comparaison avec les travaux publiés.

### 4. Méthode 1 : dictionnaire et règles (figure 06)
- **Sur la slide :** le principe en 3 points, puis la figure.
  1. Dictionnaire = toutes les entités annotées dans TRAIN, avec leur catégorie la plus fréquente.
  2. Plus longue correspondance dans le texte, sans tenir compte des majuscules.
  3. Filtre : une forme n'est gardée que si elle est annotée dans au moins 30 % de ses apparitions dans TRAIN.
- **Lire la figure :** gain de F1 de chaque règle **appliquée seule** ; barres foncées = toutes ensemble.
  En haut, les 5 règles (DIC-v1 → v2) ; en bas, les 4 ajouts (DIC-v2 → v3).
- **À dire :**
  - Le filtre évite les mots ambigus : « cancer » apparaît souvent sans être annoté (« cancer patients »).
  - **Sigles définis** (+2,0) : « 5-fluorouracil (5-FU) » → « 5-FU » prend le type de la forme longue.
  - **Suffixes appris** (+1,6) : *-dipine*, *-olam* → médicament ; *-emia* → maladie.
  - Ajouts v3 : variantes singulier/pluriel (« movement disorders ») ; propagation d'une entité trouvée une fois
    à tout le résumé.
  - ⚠️ Les gains ne s'additionnent pas (les règles se recouvrent).
- **Transition :** « Avec ces règles, on plafonne à 0,80. Il manque surtout du vocabulaire : environ 1 600 entités
  manquées ont une forme qui n'apparaît jamais dans TRAIN. »

### 5. Méthode 1 (suite) : ajout du lexique MeSH — DIC-v4 (figure 16)
- **Sur la slide :** la figure, et 3 points.
  1. **MeSH** = le vocabulaire médical de la bibliothèque américaine de médecine, qui sert à indexer PubMed :
     841 445 termes gardés (maladies → Disease, substances → Chemical, avec tous les synonymes).
  2. **Filtre par terme** : un terme MeSH présent dans TRAIN mais annoté moins de 30 % du temps est retiré (148 termes).
  3. **Filtre par branche** : MeSH est rangé en arbre ; une branche entière est écartée si ses termes sont
     annotés moins de 30 % du temps dans TRAIN (29 branches sur 275).
- **Lire la figure :** chaque étape s'ajoute à la précédente (VALIDATION). Vert = précision, violet = rappel,
  orange = F1 ; pointillé bleu = F1 du modèle appris.
- **À dire :**
  - Ajouter MeSH sans précaution fait bondir le rappel (0,73 → 0,86) mais **chuter** la précision (0,88 → 0,77) :
    des mots comme *drug*, *disease*, *protein* sont dans MeSH mais ne sont jamais annotés.
  - Les filtres appris sur TRAIN adaptent MeSH aux conventions de BC5CDR. Exemples de branches écartées :
    classes de médicaments (*analgesic* : annoté 17 % du temps), protéines (11 %), préparations (*drug*, *solution* : 0 %).
  - Résultat : la précision remonte au-dessus de DIC-v3 (0,90) et le rappel reste haut. F1 VALIDATION 0,799 → **0,885**.
  - Toujours aucun apprentissage statistique : seulement un vocabulaire et des filtres comptés sur TRAIN.
  - L'ajout d'un lexique externe a été validé par l'enseignant.
- **Question possible :** « N'est-ce pas un avantage injuste ? » → Les outils officiels de 2015 (tmChem, DNorm)
  utilisent aussi MeSH. Précaution : MeSH crée des fiches pour les nouvelles substances citées dans PubMed ;
  la version 2026 peut donc contenir des noms venant des résumés du corpus eux-mêmes. Le score peut être un peu optimiste.

### 6. Méthode 2 : modèle appris (figure 05)
- **Sur la slide :** « Étiquetage mot par mot B / I / O avec un modèle BERT pré-entraîné sur des textes biomédicaux ».
- **Lire la figure :** F1 de VALIDATION après chaque époque (un passage complet sur TRAIN). Les points marquent
  l'époque retenue ; la croix rouge est APP-v1.
- **À dire :**
  - B/I/O : « Tricuspid » = B-Disease (début), « valve regurgitation » = I-Disease (suite), le reste = O.
  - APP-v1 s'arrêtait à 2 époques : le modèle n'avait pas fini d'apprendre (0,855).
  - En entraînant plus longtemps (10 époques, taux plus élevé, montée progressive), BioBERT atteint 0,893.
  - En passant à PubMedBERT (pré-entraîné sur PubMed seul), on obtient 0,912.
  - Exemple : « Doxorubicin-induced cardiomyopathy » = 4 morceaux pour PubMedBERT, 12 pour BioBERT.
- **Question possible :** « Comment avez-vous choisi le nombre d'époques ? » → Meilleur F1 de VALIDATION,
  en moyenne sur 2 graines aléatoires ; règle fixée à l'avance : remplacer le modèle seulement si le gain dépasse 0,5 point.

### 7. L'évolution des versions (figure 01) — slide qui résume la partie 1
- **Lire la figure :** en abscisse la précision (part de justes parmi ce qui est trouvé), en ordonnée le rappel
  (part trouvée parmi ce qu'il faut trouver). Les pointillés relient les points de même F1 ; plus on va en haut à droite, mieux c'est.
- **À dire :**
  - De DIC-v1 à DIC-v3, les règles font peu bouger le rappel : le dictionnaire ne trouve que ce qu'il a vu dans TRAIN.
  - DIC-v4 fait un grand saut vers le haut (rappel 0,73 → 0,87) **et** vers la droite (précision 0,88 → 0,90) grâce à MeSH filtré.
  - Le modèle appris reste devant sur le rappel (0,92) : il reconnaît des entités jamais vues grâce au contexte.
  - Sur VALIDATION, il reste 2,7 points entre DIC-v4 (0,885) et APP-v3 (0,912).

### 8. Où sont les erreurs (figure 03)
- **Lire la figure :** trois types d'erreurs sur les 9 591 entités de VALIDATION.
  - **Entités manquées** : aucune prédiction ne touche l'entité.
  - **Bornes fausses** : l'entité est trouvée mais mal découpée.
  - **Fausses détections** : une entité trouvée là où la référence n'en a pas.
- **À dire :**
  - Les entités manquées du dictionnaire passent de 1 941 (DIC-v3) à 832 (DIC-v4) ; le modèle n'en manque que 334.
  - Bornes fausses (437 contre 432) et fausses détections (446 contre 499) : DIC-v4 et APP-v3 sont désormais au même niveau.
  - La différence restante entre les deux méthodes tient donc surtout aux entités manquées.
  - Les erreurs de catégorie (Chemical ↔ Disease) sont négligeables : 4 à 14 cas.
- **Transition :** « Nous avons analysé cinq erreurs à la main. »

### 9. Erreurs commentées en extraction (`resultats/extraction/erreurs_commentees.md`)
- **Sur la slide :** un tableau (erreurs d'APP-v3 tirées au hasard sur VALIDATION, choisies pour avoir des causes
  différentes). La colonne DIC-v4 a été vérifiée sur ses prédictions (le fichier, plus ancien, compare avec DIC-v2).

| Phrase (extrait) | Référence | APP-v3 | DIC-v4 | Cause |
|---|---|---|---|---|
| « progressive **deterioration of vision** » | deterioration of vision | *of vision* | rien | maladie décrite par une expression courante |
| « **hepatitis B** and **rubella** prevention… hepatitis B vaccine » | hepatitis B / rubella, séparées | *hepatitis B and rubella* ; *hepatitis B vaccine* en Chemical | hepatitis B ✓, rubella ✓, mais aussi *hepatitis B vaccine* en Chemical | coordination + contexte de vaccin |
| « combined oral contraceptives (**COCs**) » | COCs (Chemical) | rien (7 manquées) | ✓ | sigle jamais annoté dans TRAIN |
| « tricyclic **antidepressant** overdose » | rien | *antidepressant* (Chemical) | rien ✓ | annotation irrégulière |

- **À dire (une phrase par cas) :**
  1. **Bornes fausses.** Expression ordinaire : le modèle rate le début sur « deterioration » et ouvre l'entité sur
     « of ». Même chose pour « increase in MAP », prédit « increase in ». Aucune des deux méthodes ne la trouve.
     Chaque erreur de ce type compte double : une fausse détection et une entité manquée.
  2. **Coordination.** La référence sépare ici les deux maladies. Devant « vaccine », le modèle annote le vaccin comme
     un produit. Avec MeSH, le dictionnaire fait maintenant la même erreur : « hepatitis B vaccine » est un terme MeSH.
  3. **Sigle.** « COCs » apparaît 3 fois dans TRAIN sans jamais être annoté : le modèle a appris à l'ignorer.
     Le dictionnaire le retrouve grâce à la règle des sigles définis dans le texte.
  4. **Annotation irrégulière.** « antidepressant » est annoté à ses 15 apparitions dans TRAIN, à aucune des 15 de
     VALIDATION : l'erreur vient de l'annotation, pas du modèle. Le dictionnaire l'évite (filtre des classes de médicaments).
  - *(Si le temps le permet : « contralateral rotation », un comportement anormal du rat annoté comme maladie,
    qu'aucune méthode ne reconnaît.)*
- **Message :** une partie des erreurs vient des conventions d'annotation. Les deux méthodes n'ont pas exactement les mêmes points faibles.
- **Transition :** « Alors pourquoi ne pas combiner les deux méthodes ? »

### 10. Pourquoi ne pas combiner les deux méthodes (figure 14)
- **Lire la figure :** à gauche, précision / rappel / F1 de chaque combinaison (pointillé bleu = F1 d'APP-v3 seul) ;
  à droite, qui trouve quoi parmi les entités de référence (VALIDATION, avec DIC-v4).
- **À dire :**
  - Les deux méthodes trouvent les mêmes entités dans 83 % des cas ; le dictionnaire n'en trouve seul que 322 (3,4 %).
  - **Intersection** (ce que les deux trouvent) : précision 0,97 mais rappel 0,83.
  - **Union** (tout ce que l'un ou l'autre trouve) : rappel 0,95 mais beaucoup de fausses détections.
  - **Ajout du dictionnaire seulement là où le modèle n'a rien trouvé** : 368 ajouts, dont 95 justes → 0,905.
  - Aucune ne dépasse APP-v3 seul (0,912). Même conclusion qu'avec DIC-v3 : pas de méthode hybride.

### 11. Résultats sur TEST (figures 02 et 07)
- **Sur la slide :** figure 02 en grand, figure 07 en petit.
- **À dire :**
  - Sur TEST : F1 de **0,889** (DIC-v4) contre **0,894** (APP-v3) : 0,5 point d'écart, contre 9,6 avec DIC-v3.
  - Les deux méthodes ont des profils différents : DIC-v4 est plus **précis** (0,901 contre 0,878), APP-v3 a un
    meilleur **rappel** (0,910 contre 0,877).
  - Chemical : quasi-égalité (0,923 contre 0,928). Disease : 0,846 contre 0,853. Disease reste la catégorie difficile :
    noms plus variés et descriptifs (« impaired renal function »).
  - Figure 07 : DIC-v4 est stable entre VALIDATION et TEST (+0,4 point) ; APP-v3 perd 1,8 point, ce qui est normal
    puisque ses réglages ont été choisis sur VALIDATION.
  - Coût : le dictionnaire tourne en 3 s sur un processeur ordinaire (plus 25 s de construction, 1,3 Go de mémoire) ;
    le modèle demande un GPU (17 s) et un entraînement.

### 12. Comparaison avec l'état de l'art (figure 04)
- **À dire :**
  - APP-v3 : 92,8 (Chemical) et 85,2 (Disease), contre 93,3 et 85,6 pour PubMedBERT publié : nous retrouvons le niveau publié.
  - DIC-v4 dépasse les outils officiels de 2015 (tmChem + DNorm), lancés nous-mêmes sur notre TEST : égalité en
    Chemical (92,3 contre 92,2), +4,4 points en Disease. Il se place au niveau de BioBERT et SciBERT.
  - Le saut depuis DIC-v3 (clair) montre que l'écart venait du vocabulaire, pas de la méthode.
  - Les protocoles publiés sont proches mais pas identiques : la comparaison est indicative.
- **Question possible :** « Et les LLM ? » → Sans ajustement, environ 0,80 en Chemical d'après la littérature :
  ils ignorent les conventions d'annotation de BC5CDR.

---

## Partie 2 — Négation

### 13. Détecter la négation (figure 09 + `resultats/negation/erreurs_commentees.md`)
- **Sur la slide :** matrice à gauche ; à droite, les 2 erreurs et 2 cas difficiles bien traités ; « kappa = 0,51 ».
- **Méthode, en une phrase :** déclencheurs (no, not, without, ruled out…), portée de 8 mots au maximum,
  pseudo-négations ignorées (« cannot be excluded »). Règles écrites **avant** la génération des phrases de test.
- **Les deux erreurs (à afficher) :**

| Phrase | Mention | Attendu | Prédit | Pourquoi |
|---|---|---|---|---|
| The normal ECG did **not** exclude myocardial ischemia. | myocardial ischemia | non nié | nié | double négation : « ne pas exclure » = possible |
| The patient did **not**, despite the high cumulative dose of doxorubicin, develop cardiomyopathy. | cardiomyopathy | nié | non nié | 11 mots entre « not » et la maladie (> 8) |

- **À dire :**
  - Première erreur : la règle connaît « cannot be excluded » et « not ruled out », pas « did not exclude ».
    On pourrait l'ajouter, mais pas maintenant : ce serait régler la méthode sur le test.
  - Seconde erreur : une portée en nombre de mots ne gère pas une incise. Il faudrait une portée fondée sur la syntaxe.
- **Cas difficiles bien traités :**
  - « She experienced **neither** nausea **nor** vomiting » : la négation atteint le second élément.
  - « Acute hepatitis **was ruled out** by liver biopsy » : déclencheur placé **après** la maladie.
  - « There was **no increase** in seizure frequency » : c'est la fréquence qui n'augmente pas ; les crises existent.
- **Limite repérée sur DEV :** « no rash, jaundice or edema, **and** mild hypertension was noted » n'est juste que
  grâce à la limite de 8 mots ; une liste plus longue aurait étendu la négation à l'hypertension.
- **Accord entre annotateurs :** kappa 0,51 ; 5 désaccords résolus ensemble (ex. « no increase in » :
  est-ce la hausse ou la maladie qui est niée ?).
- **Honnêteté :** sur 10 phrases, une erreur fait varier le F1 d'environ 0,1. C'est un test contrôlé, pas une
  évaluation sur de vrais dossiers.

---

## Partie 3 — Question-réponse

### 14. Corpus et questions
- **Sur la slide :** 10 documents INCa → 413 passages ; 20 questions DEV + 10 TEST ; un exemple de question avec sa réponse de référence.
- **À dire :**
  - Réponses de référence rédigées par nous (pas copiées) ; preuves = extraits exacts des documents.
  - Cas difficiles prévus exprès :
    - questions **sans réponse** (« Le gingembre aide-t-il contre les nausées ? ») ;
    - **sources qui se contredisent** (remboursement du psychologue) ;
    - **vocabulaire de patient** (« envie de vomir en arrivant à l'hôpital » = nausées anticipatoires).

### 15. Retrouver les bons passages (figure 10)
- **Lire la figure :** pour chaque question, on regarde les 5 premiers passages renvoyés.
  - **Hit@5** : au moins une preuve dans les 5.
  - **Rappel@5** : part des preuves retrouvées.
  - **Couverture des éléments** : part des éléments de la réponse présents dans ces passages.
- **À dire :**
  - BM25 classe les passages selon les mots partagés avec la question.
  - **Racinisation** : « diarrhée » et « diarrhées » deviennent le même mot. La preuve de la question sur la
    diarrhée passe du rang 23 au rang 2.
  - **Recherche dense** : compare le sens, pas les mots. Elle relie « nourri par sonde » et « nutrition entérale », sans mot commun.
  - Sur TEST, son avance disparaît (même rappel, 0,77) : elle retrouve une question ratée par BM25 mais en perd
    d'autres (ergothérapeute, psychologue). L'avantage vu sur DEV était optimiste.

### 16. Pourquoi pas de recherche hybride (figure 15)
- **Lire la figure :** barre foncée = rappel@5, barre claire = couverture ; pointillé bleu = rappel de la recherche dense seule.
- **À dire :**
  - Testé : fusion des classements (RRF) à poids égaux ou en favorisant la recherche dense, règle « grand écart »,
    reclassement par un second modèle (cross-encoder).
  - Aucune ne dépasse la recherche dense seule sur DEV.
  - Le reclassement atteint le même rappel mais coûte 3,5 s par question au lieu de 0,04 s.
  - Sur TEST, BM25 et recherche dense font jeu égal : rien à gagner à combiner sur 413 passages.

### 17. Q0 / Q1 / Q2 : les scores (figure 11)
- **Sur la slide :** les trois configurations, une ligne chacune, puis la figure.
  - **Q0** : les passages BM25 renvoyés tels quels, sans LLM.
  - **Q1** : le LLM répond en 1 à 3 phrases en citant les passages.
  - **Q2** : le LLM n'utilise **que** les passages, garde négations et chiffres, cite chaque affirmation, et écrit
    « Information insuffisante dans les documents fournis » s'il ne trouve pas.
- **Lire la figure :** à gauche les mesures automatiques (ROUGE, BLEU = mots communs avec la référence) ; à droite
  la grille de lecture (exactitude, complétude, abstentions justes).
- **À dire :**
  - Selon ROUGE, Q1 et Q2 sont presque à égalité. Selon la grille, Q2 est le plus juste (1,7 / 2) et le seul à
    s'abstenir correctement sur les 2 questions sans réponse.
  - Q1 est un peu plus complet mais répond même quand il ne devrait pas.
  - ROUGE et BLEU mesurent la ressemblance des mots, pas la justesse. En santé, une réponse inventée est pire qu'une abstention.
  - Les citations sont presque toujours soutenues : 18 sur 19 pour Q2.
- **Question possible :** « Qui a noté la grille ? » → Un LLM juge sans contexte du projet, lancé deux fois
  indépendamment, avec des notes identiques. C'est une limite à mentionner.
- **Transition :** « Les chiffres ne disent pas tout : regardons des réponses réelles. »

### 18. Q0 / Q1 / Q2 : exemples de réponses (TEST, `resultats/qa/grille_manuelle.csv`)
- **Sur la slide :** une question en haut, trois encadrés côte à côte (Q0 | Q1 | Q2), passages importants surlignés,
  note du juge sous chaque encadré. Exemple 1 en principal ; exemples 2 et 3 en petit ou en animation.

**Exemple 1 — Q030 : « Les séances d'acupuncture sont-elles remboursées pendant un traitement contre le cancer ? »**
(les documents ne répondent pas)

| | Réponse (extraits réels) | Exactitude |
|---|---|---|
| **Q0** | « Si vous souffrez du syndrome main-pied : • assurez des soins d'hygiène rigoureux… Deux séances de pédicure sont notamment remboursées… » | 1 / 2 |
| **Q1** | « Les séances d'acupuncture **ne sont pas remboursées** pendant un traitement contre le cancer, car elles font partie des pratiques de soins non conventionnelles […] et ne sont pas prises en charge par l'Assurance maladie (DOC008_P032). » | **0 / 2** |
| **Q2** | « Les séances d'acupuncture **ne sont pas mentionnées** comme remboursées pendant un traitement contre le cancer […] (DOC008_P032). » | **2 / 2** |

- **À dire :**
  - Q0 renvoie un passage hors sujet, choisi pour les mots « séances » et « remboursées ».
  - Q1 **invente** : le passage cité parle de l'acupuncture, jamais de remboursement.
  - Q2 ne dit que ce que contient le document, comme le demande sa consigne (« n'ajoute pas de réponse issue de tes connaissances générales »).

**Exemple 2 — Q021 : « Pour le casque réfrigérant, combien de temps avant la perfusion est-il posé, à quel rythme est-il changé et quand l'enlève-t-on ? »**

| | Réponse | Exactitude |
|---|---|---|
| **Q0** | Passage sur la douleur après une opération (« combien de temps durera la douleur ? ») | 0 / 2 |
| **Q1 / Q2** | « posé environ 10 à 15 minutes avant le début de la perfusion, changé […] généralement toutes les 45 minutes […], et retiré environ 30 minutes après la fin de la perfusion (DOC004_P006, DOC001_P182, DOC001_P179) » | 2 / 2, complet |

- **À dire :** BM25 s'est accroché à « combien de temps » ; Q1 et Q2 assemblent trois passages de deux documents
  pour répondre aux trois parties de la question.

**Exemple 3 — Q029 : « Le gingembre est-il efficace pour calmer les nausées dues à la chimiothérapie ? »** (les documents n'en parlent pas)
- **Q0 :** un passage sur « l'efficacité d'une chimiothérapie », trouvé par le mot « efficace ».
- **Q1 :** explique que les passages n'en parlent pas, mais cite 5 passages qui ne traitent pas du sujet.
- **Q2 :** « Information insuffisante dans les documents fournis. »

**Ce qui résiste aux trois configurations (bas de slide ou à l'oral) :**
- **Sources contradictoires (Q022, psychologue)** : selon un document, seul le psychiatre est remboursé ; selon
  l'autre, « Mon soutien psy » couvre des séances chez un psychologue. Q2 fond les deux en une seule réponse, sans
  signaler la contradiction (Mistral aussi).
- **Vocabulaire du patient (Q025, « envie de vomir dès que j'arrive à l'hôpital »)** : BM25 ne trouve pas le passage
  sur les nausées anticipatoires ; Q1 et Q2 répondent avec un passage sur les odeurs (1 / 2). La recherche dense le trouve :
  l'erreur vient de la recherche, pas du LLM.

- **Message :** du passage brut (Q0) à la réponse rédigée (Q1), on gagne en pertinence ; sans consigne de prudence,
  le LLM comble les trous avec ses connaissances ; Q2 corrige ce défaut. Restent les contradictions entre sources
  et les questions formulées autrement que les documents.
- **Question possible :** « Pour l'acupuncture, Q2 n'a pas écrit la phrase d'abstention exacte : pourquoi est-ce
  compté comme une abstention ? » → Il dit explicitement que le remboursement n'est pas mentionné, sans rien inventer.

### 19. Robustesse des choix (figures 13 et 12)
- **Figure 13, à dire :** avec 3 passages, il manque des preuves (3 abstentions à tort) ; avec 10, plus de bruit
  (une réponse non soutenue sur les signes d'infection) ; 5 est le meilleur compromis.
- **Figure 12, à dire :**
  - Toutes les questions rejouées avec un second LLM (Mistral) : scores un peu meilleurs, en partie parce que ses réponses sont plus courtes.
  - Il se trompe aux mêmes endroits (contradiction du psychologue non signalée).
  - Conclusion : les erreurs viennent surtout de la recherche de passages, pas du LLM.

---

## Conclusion

### 20. Bilan et limites
- **Bilan :**
  - Extraction : les deux approches arrivent presque à égalité sur TEST (0,889 pour le dictionnaire + MeSH, 0,894 pour
    le modèle appris). Le dictionnaire est plus précis, rapide, explicable et sans GPU ; le modèle a un meilleur rappel
    et n'a besoin d'aucun lexique. L'écart initial (9,6 points) venait du vocabulaire.
  - Négation : des règles simples suffisent dans les cas courants ; doubles négations et portées longues résistent.
  - QA : la qualité dépend d'abord de la recherche de passages ; une consigne de prudence (Q2) évite les réponses inventées.
- **Limites :**
  - Seulement 10 phrases de test (négation) et 10 questions TEST (QA) : chiffres fragiles.
  - Grille QA notée par un LLM.
  - Réponses du LLM pas parfaitement reproductibles même à température 0 (mises en cache).
  - MeSH peut contenir des noms venant des résumés du corpus : le score de DIC-v4 est peut-être un peu optimiste.
  - Une partie des erreurs d'extraction vient de l'annotation elle-même (« antidepressant », « hepatitis B vaccine ») :
    l'évaluation stricte pénalise des prédictions défendables.
- **Pistes, en une phrase :** portée de négation fondée sur la syntaxe ; signaler explicitement les sources qui se contredisent.

### 21. Merci / questions
- **Annexes :** figures 06, 05, 04, 13 et 12 si retirées ; tableau des versions (DIC-v1 → v4, APP-v1 → v3) ;
  un exemple complet de réponse de Q2 avec ses citations.

---

## Questions probables du jury
- **« Pourquoi le F1 ? »** Il combine précision et rappel ; c'est la mesure standard de BC5CDR.
- **« Temps de calcul ? »** Dictionnaire (DIC-v4) : 3 s sur un processeur ordinaire, plus 25 s de construction
  (1,3 Go de mémoire). Modèle : 17 s sur GPU, plus quelques minutes d'entraînement par essai.
- **« Lequel choisir ? »** À F1 presque égal : le dictionnaire si l'on veut de la précision, de l'explicabilité et pas
  de GPU ; le modèle si l'on veut le meilleur rappel ou travailler sans lexique (autre langue, autre domaine).
- **« Pourquoi pas les deux ensemble ? »** Testé : aucune combinaison ne dépasse le modèle seul (slide 10).
- **« Le lexique MeSH, c'est permis ? »** Validé par l'enseignant ; les outils officiels de 2015 l'utilisent aussi.
  Précaution : MeSH peut contenir des noms issus du corpus lui-même.
- **« Pourquoi gpt-4.1-mini ? »** Bon rapport coût / qualité ; température 0 et graine fixée pour la reproductibilité.
- **« Pourquoi ne pas corriger les règles de négation après le test ? »** Ce serait régler la méthode sur le test ;
  les corrections possibles sont décrites mais pas appliquées.
