# -*- coding: utf-8 -*-
"""Étape 6 - le pont arqué.

Produit, à côté de ce script :
  06-pont-plans-A4.pdf : 2 pages A4 portrait, toutes deux à l'échelle 1
  06-pont-apercu.svg   : la première page seule

Cotes en millimètres. Portée 105, largeur 37, flèche 13,5.
Aucune dépendance : python generer_plan_pont.py
"""
import math
import os

from generer_plan_maison import dim_h, draw, part
from generer_plan_socle import BLUE, CUT, THIN, TRACE, Canvas, circle, rect, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 210, 297

R, HALF = 110.0, 0.5                 # rayon du dessus des longerons, demi-angle
R_IN = 100.0                         # rayon du dessous
FOOT = 4.0                           # talon vertical à chaque extrémité
SPAN = 2 * R * math.sin(HALF)        # 105,5
WIDTH, PLANK, T_PLANK = 37, 10, 3
Y0 = FOOT - R * math.cos(HALF)       # décalage vertical de l'arc
POSTS = [-0.47, -0.16, 0.16, 0.47]   # angles des poteaux de rambarde
RAILS = [12.5, 23.0]                 # hauteur des lisses au-dessus des planches


def top(th, dy=0.0):
    return (R * math.sin(th), R * math.cos(th) + Y0 + dy)


def stringer():
    xin = math.sqrt(R_IN ** 2 - (R * math.cos(HALF) - FOOT) ** 2)
    ain = math.asin(xin / R_IN)
    pts = [(-SPAN / 2, 0)] + [top(-HALF + i * 2 * HALF / 40) for i in range(41)] + [(SPAN / 2, 0), (xin, 0)]
    pts += [(R_IN * math.sin(a), R_IN * math.cos(a) - (R * math.cos(HALF) - FOOT)) for a in [ain - i * 2 * ain / 30 for i in range(31)]]
    return pts


STRINGER = stringer()


def under_y(x):
    y = math.sqrt(max(R_IN ** 2 - x ** 2, 0)) - (R * math.cos(HALF) - FOOT)
    return max(0.0, y)


def elevation(cv, ox, oy):
    """Vue de côté à l'échelle 1 ; (ox, oy) = milieu du pont au niveau du sol."""
    T = lambda x, y: (ox + x, oy - y)
    cv.poly([T(*p) for p in STRINGER], CUT, True)
    for i in range(10):
        th = -HALF + (i + 0.5) * 0.1
        c, s = math.cos(th), math.sin(th)
        cx, cy = top(th, 0)
        pts = [(cx + dx * c + dy * s, cy - dx * s + dy * c) for dx, dy in ((-5, 0), (5, 0), (5, T_PLANK), (-5, T_PLANK))]
        cv.poly([T(*p) for p in pts], THIN, True)
    for th in POSTS:
        x, y = top(th, T_PLANK)
        cv.poly([T(*p) for p in rect(x - 1.5, under_y(x), x + 1.5, y + 25)], CUT, True)
    for h in RAILS:
        cv.poly([T(*top(-0.52 + i * 1.04 / 40, T_PLANK + h)) for i in range(41)], TRACE)
    cv.poly([T(-70, 0), T(70, 0)], THIN)


def plan_view(cv, ox, oy):
    """Vue de dessus à l'échelle 1 ; (ox, oy) = coin arrière gauche du tablier."""
    T = lambda x, y: (ox + SPAN / 2 + x, oy + y)
    cv.poly([T(*p) for p in rect(-SPAN / 2, 0, SPAN / 2, WIDTH)], CUT, True)
    for i in range(1, 10):
        x = R * math.sin(-HALF + i * 0.1)
        cv.poly([T(x, 0), T(x, WIDTH)], THIN)
    for y in (0, WIDTH - 5):
        cv.poly([T(*p) for p in rect(-SPAN / 2, y, SPAN / 2, y + 5)], TRACE, True)
    for th in POSTS:
        for y in (-1.5, WIDTH + 1.5):
            cv.poly([T(*p) for p in circle((R * math.sin(th), y), 1.5, 16)], CUT, True)


def block(cv, x, y, title, lines):
    cv.text(x, y, title, 3.1, bold=True)
    y += 5.2
    for s in lines:
        cv.text(x, y, s, 2.7)
        y += 4.4
    return y + 3.5


def page1():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Crèche en liège - étape 6 : le pont", 5.5, bold=True)
    cv.text(14, 20, "Les deux vues ci-dessous sont à l'échelle 1 : on peut assembler le pont directement dessus.", 3)

    cv.text(14, 32, "VUE DE CÔTÉ", 3, bold=True)
    elevation(cv, 80, 82)
    dim_h(cv, 80 - SPAN / 2, 80 + SPAN / 2, 88, "105")
    cv.text(140, 44, "tireté bleu : les deux lisses.", 2.6, BLUE)
    cv.text(140, 48.4, "Cintrer les baguettes sur", 2.6, BLUE)
    cv.text(140, 52.8, "ce tracé avant de coller.", 2.6, BLUE)
    cv.text(140, 62, "8 poteaux Ø 3", 2.6, BLUE)
    cv.text(140, 70, "10 planches Z", 2.6, BLUE)
    cv.text(140, 78, "longeron Y", 2.6, BLUE)

    cv.text(14, 104, "VUE DE DESSUS", 3, bold=True)
    plan_view(cv, 80 - SPAN / 2, 112)
    cv.text(140, 120, "tireté bleu : les deux longerons,", 2.6, BLUE)
    cv.text(140, 124.4, "au ras des bouts de planches.", 2.6, BLUE)
    cv.text(140, 133, "ronds : poteaux, collés contre", 2.6, BLUE)
    cv.text(140, 137.4, "le chant extérieur.", 2.6, BLUE)
    cv.text(80 - SPAN / 2 - 3, 112 + WIDTH / 2 + 1, "37", 2.8, anchor="end")

    y = block(cv, 14, 166, "PIÈCES", [
        "Y  2 longerons arqués, contreplaqué 5 mm, 105 × 18 (gabarit page suivante)",
        "Z  10 planches de 37 × 10 mm : bâtonnets de glace de 10 mm de large recoupés,",
        "    ou bandes de contreplaqué 3 mm",
        "8 poteaux : pique à brochette en bambou Ø 3 mm, longueur 38 mm",
        "4 lisses : pique à brochette Ø 2,5 à 3 mm, longueur 115 mm",
    ])
    y = block(cv, 14, y, "MONTAGE", [
        "1. Poser les deux longerons debout, à 37 mm hors tout (27 mm entre eux).",
        "    Les caler avec deux chutes le temps du collage.",
        "2. Coller les planches en partant du milieu, avec 1 mm de jour entre elles.",
        "3. Coller les 8 poteaux contre le chant extérieur des longerons, bien verticaux,",
        "    le pied au niveau du dessous du longeron. Les deux du milieu dépassent plus haut.",
        "4. Tremper les lisses 10 minutes dans l'eau chaude, les cintrer sur le tracé bleu",
        "    de la vue de côté, laisser sécher sous un poids, puis les coller sur les poteaux.",
        "5. Recouper les têtes de poteaux à 2 mm au-dessus de la lisse haute.",
        "6. Teinter au brou de noix dilué, puis brosser un peu de blanc à sec.",
    ])
    block(cv, 14, y, "SUR LE SOCLE", [
        "Le pont enjambe la rivière sur le rectangle bleu marqué PONT du plan du socle.",
        "Ne le coller qu'une fois le bac de rivière en place : ses talons reposent sur les berges.",
    ])
    return cv


def page2():
    cv = Canvas(PW, PH)
    cv.text(14, 10, "Pont - gabarits - échelle 1", 4, bold=True)
    shifted = [(x + SPAN / 2, y) for x, y in STRINGER]
    marks = []
    for i in range(11):
        th = -HALF + i * 0.1
        x, y = top(th)
        marks.append([(x + SPAN / 2, y), (x + SPAN / 2 - 2.5 * math.sin(th), y - 2.5 * math.cos(th))])
    for n in range(2):
        Y = part("Y - LONGERON (contreplaqué 5 mm, × 2)", ["petits traits : limites des planches"], shifted, (SPAN / 2, -6), traces=marks)
        draw(cv, Y, 14, 22 + n * 40)
    Z = part("Z", [], rect(0, 0, PLANK, WIDTH), (5, 17))
    for i in range(10):
        draw(cv, Z, 14 + i * 13, 108)
    cv.text(14, 151, "Z - PLANCHE, 37 × 10 (× 10)", 2.8)
    cv.poly(rect(14, 164, 52, 167), CUT, True)
    cv.text(56, 166.6, "Poteau : Ø 3, longueur 38 (× 8)", 2.8)
    cv.poly(rect(14, 176, 129, 178.5), CUT, True)
    cv.text(133, 178.4, "Lisse : Ø 2,5, longueur 115 (× 4)", 2.8)
    cv.poly([(14, 290), (114, 290)], CUT)
    for x in (14, 64, 114):
        cv.poly([(x, 288.5), (x, 291.5)], THIN)
    cv.text(118, 291, "Contrôle : 100 mm. Imprimer à 100 %, sans ajustement.", 2.8)
    return cv


if __name__ == "__main__":
    p1 = page1()
    write_pdf(os.path.join(HERE, "06-pont-plans-A4.pdf"), [p1, page2()])
    with open(os.path.join(HERE, "06-pont-apercu.svg"), "w", encoding="utf-8") as f:
        f.write(p1.svg())
    print("ok, portée %.1f" % SPAN)
