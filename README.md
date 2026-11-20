# Décor de crèche en liège

Reproduction à fabriquer à la main d'un décor de crèche vu en photo : abri en écorce, escalier, maisonnette, pont, une rivière en circuit fermé avec mini cascade, et un éclairage LED (fenêtres, abri, feu de bois). Le socle fait 46 × 32 cm pour 7 cm de haut.

Ce fichier sert de point d'entrée pour reprendre le projet plus tard.

## Contenu du dossier

| Élément | Rôle |
|---|---|
| `decor-creche-3d.html` | Maquette 3D interactive (Three.js). Vue d'ensemble stylisée, publiée sur https://claude.ai/artifact/Twbd7q9toUVPy76Lyu1K8F |
| `plans/02-socle-gabarit-A4.pdf` | Socle : vue d'ensemble + 4 feuilles A4 paysage à assembler |
| `plans/03-maison-gabarits-A4.pdf` | Maison : 4 planches, contreplaqué 3 mm |
| `plans/04-escalier-gabarits-A4.pdf` | Escalier et mur de briques : 4 planches |
| `plans/05-abri-plans-A4.pdf` | Abri : vue cotée + 2 planches, contreplaqué 5 mm |
| `plans/06-pont-plans-A4.pdf` | Pont : 2 pages |
| `plans/07-impression-3d-notice.pdf` | Schéma du circuit d'eau, réglages d'impression, montage |
| `plans/08-schema-electrique.pdf` | Schéma de branchement des LED : module micro-USB, résistances, zones |
| `plans/0X-*-cotes.pdf` | **Plans cotés, pour tracer à la règle sans imprimante papier** : chaque pièce avec ses cotes et un tableau de coordonnées depuis une origine O |
| `impression3d/gabarits/*.stl` | Gabarits de traçage de 2 mm à imprimer en 3D : évidement de la rivière, longeron du pont, crémaillère, limons |
| `plans/*.svg` | Aperçu de la première page de chaque PDF |
| `plans/generer_*.py` | Scripts qui produisent les PDF et SVG |
| `impression3d/*.stl` | Pièces à imprimer, déjà orientées |
| `impression3d/generer_pieces_3d.py` | Script qui produit les STL |

Les gabarits PDF `0X-...-A4.pdf` sont à l'échelle 1 : imprimer à 100 % et vérifier le trait de contrôle de 100 mm.

Sans imprimante papier : utiliser les plans cotés `0X-...-cotes.pdf` (à lire sur écran, sans y mesurer) et reporter les points à la règle et à l'équerre. Pour les formes longues à reporter, imprimer en 3D les gabarits de `impression3d/gabarits/` et tracer autour.

## Régénérer après une modification

Les PDF, SVG et STL sont des fichiers générés : on modifie le script, puis on le relance.

```bash
python plans/generer_plan_socle.py
python plans/generer_plan_maison.py
python plans/generer_plan_escalier.py
python plans/generer_plan_abri.py
python plans/generer_plan_pont.py
python plans/generer_notice_impression.py
python plans/generer_schema_electrique.py
python plans/generer_plans_cotes.py
python impression3d/generer_pieces_3d.py
python impression3d/generer_gabarits.py
```

- Les scripts de `plans` n'ont aucune dépendance. Ils écrivent le PDF directement, sans bibliothèque.
- `generer_pieces_3d.py` demande `pip install manifold3d numpy`.
- `generer_plan_socle.py` contient les outils communs (classe `Canvas`, `write_pdf`, styles de trait) que les autres scripts importent.

### Ce qui dépend de quoi

- Le **tracé de la rivière** (`RIVER_AXIS`, `POOL_C` dans `generer_plan_socle.py`) est lu par `generer_pieces_3d.py`. Si on le change, relancer les deux, sinon le bac imprimé ne rentre plus dans l'évidement du plateau.
- Le **contour du socle** et l'**axe de la rivière** sont recopiés à la main dans `decor-creche-3d.html` (en centimètres). La maquette ne se met pas à jour toute seule.
- Les textes de la notice (`generer_notice_impression.py`) citent des tailles de pièces en dur : les corriger si les STL changent.

## Repère et unités

- Plans et STL en millimètres ; maquette 3D en centimètres (1 unité = 10 mm).
- Repère du plan du socle : x vers la droite, y vers l'avant (le spectateur), origine au milieu.
- Dans `generer_pieces_3d.py`, Y est inversé (Y = −y du plan) pour que les pièces ne sortent pas en miroir.
- Hauteurs du circuit d'eau : 0 = dessus du plateau.

## Paramètres les plus susceptibles de changer

| Paramètre | Fichier | Valeur | À changer si |
|---|---|---|---|
| `TUBE_OD` | `impression3d/generer_pieces_3d.py` | 10 mm | On change de tuyau (actuel : silicone 8 × 10 mm) |
| `RES` | idem | 115 × 75 mm | La pompe ne rentre pas. Zone libre à gauche, hors de dessous le bassin : 51 × 70 mm. Garder `RESERVOIR` identique dans `plans/generer_plan_socle.py` |
| `CAVITY` | idem | 55 mm | La pompe et la courbe du tuyau ne tiennent pas en hauteur (51 mm libres dans le réservoir). Reporter la valeur dans les textes du plan du socle (entretoises, hauteur du caisson, chant) |
| `CLEAR` | idem | 0,4 mm | Les pièces imprimées forcent ou flottent dans le bois |
| `WEIR`, `CUP_LEVEL` | idem | −3 et −6 mm | On veut plus ou moins d'eau dans la rivière |
| `ROCKY_BED`, `PEBBLES`, `PEBBLE_MAX` | idem | oui, 340, 2,2 mm | Fond de rivière en galets : `False` pour un fond lisse (rivière et bassin), plus ou moins de galets, galets plus hauts (au-delà de 4 mm ils sortent de l'eau) |
| `CUP_PEBBLES` | idem | 110 | Plus ou moins de galets au fond du bassin de reprise (10 mm d'eau, galets jusqu'à 3 mm) |
| `FRONT`, `OUTLINE` | `plans/generer_plan_socle.py` | — | On veut une autre forme de socle |
| `W`, `D`, `EAVE`, `RIDGE` | `plans/generer_plan_maison.py` | 100, 80, 220, 265 | On change la taille de la maison |
| `RISE`, `RUN`, `STEPS` | `plans/generer_plan_escalier.py` | 13, 12, 10 | On change l'escalier (le palier doit rester à la hauteur de la porte, 130 mm) |

## Choix de conception à connaître

- **Outils** : scie sauteuse et scie à chantourner, pas de découpe laser ni de CNC. Les assemblages sont donc à plat-joint, sans queues droites.
- **Socle en caisson** de 70 mm : plateau contreplaqué 10 mm, 12 entretoises de 55 mm, fond 5 mm, chant fermé par une bande de liège. Il cache le réservoir, la pompe et le tuyau.
- **Rivière encastrée** : le bac imprimé tombe dans un évidement du plateau et tient par une collerette. Un déversoir garde 4 mm d'eau pompe arrêtée.
- **Lit de rivière et fond du bassin en galets** : le fond est relevé en galets aplatis de tailles variées avec un grain de sable entre eux, et des blocs sont pris dans les berges de la rivière. Les galets restent à distance des parois et du trop-plein, et les blocs sont rognés pour ne jamais dépasser à l'extérieur du bac, qui garde donc la même forme pour s'encastrer dans le bois. Pas de blocs dans le bassin : sa marche intérieure (3,6 mm) est trop étroite pour en porter de crédibles.
- **Bassin de reprise amovible**, non collé : c'est l'accès à la pompe.
- **Pompe couchée sur le flanc** : sa sortie est sur le dessus, et un tuyau de 10 mm ne peut pas se courber à 90° sous le plateau. On la couche donc sur le flanc, à gauche du réservoir, ventouses contre la paroi (le fabricant prévoit cette pose), embout vers la droite : le tuyau part à l'horizontale et remonte doucement vers l'encoche. C'est pour cette pompe que le caisson est passé de 55 à 70 mm et le réservoir de 95 à 115 mm de long. Couchée, elle fait 38 mm de haut : garder le réservoir rempli jusqu'à 1 cm du bord.
- **Abri** : structure en U en contreplaqué 5 mm, entièrement habillée d'écorce de liège. Les poteaux descendent jusqu'au socle.
- **Escalier** : deux crémaillères collées dans les limons portent les marches. Le limon droit est abaissé au palier pour laisser passer vers la porte.
- **Matières imprimées** : PETG pour ce qui touche l'eau, PLA pour rochers, pelle et tuiles.

## Éclairage LED (USB 5 V)

Trois passages de câble sont percés dans le plateau (`LED_HOLES` dans `plans/generer_plan_socle.py`). Les prises USB et les boîtiers de commande restent dans le caisson ; on enfile le côté LED **par en dessous**.

| Lumière | Trou | Emplacement | LED prévues |
|---|---|---|---|
| Fenêtres de la maison | Ø 14 | Sous la maison, à gauche du tuyau. Percer aussi le raidisseur G du bas à l'aplomb | 2 LED blanches, une derrière chaque fenêtre, entre les deux raidisseurs. Papier calque derrière les fenêtres |
| Abri | Ø 14 | Au pied de la paroi du fond, côté droit. Les fils montent derrière l'écorce | 3 ou 4 LED blanches collées sous le toit X, près de l'avant |
| Feu de bois | Ø 8 | Dans la cour, devant l'abri, à l'écart de la paille | 2 ou 3 LED orange, rouges ou ambre (« flicker » si possible) |

Choix retenu : LED unitaires de récupération, soudées, alimentées en 5 V par un module micro-USB à bornes placé dans le caisson. Schéma de branchement : `plans/08-schema-electrique.pdf` (généré par `plans/generer_schema_electrique.py` ; nombre de LED et résistances dans `GROUPS`).

- **Une résistance par LED**, en série sur le fil positif, toutes les LED en parallèle sur le 5 V. Jamais de LED branchée sans résistance.
- Valeurs pour 5 V et environ 15 mA : LED blanche ou bleue 120 à 150 Ω ; LED rouge, orange, ambre ou jaune 220 Ω.
- Les LED blanches de récupération sont souvent froides : un voile de vernis à ongles orange ou de peinture vitrail jaune les réchauffe.
- Câblage : deux fils communs (+ et −) sous le plateau, une dérivation par LED. Résistances et soudures dans le caisson, isolées par gaine thermorétractable, pour pouvoir y accéder.
- La pompe garde son propre port USB. Les câbles sortent par une encoche à l'arrière, dans la bande de liège.

## Ce qui n'a pas été vérifié

- Les PDF n'ont pas été affichés tels quels : seuls leurs équivalents SVG ont été contrôlés à l'écran.
- Aucune pièce n'a été tranchée ni imprimée. Les maillages sont valides et sans collision, mais les jeux et le comportement réel de l'eau restent à valider.
- L'étanchéité repose sur un vernis époxy à appliquer : faire un essai de 24 h avant montage.
- Les proportions viennent d'une seule photo ; l'arrière et les côtés sont inventés.
- La pompe et le tuyau sont achetés mais pas encore essayés dans les pièces imprimées. Pompe : GERUI, mini pompe USB 5 V, 38 × 37 × 28 mm, embout de 8,4 mm sur le dessus, 180 L/h réglable, lot de 3. Tuyau : silicone 8 × 10 mm. Cotes lues sur les fiches Amazon, pas mesurées.
- La quantité d'écorce (3 ou 4 plaques de 30 × 20 cm) est une estimation.
- Les santons n'étaient pas achetés : l'échelle du décor n'a pas été confrontée à leur taille.
- Les LED de récupération (couleur, tension exacte) et le module micro-USB n'ont pas été identifiés précisément : les résistances sont des valeurs standard à confirmer par un essai.

## Écarts connus entre la maquette 3D et les plans

La maquette est une illustration, les plans et les STL font foi. Elle ne montre pas la structure en contreplaqué sous l'écorce, ni le détail des pièces imprimées. Le poteau droit de l'abri y est droit, comme dans les plans, alors qu'il penche sur la photo. Son bouton « Nuit » simule l'ambiance des éclairages, pas l'intensité réelle des LED.

## Pistes de reprise

- Vérifier à la réception que le tuyau entre juste dans le seuil imprimé (logement de 10,4 mm).
- Adapter l'échelle aux santons si besoin.
- Donner une légère pente au fond de la rivière : la base sous les galets est plate.
- Ajouter un gabarit pour le fond du caisson et une trappe sous le réservoir.
- Exporter la maquette en GLB (non fait, écarté au départ).
