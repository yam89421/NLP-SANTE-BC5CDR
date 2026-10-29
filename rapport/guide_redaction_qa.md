# Guide de rédaction des questions QA

AMARA Yanis, TOMAS Alban · section 3.3 du livret · créé le 23/10/2026

Ce guide fixe les règles d'écriture des questions DEV et TEST, et consigne les désaccords de relecture
et leur résolution. Toute règle ajoutée après le début de l'annotation s'applique aussi aux questions
déjà écrites.

## 1. Questions

1. **Reformuler, ne pas recopier.** Une question évite de reprendre la formulation exacte du passage
   qui y répond (synonymes, autre construction, vocabulaire d'un patient). Sinon, la recherche lexicale
   (BM25) la retrouve trop facilement et Q0 est surévaluée.
2. Une question porte sur l'usage défini au 3.1 : effets indésirables de la chimiothérapie et leur prise
   en charge, pour un patient ou un proche. Pas de conseil médical personnalisé.
3. Les reformulations d'une même question partagent un `family_id` et restent dans le même jeu (DEV ou TEST).
4. Question à deux passages : chaque passage apporte un élément indispensable que l'autre ne contient pas.
5. **Prémisse inexacte** : une question peut contenir une erreur de l'usager (ex. Q008 demande un seuil en kilos,
   le corpus le donne en pourcentage du poids). La référence corrige la prémisse au lieu d'y répondre telle quelle ;
   une `note_annotation` le signale.
6. **Information datée** : quand un chiffre vient d'un document ancien (guide de 2011), la référence le date
   (ex. Q017, forfait perruque de 125 euros).

## 2. Références

1. **Concise et reformulée** : une à trois phrases, dans nos propres mots. Pas de copie de phrases du
   corpus, pour ne pas avantager dans BLEU/ROUGE les sorties qui recopient les passages (Q0 en particulier).
2. **Nombres, unités et négations exacts** : on reformule autour d'eux, jamais eux.
3. **Sources divergentes** : quand deux documents donnent des informations différentes, la référence
   donne chaque version avec sa source et sa date, sans trancher ; chaque version est un élément attendu.
   La question porte `sources_divergentes: true` et une `note_annotation` qui décrit la réponse attendue.
   Exemple : Q001 (repousse des cheveux, guide de 2011 et page de 2024).
4. La référence est vérifiée dans les sources avant toute lecture des réponses de l'outil évalué.

## 3. Éléments attendus et preuves

1. Un élément = une information indispensable à la réponse, formulée brièvement.
2. Chaque élément est relié à ses preuves par un **extrait verbatim** du document (`preuves_extraits`) :
   celui-ci reste exact, puisqu'il sert à localiser le passage. Les identifiants de passages sont
   recalculés à chaque découpage par le notebook 3.
3. Un passage d'un autre document donnant la même information est noté dans `equivalents_extraits` :
   il est indiqué comme équivalent mais n'entre pas dans le calcul du Rappel@5.

## 4. Questions sans réponse

1. Vérifier l'absence dans **les dix documents** (recherche des termes et de leurs synonymes), même si
   la réponse existe ailleurs.
2. La justification cite les passages proches qui ne répondent pas, et dit pourquoi.

## 5. Aide d'un LLM et relecture

Le livret autorise une aide du LLM à la formulation si elle est déclarée. Les questions Q006 à Q030 (DEV et TEST) ont été
rédigées avec l'aide de Claude (Anthropic), à partir des passages lus dans `data/passages.jsonl` ; chaque preuve
est un extrait verbatim vérifié automatiquement par le notebook 3, et chaque absence (Q018-Q020, Q029-Q030) a été recherchée
dans les dix documents. Champs : `redaction` (origine) et `statut_relecture` (`a_relire` → `relue_AMARA` /
`relue_TOMAS` → `validee`). Une question n'est utilisée pour les réglages qu'une fois relue par un membre du binôme ;
les désaccords sont reportés ci-dessous.

## 6. Désaccords de relecture et résolution

| Date | Question | Désaccord | Résolution |
|---|---|---|---|
| 23/10/2026 | Q001 | Les sources divergent sur la repousse des cheveux (6 à 8 semaines en 2011, 3 à 6 mois en 2024) ; la référence ne citait que DOC001. | Règle 2.3 : les deux délais avec leur source. |
| 23/10/2026 | Q001, Q002, Q004 | Références largement recopiées des passages (segments de 11 à 16 mots). | Règles 1.1 et 2.1 : références reformulées (segment recopié le plus long : 9 mots, chiffres compris). |
| 23/10/2026 | Q016 | Référence recopiant la liste des seuils de température (13 mots). | Reformulée (règle 2.1). |
| 28/10/2026 | Q001-Q030 | Relecture par AMARA Yanis des 30 questions (questions, références, éléments, preuves, justifications d'absence). | Aucune modification demandée ; statut `relue_AMARA`. |
