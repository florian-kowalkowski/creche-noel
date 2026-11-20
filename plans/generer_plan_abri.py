# -*- coding: utf-8 -*-
"""Étape 5 - structure de l'abri (contreplaqué 5 mm), support de l'écorce de liège.

Produit, à côté de ce script :
  05-abri-plans-A4.pdf : vue d'ensemble cotée + 2 planches A4 portrait à l'échelle 1
  05-abri-apercu.svg   : la vue d'ensemble seule

Cotes en millimètres, même repère que le plan du socle (x vers la droite, y vers l'avant).
Seules les pièces à profil ont un gabarit ; les rectangles se tracent à l'équerre.
Aucune dépendance : python generer_plan_abri.py
"""
import os

from generer_plan_maison import dim_h, dim_v, draw, part
from generer_plan_socle import BLUE, CUT, THIN, TRACE, Canvas, circle, rect, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 210, 297

H_BACK = 198                                   # hauteur de la paroi du fond
BACK = (-205, 15)                              # la paroi V va de x = -205 à x = 15 (220 de large)
ROOF = (-175, -135, 20, -22)                   # emprise du toit X : 195 x 113
POST_L, POST_R = (-145, -35), (1, -56)         # poteaux, Ø 17 et Ø 12

# T : joue gauche, vue de l'intérieur de l'abri. x = distance depuis l'arrière.
T_OUT = [(0, 0), (165, 0), (165, 80), (130, 80), (130, 160), (0, 160)]
# U : joue droite (côté escalier).
U_OUT = [(0, 0), (95, 0), (95, 95), (50, 95), (50, H_BACK), (0, H_BACK)]

T = part("T - JOUE GAUCHE", ["contreplaqué 5 mm", "165 × 160"], T_OUT, (65, 90),
         traces=[rect(0, 0, 5, 160)],
         notes=[(22, 150, "ARRIÈRE"), (148, 70, "AVANT"), (36, 20, "tireté : chant de la paroi V"),
                (148, 40, "appui de la pelle")])
U = part("U - JOUE DROITE", ["contreplaqué 5 mm", "95 × 198"], U_OUT, (26, 110),
         traces=[rect(0, 0, 5, H_BACK)],
         notes=[(25, 190, "ARRIÈRE"), (78, 86, "AVANT"), (72, 50, "pilier")])
W = part("W", [], [(0, 0), (40, 0), (0, 40)], (11, 14))


def sheet(n, what):
    cv = Canvas(PW, PH)
    cv.text(14, 10, "Abri - planche %d/2 - %s - échelle 1" % (n, what), 4, bold=True)
    cv.poly([(14, 290), (114, 290)], CUT)
    for x in (14, 64, 114):
        cv.poly([(x, 288.5), (x, 291.5)], THIN)
    cv.text(118, 291, "Contrôle : 100 mm. Imprimer à 100 %, sans ajustement.", 2.8)
    return cv


def sheets():
    s1 = sheet(1, "contreplaqué 5 mm")
    draw(s1, T, 14, 20)
    for i in range(4):
        draw(s1, W, 14 + i * 44, 200)
    s1.text(14, 247, "W - ÉQUERRE DE RENFORT, 40 × 40 (× 4) : deux derrière chaque angle, entre paroi et joue.", 2.8)
    s2 = sheet(2, "contreplaqué 5 mm")
    draw(s2, U, 14, 20)
    s2.text(120, 40, "Pièces sans gabarit,", 3, bold=True)
    s2.text(120, 45, "à tracer à l'équerre :", 3, bold=True)
    s2.text(120, 53, "V - paroi du fond", 2.8)
    s2.text(120, 57.5, "    220 × 198, 5 mm", 2.8)
    s2.text(120, 65, "X - toit", 2.8)
    s2.text(120, 69.5, "    195 × 113, 5 mm", 2.8)
    s2.text(120, 77, "Poteaux : branches", 2.8)
    s2.text(120, 81.5, "    Ø 17 × 186 et Ø 12 × 188", 2.8)
    return [s1, s2]


def overview():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Crèche en liège - étape 5 : l'abri", 5.5, bold=True)
    cv.text(14, 20, "Structure en contreplaqué 5 mm, à habiller d'écorce. Vues à l'échelle 0,4.", 3)
    k = 0.4

    # --- vue de dessus
    ox, oy = 18, 40
    Tp = lambda x, y: (ox + (x + 210) * k, oy + (y + 140) * k)
    Pp = lambda pts: [Tp(*q) for q in pts]
    cv.text(ox + 44, oy - 6, "VUE DE DESSUS", 3, bold=True, anchor="middle")
    cv.poly(Pp(rect(BACK[0], -140, BACK[1], -135)), CUT, True)
    cv.poly(Pp(rect(-210, -140, -205, 25)), CUT, True)
    cv.poly(Pp(rect(15, -140, 20, -45)), CUT, True)
    cv.poly(Pp(rect(*ROOF)), TRACE, True)
    for c, r in ((POST_L, 8.5), (POST_R, 6)):
        cv.poly(Pp(circle(c, r, 24)), CUT, True)
    for x0, sx in ((-205, 1), (15, -1)):
        cv.poly(Pp([(x0, -135), (x0 + sx * 40, -135), (x0, -95)]), THIN, True)
    cv.text(Tp(-95, 0)[0], Tp(0, -128)[1], "paroi V", 2.5, BLUE, anchor="middle")
    cv.text(Tp(-200, 0)[0], Tp(0, 5)[1], "joue T", 2.5, BLUE)
    cv.text(Tp(12, 0)[0], Tp(0, -100)[1], "joue U", 2.5, BLUE, anchor="end")
    cv.text(Tp(-80, 0)[0], Tp(0, -75)[1], "toit X (tireté)", 2.5, BLUE, anchor="middle")
    cv.text(Tp(-134, 0)[0], Tp(0, -33)[1], "poteau Ø 17", 2.5, BLUE)
    cv.text(Tp(-8, 0)[0], Tp(0, -54)[1], "Ø 12", 2.5, BLUE, anchor="end")
    cv.text(Tp(-95, 0)[0], Tp(0, 20)[1], "AVANT", 2.5, anchor="middle")
    dim_h(cv, Tp(-210, 0)[0], Tp(20, 0)[0], Tp(0, 25)[1] + 6, "230 hors tout")

    # --- vue de face
    ox2, oy2 = 116, 40
    Tf = lambda x, y: (ox2 + (x + 210) * k, oy2 + (205 - y) * k)
    Pf = lambda pts: [Tf(*q) for q in pts]
    cv.text(ox2 + 44, oy2 - 6, "VUE DE FACE", 3, bold=True, anchor="middle")
    cv.poly(Pf(rect(BACK[0], 0, BACK[1], H_BACK)), THIN, True)
    cv.poly(Pf([(-210, 0), (-205, 0), (-205, 160), (-210, 160)]), CUT, True)
    cv.poly(Pf(rect(15, 0, 20, H_BACK)), CUT, True)
    cv.poly(Pf(rect(-153.5, 0, -136.5, 186)), CUT, True)
    cv.poly(Pf(rect(-5, 0, 7, 188)), CUT, True)
    cv.poly(Pf(rect(ROOF[0], 185, ROOF[2], 203)), CUT, True)
    cv.text(Tf(-80, 0)[0], Tf(0, 100)[1], "paroi V 220 × 198", 2.5, BLUE, anchor="middle")
    cv.text(Tf(-80, 0)[0], Tf(0, 208)[1], "toit X, incliné vers l'avant", 2.5, BLUE, anchor="middle")
    dim_v(cv, Tf(20, 0)[0] + 4, Tf(0, H_BACK)[1], Tf(0, 0)[1], "198")

    # --- toit vu de dessous
    ox3, oy3 = 18, 128
    Tr = lambda x, y: (ox3 + x * k, oy3 + y * k)
    cv.text(ox3 + 39, oy3 - 4, "TOIT X, VU DE DESSOUS", 3, bold=True, anchor="middle")
    cv.poly([Tr(*q) for q in rect(0, 0, 195, 113)], CUT, True)
    for (px, py), r in (((165, 100), 8.5), ((19, 79), 6)):
        cv.poly([Tr(*q) for q in circle((px, py), r, 24)], TRACE, True)
    cv.text(Tr(97, 0)[0], Tr(0, 8)[1], "ARRIÈRE (posé sur la paroi V)", 2.5, BLUE, anchor="middle")
    cv.text(Tr(150, 0)[0], Tr(0, 102)[1], "Ø 17", 2.5, BLUE, anchor="end")
    cv.text(Tr(30, 0)[0], Tr(0, 81)[1], "Ø 12", 2.5, BLUE)
    dim_h(cv, Tr(0, 0)[0], Tr(195, 0)[0], Tr(0, 113)[1] + 5, "195")
    dim_v(cv, Tr(195, 0)[0] + 4, Tr(0, 0)[1], Tr(0, 113)[1], "113")
    cv.text(18, 186, "Poteaux : Ø 17 à 30 du bord et 13 de l'avant ; Ø 12 à 19 du bord et 34 de l'avant.", 2.6)

    def block(x, y, title, lines):
        cv.text(x, y, title, 3.1, bold=True)
        y += 5.2
        for s in lines:
            cv.text(x, y, s, 2.7)
            y += 4.4
        return y + 3.5

    block(116, 128, "ÉCORCE DE LIÈGE", [
        "Écorce brute (liège vierge), vendue pour les",
        "crèches et les terrariums. Prévoir large :",
        "3 ou 4 plaques d'environ 30 × 20 cm.",
        "Elle se casse à la main ou se scie.",
        "Collage : pistolet à colle, ou colle à bois",
        "et épingles le temps du séchage.",
        "Les joints se cachent sous la mousse.",
    ])
    y = block(14, 196, "PIÈCES - contreplaqué 5 mm", [
        "T  joue gauche 165 × 160 (gabarit)        U  joue droite 95 × 198 (gabarit)",
        "V  paroi du fond 220 × 198 (rectangle)    X  toit 195 × 113 (rectangle)",
        "W  4 équerres de renfort 40 × 40 (gabarit)",
        "Poteaux : 2 branches bien sèches, Ø 17 × 186 mm et Ø 12 × 188 mm (ou tourillons).",
    ])
    block(14, y, "MONTAGE", [
        "1. Coller la paroi V entre les joues T et U, au ras de leur chant arrière. Renforcer",
        "    chaque angle avec deux équerres W, côté intérieur, en haut et en bas.",
        "2. Coller ce U sur le socle : la paroi à 5 mm du bord arrière, la joue U contre le mur",
        "    de briques de l'escalier.",
        "3. Coller les poteaux debout sur le socle, sur les ronds bleus du plan du socle.",
        "    Ils descendent jusqu'au sol : l'écorce du rebord et du pilier viendra les entourer.",
        "4. Poser le toit X à blanc : l'arrière sur la paroi V, l'avant sur les poteaux.",
        "    Recouper les poteaux si besoin, puis coller.",
        "5. Habiller d'écorce : paroi, face intérieure et dessus des joues, pilier autour du",
        "    poteau Ø 12, rebord autour du poteau Ø 17, puis le dessus du toit.",
        "    Laisser libre le milieu du toit pour les tuiles (étape impression 3D).",
    ])
    return cv


if __name__ == "__main__":
    ov = overview()
    write_pdf(os.path.join(HERE, "05-abri-plans-A4.pdf"), [ov] + sheets())
    with open(os.path.join(HERE, "05-abri-apercu.svg"), "w", encoding="utf-8") as f:
        f.write(ov.svg())
    print("ok")
