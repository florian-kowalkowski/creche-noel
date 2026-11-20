# -*- coding: utf-8 -*-
"""Étape 2 - gabarit du socle de la crèche.

Produit, à côté de ce script :
  02-socle-gabarit-A4.pdf : vue d'ensemble + 4 feuilles A4 paysage à l'échelle 1, à assembler
  02-socle-apercu.svg     : la vue d'ensemble seule

Toutes les cotes sont en millimètres. Repère du plan : x vers la droite, y vers l'avant
(le spectateur). C'est le même repère que la maquette 3D (1 unité = 10 mm).
Aucune dépendance : python generer_plan_socle.py
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MM = 72 / 25.4

# ----------------------------------------------------------------------------- géométrie


def _cr(p0, p1, p2, p3, t):
    def f(a, b, c, d):
        v0, v1, t2 = (c - a) * 0.5, (d - b) * 0.5, t * t
        return (2 * b - 2 * c + v0 + v1) * t2 * t + (-3 * b + 3 * c - 2 * v0 - v1) * t2 + v0 * t + b
    return (f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1]))


def spline(pts, per_seg=12, extrapolate=False):
    """Catmull-Rom uniforme passant par les points (mêmes formules que la maquette)."""
    n, out = len(pts), []
    for i in range(n - 1):
        if i > 0:
            p0 = pts[i - 1]
        elif extrapolate:
            p0 = (2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])
        else:
            p0 = pts[0]
        if i + 2 < n:
            p3 = pts[i + 2]
        elif extrapolate:
            p3 = (2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])
        else:
            p3 = pts[-1]
        for k in range(per_seg):
            out.append(_cr(p0, pts[i], pts[i + 1], p3, k / per_seg))
    out.append(pts[-1])
    return out


def circle(c, r, n=72):
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rot_rect(cx, cy, length, width, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + dx * c - dy * s, cy + dx * s + dy * c)
            for dx, dy in ((-length / 2, -width / 2), (length / 2, -width / 2), (length / 2, width / 2), (-length / 2, width / 2))]


# Contour du plateau : arrière et côtés droits, avant organique.
FRONT = [(220, 20), (224, 60), (205, 105), (160, 150), (120, 175), (60, 178), (0, 168),
         (-60, 158), (-120, 145), (-180, 122), (-222, 85), (-235, 40)]
OUTLINE = [(-235, -145), (220, -145)] + spline(FRONT)

# Rivière : axe, demi-largeur d'eau 13 -> 18 mm, + 3 mm pour la paroi du bac imprimé et le jeu.
RIVER_AXIS = [(145, -44), (148, -10), (138, 28), (117, 62), (110, 88), (114, 108)]
POOL_C, POOL_R = (115, 118), 30       # ouverture de reprise au-dessus du réservoir
TRAY_MARGIN = 3


def river_slot():
    c = spline(RIVER_AXIS, 12, True)
    n = len(c) - 1
    left, right = [], []
    for i, p in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, n)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        k = math.hypot(tx, ty)
        nx, ny = -ty / k, tx / k
        o = 13 + 5 * i / n + TRAY_MARGIN
        left.append((p[0] - nx * o, p[1] - ny * o))
        right.append((p[0] + nx * o, p[1] + ny * o))

    def cut(side):
        out = []
        for p in side:
            d = math.hypot(p[0] - POOL_C[0], p[1] - POOL_C[1])
            if d <= POOL_R:
                out.append((POOL_C[0] + (p[0] - POOL_C[0]) * POOL_R / d, POOL_C[1] + (p[1] - POOL_C[1]) * POOL_R / d))
                break
            out.append(p)
        return out

    left, right = cut(left), cut(right)
    a0 = math.atan2(left[-1][1] - POOL_C[1], left[-1][0] - POOL_C[0])
    a1 = math.atan2(right[-1][1] - POOL_C[1], right[-1][0] - POOL_C[0])
    ref = c[int(n * 0.6)]
    best = None
    for sign in (1, -1):
        span = (a1 - a0) * sign % (2 * math.pi)
        arc = [(POOL_C[0] + POOL_R * math.cos(a0 + sign * span * k / 40), POOL_C[1] + POOL_R * math.sin(a0 + sign * span * k / 40)) for k in range(1, 40)]
        mid = arc[len(arc) // 2]
        far = math.hypot(mid[0] - ref[0], mid[1] - ref[1])
        if best is None or far > best[0]:
            best = (far, arc)
    return left + best[1] + right[::-1], c


SLOT, RIVER_C = river_slot()
TUBE_HOLE = ((145, -66), 7)
# Passages des câbles LED (USB), percés dans le plateau : centre, rayon, étiquette, position et ancrage du texte
LED_HOLES = [((110, -95), 7, "LED fenêtres Ø 14", (110, -84), "middle"),
             ((-40, -126), 7, "LED abri Ø 14", (-50, -126), "end"),
             ((-60, 50), 4, "LED feu Ø 8", (-53, 50), "start")]

# Implantations à reporter au crayon (rien à découper).
HOUSE = rect(85, -125, 185, -45)
STAIRS = rect(25, -130, 79, 16)
BRICK_WALL = rect(20, -140, 84, -130)
BACK_WALL = rect(-195, -140, 15, -90)
LEFT_WING = rect(-210, -100, -160, -10)
PILLAR = rect(-15, -95, 20, -45)
POSTS = [((-145, -35), 8.5, "poteau Ø 17"), ((1, -56), 6, "poteau Ø 12")]
BRIDGE = rot_rect(103, 66, 105, 37, 0.2)

# Sous le plateau.
RESERVOIR = rect(35, 75, 150, 150)
TUBE = [(140, 80), (168, 45), (168, -40), (147, -64)]
SPACERS = [(-215, -125), (-120, -125), (0, -125), (100, -125), (200, -125), (-215, 20), (-20, 0),
           (60, 20), (200, 0), (180, 80), (-120, 115), (0, 140)]
SPACER = 30

XS = [p[0] for p in OUTLINE]
YS = [p[1] for p in OUTLINE]
BBOX = (min(XS), min(YS), max(XS), max(YS))
PERIMETER = sum(math.hypot(OUTLINE[i][0] - OUTLINE[i - 1][0], OUTLINE[i][1] - OUTLINE[i - 1][1]) for i in range(len(OUTLINE)))

# ----------------------------------------------------------------------------- dessin

BLACK, BLUE, RED, GREY = (0, 0, 0), (0.12, 0.33, 0.7), (0.78, 0.18, 0.1), (0.78, 0.78, 0.78)
CUT = (0.5, BLACK, None)
TRACE = (0.25, BLUE, (3, 1.5))
UNDER = (0.3, RED, (1, 1.2))
GRID = (0.1, GREY, None)
THIN = (0.2, BLACK, None)


class Canvas:
    """Page en mm, origine en haut à gauche ; exporte en PDF ou en SVG."""

    def __init__(self, w, h):
        self.w, self.h, self.ops = w, h, []

    def poly(self, pts, style, closed=False):
        self.ops.append(("p", list(pts), style, closed))

    def text(self, x, y, s, size=3.0, color=BLACK, bold=False, anchor="start"):
        self.ops.append(("t", x, y, s, size, color, bold, anchor))

    def clip(self, x, y, w, h):
        self.ops.append(("c", x, y, w, h))

    def unclip(self):
        self.ops.append(("u",))

    def pdf(self):
        o = ["1 j 1 J"]
        for op in self.ops:
            if op[0] == "p":
                _, pts, (lw, col, dash), closed = op
                d = "[%s] 0" % " ".join("%.2f" % (v * MM) for v in dash) if dash else "[] 0"
                o.append("%.3f w %.3f %.3f %.3f RG %s d" % (lw * MM, col[0], col[1], col[2], d))
                path = " ".join("%.2f %.2f %s" % (x * MM, (self.h - y) * MM, "l" if i else "m") for i, (x, y) in enumerate(pts))
                o.append(path + (" h S" if closed else " S"))
            elif op[0] == "t":
                _, x, y, s, size, col, bold, anchor = op
                wd = 0.5 * size * len(s)
                x -= wd / 2 if anchor == "middle" else wd if anchor == "end" else 0
                esc = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                o.append("BT /%s %.2f Tf %.3f %.3f %.3f rg %.2f %.2f Td (%s) Tj ET"
                         % ("F2" if bold else "F1", size * MM, col[0], col[1], col[2], x * MM, (self.h - y) * MM, esc))
            elif op[0] == "c":
                _, x, y, w, h = op
                o.append("q %.2f %.2f %.2f %.2f re W n" % (x * MM, (self.h - y - h) * MM, w * MM, h * MM))
            else:
                o.append("Q")
        return "\n".join(o).encode("cp1252")

    def svg(self):
        rgb = lambda c: "rgb(%d,%d,%d)" % tuple(round(v * 255) for v in c)
        o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%gmm" height="%gmm" viewBox="0 0 %g %g">' % (self.w, self.h, self.w, self.h),
             '<rect width="100%" height="100%" fill="white"/>']
        for op in self.ops:
            if op[0] == "p":
                _, pts, (lw, col, dash), closed = op
                o.append('<%s points="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linejoin="round"%s/>' % (
                    "polygon" if closed else "polyline", " ".join("%.2f,%.2f" % p for p in pts), rgb(col), lw,
                    ' stroke-dasharray="%s"' % " ".join("%g" % v for v in dash) if dash else ""))
            elif op[0] == "t":
                _, x, y, s, size, col, bold, anchor = op
                s = s.replace("&", "&amp;").replace("<", "&lt;")
                o.append('<text x="%.2f" y="%.2f" font-family="Helvetica,Arial,sans-serif" font-size="%g" fill="%s" text-anchor="%s"%s>%s</text>'
                         % (x, y, size, rgb(col), anchor, ' font-weight="bold"' if bold else "", s))
        o.append("</svg>")
        return "\n".join(o)


def draw_plan(cv, T, ts, full):
    """Dessine le plan ; T convertit (x, y) du plan en mm de page, ts = taille du texte."""
    P = lambda pts: [T(x, y) for x, y in pts]

    def label(x, y, s, color=BLUE, anchor="middle", bold=False, k=1.0):
        px, py = T(x, y)
        cv.text(px, py + ts * k * 0.35, s, ts * k, color, bold, anchor)

    # sous le plateau
    cv.poly(P(RESERVOIR), UNDER, True)
    cv.poly(P(TUBE), UNDER)
    for x, y in SPACERS:
        cv.poly(P(rect(x - SPACER / 2, y - SPACER / 2, x + SPACER / 2, y + SPACER / 2)), UNDER, True)
        label(x, y, "E", RED)
    label(30, 112, "réservoir 115 × 75", RED, "end")
    label(30, 112 + ts * 1.4 / (T(0, 1)[1] - T(0, 0)[1]), "(sous le plateau)", RED, "end")
    label(172, -12, "tuyau", RED, "start")

    # implantations
    for shape in (HOUSE, STAIRS, BRICK_WALL, BACK_WALL, LEFT_WING, PILLAR, BRIDGE):
        cv.poly(P(shape), TRACE, True)
    for c, r, name in POSTS:
        cv.poly(P(circle(c, r, 36)), TRACE, True)
        if full:
            label(c[0], c[1] + r + 6, name)
    label(135, -95, "MAISON 100 × 80", bold=True)
    label(52, -70, "ESCALIER", bold=True)
    label(-90, -115, "PAROI DU FOND", bold=True)
    label(-185, -55, "AILE", bold=True)
    label(2, -78, "PILIER", bold=True)
    label(66, 62, "PONT", bold=True)
    label(-75, -30, "sol de l'abri")
    if full:
        label(52, -135, "mur de briques", k=0.8)
        label(162, -66, "trou Ø 14 (tuyau)", BLACK, "start")

    # à découper
    cv.poly(P(OUTLINE), CUT, True)
    cv.poly(P(SLOT), CUT, True)
    cv.poly(P(circle(*TUBE_HOLE, n=36)), CUT, True)
    for c, r, name, at, anchor in LED_HOLES:
        cv.poly(P(circle(c, r, 36)), CUT, True)
        if full:
            label(at[0], at[1], name, BLACK, anchor)
    label(118, 12, "RIVIÈRE", BLACK, "end", True)
    label(118, 12 + ts * 1.4 / (T(0, 1)[1] - T(0, 0)[1]), "à évider", BLACK, "end")
    label(150, 128, "REPRISE Ø 60", BLACK, "start", True)
    label(-40, 150, "AVANT", BLACK, "middle", True)


def overview():
    cv = Canvas(297, 210)
    k, ox, oy = 0.45, 14, 44
    T = lambda x, y: (ox + (x - BBOX[0]) * k, oy + (y - BBOX[1]) * k)
    draw_plan(cv, T, 2.3, False)
    w, h = BBOX[2] - BBOX[0], BBOX[3] - BBOX[1]
    # cotes
    x0, y0 = T(BBOX[0], BBOX[1])
    x1, y1 = T(BBOX[2], BBOX[3])
    cv.poly([(x0, y0 - 6), (x1, y0 - 6)], THIN)
    for x in (x0, x1):
        cv.poly([(x, y0 - 8), (x, y0 - 2)], THIN)
    cv.text((x0 + x1) / 2, y0 - 7.5, "%d mm" % round(w), 3, anchor="middle")
    cv.poly([(x1 + 5, y0), (x1 + 5, y1)], THIN)
    for y in (y0, y1):
        cv.poly([(x1 + 3, y), (x1 + 9, y)], THIN)
    cv.text(x1 + 5, y1 + 5, "%d mm" % round(h), 3, anchor="middle")
    cv.text((x0 + x1) / 2, y0 - 14, "ARRIÈRE", 2.6, anchor="middle", bold=True)

    cv.text(14, 14, "Crèche en liège - étape 2 : le socle", 5.5, bold=True)
    cv.text(14, 20, "Vue d'ensemble réduite (ne pas découper dessus). Les 4 feuilles suivantes sont à l'échelle 1.", 3)

    lx, ly = 240, 50
    lines = [
        ("LÉGENDE", True, BLACK),
        ("Noir plein : à découper", False, BLACK),
        ("Bleu tireté : à reporter au crayon", False, BLUE),
        ("Rouge pointillé : sous le plateau", False, RED),
        ("E : entretoise", False, RED),
        ("", False, BLACK),
        ("PIÈCES", True, BLACK),
        ("1 plateau, contreplaqué 20 mm", False, BLACK),
        ("   contour, rivière, 4 trous (tuyau, LED)", False, BLACK),
        ("1 fond, contreplaqué 5 mm", False, BLACK),
        ("   même contour, sans évidement", False, BLACK),
        ("%d entretoises, tasseau 30 × 30" % len(SPACERS), False, BLACK),
        ("   longueur 55 mm chacune", False, BLACK),
        ("Chant : bande de liège 80 mm", False, BLACK),
        ("   longueur %.2f m environ" % (PERIMETER / 1000 + 0.05), False, BLACK),
        ("", False, BLACK),
        ("HAUTEUR DU CAISSON", True, BLACK),
        ("20 + 55 + 5 = 80 mm", False, BLACK),
        ("", False, BLACK),
        ("ASSEMBLAGE DES FEUILLES", True, BLACK),
        ("A1  A2   (arrière)", False, BLACK),
        ("B1  B2   (avant)", False, BLACK),
    ]
    for i, (s, bold, col) in enumerate(lines):
        cv.text(lx, ly + i * 5, s, 2.7, col, bold)
    return cv


TILE_W, TILE_H, MARGIN = 267, 180, 15


def tiles():
    w, h = BBOX[2] - BBOX[0], BBOX[3] - BBOX[1]
    gx0 = BBOX[0] - (2 * TILE_W - w) / 2
    gy0 = BBOX[1] - (2 * TILE_H - h) / 2
    pages = []
    for r in range(2):
        for c in range(2):
            name = "AB"[r] + str(c + 1)
            cv = Canvas(297, 210)
            px0, py0 = gx0 + c * TILE_W, gy0 + r * TILE_H
            T = lambda x, y, px0=px0, py0=py0: (MARGIN + x - px0, MARGIN + y - py0)
            cv.clip(MARGIN, MARGIN, TILE_W, TILE_H)
            gx = math.ceil(px0 / 50) * 50
            while gx <= px0 + TILE_W:
                cv.poly([T(gx, py0), T(gx, py0 + TILE_H)], GRID)
                gx += 50
            gy = math.ceil(py0 / 50) * 50
            while gy <= py0 + TILE_H:
                cv.poly([T(px0, gy), T(px0 + TILE_W, gy)], GRID)
                gy += 50
            draw_plan(cv, T, 3.4, True)
            cv.unclip()
            cv.poly(rect(MARGIN, MARGIN, MARGIN + TILE_W, MARGIN + TILE_H), THIN, True)
            where = ("arrière" if r == 0 else "avant") + (" gauche" if c == 0 else " droit")
            cv.text(MARGIN, 10, "Socle - feuille %s (%s) - échelle 1" % (name, where), 4, bold=True)
            cv.text(MARGIN + TILE_W, 10, "Imprimer à 100 % (taille réelle, sans ajustement)", 3, anchor="end")
            cv.poly([(MARGIN, 201), (MARGIN + 100, 201)], CUT)
            for x in (MARGIN, MARGIN + 50, MARGIN + 100):
                cv.poly([(x, 199.5), (x, 202.5)], THIN)
            cv.text(MARGIN + 104, 202, "Contrôle : ce trait mesure 100 mm. Quadrillage gris : 50 mm.", 3)
            cv.text(MARGIN + TILE_W, 202, "Couper au cadre, assembler bord à bord : A1 A2 / B1 B2", 3, anchor="end")
            pages.append(cv)
    return pages


def write_pdf(path, pages):
    objs = [None, None,
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"]
    kids = []
    for cv in pages:
        data = cv.pdf()
        page_id = len(objs) + 1
        kids.append(page_id)
        objs.append(("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Contents %d 0 R "
                     "/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> >>" % (cv.w * MM, cv.h * MM, page_id + 1)).encode())
        objs.append(b"<< /Length %d >>\nstream\n" % len(data) + data + b"\nendstream")
    objs[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objs[1] = ("<< /Type /Pages /Count %d /Kids [%s] >>" % (len(kids), " ".join("%d 0 R" % k for k in kids))).encode()
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objs):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % (i + 1) + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    with open(path, "wb") as f:
        f.write(out)


if __name__ == "__main__":
    ov = overview()
    write_pdf(os.path.join(HERE, "02-socle-gabarit-A4.pdf"), [ov] + tiles())
    with open(os.path.join(HERE, "02-socle-apercu.svg"), "w", encoding="utf-8") as f:
        f.write(ov.svg())
    print("Plateau : %d x %d mm, périmètre %d mm" % (BBOX[2] - BBOX[0], BBOX[3] - BBOX[1], PERIMETER))
