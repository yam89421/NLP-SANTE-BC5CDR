# Premier contrôle QA — 3 documents et 5 questions annotées

AMARA Yanis, TOMAS Alban · Jalon E (09/10/2026)

**Usage** : « Cet outil aide les patients traités par chimiothérapie et leurs proches à retrouver les effets indésirables possibles et leur prise en charge dans les documents d'information de l'Institut national du cancer. »

## Documents

| ID | Titre | Version | Accès |
|---|---|---|---|
| DOC001 | [Comprendre la chimiothérapie (guide patients, réf. GUICHIM11)](https://cancer.fr/content/download/7202/file/Comprendre_la_chimiotherapie_mel_20181015.pdf?version=8) | 2011-09 (PDF mis en ligne le 2018-10-15) | Licence ouverte INCa : réutilisation avec mention de la source et de la date |
| DOC002 | [Cancers et soins de support (fiche Cancer info)](https://www.cancer.fr/Media/documents/publications/fsoinsup25_cancers-et-soins-de-support) | 2024-11 | Licence ouverte INCa : réutilisation avec mention de la source et de la date |
| DOC003 | [Les effets indésirables généraux de la chimiothérapie (page web)](https://www.cancer.fr/personnes-malades/parcours-de-soins/principaux-traitements/chimiotherapie/chimiotherapie-quels-effets-indesirables-possibles/effets-indesirables-generaux) | 2019-04-28 | Licence ouverte INCa : réutilisation avec mention de la source et de la date |

Texte sélectionnable vérifié pour les trois documents (récupérés le 07/10/2026). Le découpage en passages ci-dessous est provisoire : seuls les passages cités comme preuves sont découpés ; le découpage complet sera fait pour le jalon QA1.

## Questions

### Q001 — Quand la chute des cheveux commence-t-elle après une chimiothérapie, et quand les cheveux repoussent-ils ?

- **Référence** : Elle commence en général 15 jours à 3 semaines après la première perfusion ; les cheveux recommencent à pousser environ 6 à 8 semaines après la fin du traitement.
- **Éléments attendus → preuves** :
  - début 15 jours à 3 semaines après la première perfusion → DOC001_P02
  - repousse environ 6 à 8 semaines après la fin du traitement → DOC001_P02
- **DOC001_P02** (DOC001, 6. Les effets secondaires d'une chimiothérapie > Une chute des cheveux, p. 48-49) : « La chute des cheveux est fréquente, souvent progressive, mais toujours temporaire. Elle commence en général 15 jours à 3 semaines après la première perfusion. Les cheveux recommencent à pousser environ 6 à 8 semaines après la fin du traitement. Même si les cheveux repoussent plus fins ou différents au début (quelquefois, ils repoussent bouclés alors qu’ils étaient raides, et inversement), ils retrouvent petit-à-petit leur aspect initial. »

### Q002 — Combien de temps durent en général les nausées et les vomissements après une séance de chimiothérapie ?

- **Référence** : Les nausées durent rarement plus de 72 heures après le traitement et les vomissements ne persistent en général pas plus de 48 heures ; au-delà, il est conseillé d'en parler à son médecin.
- **Éléments attendus → preuves** :
  - nausées : rarement plus de 72 heures après le traitement → DOC001_P01
  - vomissements : en général pas plus de 48 heures après le traitement → DOC001_P01
- **DOC001_P01** (DOC001, 6. Les effets secondaires d'une chimiothérapie > Des nausées et des vomissements, p. 42-43) : « Les nausées commencent souvent le soir ou le lendemain de la perfusion. Elles apparaissent quelques minutes après la chimiothérapie ou plusieurs jours après. La personne se sent alors barbouillée, mais cela dure rarement plus de 72 heures après le traitement. Les nausées ne sont pas systématiquement accompagnées de vomissements. Lorsque des vomissements surviennent, il est conseillé de se rincer la bouche avec de l’eau froide et d’attendre 1 à 2 heures avant de manger. Les vomissements ne persistent en général pas plus de 48 heures après le traitement. Si l’un ou l’autre de ces effets secondaires dure plus longtemps, il est conseillé d’en parler à son médecin. »

### Q003 — Que faire si l'on perd ou prend rapidement du poids pendant une chimiothérapie, et l'accompagnement diététique proposé fait-il partie des soins de support remboursés ?

- **Référence** : Il faut informer son médecin en cas de perte ou de prise rapide de deux kilos ou plus ; il peut orienter vers une diététicienne. L'accompagnement diététique et nutritionnel fait partie des neuf soins de support remboursés totalement ou partiellement par l'Assurance maladie.
- **Éléments attendus → preuves** :
  - informer le médecin en cas de perte ou de prise rapide de deux kilos ou plus → DOC003_P01
  - orientation possible vers une diététicienne → DOC003_P01
  - accompagnement diététique et nutritionnel inclus dans les neuf soins de support remboursés totalement ou partiellement → DOC002_P01
- **DOC003_P01** (DOC003, Les perturbations du poids) : « Cependant, certaines personnes traitées par chimiothérapie prennent du poids. Les médicaments de chimiothérapie ne sont pas eux-mêmes responsables de cette prise de poids. Il est possible que le stress et le ralentissement de l’activité physique provoqués par la chimiothérapie y contribuent. Il est conseillé de suivre régulièrement son poids et d’informer son médecin si le patient perd ou prend rapidement deux kilos ou plus. Le médecin peut orienter la personne vers une diététicienne dont le rôle est de l’aider à trouver un équilibre alimentaire, avant, pendant et après la chimiothérapie. Pendant le traitement de chimiothérapie, il est possible de manger comme d’habitude et ce que l’on souhaite en privilégiant toutefois une alimentation équilibrée. »
- **DOC002_P01** (DOC002, Les soins oncologiques de support, qu'est-ce que c'est ? > Le panier de soins de support, p. 3-4) : « Au total, neuf soins de support sont considérés comme indispensables et font l’objet d’un remboursement total ou partiel par l’Assurance maladie. Ils composent ce que l’on appelle le « panier de soins de support », validé au niveau national. Ainsi, les soins listés ci-dessous doivent vous être proposés, si besoin, lors de votre parcours de soins : • la gestion de la douleur, qu’elle soit la conséquence des traitements ou de la maladie elle-même ; • un accompagnement concernant l’alimentation (diététique et nutritionnel) ; • un accompagnement psychologique ; • un accompagnement social, familial et professionnel (suivi auprès d’un assistant de service social, aide au retour à l’emploi…) ; • l’aide à la pratique d’une activité physique adaptée pendant et/ou après les traitements ; • le soutien à la mise en œuvre de la préservation de la fertilité ; • la gestion des troubles de la sexualité ; • des conseils d’hygiène de vie (aide à l’arrêt du tabac, à la réduction de la consommation d’alcool, à l’arrêt de produits addictifs…) ; • le soutien psychologique des proches et des aidants. »

### Q004 — Après un cancer, jusqu'à quand et dans quelle limite les bilans et consultations de soins de support peuvent-ils être prescrits ?

- **Référence** : Pour les personnes en ALD, ils peuvent être prescrits jusqu'à 12 mois après la fin du traitement, dans la limite de 180 euros par an et de six consultations au maximum.
- **Éléments attendus → preuves** :
  - jusqu'à 12 mois après la fin du traitement → DOC002_P02
  - montant maximal de 180 euros par an → DOC002_P02
  - six consultations au maximum → DOC002_P02
- **DOC002_P02** (DOC002, Comment bénéficier des soins de support ? > Prescription médicale des soins de support après cancer, p. 6-7) : « Depuis décembre 2020, un ensemble de bilans et de consultations peut vous être prescrit si vous bénéficiez d’une affection de longue durée (ALD) dans le cadre de votre parcours de soins global après le traitement d’un cancer. Ce parcours comprend : • un bilan fonctionnel et motivationnel d’activité physique adapté (APA), pouvant donner lieu à l’élaboration d’un projet d’APA ; • un bilan nutritionnel ; • un bilan psychologique ; • des consultations de suivi nutritionnel et/ou psychologique dédiées. Au maximum, six consultations peuvent être prescrites. Le contenu du parcours peut ne comprendre qu’une partie de ces actions. Il est individualisé pour chaque personne, en fonction des besoins identifiés par le médecin prescripteur. Ces bilans et consultations peuvent être prescrits par votre médecin traitant, votre cancérologue ou le pédiatre jusqu’à 12 mois après la fin du traitement dans la limite d’un montant maximal de 180 euros par an. Ils sont réalisés par des professionnels conventionnés ou des salariés de la structure coordinatrice (diététiciens, psychologues, enseignants en activité physique adaptée). Dans le cadre de ce parcours, le tarif maximal spécifique est de 45 euros pour un bilan d’une heure. Il s’élève à 22,50 euros pour une consultation de suivi diététique ou psychologique d’une demi-heure. »

### Q005 — Comment dépiste-t-on un déficit en enzyme DPD avant une chimiothérapie à base de 5-fluorouracile ?

- **Sans réponse dans le corpus.**
- **Justification** : DOC003 signale seulement que le 5-FU et la capécitabine peuvent causer des effets graves chez les patients qui éliminent mal ces médicaments, et renvoie vers une fiche externe au corpus. Aucun des trois documents ne décrit le test de dépistage du déficit en DPD.

## Couverture des contraintes du livret (section 3.3)

- 4 questions répondables, 1 sans réponse (Q005).
- 1 question nécessitant deux passages complémentaires de deux documents (Q003 : DOC003 + DOC002).
- Questions avec nombres (Q001, Q002, Q004) et négations dans les preuves (« ne sont pas systématiquement accompagnées », « ne persistent en général pas plus de 48 heures »).
- Relecture croisée par le second membre du binôme : à faire, désaccords à consigner dans le guide de rédaction.
