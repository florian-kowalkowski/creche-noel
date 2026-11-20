# -*- coding: utf-8 -*-
"""Étape 4 - gabarits de l'escalier et du mur de briques.

Produit, à côté de ce script :
  04-escalier-gabarits-A4.pdf : vue d'ensemble + 4 planches A4 portrait à l'échelle 1
  04-escalier-apercu.svg      : la vue d'ensemble seule

Cotes en millimètres. Escalier : 10 hauteurs de 13 mm, giron 12 mm, palier à 130 mm.
Aucune dépendance : python generer_plan_escalier.py
"""
import os

from generer_plan_maison import dim_h, dim_v, draw, part
from generer_plan_socle import BLUE, CUT, THIN, Canvas, rect, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 210, 297

RISE, RUN, STEPS = 13, 12, 10
TOP = RISE * STEPS            # 130 : niveau du palier
LAND_END = 140                # fond du palier, mesuré depuis le nez de la première marche
PARAPET = 12                  # hauteur du limon au-dessus des nez de marche

# Crémaillère (3 mm) : porte les marches. Origine = 3 mm derrière le nez de la première marche.
RACK = [(0, 0)]
for i in range(STEPS):
    RACK += [(RUN * i, 10 + RISE * i), (RUN * (i + 1) if i < STEPS - 1 else LAND_END - 3, 10 + RISE * i)]
RACK.append((LAND_END - 3, 0))
RACK_ON_WALL = [(x + 13, y) for x, y in RACK]      # sa place sur le limon (qui déborde de 10 mm à l'avant)

WALL_L = [(0, 0), (150, 0), (150, TOP + PARAPET), (118, TOP + PARAPET), (10, RISE + PARAPET), (0, 16)]
WALL_R = [(0, 0), (150, 0), (150, TOP - 3), (118, TOP - 3), (118, TOP + PARAPET), (10, RISE + PARAPET), (0, 16)]

M = part("M - LIMON GAUCHE", ["contreplaqué 5 mm", "150 × 142"], WALL_L, (105, 40), traces=[RACK_ON_WALL],
         notes=[(70, 8, "tireté : place de la crémaillère O, côté intérieur")])
N = part("N - LIMON DROIT", ["contreplaqué 5 mm", "150 × 142", "abaissé au palier :", "passage vers la porte"], WALL_R, (105, 48),
         traces=[RACK_ON_WALL], notes=[(70, 8, "tireté : place de la crémaillère O, côté intérieur")])
O = part("O - CRÉMAILLÈRE", ["contreplaqué 3 mm", "137 × 127 (× 2)"], RACK, (100, 40))
P = part("P", [], rect(0, 0, 44, 15), (22, 6))
Q = part("Q", [], rect(0, 0, 44, 10), (22, 3.5))
R = part("R - PALIER", ["3 mm, 55 × 32"], rect(0, 0, 55, 32), (27.5, 20))
S = part("S - MUR", ["contreplaqué 5 mm", "64 × 195"], rect(0, 0, 64, 195), (32, 110))


def sheet(n, what):
    cv = Canvas(PW, PH)
    cv.text(14, 10, "Escalier - planche %d/4 - %s - échelle 1" % (n, what), 4, bold=True)
    cv.poly([(14, 290), (114, 290)], CUT)
    for x in (14, 64, 114):
        cv.poly([(x, 288.5), (x, 291.5)], THIN)
    cv.text(118, 291, "Contrôle : 100 mm. Imprimer à 100 %, sans ajustement.", 2.8)
    return cv


def sheets():
    s1 = sheet(1, "contreplaqué 5 mm")
    draw(s1, M, 14, 20)
    s2 = sheet(2, "contreplaqué 5 mm")
    draw(s2, N, 14, 20)
    s3 = sheet(3, "contreplaqué 3 mm")
    draw(s3, O, 14, 18)
    draw(s3, O, 14, 153)
    s4 = sheet(4, "mur en 5 mm, marches en 3 mm")
    draw(s4, S, 14, 18)
    draw(s4, R, 14, 224)
    for i in range(STEPS - 1):
        draw(s4, P, 92, 18 + i * 18)
    s4.text(92, 184, "P - MARCHE, 44 × 15 (× 9)", 2.8)
    for i in range(STEPS):
        draw(s4, Q, 146, 18 + i * 13)
    s4.text(146, 152, "Q - CONTREMARCHE, 44 × 10 (× 10)", 2.8)
    s4.text(92, 200, "Astuce : débiter une bande de 44 mm de large,", 2.8)
    s4.text(92, 204.8, "puis la recouper tous les 15 mm et tous les 10 mm.", 2.8)
    return [s1, s2, s3, s4]


def overview():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Crèche en liège - étape 4 : escalier et mur de briques", 5.5, bold=True)
    cv.text(14, 20, "Vues d'ensemble à l'échelle 0,6. Les 4 planches suivantes sont à l'échelle 1.", 3)
    k, oy = 0.6, 36

    # --- coupe de profil (x = distance depuis l'avant du limon)
    ox = 24
    T = lambda x, y: (ox + x * k, oy + (200 - y) * k)
    Pp = lambda pts: [T(*q) for q in pts]
    cv.poly(Pp(WALL_L), THIN, True)
    for i in range(STEPS):
        u, h = 10 + RUN * i, RISE * (i + 1)
        cv.poly(Pp(rect(u, h - RISE, u + 3, h - 3)), CUT, True)
        cv.poly(Pp(rect(u, h - 3, u + 15, h) if i < STEPS - 1 else rect(u, h - 3, 150, h)), CUT, True)
    cv.poly(Pp(rect(150, 0, 155, 195)), CUT, True)
    cv.text(ox + 75 * k, oy - 2 + 60 * k, "PROFIL", 3, bold=True, anchor="middle")
    x0, y0 = T(0, 0)
    dim_h(cv, x0, T(150, 0)[0], y0 + 5, "150")
    dim_v(cv, T(155, 0)[0] + 6, T(0, TOP)[1], y0, "130 (palier)")
    dim_v(cv, T(155, 0)[0] + 30, T(0, 195)[1], y0, "195 (mur S)")
    cv.text(T(40, 0)[0], T(0, 90)[1], "limon M ou N", 2.5, BLUE, anchor="middle")
    cv.text(T(60, 0)[0], T(0, 20)[1], "marche : giron 12, hauteur 13", 2.5, BLUE)

    # --- vue de face
    ox2 = 166
    F = lambda x, y: (ox2 + x * k, oy + (200 - y) * k)
    Fp = lambda pts: [F(*q) for q in pts]
    cv.poly(Fp(rect(-5, 0, 59, 195)), THIN, True)
    cv.poly(Fp(rect(0, 0, 5, TOP + PARAPET)), CUT, True)
    cv.poly(Fp([(49, 0), (54, 0), (54, TOP - 3), (49, TOP - 3)]), CUT, True)
    for i in range(STEPS):
        cv.poly(Fp([(5, RISE * (i + 1)), (49, RISE * (i + 1))]), THIN)
    cv.poly(Fp([(49, TOP), (60, TOP)]), THIN)
    cv.text(ox2 + 27 * k, oy - 2 + 0 * k, "FACE", 3, bold=True, anchor="middle")
    a0, b0 = F(0, 0)
    dim_h(cv, a0, F(54, 0)[0], b0 + 5, "54")
    cv.text(F(27, 0)[0], F(0, 160)[1], "mur S", 2.5, BLUE, anchor="middle")
    cv.text(F(27, 0)[0], F(0, TOP + 4)[1], "palier R, vers la porte à droite", 2.5, BLUE, anchor="middle")

    y = 176
    blocks = [
        ("PIÈCES", [
            "M, N  limons gauche et droit, contreplaqué 5 mm, 150 × 142",
            "O  2 crémaillères, contreplaqué 3 mm, 137 × 127",
            "P  9 marches 44 × 15    Q  10 contremarches 44 × 10    R  palier 55 × 32  (3 mm)",
            "S  mur de briques, contreplaqué 5 mm, 64 × 195",
        ]),
        ("MONTAGE", [
            "1. Coller une crémaillère O sur la face intérieure de chaque limon, sur le tireté :",
            "    bas et arrière alignés. Attention, les deux limons se font en miroir.",
            "2. Réunir les deux limons par le palier R et la première contremarche Q,",
            "    avec 44 mm entre eux. Vérifier l'équerre et laisser sécher.",
            "3. Monter de bas en haut : une contremarche, puis la marche posée dessus.",
            "    Chaque marche passe sous la contremarche suivante.",
            "4. Coller le mur S au dos de l'escalier, centré.",
            "5. Finition : liège en feuille de 2 mm sur les marches, ou peinture sablée.",
            "    Sur le mur, graver les joints de briques au cutter avant peinture.",
        ]),
        ("SUR LE SOCLE", [
            "L'escalier se place sur le tracé bleu du plan du socle, palier contre le mur du fond,",
            "limon droit N à 6 mm du mur gauche de la maison. Le palier R comble cet espace.",
        ]),
    ]
    for title, lines in blocks:
        cv.text(14, y, title, 3.2, bold=True)
        y += 5.5
        for s in lines:
            cv.text(14, y, s, 2.9)
            y += 4.8
        y += 4
    return cv


if __name__ == "__main__":
    ov = overview()
    write_pdf(os.path.join(HERE, "04-escalier-gabarits-A4.pdf"), [ov] + sheets())
    with open(os.path.join(HERE, "04-escalier-apercu.svg"), "w", encoding="utf-8") as f:
        f.write(ov.svg())
    print("ok")
