# Négation — erreurs et cas difficiles

Règles `v0` (figées le 07/10/2026 à 16:40:40, avant la génération des phrases), évaluées une fois sur les
10 mentions de test. Référence **provisoire** tant que la double annotation n'est pas faite : à relire après
résolution des désaccords.

Résultat : 8 mentions correctes sur 10 ; F1 = 0,80 pour « niée » comme pour « non niée » ; moyenne des deux
F1 = 0,80. Sur 10 exemples, une erreur fait varier le F1 d'environ 0,1 : ce jeu rédigé par ses auteurs est
un test contrôlé, pas une estimation sur des dossiers réels.

## Erreurs

### NEG015 — double négation (référence : non niée ; prédit : niée)

> The normal ECG did **not** exclude **myocardial ischemia**.

« not » est reconnu comme déclencheur avant la mention, et « ischemia » est dans sa portée. Mais « not »
porte sur le verbe « exclude » : ne pas exclure une ischémie, c'est la laisser **possible**. La règle connaît
« cannot be excluded » et « not ruled out » comme pseudo-déclencheurs, mais pas la forme active
« did not exclude ». C'est le piège décrit en cours : « une règle *contient pas, donc absent* inverse ici
l'information ». Correction possible : ajouter « not exclude », « did not exclude », « does not rule out » aux
pseudo-déclencheurs ; elle ne peut pas être faite maintenant, car elle serait réglée sur le test.

### NEG019 — portée longue (référence : niée ; prédit : non niée)

> The patient did **not**, despite the high cumulative dose of doxorubicin, develop **cardiomyopathy**.

« not » est bien un déclencheur, mais 11 tokens le séparent de « cardiomyopathy », au-delà de la portée
maximale de 8 tokens. La limite de portée évite d'étendre une négation à toute la phrase ; ici, elle coupe une
négation réelle séparée de sa mention par une incise. Une portée calculée sur la syntaxe (le complément du
verbe nié) traiterait ce cas ; une portée en nombre de tokens ne le peut pas.

## Cas difficiles correctement traités

| Phrase | Mention | Pourquoi c'est difficile |
|---|---|---|
| She experienced **neither** nausea **nor** vomiting during the treatment. | vomiting | coordination : la négation doit atteindre le second élément |
| Acute hepatitis **was ruled out** by liver biopsy. | Acute hepatitis | déclencheur placé après la mention |
| There was **no increase** in seizure frequency after the dose change. | seizure | pseudo-négation : c'est la fréquence qui ne change pas, les crises existent |
| No fever was recorded, **but** the child developed a persistent cough. (dev) | persistent cough | « but » ferme la portée de « No » |
| Drug-induced lupus **cannot be excluded** at this stage. (dev) | Drug-induced lupus | incertitude, pas négation |

## Limite connue repérée sur le développement

NEG008 (« no rash, jaundice or edema, **and** mild hypertension was noted ») est correct seulement grâce à la
limite de 8 tokens : la règle ne reconnaît pas « and » suivi d'une nouvelle proposition comme fin de portée.
Une liste plus longue après « no » aurait étendu la négation à « hypertension ».
