# Fiche du corpus d'extraction

| Élément | Valeur |
|---|---|
| Nom | BioCreative V CDR (BC5CDR) |
| Version | `CDR.Corpus.v010516` (fichiers PubTator) |
| Source | https://ftp.ncbi.nlm.nih.gov/pub/lu/BC5CDR/ |
| Conditions d'utilisation | Domaine public (« United States Government Work », NCBI/NLM), citation des auteurs demandée |
| Références | Li et al., 2015 (corpus) ; Wei et al., 2015 (tâche CDR) |
| Langue, textes | Anglais ; titres et résumés PubMed |
| Catégories retenues | Chemical, Disease |
| Partitions | Officielles : TRAIN = TrainingSet, VALIDATION = DevelopmentSet, TEST = TestSet (voir 2.2) |
| Unité des positions | Caractères, base 0, `[debut, fin[`, sur `titre + " " + résumé` |
| Mentions composites | 253 au total, gardées comme une seule mention continue (voir 2.2) |
| Hors socle | Identifiants MeSH (normalisation) et relations CID ignorés |

## Effectifs

| Partition | Documents | Chemical | Disease | Total | Composites | Phrases sans mention |
|---|---|---|---|---|---|---|
| train | 500 | 5203 | 4182 | 9385 | 107 | 773 / 4580 |
| validation | 500 | 5347 | 4244 | 9591 | 89 | 787 / 4592 |
| test | 500 | 5385 | 4424 | 9809 | 57 | 837 / 4821 |

## Exemple

PMID 227508 : « [Naloxone]<Chemical> reverses the antihypertensive effect of [clonidine]<Chemical>. »
puis dans le résumé « spontaneously [hypertensive]<Disease> rats ».
