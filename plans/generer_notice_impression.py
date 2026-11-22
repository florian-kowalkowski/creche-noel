# -*- coding: utf-8 -*-
"""Étape 7 - notice des pièces imprimées en 3D : schéma en coupe du circuit d'eau et réglages.

Produit, à côté de ce script :
  07-impression-3d-notice.pdf : 2 pages A4 portrait
  07-circuit-eau-apercu.svg   : la première page seule
Les fichiers STL eux-mêmes sont produits par ../impression3d/generer_pieces_3d.py
"""
import math
import os

from generer_plan_socle import BLACK, BLUE, CUT, RED, THIN, TRACE, Canvas, rect, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 210, 297
WATER = (0.6, BLUE, None)
WOOD = (0.3, (0.55, 0.4, 0.2), None)


def block(cv, x, y, title, lines, size=2.7, step=4.4):
    cv.text(x, y, title, 3.1, bold=True)
    y += 5.2
    for s in lines:
        cv.text(x, y, s, size)
        y += step
    return y + 3.5


def page1():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Crèche en liège - étape 7 : le circuit d'eau", 5.5, bold=True)
    cv.text(14, 20, "Schéma en coupe le long de la rivière. Hauteurs agrandies, longueurs raccourcies : ne rien mesurer dessus.", 3)

    T = lambda u, z: (18 + u * 0.7, 92 - z * 1.6)
    R = lambda u0, z0, u1, z1, st: cv.poly([T(*p) for p in rect(u0, z0, u1, z1)], st, True)
    L = lambda pts, st: cv.poly([T(*p) for p in pts], st)

    # bois : fond, plateau, façade de la maison
    R(0, -55, 250, -50, WOOD)
    R(0, -10, 60, 0, WOOD)
    R(238.5, -10, 250, 0, WOOD)
    R(54, 32, 57, 44, WOOD)
    cv.text(T(4, 0)[0], T(0, -6.5)[1], "plateau 20 mm", 2.4, WOOD[1])
    cv.text(T(4, 0)[0], T(0, -54)[1] - 3.2, "fond 5 mm", 2.4, WOOD[1])
    cv.text(T(59, 0)[0], T(0, 37)[1], "façade", 2.4, WOOD[1])

    # 1 seuil de cascade
    cv.poly([T(*p) for p in [(22, 0), (63, 0), (63, 3), (66, 6), (69, 6), (69, 27), (22, 27)]], CUT, True)   # bloc
    # tuyau : il traverse tout le seuil dans un fourreau courbe et ressort par la bouche
    for rr, u0, z0, u1 in ((18.5, 29.5, -30, 200), (11.5, 36.5, -26, 204)):
        bend = [(48 - rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a))) for a in range(0, 91, 10)]
        L([(u1, -34), (u1, z0), (u0, z0)] + bend + [(71, rr)], (0.5, RED, None))
    L([(71.5, 15), (75, 12), (77.5, 4), (78.5, -3.6)], WATER)
    # 2 bac de rivière
    cv.poly([T(*p) for p in [(60.5, 0), (60.5, -9), (176, -9), (176, -4), (174, -4), (174, -7), (150, -7), (62.5, -5.5), (62.5, 0)]], CUT, True)
    cv.poly([T(100, 6.6), T(174, 6.6)], TRACE)
    L([(62.5, -3.6), (175, -3.6), (176.6, -5.4), (181, -5.4), (183, -9)], WATER)
    # 3 bassin de reprise
    cv.poly([T(*p) for p in [(176.2, -5.6), (176.2, -7.6), (181, -7.6), (181, -18), (214, -18), (214, -9), (217, -9), (217, -16), (183, -16), (183, -5.6)]], CUT, True)
    cv.poly([T(*p) for p in [(223, -9), (226, -9), (226, -18), (238, -18), (238, 0), (236, 0), (236, -16), (223, -16)]], CUT, True)
    L([(183, -9), (214, -9)], WATER)
    L([(226, -9), (236, -9)], WATER)
    L([(220, -9), (220, -22)], WATER)
    # 4 réservoir et pompe
    cv.poly([T(*p) for p in [(150, -11), (150, -50), (246, -50), (246, -11), (243.6, -11), (243.6, -47.6), (152.4, -47.6), (152.4, -11)]], CUT, True)
    L([(152.4, -22), (243.6, -22)], WATER)
    R(186, -47.6, 222, -34, TRACE)
    cv.text(T(204, 0)[0], T(0, -42)[1], "pompe", 2.4, BLUE, anchor="middle")

    for u, z, s in [(40, 31, "1 seuil"), (118, 3, "2 bac de rivière"), (198, 4, "3 bassin"), (165, -38, "4 réservoir")]:
        cv.text(T(u, 0)[0], T(0, z)[1], s, 2.8, BLACK, True, "middle")
    cv.text(T(80, 0)[0], T(0, 5)[1], "jet : chute de 19 mm", 2.4, BLUE)
    cv.text(T(100, 0)[0], T(0, -12.5)[1], "lit en pente, 2 à 3 mm d'eau", 2.4, BLUE)
    cv.text(T(104, 0)[0], T(0, 9)[1], "berges : 5 mm au-dessus de la collerette", 2.4, BLUE)
    cv.text(T(176, 0)[0], T(0, -12)[1], "chute", 2.4, BLUE, anchor="end")
    cv.text(T(222, 0)[0], T(0, -2)[1], "trop-plein", 2.4, BLUE, anchor="middle")
    cv.text(T(100, 0)[0], T(0, -33)[1], "tuyau souple, sous le plateau", 2.4, RED)

    y = block(cv, 14, 196, "COMMENT ÇA MARCHE", [
        "La pompe, au fond du réservoir, pousse l'eau dans le tuyau jusqu'au seuil, à l'intérieur de la maison.",
        "Le tuyau traverse tout le seuil dans un fourreau courbe et sort par sa bouche, sous l'arche de la façade :",
        "    aucun raccord, donc aucune fuite cachée. L'eau en sort et retombe 19 mm plus bas dans la rivière.",
        "Le lit descend de 1,5 mm vers l'aval. Au bout, un déversoir de 28 mm de large garde 3 mm d'eau",
        "pompe arrêtée. Des berges de 5 mm, imprimées avec le bac, retiennent l'eau en marche.",
        "L'eau tombe du déversoir sur la lèvre du bassin, puis dans le bassin, 5 mm plus bas : c'est la chute.",
        "Elle retombe au réservoir par le trop-plein, un tube de 15 mm qui avale le débit sans faire monter l'eau.",
        "Le bassin n'est pas collé : on le soulève pour atteindre la pompe et pour remettre de l'eau.",
    ])
    block(cv, 14, y, "À SAVOIR", [
        "Pompe : uniquement une mini pompe immergée en basse tension (USB 5 V), à débit réglable.",
        "    Pompe retenue : 38 × 37 × 28 mm, embout de 8,4 mm sur le dessus. La coucher sur le flanc dans",
        "    la partie gauche du réservoir, ventouses contre la paroi, embout vers la droite, grille dégagée.",
        "    Jamais de pompe en 230 V dans un caisson en bois.",
        "Tuyau : silicone 8 × 10 mm ; le fourreau du seuil fait 11,5 mm, courbe de 18 mm de rayon. Si le vôtre",
        "    est différent, changer TUBE_BORE et BEND_R en tête du script generer_pieces_3d.py et le relancer.",
        "Eau : environ 350 mL en tout. Compléter chaque semaine ; l'eau déminéralisée évite le calcaire.",
        "Le socle doit être de niveau, sinon la rivière se vide d'un côté.",
    ])
    return cv


def page2():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Pièces à imprimer - Creality K1C", 5.5, bold=True)
    cv.text(14, 20, "Dossier impression3d. Chaque fichier STL est déjà orienté pour l'impression.", 3)
    rows = [
        ("Fichier", "Taille (mm)", "Matière", "Supports", True),
        ("bac-riviere.stl", "83 × 145 × 17", "PETG", "oui, sous la collerette", False),
        ("bassin-reprise.stl", "69 × 65 × 20", "PETG", "oui, sous la collerette et la lèvre", False),
        ("reservoir.stl", "115 × 75 × 54", "PETG", "non", False),
        ("seuil-cascade.stl", "38 × 38 × 28", "PETG ou PLA", "non", False),
        ("rochers.stl (16 rochers)", "157 × 133 × 16", "PLA", "non", False),
        ("pelle.stl", "18 × 118 × 3", "PLA", "non", False),
        ("tuiles-auvent.stl", "100 × 10 × 36", "PLA", "non, bordure de 5 mm", False),
        ("tuiles-abri-avant.stl", "77 × 11 × 46", "PLA", "non, bordure de 5 mm", False),
        ("tuiles-abri-arriere.stl", "68 × 11 × 30", "PLA", "non, bordure de 5 mm", False),
    ]
    y = 32
    for a, b, c, d, bold in rows:
        for x, s in ((14, a), (72, b), (108, c), (128, d)):
            cv.text(x, y, s, 2.8, bold=bold)
        cv.poly([(14, y + 1.8), (196, y + 1.8)], THIN)
        y += 6
    cv.text(14, y + 1, "apercu-assemblage.stl montre les 4 pièces du circuit d'eau à leur place : à regarder, pas à imprimer.", 2.6)

    y = block(cv, 14, y + 12, "RÉGLAGES", [
        "Circuit d'eau (PETG) : couches de 0,2 mm, 4 parois, 5 couches pleines dessus et dessous,",
        "    remplissage 25 %. Supports arborescents, sur le plateau uniquement.",
        "Décor (PLA) : couches de 0,2 mm, 2 parois, remplissage 10 %.",
        "Tuiles : elles s'impriment debout, sur la tranche ondulée. Ajouter une bordure de 5 mm pour",
        "    qu'elles ne se décollent pas. PLA terre cuite, ou peinture acrylique ensuite.",
        "Pelle : à plat, dos sur le plateau. Peinture argent sur la lame, brou de noix sur le manche.",
        "Rochers : teinte liège clair ou gris ; ils se collent à plat sur les berges et les collerettes.",
    ])
    y = block(cv, 14, y, "ÉTANCHÉITÉ", [
        "Une pièce imprimée n'est pas étanche d'office. Passer 2 couches fines de résine époxy",
        "    transparente à l'intérieur du bac, du bassin, du réservoir. Le conduit du seuil n'en a pas besoin.",
        "Essai avant montage : remplir chaque pièce et la laisser 24 h sur du papier absorbant.",
    ])
    y = block(cv, 14, y, "MONTAGE", [
        "1. Présenter le bac dans l'évidement du plateau. S'il force, limer le bois, pas le bac.",
        "2. Poser le réservoir sur le fond du caisson, à l'emplacement rouge du plan du socle,",
        "    avant de fermer le caisson. Y placer la pompe, tuyau et câble dans l'encoche.",
        "3. Faire sortir le câble par l'arrière du caisson, par une encoche dans la bande de liège.",
        "4. Pousser le tuyau dans le seuil par-dessous jusqu'à ce qu'il sorte par la bouche (eau savonneuse s'il",
        "    accroche), puis le passer dans le trou de 14 mm du plateau. Le couper au ras de la bouche, ou 2 mm devant.",
        "5. Coller le seuil sur le plateau, le nez au-dessus du bac. Coller le bac au silicone sous sa",
        "    collerette. Poser le bassin sans le coller.",
        "6. Coller alors la maison par-dessus le seuil, puis le pont, puis les rochers sur les collerettes.",
        "    Le rocher posé sur la collerette du bassin ne doit pas déborder sur le plateau.",
    ])
    block(cv, 14, y, "MISE EN EAU", [
        "Verser l'eau dans le bassin jusqu'à 1 cm sous le bord du réservoir, puis remplir la rivière.",
        "Démarrer la pompe au débit minimum et augmenter jusqu'à ce que le jet tombe dans le lit, sans éclabousser.",
    ])
    return cv


if __name__ == "__main__":
    p1 = page1()
    write_pdf(os.path.join(HERE, "07-impression-3d-notice.pdf"), [p1, page2()])
    with open(os.path.join(HERE, "07-circuit-eau-apercu.svg"), "w", encoding="utf-8") as f:
        f.write(p1.svg())
    print("ok")
