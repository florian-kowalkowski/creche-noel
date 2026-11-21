# -*- coding: utf-8 -*-
"""Plans cotés, pour tracer à la règle sans imprimante papier.

Chaque pièce est dessinée en réduction, avec ses cotes et un tableau de coordonnées :
on reporte les points au crayon depuis une origine O, à la règle et à l'équerre.
Produit, à côté de ce script, un PDF par étape :
  02-socle-cotes.pdf, 03-maison-cotes.pdf, 04-escalier-cotes.pdf, 05-abri-cotes.pdf, 06-pont-cotes.pdf
Toutes les géométries viennent des scripts generer_plan_*.py : les cotes restent justes s'ils changent.
Aucune dépendance : python generer_plans_cotes.py
"""
import math
import os

import generer_plan_abri as AB
import generer_plan_escalier as ES
import generer_plan_maison as MA
import generer_plan_pont as PO
import generer_plan_socle as SO
from generer_plan_socle import BLACK, BLUE, CUT, RED, THIN, TRACE, UNDER, Canvas, circle, rect, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 210, 297
WARN = "Dessin réduit : ne pas mesurer sur l'écran, reporter les cotes à la règle."


# ----------------------------------------------------------------------------- outils

def f(v):
    r = round(v * 2) / 2
    return ("%g" % (r + 0.0)).replace(".", ",")


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def is_rect(pts):
    return len(pts) == 4 and len({round(p[0], 3) for p in pts}) == 2 and len({round(p[1], 3) for p in pts}) == 2


def describe(pts):
    x0, y0, x1, y1 = bbox(pts)
    if is_rect(pts):
        return "X %s à %s ; Y %s à %s" % (f(x0), f(x1), f(y0), f(y1))
    if len(pts) >= 16:
        return "Ø %s, centre X %s ; Y %s" % (f(x1 - x0), f((x0 + x1) / 2), f((y0 + y1) / 2))
    if len(pts) == 2:
        if abs(y1 - y0) < 1e-6:
            return "trait à Y %s, de X %s à %s" % (f(y0), f(x0), f(x1))
        return "trait à X %s, de Y %s à %s" % (f(x0), f(y0), f(y1))
    return " ; ".join("(%s, %s)" % (f(x), f(y)) for x, y in pts)


def dim_h(cv, x0, x1, y, s):
    cv.poly([(x0, y), (x1, y)], THIN)
    for x in (x0, x1):
        cv.poly([(x, y - 1.5), (x, y + 1.5)], THIN)
    cv.text((x0 + x1) / 2, y + 3.8, s, 2.8, anchor="middle")


def dim_v(cv, x, y0, y1, s):
    cv.poly([(x, y0), (x, y1)], THIN)
    for y in (y0, y1):
        cv.poly([(x - 1.5, y), (x + 1.5, y)], THIN)
    cv.text(x - 2, (y0 + y1) / 2 + 1, s, 2.8, anchor="end")


def header(cv, title, w=PW):
    cv.text(14, 12, title, 5, bold=True)
    cv.text(14, 17.5, WARN, 2.8, RED)


def table(cv, x, y, lines, size=2.6, step=3.7, col_w=None):
    """lines : liste de (texte, gras, couleur). Renvoie le y final."""
    for s, bold, col in lines:
        cv.text(x, y, s, size, col, bold)
        y += step
    return y


def cell(cv, x, y, w, h, title, sub, outline, feats=(), notes=(), origin="coin bas gauche", draw_w=0.5):
    """Une pièce : dessin coté à gauche, tableau à droite. feats : (étiquette ou None, 'cut'|'trace', points)."""
    cv.text(x, y + 4, title, 3.8, bold=True)
    yy = y + 9
    for s in sub:
        cv.text(x, yy, s, 2.7)
        yy += 4
    top = yy + 3
    minx, miny, maxx, maxy = bbox(outline)
    W, H = maxx - minx, maxy - miny
    aw, ah = w * draw_w, y + h - top - 14
    k = min(aw / W, ah / H)
    ox, oy = x + 14, top + H * k
    P = lambda px, py: (ox + (px - minx) * k, oy - (py - miny) * k)

    rows = [("Origine O : %s." % origin, False, BLACK), ("X vers la droite, Y vers le haut, en mm.", False, BLACK)]
    tags = iter("abcdefghijk")
    feat_rows = []
    for label, kind, pts in feats:
        cv.poly([P(*q) for q in pts], CUT if kind == "cut" else TRACE, len(pts) > 2)
        if label:
            t = next(tags)
            fx0, fy0, fx1, fy1 = bbox(pts)
            px, py = P((fx0 + fx1) / 2, (fy0 + fy1) / 2)
            cv.text(px, py + 1, t, 2.6, BLUE if kind != "cut" else BLACK, True, "middle")
            feat_rows.append(("%s  %s" % (t, label), True, BLUE if kind != "cut" else BLACK))
            feat_rows.append(("    " + describe(pts), False, BLACK))
    cv.poly([P(*q) for q in outline], CUT, True)
    ax, ay = P(minx, miny)
    cv.text(ax - 2.5, ay + 2.5, "O", 2.8, RED, True, "end")

    if not is_rect(outline):
        gx = sum(p[0] for p in outline) / len(outline)
        gy = sum(p[1] for p in outline) / len(outline)
        cx, cy = P(gx, gy)
        for i, q in enumerate(outline):
            sx, sy = P(*q)
            d = math.hypot(sx - cx, sy - cy) or 1
            cv.text(sx + (sx - cx) / d * 3.2, sy + (sy - cy) / d * 3.2 + 1, str(i + 1), 2.4, RED, anchor="middle")
        rows.append(("Points du contour (n : X ; Y) :", True, RED))
        pts = ["%d : %s ; %s" % (i + 1, f(px), f(py - miny)) for i, (px, py) in enumerate([(q[0] - minx, q[1]) for q in outline])]
        half = (len(pts) + 1) // 2 if len(pts) > 12 else len(pts)
        tx = x + w * draw_w + 22
        ty = y + 9 + 7.4
        ty = table(cv, tx, ty, rows) + 0
        for j in range(half):
            cv.text(tx, ty + j * 3.5, pts[j], 2.5, RED)
            if j + half < len(pts):
                cv.text(tx + 30, ty + j * 3.5, pts[j + half], 2.5, RED)
        ty += half * 3.5 + 2
    else:
        tx = x + w * draw_w + 22
        ty = table(cv, tx, y + 9 + 7.4, rows + [("Rectangle %s × %s." % (f(W), f(H)), True, BLACK)])
    ty = table(cv, tx, ty, feat_rows)
    table(cv, tx, ty + 1, [(n, False, BLUE) for n in notes])

    dim_h(cv, ox, ox + W * k, oy + 8, f(W))
    dim_v(cv, ox - 5, oy - H * k, oy, f(H))


def list_cell(cv, x, y, title, rows):
    cv.text(x, y + 4, title, 3.8, bold=True)
    table(cv, x, y + 10, [(r, False, BLACK) for r in rows], 2.8, 4.4)


def cell_slots(cv):
    return (14, 22, 182, 132), (14, 158, 182, 132)


# ----------------------------------------------------------------------------- maison

def maison():
    p1 = Canvas(PW, PH)
    header(p1, "Maison - plans cotés (contreplaqué 3 mm)")
    s1, s2 = cell_slots(p1)
    cell(p1, *s1, "A - Façade avant", ["Vue de l'extérieur. Égout à 220, faîtage à 265."], MA.A["outline"],
         [("fenêtre haute, à découper", "cut", MA.WIN[0]), ("fenêtre basse, à découper", "cut", MA.WIN[1]),
          ("parement brique H, repère", "trace", MA.BRICK), ("dessous de l'auvent I", "trace", [(0, 103), (100, 103)])]
         + [(None, "trace", s) for s in MA.SHUTTERS],
         ["Points 2 à 5 : encoche de sortie d'eau.", "Volets J collés de chaque côté", "des fenêtres (tirets bleus)."])
    cell(p1, *s2, "B - Façade arrière", ["Même pignon que A, sans fenêtre."], MA.B["outline"],
         [("trappe d'accès (facultative)", "trace", rect(25, 0, 75, 60))])

    p2 = Canvas(PW, PH)
    header(p2, "Maison - plans cotés (suite)")
    s1, s2 = cell_slots(p2)
    cell(p2, *s1, "C - Côté gauche (et D, côté droit)", ["Vu de l'extérieur, avant à droite. D est identique, sans porte."],
         MA.C["outline"], [("porte K, repère", "trace", rect(7.5, 137, 24.5, 171))],
         ["C et D se collent entre A et B :", "leur largeur 74 = 80 - 2 × 3 mm."])
    cell(p2, *s2, "H - Parement brique", ["Collé sur la façade, sur le repère c de A."], MA.H["outline"],
         [("niche de la clochette, à découper", "cut", rect(39, 17, 49, 34))])

    p3 = Canvas(PW, PH)
    header(p3, "Maison - plans cotés (suite)")
    s1, s2 = cell_slots(p3)
    cell(p3, *s1, "L - Console d'auvent (× 2)", ["Le côté haut de 10 mm se colle sur la façade."], MA.L["outline"], draw_w=0.45)
    list_cell(p3, *s2[:2], "Pièces rectangulaires (à tracer à l'équerre)", [
        "D  côté droit : 74 × 220",
        "E  pan de toit : 85 × 100",
        "F  pan de toit : 82 × 100",
        "G  raidisseur : 74 × 94 (× 2). Celui du bas : trou Ø 14 pour le câble LED,",
        "    à percer au montage, à l'aplomb du trou du socle.",
        "I  auvent : 98 × 35",
        "J  volet : 11 × 30 (× 4)",
        "K  porte : 17 × 34",
        "Chevrons : baguette ronde Ø 6, longueur 36 (× 4)",
        "",
        "Astuce : tracer les rectangles en partant d'un bord bien droit de la plaque,",
        "et vérifier l'équerre en mesurant les deux diagonales : elles doivent être égales.",
    ])
    return [p1, p2, p3]


# ----------------------------------------------------------------------------- escalier

def escalier():
    p1 = Canvas(PW, PH)
    header(p1, "Escalier - plans cotés (blocs empilés)")
    s1, s2 = cell_slots(p1)
    rows = ["9 blocs découpés dans une planche de 15 mm (largeur x profondeur) :", ""]
    for i, (name, w, d) in enumerate(ES.BLOCKS):
        tag = "  (en bas)" if i == 0 else ("  (palier, côté maison +6)" if i == ES.STEPS - 1 else "")
        rows.append("%s : %s × %s%s" % (name, f(w), f(d), tag))
    rows += ["",
             "Chaque marche : hauteur 15 (la planche), giron %s." % f(ES.RUN),
             "Empiler B1 à B9, dos alignés contre le mur du fond, côté gauche aligné.",
             "Palier à %s : la porte se pose dessus (vantail Y 137 à 171 sur le côté C)." % f(ES.TOP)]
    list_cell(p1, *s1[:2], "Blocs de l'escalier", rows)
    list_cell(p1, *s2[:2], "Mur de briques", [
        "S  mur : %s × %s, contreplaqué 5 mm, collé contre le dos de l'escalier." % ES.WALL_S,
        "Parement : moule-briques-escalier (voir la notice des briques).",
        "",
        "Astuce : débiter d'abord une bande de 54 mm de large dans la planche,",
        "puis la recouper à la longueur de chaque bloc, à l'équerre.",
        "Poncer les tranches avant collage : elles seront visibles sur les côtés.",
    ])
    return [p1]


# ----------------------------------------------------------------------------- abri

def abri():
    p1 = Canvas(PW, PH)
    header(p1, "Abri - plans cotés (contreplaqué 5 mm)")
    s1, s2 = cell_slots(p1)
    cell(p1, *s1, "T - Joue gauche", ["Vue de l'intérieur de l'abri, arrière à gauche."], AB.T_OUT,
         [("chant de la paroi V, repère", "trace", rect(0, 0, 5, 160))], ["Le décrochement (points 3 à 5)", "reçoit la pelle."],
         origin="bas, côté arrière")
    cell(p1, *s2, "U - Joue droite", ["Côté escalier, arrière à gauche."], AB.U_OUT,
         [("chant de la paroi V, repère", "trace", rect(0, 0, 5, AB.H_BACK))], ["Partie basse (points 2 à 4) : le pilier."],
         origin="bas, côté arrière")

    p2 = Canvas(PW, PH)
    header(p2, "Abri - plans cotés (suite)")
    s1, s2 = cell_slots(p2)
    cell(p2, *s1, "W - Équerre de renfort (× 4)", ["Triangle rectangle : deux côtés de 40 à l'équerre."], AB.W["outline"], draw_w=0.4)
    list_cell(p2, *s2[:2], "Pièces rectangulaires et poteaux", [
        "V  paroi du fond : 220 × 198",
        "X  toit : 195 × 113",
        "Poteau gauche : branche Ø 17, longueur 186",
        "Poteau droit : branche Ø 12, longueur 188",
        "",
        "Le toit X se pose à blanc sur la paroi et les poteaux :",
        "recouper les poteaux à la demande avant de coller.",
        "Positions des poteaux : voir le plan coté du socle.",
    ])
    return [p1, p2]


# ----------------------------------------------------------------------------- pont

def pont():
    p = Canvas(PW, PH)
    header(p, "Pont - plans cotés")
    R, RIN, half_span = PO.R, PO.R_IN, PO.SPAN / 2
    c = R * math.cos(PO.HALF) - PO.FOOT                   # le centre des arcs est à c mm sous la base
    xin = math.sqrt(RIN ** 2 - c ** 2)
    p.text(14, 30, "Y - Longeron arqué (contreplaqué 5 mm, × 2)", 3.8, bold=True)

    k, ox, oy = 1.2, 105, 72
    T = lambda x, y: (ox + x * k, oy - y * k)
    p.poly([T(*q) for q in PO.STRINGER], CUT, True)
    p.poly([T(-half_span - 6, 0), T(half_span + 6, 0)], THIN)
    p.poly([T(0, 0), T(0, R - c + 3)], (0.2, BLUE, (2, 1)))
    dim_h(p, T(-half_span, 0)[0], T(half_span, 0)[0], oy + 5, "105,5 (base)")
    p.text(T(0, R - c)[0] + 2, T(0, R - c)[1] - 1.5, "17,5 au milieu", 2.6, BLUE)
    p.text(T(0, RIN - c)[0] + 2, T(0, RIN - c)[1] + 4, "7,5", 2.6, BLUE)
    p.text(T(-half_span, 0)[0] - 2, T(0, 2)[1], "4", 2.6, BLUE, anchor="end")
    p.text(T(-xin, 0)[0], oy + 13, "dessous à 37,9 du milieu", 2.6, BLUE, anchor="middle")

    rows = [
        ("Tracé au compas (ou avec une ficelle, un clou et un crayon) :", True, BLACK),
        ("1. Tracer la base : un trait de 105,5 mm. Marquer son milieu M.", False, BLACK),
        ("2. Depuis M, descendre à l'équerre de %s mm : c'est le centre C." % f(c), False, BLACK),
        ("    C tombe hors de la pièce : poser la planche sur une chute et y planter le clou.", False, BLACK),
        ("3. Arc de rayon 110 depuis C : le dessus. Il passe à 4 mm au-dessus de la base", False, BLACK),
        ("    aux deux bouts, et à 17,5 mm au milieu.", False, BLACK),
        ("4. Arc de rayon 100 depuis C : le dessous. Il coupe la base à 37,9 mm de chaque", False, BLACK),
        ("    côté de M, et passe à 7,5 mm au milieu.", False, BLACK),
        ("5. Fermer les bouts par deux traits verticaux de 4 mm.", False, BLACK),
        ("6. Repères de planches : tous les 11 mm le long de l'arc du dessus, en partant de M.", False, BLACK),
        ("", False, BLACK),
        ("Sans compas : reporter ces hauteurs au-dessus de la base (X depuis le bout gauche) :", True, BLACK),
    ]
    y = table(p, 14, 100, rows, 2.8, 4.4)
    xs = [-half_span] + list(range(-45, 50, 10)) + [half_span]
    p.text(14, y + 1, "X", 2.7, bold=True)
    p.text(14, y + 5.5, "dessus", 2.7, bold=True)
    p.text(14, y + 10, "dessous", 2.7, bold=True)
    for i, x in enumerate(xs):
        tx = 34 + i * 12.5
        top = math.sqrt(R ** 2 - x ** 2) - c
        bot = max(0.0, math.sqrt(max(RIN ** 2 - x ** 2, 0)) - c)
        p.text(tx, y + 1, f(x + half_span), 2.7, anchor="middle")
        p.text(tx, y + 5.5, f(top), 2.7, anchor="middle")
        p.text(tx, y + 10, f(bot), 2.7, anchor="middle")
    table(p, 14, y + 22, [
        ("Autres pièces", True, BLACK),
        ("Z  planche : 37 × 10, bâtonnet de glace ou contreplaqué 3 mm (× 10)", False, BLACK),
        ("Poteaux de rambarde : pique en bambou Ø 3, longueur 38 (× 8)", False, BLACK),
        ("Lisses : pique Ø 2,5 à 3, longueur 115 (× 4)", False, BLACK),
        ("Écartement des longerons : 37 hors tout, donc 27 entre eux.", False, BLACK),
        ("Poteaux : aux X 7, 35, 70,5 et 98,5 le long de la base, contre le chant extérieur.", False, BLACK),
        ("", False, BLACK),
        ("Gabarit à imprimer en 3D : impression3d/gabarits/gabarit-longeron-pont.stl", True, BLUE),
    ], 2.8, 4.4)
    return [p]


# ----------------------------------------------------------------------------- socle

SX, SY = -235, -145          # origine O du socle : coin arrière gauche


def so(p):
    return (p[0] - SX, p[1] - SY)


def sample(path, step):
    out, acc = [path[0]], 0.0
    for a, b in zip(path, path[1:]):
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        if acc >= step:
            out.append(b)
            acc = 0.0
    if out[-1] != path[-1]:
        if math.hypot(out[-1][0] - path[-1][0], out[-1][1] - path[-1][1]) < step * 0.4:
            out[-1] = path[-1]
        else:
            out.append(path[-1])
    return out


def socle_view(cv, box, k=None):
    """Vue de dessus du socle, arrière en haut ; renvoie la transformation (repère O)."""
    bx, by, bw, bh = box
    W, H = SO.BBOX[2] - SX, SO.BBOX[3] - SY
    k = k or min(bw / W, bh / H)
    return (lambda X, Y: (bx + X * k, by + Y * k)), k


def socle():
    pages = []
    LW, LH = 297, 210
    front = sample(SO.spline(SO.FRONT), 30)
    pts = [(-235, -145), (220, -145)] + front           # contour simplifié : les points à reporter

    # page 1 : contour
    p = Canvas(LW, LH)
    header(p, "Socle - plan coté 1/3 : contour du plateau (contreplaqué 20 mm)")
    T, k = socle_view(p, (24, 42, 165, 140))
    Q = lambda q: T(*so(q))
    p.poly([Q(q) for q in SO.OUTLINE], CUT, True)
    for i, q in enumerate(pts):
        X, Y = Q(q)
        cx, cy = T(235, 150)
        d = math.hypot(X - cx, Y - cy) or 1
        p.text(X + (X - cx) / d * 4, Y + (Y - cy) / d * 4 + 1, str(i + 1), 2.6, RED, True, "middle")
    p.text(T(0, 0)[0] - 2, T(0, 0)[1] - 1.5, "O", 3, RED, True, "end")
    dim_h(p, T(0, 0)[0], T(455, 0)[0], T(0, 0)[1] - 6, "455 (bord arrière droit)")
    p.text(T(227, 0)[0], T(0, 0)[1] - 13, "ARRIÈRE", 2.8, bold=True, anchor="middle")
    p.text(T(227, 0)[0], T(0, 315)[1] + 13, "AVANT", 2.8, bold=True, anchor="middle")
    rows = [("Origine O : coin arrière gauche.", True, BLACK),
            ("X vers la droite, Y vers l'avant, en mm.", False, BLACK),
            ("Côtés gauche et droit : droits, à l'équerre", False, BLACK),
            ("du bord arrière, jusqu'aux points %d et 3." % len(pts), False, BLACK),
            ("Avant : relier les points par une courbe", False, BLACK),
            ("régulière, avec une latte souple maintenue", False, BLACK),
            ("par des clous fins plantés sur les points.", False, BLACK),
            ("", False, BLACK),
            ("Points (n : X ; Y) :", True, RED)]
    y = table(p, 205, 30, rows, 2.7, 4)
    half = (len(pts) + 1) // 2
    for j, q in enumerate(pts):
        X, Y = so(q)
        col = 205 if j < half else 245
        p.text(col, y + (j % half) * 3.8, "%d : %s ; %s" % (j + 1, f(X), f(Y)), 2.6, RED)
    y += half * 3.8 + 4
    table(p, 205, y, [("Le fond (contreplaqué 5 mm) a le même", False, BLACK),
                      ("contour : le tracer autour du plateau", False, BLACK),
                      ("une fois celui-ci découpé.", False, BLACK)], 2.7, 4)
    pages.append(p)

    # page 2 : évidement de la rivière et perçages
    p = Canvas(LW, LH)
    header(p, "Socle - plan coté 2/3 : évidement de la rivière et perçages")
    slot = sample(SO.SLOT + [SO.SLOT[0]], 14)[:-1]
    T, k = socle_view(p, (24, 42, 165, 140))
    Q = lambda q: T(*so(q))
    p.poly([Q(q) for q in SO.OUTLINE], THIN, True)
    p.poly([Q(q) for q in SO.SLOT], CUT, True)
    for i, q in enumerate(slot):
        X, Y = Q(q)
        cx, cy = Q((128, 40))
        d = math.hypot(X - cx, Y - cy) or 1
        p.text(X + (X - cx) / d * 3.5, Y + (Y - cy) / d * 3.5 + 1, str(i + 1), 2.2, RED, anchor="middle")
    holes = [("trou du tuyau", SO.TUBE_HOLE[0], SO.TUBE_HOLE[1])] + [(n.split(" Ø")[0], c, r) for c, r, n, _, _ in SO.LED_HOLES]
    tags = "abcd"
    for t, (n, c, r) in zip(tags, holes):
        p.poly([Q(q) for q in circle(c, r, 24)], CUT, True)
        X, Y = Q(c)
        p.text(X + 3, Y + 1, t, 2.6, BLUE, True)
    p.text(T(0, 0)[0] - 2, T(0, 0)[1] - 1.5, "O", 3, RED, True, "end")
    rows = [("Origine O : coin arrière gauche ; X vers la droite, Y vers l'avant.", True, BLACK),
            ("Méthode conseillée : gabarit imprimé en 3D", True, BLUE),
            ("impression3d/gabarits/gabarit-evidement-riviere.stl : la forme exacte de", False, BLACK),
            ("l'évidement, avec 2 trous de repère Ø 3. Marquer au plateau les points", False, BLACK),
            ("R1 et R2, y piquer deux clous, enfiler le gabarit, tracer autour.", False, BLACK)]
    r1, r2 = so(SO.POOL_C), so(gabarit_ref())
    rows += [("    R1 (centre du bassin) : X %s ; Y %s" % (f(r1[0]), f(r1[1])), False, RED),
             ("    R2 (dans la rivière) : X %s ; Y %s" % (f(r2[0]), f(r2[1])), False, RED),
             ("Le rond du bassin : Ø 60 au compas, centre R1.", False, BLACK),
             ("Sans gabarit : relier les points de l'évidement (n : X ; Y) :", True, RED)]
    y = table(p, 192, 30, rows, 2.5, 3.7)
    third = (len(slot) + 2) // 3
    for j, q in enumerate(slot):
        X, Y = so(q)
        p.text(192 + (j // third) * 33, y + (j % third) * 3.4, "%d : %s ; %s" % (j + 1, f(X), f(Y)), 2.4, RED)
    y += third * 3.4 + 3
    rows = [("Perçages (centre X ; Y) :", True, BLUE)]
    for t, (n, c, r) in zip(tags, holes):
        X, Y = so(c)
        rows.append(("%s  %s : Ø %s, X %s ; Y %s" % (t, n, f(2 * r), f(X), f(Y)), False, BLACK))
    rows.append(("Percer le trou de la rivière (Ø 10) à l'intérieur du tracé pour passer la lame.", False, BLACK))
    table(p, 192, y, rows, 2.5, 3.7)
    pages.append(p)

    # page 3 : implantations et dessous
    p = Canvas(LW, LH)
    header(p, "Socle - plan coté 3/3 : emplacements à tracer au crayon, et dessous du caisson")
    T, k = socle_view(p, (24, 42, 165, 140))
    Q = lambda q: T(*so(q))
    p.poly([Q(q) for q in SO.OUTLINE], THIN, True)
    p.poly([Q(q) for q in SO.SLOT], THIN, True)
    items = [("maison", SO.HOUSE), ("escalier", SO.STAIRS), ("mur de briques", SO.BRICK_WALL),
             ("paroi du fond (avec écorce)", SO.BACK_WALL), ("aile gauche", SO.LEFT_WING), ("pilier", SO.PILLAR)]
    rows = [("Origine O : coin arrière gauche ; X vers la droite, Y vers l'avant.", True, BLACK),
            ("Dessus du plateau, au crayon (rectangles X de..à ; Y de..à) :", True, BLUE)]
    for i, (n, r) in enumerate(items):
        p.poly([Q(q) for q in r], TRACE, True)
        x0, y0, x1, y1 = bbox([so(q) for q in r])
        X, Y = Q(((r[0][0] + r[2][0]) / 2, (r[0][1] + r[2][1]) / 2))
        p.text(X, Y + 1, str(i + 1), 2.6, BLUE, True, "middle")
        rows.append(("%d  %s : X %s à %s ; Y %s à %s" % (i + 1, n, f(x0), f(x1), f(y0), f(y1)), False, BLACK))
    for (c, r, n) in SO.POSTS:
        p.poly([Q(q) for q in circle(c, r, 24)], TRACE, True)
        X, Y = so(c)
        rows.append(("    %s : centre X %s ; Y %s" % (n, f(X), f(Y)), False, BLACK))
    p.poly([Q(q) for q in SO.BRIDGE], TRACE, True)
    rows.append(("    pont, 4 coins : " + " ; ".join("(%s, %s)" % tuple(f(v) for v in so(q)) for q in SO.BRIDGE), False, BLACK))
    rows += [("", False, BLACK), ("Dessus du fond (5 mm), même origine O :", True, RED)]
    p.poly([Q(q) for q in SO.RESERVOIR], UNDER, True)
    x0, y0, x1, y1 = bbox([so(q) for q in SO.RESERVOIR])
    rows.append(("réservoir : X %s à %s ; Y %s à %s" % (f(x0), f(x1), f(y0), f(y1)), False, BLACK))
    rows.append(("entretoises 30 × 30 × 55, centres (X ; Y) :", False, BLACK))
    sp = [so(c) for c in SO.SPACERS]
    for c in SO.SPACERS:
        p.poly([Q(q) for q in rect(c[0] - 15, c[1] - 15, c[0] + 15, c[1] + 15)], UNDER, True)
    for j in range(0, len(sp), 4):
        rows.append(("    " + "   ".join("(%s ; %s)" % (f(X), f(Y)) for X, Y in sp[j:j + 4]), False, BLACK))
    rows += [("", False, BLACK),
             ("Le fond se trace autour du plateau découpé, puis on retourne", False, BLACK),
             ("le plateau sur le fond pour vérifier les emplacements.", False, BLACK)]
    table(p, 192, 30, rows, 2.5, 3.8)
    pages.append(p)
    return pages


def gabarit_ref():
    """Second point de repère du gabarit de la rivière : sur l'axe, 25 mm après le départ."""
    c = SO.spline(SO.RIVER_AXIS, 12, True)
    s = 0.0
    for a, b in zip(c, c[1:]):
        s += math.hypot(b[0] - a[0], b[1] - a[1])
        if s >= 25:
            return b
    return c[-1]


if __name__ == "__main__":
    out = [("02-socle-cotes.pdf", socle()), ("03-maison-cotes.pdf", maison()), ("04-escalier-cotes.pdf", escalier()),
           ("05-abri-cotes.pdf", abri()), ("06-pont-cotes.pdf", pont())]
    for name, pages in out:
        write_pdf(os.path.join(HERE, name), pages)
        print(name, len(pages), "page(s)")
