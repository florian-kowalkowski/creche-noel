# -*- coding: utf-8 -*-
"""Étape 4 - escalier en blocs empilés et mur de briques.

L'escalier est un empilement de 9 blocs rectangulaires découpés dans une planche de 15 mm :
chaque bloc est une marche, plus court que celui du dessous. Pas de limons ni de crémaillères.
Produit, à côté de ce script :
  04-escalier-gabarits-A4.pdf : 1 page A4 portrait (vues cotées, débit, montage)
  04-escalier-apercu.svg      : la même page
Aucune dépendance : python generer_plan_escalier.py
"""
import os

from generer_plan_maison import dim_h, dim_v
from generer_plan_socle import BLUE, CUT, THIN, Canvas, rect, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 210, 297

BOARD = 15.0                  # épaisseur de la planche = hauteur d'une marche
STEPS = 9
RISE = BOARD
TOP = RISE * STEPS            # 135 : niveau du palier (le dessus du dernier bloc)
DEPTH = 140.0                 # profondeur du bloc du bas, du nez de la première marche au mur du fond
LANDING = 32.0                # profondeur du palier (bloc du haut)
RUN = (DEPTH - LANDING) / (STEPS - 1)    # 13,5 : giron de chaque marche
WIDTH = 54.0                  # largeur des marches
LANDING_W = 60.0              # le palier va jusqu'au mur de la maison (6 mm de plus, côté maison)

# blocs du bas (B1) vers le haut (B9) : (nom, largeur, profondeur)
BLOCKS = [("B%d" % (k + 1), LANDING_W if k == STEPS - 1 else WIDTH, LANDING + RUN * (STEPS - 1 - k)) for k in range(STEPS)]
WALL_S = (64, 195)            # mur de briques S, contreplaqué 5 mm, derrière l'escalier


def page():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Crèche en liège - étape 4 : escalier en blocs empilés", 5.5, bold=True)
    cv.text(14, 20, "9 blocs découpés dans une planche de 15 mm, empilés et collés. Vues réduites, cotes en mm.", 3)
    k, oy = 0.6, 32

    # --- profil (x = distance depuis le nez de la première marche)
    ox = 24
    T = lambda x, y: (ox + x * k, oy + (200 - y) * k)
    Pp = lambda pts: [T(*q) for q in pts]
    for i, (name, w, d) in enumerate(BLOCKS):
        cv.poly(Pp(rect(DEPTH - d, i * RISE, DEPTH, (i + 1) * RISE)), CUT, True)
        tx, ty = T(DEPTH - d + 3, i * RISE + RISE / 2)
        cv.text(tx, ty + 1, name, 2.4, BLUE)
    cv.poly(Pp(rect(DEPTH, 0, DEPTH + 5, WALL_S[1])), THIN, True)
    cv.text(ox + 70 * k, oy + 2, "PROFIL", 3, bold=True, anchor="middle")
    x0, y0 = T(0, 0)
    dim_h(cv, x0, T(DEPTH, 0)[0], y0 + 5, "140")
    dim_v(cv, T(DEPTH + 5, 0)[0] + 6, T(0, TOP)[1], y0, "135 (palier)")
    cv.text(T(0, 0)[0], T(0, RISE * 4.6)[1], "giron 13,5", 2.5, BLUE)
    cv.text(T(0, 0)[0], T(0, RISE * 4.6)[1] + 4, "hauteur 15", 2.5, BLUE)

    # --- vue de face
    ox2 = 146
    F = lambda x, y: (ox2 + x * k, oy + (200 - y) * k)
    Fp = lambda pts: [F(*q) for q in pts]
    cv.poly(Fp(rect(-5, 0, 59, WALL_S[1])), THIN, True)
    for i, (name, w, d) in enumerate(BLOCKS):
        cv.poly(Fp(rect(0, i * RISE, w, (i + 1) * RISE)), CUT, True)
    cv.text(ox2 + 30 * k, oy + 2, "FACE", 3, bold=True, anchor="middle")
    a0, b0 = F(0, 0)
    dim_h(cv, a0, F(WIDTH, 0)[0], b0 + 5, "54")
    cv.text(F(27, 0)[0], F(0, 172)[1], "mur S, 195 de haut", 2.5, BLUE, anchor="middle")
    cv.text(F(LANDING_W, 0)[0] + 1, F(0, TOP - 4)[1], "palier 60 :", 2.4, BLUE)
    cv.text(F(LANDING_W, 0)[0] + 1, F(0, TOP - 4)[1] + 3.5, "touche la maison", 2.4, BLUE)

    y = 168
    cv.text(14, y, "DÉBIT : 9 blocs dans une planche de 15 mm", 3.2, bold=True)
    y += 6
    for i, (name, w, d) in enumerate(BLOCKS):
        col = 14 if i < 5 else 80
        cv.text(col, y + (i % 5) * 4.6, "%s : %g × %s mm%s" % (name, w, ("%g" % d).replace(".", ","),
                                                             "  (palier)" if i == STEPS - 1 else ("  (en bas)" if i == 0 else "")), 2.8)
    cv.text(146, y, "Mur S : 64 × 195,", 2.8)
    cv.text(146, y + 4.6, "contreplaqué 5 mm", 2.8)
    y += 5 * 4.6 + 6
    lines = [
        ("MONTAGE", True),
        ("1. Débiter une bande de 54 mm de large sur toute la longueur de la planche (largeur des marches).", False),
        ("    Puis recouper à la longueur de chaque bloc. Le palier B9 se coupe à part, en 60 mm de large.", False),
        ("2. Poncer les faces visibles et marquer au crayon le dos de chaque bloc : tous les dos sont alignés.", False),
        ("3. Coller B1 sur le socle, dos contre le mur du fond. Puis B2 sur B1, dos alignés, côté gauche aligné,", False),
        ("    et ainsi de suite jusqu'à B9. Serrer avec un serre-joint ou un poids pendant le séchage.", False),
        ("4. Le palier B9 dépasse de 6 mm côté maison : il vient toucher le mur, juste sous la porte.", False),
        ("5. Coller le mur S (et son parement de briques) contre le dos de l'escalier.", False),
        ("FINITION", True),
        ("Les tranches du contreplaqué se voient sur les côtés et les contremarches : les masquer avec du liège", False),
        ("en feuille de 2 mm, de l'écorce, ou de l'enduit de rebouchage peint en pierre. Dessus des marches :", False),
        ("liège en feuille ou peinture sablée. Un jus brun dans les angles des marches les vieillit.", False),
        ("PORTE", True),
        ("Le palier est à 135 mm (5 mm plus haut qu'avec l'ancien escalier) : la porte imprimée se colle avec", False),
        ("son seuil posé sur le palier, le vantail de Y 137 à 171 sur le côté C de la maison.", False),
    ]
    for s, bold in lines:
        if bold:
            y += 2
        cv.text(14, y, s, 3.1 if bold else 2.75, bold=bold)
        y += 4.4
    return cv


if __name__ == "__main__":
    p = page()
    write_pdf(os.path.join(HERE, "04-escalier-gabarits-A4.pdf"), [p])
    with open(os.path.join(HERE, "04-escalier-apercu.svg"), "w", encoding="utf-8") as fh:
        fh.write(p.svg())
    print("ok, giron %.1f" % RUN)
