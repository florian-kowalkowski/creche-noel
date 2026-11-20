# -*- coding: utf-8 -*-
"""Notice de fabrication des tuiles canal en argile autodurcissante.

Produit, à côté de ce script :
  09-tuiles-argile-notice.pdf : 2 pages A4 portrait
  09-tuiles-argile-apercu.svg : la première page
Les cotes viennent de ../impression3d/generer_pieces_3d.py (TILE_*, CLAY_*) : relancer ce script si on les change.
Dépendances : celles de generer_pieces_3d.py (manifold3d, numpy), seulement pour lire les cotes.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "impression3d"))
import generer_pieces_3d as P3  # noqa: E402
from generer_plan_socle import BLACK, BLUE, CUT, RED, THIN, TRACE, Canvas, write_pdf  # noqa: E402

PW, PH = 210, 297
CLAY = (0.6, (0.72, 0.36, 0.2), None)


def f(v):
    return ("%g" % round(v, 1)).replace(".", ",")


def block(cv, x, y, title, lines, size=2.85, step=4.5, width=None):
    if title:
        cv.text(x, y, title, 3.4, bold=True)
        y += 5.6
    for s in lines:
        bold = s.startswith("!")
        cv.text(x, y, s.lstrip("!"), size, bold=bold)
        y += step
    return y + 3


def dim_h(cv, x0, x1, y, s):
    cv.poly([(x0, y), (x1, y)], THIN)
    for x in (x0, x1):
        cv.poly([(x, y - 1.2), (x, y + 1.2)], THIN)
    cv.text((x0 + x1) / 2, y + 3.6, s, 2.6, anchor="middle")


def dim_v(cv, x, y0, y1, s, right=True):
    cv.poly([(x, y0), (x, y1)], THIN)
    for y in (y0, y1):
        cv.poly([(x - 1.2, y), (x + 1.2, y)], THIN)
    cv.text(x + (2 if right else -2), (y0 + y1) / 2 + 1, s, 2.6, anchor="start" if right else "end")


def half_ring(cx, cy, r_out, r_in, up=True, n=24):
    s = -1 if up else 1
    outer = [(cx + r_out * math.cos(math.pi * i / n), cy + s * r_out * math.sin(math.pi * i / n)) for i in range(n + 1)]
    inner = [(cx + r_in * math.cos(math.pi * i / n), cy + s * r_in * math.sin(math.pi * i / n)) for i in range(n, -1, -1)]
    return outer + inner


def page1():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Crèche en liège - tuiles canal en argile autodurcissante", 5.2, bold=True)
    cv.text(14, 20, "Fabrication par fournées de 4 tuiles avec le moule imprimé en 3D.", 3)

    r1, r2, L = P3._tile_inner()
    t = P3.CLAY_T
    w1, w2 = math.pi * (r1 + t / 2), math.pi * (r2 + t / 2)
    slant = math.hypot(L, r1 - r2)

    # --- la tuile finie, vue de côté et de face (échelle 3)
    k = 3.0
    cv.text(14, 32, "La tuile finie (après séchage), dessin agrandi 3 fois", 3.4, bold=True)
    ox, oy = 20, 62
    R1, R2, LL = P3.TILE_D_BIG / 2, P3.TILE_D_SMALL / 2, P3.TILE_LEN
    cv.poly([(ox, oy), (ox + LL * k, oy), (ox + LL * k, oy - R2 * k), (ox, oy - R1 * k)], CLAY, True)
    cv.poly([(ox, oy - (R1 - t) * k), (ox + LL * k, oy - (R2 - t) * k)], TRACE)
    dim_h(cv, ox, ox + LL * k, oy + 4, "%s mm" % f(LL))
    dim_v(cv, ox - 4, oy - R1 * k, oy, "%s (Ø %s)" % (f(R1), f(2 * R1)), right=False)
    dim_v(cv, ox + LL * k + 4, oy - R2 * k, oy, "%s (Ø %s)" % (f(R2), f(2 * R2)))
    cv.text(ox + LL * k / 2, oy - R1 * k - 3, "vue de côté", 2.6, BLUE, anchor="middle")
    fx = 130
    cv.poly(half_ring(fx, oy, R1 * k, (R1 - t) * k), CLAY, True)
    cv.text(fx, oy - R1 * k - 3, "vue du gros bout", 2.6, BLUE, anchor="middle")
    dim_h(cv, fx - R1 * k, fx + R1 * k, oy + 4, "%s mm" % f(2 * R1))
    cv.text(fx + R1 * k + 3, oy - 2, "épaisseur %s" % f(t), 2.6)

    # --- le flan (échelle 3)
    cv.text(14, 82, "Le flan découpé à l'emporte-pièce (argile fraîche), agrandi 3 fois", 3.4, bold=True)
    fx0, fy0 = 60, 92
    pts = [(fx0 - w1 / 2 * k, fy0), (fx0 + w1 / 2 * k, fy0), (fx0 + w2 / 2 * k, fy0 + slant * k), (fx0 - w2 / 2 * k, fy0 + slant * k)]
    cv.poly(pts, CLAY, True)
    cv.text(fx0, fy0 + slant * k / 2 + 1, "flan", 3, (0.72, 0.36, 0.2), True, "middle")
    dim_h(cv, pts[0][0], pts[1][0], fy0 - 5, "%s mm (gros bout)" % f(w1))
    dim_h(cv, pts[3][0], pts[2][0], fy0 + slant * k + 3, "%s mm (petit bout)" % f(w2))
    dim_v(cv, fx0 + w1 / 2 * k + 6, fy0, fy0 + slant * k, "%s mm" % f(slant))
    block(cv, 118, 96, None, [
        "Un peu plus grand que la tuile finie :",
        "le moule et l'emporte-pièce compensent",
        "le retrait de l'argile au séchage (%d %%)." % round((P3.CLAY_SHRINK - 1) * 100),
        "",
        "Pas d'emporte-pièce ? Tracer ce trapèze",
        "sur un carton et découper au cutter",
        "autour du gabarit.",
    ], 2.7, 4.2)

    # --- matériel et étapes
    y = block(cv, 14, 172, "Matériel", [
        "Imprimé en PLA : moule-4-tuiles (idéalement 2 exemplaires), emporte-pièce-tuile, réglettes-1,5mm.",
        "Argile autodurcissante terre cuite (100 g suffisent pour 40 tuiles, chutes comprises), un rouleau,",
        "talc ou maïzena, un pinceau sec, une éponge ou une vieille brosse à dents, un cutter.",
    ])
    block(cv, 14, y, "Une fournée de 4 tuiles", [
        "1. Saupoudrer le moule de talc ou de maïzena, et chasser l'excès au pinceau sec.",
        "2. Poser la boule d'argile entre les deux réglettes et étaler au rouleau, appuyé sur les réglettes :",
        "    la feuille fait 1,5 mm partout.",
        "3. Découper 4 flans à l'emporte-pièce (tranchant vers l'argile, rebord vers le haut).",
        "4. Poser chaque flan sur un demi-cône, le grand côté sur le gros bout du cône.",
        "    Le petit trait gravé sur la semelle repère le côté du gros bout.",
        "5. Appuyer du bout des doigts pour que le flan épouse le cône. Lisser au doigt mouillé.",
        "6. Texture terre cuite : tapoter à l'éponge ou à la brosse à dents.",
        "7. Laisser raffermir 1 à 3 heures (stade « cuir » : ferme mais encore souple).",
        "8. Démouler en faisant glisser chaque tuile vers le petit bout du cône.",
        "9. Laisser finir de sécher 24 h, posée sans appuyer, puis ébavurer au papier de verre fin.",
    ])
    return cv


def page2():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Tuiles canal en argile - séchage, pose et finition", 5.2, bold=True)

    y = block(cv, 14, 26, "Combien en faire", [
        "Environ 40 tuiles : 2 rangées pour l'auvent de la maison, 2 ou 3 pour le toit de l'abri.",
        "Soit une dizaine de fournées. Prévoir quelques tuiles de plus pour la casse.",
    ])

    # --- schéma de pose en coupe
    cv.text(14, y + 2, "Pose en coupe : tuiles de courant et tuiles de couvert", 3.4, bold=True)
    k, base = 2.6, y + 40
    R1, t = P3.TILE_D_BIG / 2, P3.CLAY_T
    pitch = 2 * R1 + 1.5
    x0 = 22
    ncour = 4
    drop = math.sqrt((R1 - t) ** 2 - (pitch / 2 - (R1 - t)) ** 2)   # le couvert repose sur les bords des courants
    cv.poly([(x0 - 6, base + 1.5), (x0 + ncour * pitch * k + 6, base + 1.5)], (0.5, (0.45, 0.3, 0.15), None))
    for i in range(ncour):
        cx = x0 + i * pitch * k + R1 * k
        cv.poly(half_ring(cx, base - R1 * k, R1 * k, (R1 - t) * k, up=False), CLAY, True)
        if i < ncour - 1:
            cv.poly(half_ring(cx + pitch * k / 2, base - R1 * k + drop * k, R1 * k, (R1 - t) * k, up=True), CLAY, True)
    cv.text(x0 + ncour / 2 * pitch * k, base + 6.5, "support (toit en bois ou écorce)", 2.6, BLUE, anchor="middle")
    lx = x0 + ncour * pitch * k + 12
    cv.text(lx, base - R1 * k * 1.8, "couvert : bosse vers le haut,", 2.7)
    cv.text(lx, base - R1 * k * 1.8 + 4, "à cheval sur deux courants", 2.7)
    cv.text(lx, base - R1 * k * 0.5, "courant : creux vers le haut,", 2.7)
    cv.text(lx, base - R1 * k * 0.5 + 4, "côte à côte", 2.7)

    y = block(cv, 14, base + 16, "Pose", [
        "1. Durcir les tuiles sèches : vernis mat, ou colle vinylique diluée moitié eau. Laisser sécher.",
        "2. Coller une rangée de tuiles de courant, creux vers le haut, gros bout vers le bas de la pente.",
        "3. Coller les tuiles de couvert par-dessus, bosse vers le haut, à cheval sur deux courants.",
        "4. Rangée suivante : chaque tuile recouvre la précédente d'environ 6 mm, en remontant la pente.",
        "5. Les tuiles du bas dépassent de 2 à 3 mm du bord du toit. Un peu de travers, c'est plus vrai.",
        "Colle : néoprène ou pistolet à colle, en petits points pour ne pas déborder.",
    ])
    y = block(cv, 14, y, "Finition", [
        "Lavis brun très dilué passé partout puis essuyé : il reste dans les creux.",
        "Quelques tuiles plus claires ou plus rouges, une touche de vert (mousse) dans les joints.",
        "Brossage à sec beige clair sur les bosses pour l'aspect patiné.",
    ])
    block(cv, 14, y, "Si ça ne va pas", [
        "!Les tuiles fissurent au séchage :",
        "    démouler plus tôt ; sécher lentement, à l'écart d'un radiateur ; lisser au doigt mouillé.",
        "!L'argile colle au moule :",
        "    plus de talc ou de maïzena, ou une goutte d'huile essuyée au chiffon.",
        "!Les tuiles sortent trop petites ou trop grandes une fois sèches :",
        "    noter l'écart et changer CLAY_SHRINK dans generer_pieces_3d.py, puis réimprimer.",
        "!Les flans se déchirent sur le cône :",
        "    argile trop sèche : la pétrir avec un peu d'eau, et garder la réserve sous film plastique.",
    ])
    return cv


if __name__ == "__main__":
    p1 = page1()
    write_pdf(os.path.join(HERE, "09-tuiles-argile-notice.pdf"), [p1, page2()])
    with open(os.path.join(HERE, "09-tuiles-argile-apercu.svg"), "w", encoding="utf-8") as fh:
        fh.write(p1.svg())
    print("ok")
