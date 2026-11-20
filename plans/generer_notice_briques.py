# -*- coding: utf-8 -*-
"""Notice des parements en briques d'argile (mur sous l'auvent, mur du haut de l'escalier).

Produit, à côté de ce script : 10-briques-argile-notice.pdf (1 page A4 portrait).
Les cotes viennent de ../impression3d/generer_pieces_3d.py (BRICK_*, CLAY_SHRINK).
"""
import os

from generer_notice_tuiles import CLAY, P3, block, dim_h, dim_v, f
from generer_plan_socle import BLUE, Canvas, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))


def bricks(cv, x0, y0, w, h, k, niche=None):
    """Dessine un parement en briques vu de face (y vers le bas sur la page)."""
    cv.poly([(x0, y0), (x0 + w * k, y0), (x0 + w * k, y0 + h * k), (x0, y0 + h * k)], CLAY, True)
    L, H, J = P3.BRICK_L, P3.BRICK_H, P3.MORTAR
    row, y = 0, 0.0
    while y + H < h:
        yy = y0 + h * k - (y + H + J / 2) * k
        cv.poly([(x0, yy), (x0 + w * k, yy)], (0.15, CLAY[1], None))
        y += H + J
        row += 1
    row, y = 0, 0.0
    while y < h:
        x = -(L + J) / 2 if row % 2 else 0.0
        while x < w:
            xx = x + L + J / 2
            if 0 < xx < w:
                cv.poly([(x0 + xx * k, y0 + h * k - y * k), (x0 + xx * k, y0 + h * k - min(y + H, h) * k)], (0.15, CLAY[1], None))
            x += L + J
        y += H + J
        row += 1
    if niche:
        nx0, ny0, nx1, ny1 = niche
        cv.poly([(x0 + nx0 * k, y0 + (h - ny0) * k), (x0 + nx1 * k, y0 + (h - ny0) * k),
                 (x0 + nx1 * k, y0 + (h - ny1) * k), (x0 + nx0 * k, y0 + (h - ny1) * k)], (0.5, BLUE, None), True)


def page():
    cv = Canvas(210, 297)
    cv.text(14, 14, "Crèche en liège - murs en briques d'argile", 5.2, bold=True)
    cv.text(14, 20, "Deux parements moulés : sous l'auvent de la maison, et en haut de l'escalier.", 3)
    s = P3.CLAY_SHRINK

    cv.text(14, 32, "Mur sous l'auvent (remplace la pièce H) - dessin réduit", 3.4, bold=True)
    k = 1.2
    bricks(cv, 20, 38, 92, 40, k, niche=(39, 17, 49, 34))
    dim_h(cv, 20, 20 + 92 * k, 38 + 40 * k + 4, "92 mm")
    dim_v(cv, 20 + 92 * k + 4, 38, 38 + 40 * k, "40 mm")
    cv.text(20 + 44 * k, 38 + (40 - 36) * k, "niche", 2.5, BLUE, anchor="middle")
    block(cv, 14, 104, None, [
        "Moule : moule-briques-auvent.stl (100 × 46 mm).",
        "Niche de la clochette : X 39 à 49, Y 17 à 34 depuis le coin bas gauche, vu de face.",
        "Se colle sur la façade A, sur le repère c (X 4 à 96, Y 60 à 100), sous l'auvent.",
    ], 2.8, 4.4)

    cv.text(14, 128, "Mur du haut de l'escalier (sur la pièce S)", 3.4, bold=True)
    k2 = 0.45
    bricks(cv, 150, 30, 64, 195, k2)
    cv.text(150 + 32 * k2, 30 + 195 * k2 + 5, "mur de l'escalier, 64 × 195 mm", 2.6, anchor="middle")
    block(cv, 14, 134, None, [
        "Moule : moule-briques-escalier.stl (71 × 206 mm, tient sur le plateau de la K1C).",
        "Se colle sur la face avant du mur S (64 × 195), côté escalier.",
        "Panneau long et fin : le démouler en entier, puis le couper en 2 ou 3",
        "le long d'un joint horizontal au cutter : plus facile à manipuler et à coller.",
    ], 2.8, 4.4)

    y = block(cv, 14, 162, "Fabrication", [
        "1. Saupoudrer le moule de talc ou de maïzena et chasser l'excès au pinceau.",
        "2. Presser l'argile dans le moule du bout des doigts, en remplissant bien les angles.",
        "3. Araser au ras des bords en tirant une règle à plat : le parement fait %s mm." % f(P3.BRICK_T),
        "4. Laisser raffermir 1 à 2 heures, jusqu'au stade « cuir ».",
        "5. Poser une planchette sur le moule, retourner l'ensemble et tapoter : le parement tombe,",
        "    face briques en haut. Le repère en V du bord indique le haut du mur.",
        "6. Sécher 24 à 48 h à plat, sous une feuille de papier et une planchette légère pour éviter",
        "    qu'il ne gondole. Loin d'un radiateur.",
    ], 2.8, 4.4)
    y = block(cv, 14, y, "Finition et pose", [
        "Fond rouge brique, puis un jus beige ou gris clair passé partout et essuyé : il reste dans",
        "les joints et dessine le mortier. Quelques briques plus sombres ou plus orangées au pinceau.",
        "Durcir au vernis mat ou à la colle vinylique diluée, puis coller à la néoprène ou à la colle à bois.",
    ], 2.8, 4.4)
    block(cv, 14, y, "À savoir", [
        "Le moule est inversé gauche-droite : c'est normal, le parement se retourne au démoulage.",
        "Moule et parement sont agrandis de %d %% pour le retrait de l'argile (CLAY_SHRINK)." % round((s - 1) * 100),
        "Argile : environ 15 g pour le mur de l'auvent, 50 g pour celui de l'escalier.",
        "Si le parement fissure : démouler plus tôt, sécher plus lentement, reboucher à la barbotine.",
    ], 2.8, 4.4)
    return cv


if __name__ == "__main__":
    write_pdf(os.path.join(HERE, "10-briques-argile-notice.pdf"), [page()])
    with open(os.path.join(HERE, "10-briques-argile-apercu.svg"), "w", encoding="utf-8") as fh:
        fh.write(page().svg())
    print("ok")
