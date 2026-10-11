# Guide d'annotation de la négation

AMARA Yanis, TOMAS Alban · Projet NLP en santé · version 1 du 07/10/2026

## Tâche

Pour chaque phrase, une **mention cible** est donnée avec ses positions. Il faut répondre à une seule question :
**le texte nie-t-il explicitement la présence de ce que la mention nomme ?**

| Label | Quand l'attribuer |
|---|---|
| `nie` | Le texte affirme que la mention est **absente** : « no headache », « neither nausea nor vomiting », « hepatitis was ruled out », « ischemia was absent ». |
| `non_nie` | Tous les autres cas : mention affirmée, **incertaine**, hypothétique, conditionnelle, ou concernée par une négation qui porte sur autre chose. |

« Non nié » ne veut pas dire « confirmé » : une hypothèse est `non_nie`.

## Règles de décision

1. **Repérer l'indice de négation** : « no », « not », « without », « neither… nor », « denies », « negative for »,
   « absence of », « no evidence of », « was ruled out », « was excluded », « absent »…
2. **Vérifier sa portée** :
   - l'indice peut précéder la mention (« no fever ») ou la suivre (« fever was absent ») ;
   - une coordination prolonge la portée (« no rash, jaundice **or** edema » : les trois sont niées) ;
   - « but », « however », « although » ou une nouvelle proposition (« **and** mild hypertension **was noted** ») la ferment.
3. **Écarter les faux amis**, qui donnent `non_nie` :
   - « cannot be excluded », « could not be ruled out », « did not exclude » : incertitude ;
   - « no doubt », « not only … but also » : renforcement ;
   - « no increase in seizures », « no change in pain » : c'est la variation qui est niée, pas la mention ;
   - « if neuropathy appears », « possible pneumonia » : hypothèse ou condition.
4. **Ne juger que la mention cible.** Une autre mention de la même phrase peut avoir un autre label.
5. **Ne pas tenir compte** du sujet (patient ou proche) ni de la temporalité : seule la négation est annotée.

## Procédure

1. Chaque membre remplit **seul** la colonne `label` de sa feuille (`annotation_AMARA.csv` ou
   `annotation_TOMAS.csv`), sans regarder la feuille de l'autre ni le label proposé, avec `nie` ou `non_nie`,
   et une courte justification.
2. Le notebook `2.5_negation.ipynb` compte les désaccords et calcule l'accord (proportion et kappa de Cohen).
3. Les désaccords sont discutés ensemble ; la décision et sa raison sont notées dans
   `desaccords_annotation.csv` (colonnes `label_final` et `resolution`).
4. Le label final devient la référence. Une règle de ce guide modifiée après discussion est datée ici.

## Exemples (hors du jeu de 20 phrases)

| Phrase | Mention | Label | Raison |
|---|---|---|---|
| No fever nor chills, but a persistent cough. | chills | `nie` | « nor » prolonge la portée de « No » |
| No fever nor chills, but a persistent cough. | cough | `non_nie` | « but » ferme la portée |
| Headache absent. | Headache | `nie` | indice placé après la mention |
| An embolism cannot be excluded. | embolism | `non_nie` | incertitude |
| He presents not only a fever but also a cough. | fever | `non_nie` | renforcement |
