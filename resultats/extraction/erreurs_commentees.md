# Cinq erreurs d'extraction commentées (méthode apprise, VALIDATION)

Méthode : BioBERT retenu (poids 1, 2 époques). Erreurs tirées au hasard (seed 42) parmi celles de
`tals.erreurs`, puis choisies pour couvrir des causes différentes, dans cinq documents différents.
Pour chaque cas, on indique aussi la sortie du dictionnaire (2.3).

Bilan VALIDATION : 8 208 correctes ; 631 frontières, 11 types, 741 manquées (dont 330 absentes de TRAIN),
769 parasites.

## 1. Forme inconnue : mention manquée (PMID 11195262)

> « Contribution of sodium valproate to the **syndrome of inappropriate secretion of antidiuretic hormone**. »

- Référence : `syndrome of inappropriate secretion of antidiuretic hormone` <Disease>
- BioBERT : rien. Dictionnaire : rien.

La forme n'apparaît jamais dans TRAIN. Elle est longue (7 mots) et ne contient aucun mot typique d'une maladie :
le modèle devrait prédire un `B` puis six `I` sans interruption. C'est le cas le plus difficile : mention longue
et jamais vue.

## 2. Mauvaise frontière sur une mention composite (PMID 3115150)

> « …possibly enhanced CNS, **cardiovascular, and respiratory depression**. »

- Référence : `cardiovascular, and respiratory depression` <Disease> (une seule mention)
- BioBERT : `depression` <Disease>
- Dictionnaire : `respiratory depression` <Disease>

Mention composite (deux maladies dans un même intervalle), gardée entière selon la convention du 2.2. Les deux
méthodes trouvent le cœur de la mention mais pas ses limites. Avec le score strict, l'erreur compte 1 FP + 1 FN.
La frontière est la première cause d'erreur de BioBERT (631 cas).

## 3. Mention coupée en deux mots (PMID 10524660)

> « …the messenger molecule **nitric oxide** (NO) is involved in pain mechanisms… »

- Référence : `nitric oxide` <Chemical>
- BioBERT : `nitric` <Chemical> (`oxide` a reçu `O` au lieu de `I-Chemical`)
- Dictionnaire : `nitric oxide` <Chemical> ✓ (vue 8 fois dans TRAIN, toujours annotée)

La forme est connue, mais BioBERT décide mot par mot : une seule étiquette fausse coupe la mention. Le
dictionnaire cherche la suite complète et la retrouve.

## 4. Confusion de type due au contexte (PMID 15867025)

> « …administration of the **hepatitis B** vaccine birth dose to all infants… »

- Référence : `hepatitis B` <Disease>
- BioBERT : `hepatitis B` <Chemical>
- Dictionnaire : `hepatitis B` <Disease> ✓

BioBERT tient compte du contexte : devant « vaccine » ou « immune globulin », il voit un produit administré et
prédit Chemical. Les annotateurs gardent Disease pour le nom de la maladie, même dans « hepatitis B vaccine ».
Dans ce document, la première occurrence (« screening for hepatitis B ») est correcte ; l'erreur se répète 6 fois
en contexte de vaccination, de même pour « rubella vaccine ». Le dictionnaire, qui ignore le contexte, a raison
ici. Ce type d'erreur reste rare (11 cas).

## 5. Détection parasite : classe de médicaments non annotée (PMID 9201797)

> « …although **neuroleptic**-induced catalepsy was not considered a specific test for **neuroleptic**-induced akathisia. »

- Référence : `catalepsy`, `akathisia` <Disease> seulement
- BioBERT : en plus, 3 fois `neuroleptic` <Chemical> (3 FP)
- Dictionnaire : aucune fausse détection

« neuroleptic » désigne une classe de médicaments, employée ici comme adjectif. Elle n'est pas annotée dans ce
document ni dans TRAIN. BioBERT généralise à partir de mots qui ressemblent à des médicaments : c'est ce qui lui
permet de trouver des noms inconnus, mais aussi ce qui produit ce type de fausse détection (769 parasites).

## Observation : des mots fréquents manqués par BioBERT

« toxicity » est manqué 36 fois, « oxygen » 18 fois, « sodium » et « calcium » environ 13 fois, alors que ces
mots sont fréquents dans TRAIN. Le dictionnaire les trouve : c'est une bonne part des 583 mentions trouvées
par lui seul (contre 2 616 par BioBERT seul).

Raison : l'annotation de ces mots est irrégulière. « toxicity » n'est annoté que dans 72 % de ses occurrences
dans TRAIN (78 sur 108), « oxygen » dans 86 % (12 sur 14). BioBERT apprend à hésiter sur ces mots ; le
dictionnaire les prédit toujours. Sur ces cas précis, la méthode simple fait mieux.
