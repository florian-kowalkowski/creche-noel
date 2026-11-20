# -*- coding: utf-8 -*-
"""Étape 8 - schéma électrique de l'éclairage LED (5 V par module micro-USB).

Produit, à côté de ce script :
  08-schema-electrique.pdf : 1 page A4 paysage
  08-schema-electrique.svg : la même page

Les LED sont en parallèle, chacune avec sa résistance. Pour changer le nombre de LED ou les valeurs,
modifier GROUPS ci-dessous. Aucune dépendance : python generer_schema_electrique.py
"""
import os

from generer_plan_socle import BLACK, BLUE, RED, Canvas, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
ORANGE = (0.9, 0.48, 0.05)
PLUS = (0.6, RED, None)
MINUS = (0.6, BLACK, None)
PART = (0.5, BLACK, None)
BAND = (0.25, BLUE, (2.5, 1.5))

# (zone, détail, nombre de LED, couleur de LED, résistance)
GROUPS = [
    ("Fenêtres de la maison", "trou Ø 14 sous la maison", 2, "blanche", 150),
    ("Abri", "trou Ø 14 au pied de la paroi", 4, "blanche", 150),
    ("Feu de bois", "trou Ø 8 dans la cour", 3, "orange", 220),
]

X_PLUS, X_RES, X_LED, X_MINUS = 70, 88, 150, 226
BAND_L, BAND_R = 125, 190


def dot(cv, x, y, col):
    cv.poly([(x + 0.5 * dx, y + 0.5 * dy) for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1))], (1.3, col, None), True)


def led(cv, x, y, col):
    cv.poly([(x, y - 3), (x, y + 3), (x + 6, y)], (0.5, col, None), True)
    cv.poly([(x + 6, y - 3), (x + 6, y + 3)], (0.6, col, None))
    for k in (0, 2.4):
        cv.poly([(x + 2 + k, y - 3.6), (x + 4.5 + k, y - 6.1)], (0.3, col, None))
        cv.poly([(x + 3.3 + k, y - 6.1), (x + 4.5 + k, y - 6.1), (x + 4.5 + k, y - 4.9)], (0.3, col, None))


def page():
    cv = Canvas(297, 210)
    cv.text(14, 13, "Crèche en liège - étape 8 : schéma électrique de l'éclairage", 5.5, bold=True)

    # module micro-USB
    cv.poly([(14, 22), (50, 22), (50, 42), (14, 42)], PART, True)
    cv.text(32, 30, "Module micro-USB", 2.9, bold=True, anchor="middle")
    cv.text(32, 35, "sortie 5 V", 2.7, anchor="middle")
    cv.text(48.5, 29, "-", 3, anchor="end")
    cv.text(48.5, 37.3, "+", 3, anchor="end")

    # fil -, par le haut jusqu'au rail de droite
    cv.poly([(50, 28), (X_MINUS, 28)], MINUS)
    # fil + avec interrupteur facultatif
    cv.poly([(50, 36), (55, 36)], PLUS)
    cv.poly([(55, 36), (63, 32.5)], PLUS)
    cv.poly([(63.5, 36), (X_PLUS, 36)], PLUS)
    dot(cv, 55, 36, RED)
    cv.text(59, 46, "interrupteur", 2.4, BLUE, anchor="middle")
    cv.text(59, 49.2, "(facultatif)", 2.4, BLUE, anchor="middle")

    # bandes
    cv.text((X_PLUS + BAND_L) / 2 + 6, 41, "dans le caisson", 2.6, BLUE, anchor="middle")
    cv.text((BAND_L + BAND_R) / 2, 41, "dans le décor", 2.6, BLUE, anchor="middle")
    cv.text((BAND_R + X_MINUS) / 2, 41, "caisson", 2.6, BLUE, anchor="middle")

    y, first, last = 54, None, None
    for zone, detail, n, colour, ohms in GROUPS:
        col = ORANGE if colour == "orange" else BLACK
        y0 = y
        for i in range(n):
            first = first or y
            last = y
            dot(cv, X_PLUS, y, RED)
            cv.poly([(X_PLUS, y), (X_RES, y)], PLUS)
            cv.poly([(X_RES, y - 2.2), (X_RES + 16, y - 2.2), (X_RES + 16, y + 2.2), (X_RES, y + 2.2)], PART, True)
            cv.text(X_RES + 8, y - 3.4, "%d ohms" % ohms, 2.4, anchor="middle")
            cv.poly([(X_RES + 16, y), (X_LED, y)], PLUS)
            led(cv, X_LED, y, col)
            cv.text(X_LED + 9, y + 3.6, colour, 2.4, col)
            cv.poly([(X_LED + 6, y), (X_MINUS, y)], MINUS)
            dot(cv, X_MINUS, y, BLACK)
            y += 12
        y1 = y - 12
        cv.poly([(231, y0 - 3), (233, y0 - 3), (233, y1 + 3), (231, y1 + 3)], (0.3, BLUE, None))
        mid = (y0 + y1) / 2
        cv.text(236, mid - 0.5, zone, 2.9, bold=True)
        cv.text(236, mid + 3.8, "%d LED %s%s, %s" % (n, colour, "s" if n > 1 else "", detail), 2.4)
        y += 6
    bottom = last + 6

    cv.poly([(X_PLUS, 36), (X_PLUS, last)], PLUS)
    cv.poly([(X_MINUS, 28), (X_MINUS, last)], MINUS)
    for x in (BAND_L, BAND_R):
        cv.poly([(x, 44), (x, bottom)], BAND)
    cv.text(BAND_L, bottom + 3.5, "trou du plateau", 2.3, BLUE, anchor="middle")
    cv.text(BAND_R, bottom + 3.5, "même trou", 2.3, BLUE, anchor="middle")
    cv.text(X_PLUS - 2, 60, "+5 V", 2.6, RED, anchor="end")
    cv.text(X_MINUS + 2, 33, "0 V", 2.6)

    lines = [
        ("À RETENIR", True),
        ("Fil rouge : + 5 V. Fil noir : 0 V. Toutes les LED sont en parallèle, chacune avec SA résistance : jamais une LED sans résistance.", False),
        ("LED : la patte longue va au + (côté résistance), le côté plat du boîtier au -. Une LED qui ne s'allume pas est presque toujours à l'envers.", False),
        ("Résistances pour environ 15 mA : 150 ohms pour les LED blanches ou bleues, 220 ohms pour les orange, rouges, ambre ou jaunes. Trop fort : 330 ohms.", False),
        ("Les deux fils de chaque LED passent par le même trou. Résistances et soudures restent dans le caisson, sous gaine thermorétractable.", False),
        ("Essayer chaque LED avec sa résistance avant de la cacher. Total environ 140 mA : n'importe quel port USB suffit. La pompe garde son propre port.", False),
    ]
    yy = max(bottom + 12, 178)
    for s, bold in lines:
        cv.text(14, yy, s, 3.1 if bold else 2.75, bold=bold)
        yy += 4.6
    return cv


if __name__ == "__main__":
    p = page()
    write_pdf(os.path.join(HERE, "08-schema-electrique.pdf"), [p])
    with open(os.path.join(HERE, "08-schema-electrique.svg"), "w", encoding="utf-8") as f:
        f.write(p.svg())
    print("ok")
