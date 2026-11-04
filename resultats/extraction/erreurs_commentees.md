# Cinq erreurs d'extraction commentées (méthode apprise APP-v3, VALIDATION)

Méthode : PubMedBERT ajusté en BIO (APP-v3, 7 époques, graine 42), prédictions de
`predictions_apprise_v3_validation.jsonl`. Erreurs classées avec `tals.erreurs`, tirées au hasard (graine 42)
puis choisies pour couvrir des causes différentes. Pour chaque cas, on indique aussi la sortie du dictionnaire (DIC-v2).
L'analyse de la version précédente (BioBERT, APP-v1) est conservée dans `erreurs_commentees_APP-v1.md`.

## Bilan VALIDATION (9 591 mentions de référence)

| | Correctes | Frontière | Type | Manquées | Parasites |
|---|---|---|---|---|---|
| APP-v1 (BioBERT, 2 époques) | 8 208 | 631 | 11 | 741 | 769 |
| APP-v3 (PubMedBERT, 7 époques) | 8 821 | 432 | 4 | 334 | 499 |

- **Disease concentre les erreurs** : 343 frontières sur 432, 218 manquées sur 334, 300 parasites sur 499.
- **Frontières** : la mention prédite est plus longue que la référence dans 244 cas, plus courte dans 187.
- **Manquées** : 251 sur 334 ont une forme absente des mentions de TRAIN (sigles, descriptions longues).
- **Confusions de type** : presque disparues (4 cas).

## 1. Frontière trop courte sur une maladie décrite par une expression (PMID 1628552)

> « …presented with progressive **deterioration of vision**, easy fatiguability, dyspnoea… »

- Référence : `deterioration of vision` <Disease>
- APP-v3 : `of vision` <Disease>
- Dictionnaire : rien

La maladie n'est pas un nom technique mais une expression courante. Le modèle choisit une étiquette par mot :
il manque le `B` sur « deterioration » et ouvre la mention sur « of », ce qu'aucun annotateur ne ferait. Même cas
pour `increase in MAP`, prédit `increase in` (PMID 8586822). Avec le score strict, chacune de ces erreurs compte
deux fois (1 faux positif + 1 faux négatif).

## 2. Coordination et contexte de vaccination : « hepatitis B and rubella » (PMID 15867025)

> « Assessment of perinatal **hepatitis B** and **rubella** prevention… administration of the **hepatitis B** vaccine
> birth dose to all infants, administration of **hepatitis B** immune globulin… »

- Référence : `hepatitis B` <Disease> (9 fois) et `rubella` <Disease> (3 fois), chaque maladie séparément
- APP-v3 : `hepatitis B and rubella` <Disease> (une seule mention, 3 fois) ; `hepatitis B vaccine` et
  `hepatitis B immune globulin` <Chemical> ; seulement 2 `hepatitis B` exacts sur 9
- Dictionnaire : `hepatitis B` <Disease> à chaque occurrence

Deux difficultés se cumulent. La coordination « hepatitis B and rubella » ressemble aux mentions composites gardées
entières (convention du 2.2), alors qu'ici les annotateurs ont séparé les deux maladies. Devant « vaccine » ou
« immune globulin », le modèle annote le produit administré comme Chemical, alors que la référence garde seulement
le nom de la maladie. Déjà présente avec BioBERT (APP-v1), cette erreur résiste au changement de modèle : c'est
le document qui rapporte le plus d'erreurs. Le dictionnaire, qui ignore le contexte, a raison ici.

## 3. Sigle absent de TRAIN : « COCs » (PMID 12851669)

> « …among women on combined oral contraceptives (**COCs**)… per 10 000 women years among women on
> levonorgestrel-containing **COCs**… »

- Référence : `COCs` <Chemical> (7 fois dans le document)
- APP-v3 : rien (7 manquées)
- Dictionnaire : `COCs` <Chemical> ✓

Le sigle apparaît 3 fois dans TRAIN mais n'y est jamais annoté : le modèle a appris à le laisser de côté. Le
dictionnaire le retrouve grâce à la règle des sigles définis (« forme longue (SIGLE) », DIC-v2), qui lui donne le
type de « combined oral contraceptives ». Les sigles définis dans le texte (COCs, DVP, PCC, MCAO) sont la première
source de mentions manquées : c'est là que les deux méthodes se complètent le mieux.

## 4. Manquée : symptôme décrit en langage d'expérimentation (PMID 3088349)

> « …amphetamine has an irreversible effect on the post-lesion DA pool contributing to **contralateral rotation**. »

- Référence : `contralateral rotation` <Disease> (6 fois dans VALIDATION)
- APP-v3 : rien
- Dictionnaire : rien

Chez le rat, une rotation du côté opposé à la lésion est un comportement anormal, annoté comme Disease. L'expression
n'apparaît jamais dans TRAIN et ne contient aucun mot qui ressemble à une maladie. Comme pour le cas 1, les
annotations de Disease couvrent des effets décrits par des mots ordinaires, que ni le dictionnaire ni le modèle
ne savent reconnaître sans les avoir vus.

## 5. Parasite dû à une annotation irrégulière : « antidepressant » (PMID 8800187 et 7 autres)

> « Hypotension is a major contributor to mortality in tricyclic **antidepressant** overdose… »

- Référence : rien (aucune des 15 occurrences de VALIDATION n'est annotée)
- APP-v3 : `antidepressant` <Chemical> (11 parasites)
- Dictionnaire : rien

Dans TRAIN, « antidepressant » est annoté Chemical à **chacune** de ses 15 occurrences ; dans VALIDATION, à
**aucune**. Le modèle applique ce qu'il a appris : l'erreur vient de l'annotation, pas du modèle. Ce cas, comme
« insulin » (7 parasites, jamais annoté), montre la limite du score strict : une part des faux positifs sont des
noms de produits plausibles que le corpus n'annote pas de façon régulière.

## Complémentarité avec le dictionnaire

Mentions correctes trouvées par APP-v3 seul : 2 216 ; par le dictionnaire seul : 231 (*hepatitis B*, *COCs*,
*cytotoxicity*, *serotonin*, *angiotensin*, *seizures*…) ; rappel de l'union : 0,944 (APP-v3 seul : 0,920).
L'écart entre les deux méthodes s'est creusé depuis APP-v1 (621 mentions trouvées par le dictionnaire seul), mais
les deux erreurs les plus typées (cas 2 et 3) restent mieux traitées par le dictionnaire.
