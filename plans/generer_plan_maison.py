# -*- coding: utf-8 -*-
"""Étape 3 - gabarits de la maison (contreplaqué 3 mm).

Produit, à côté de ce script :
  03-maison-gabarits-A4.pdf : vue d'ensemble + 4 planches A4 portrait à l'échelle 1
  03-maison-apercu.svg      : la vue d'ensemble seule

Cotes en millimètres. Les pièces sont dessinées vues de l'extérieur, le bas en bas.
Aucune dépendance : python generer_plan_maison.py
"""
import math
import os

from generer_plan_socle import BLACK, BLUE, CUT, THIN, TRACE, Canvas, rect, write_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 210, 297

# ----------------------------------------------------------------------------- cotes
W, D = 100, 80            # emprise au sol (largeur de façade x profondeur)
EAVE, RIDGE = 220, 265    # hauteur des murs à l'égout, hauteur du faîtage
T3 = 3                    # épaisseur du contreplaqué
WIN = [rect(28, 168, 42, 198), rect(64, 121, 78, 151)]          # fenêtres 14 x 30
SHUTTERS = [rect(16, 168, 27, 198), rect(43, 168, 54, 198), rect(52, 121, 63, 151), rect(79, 121, 90, 151)]
BRICK = rect(4, 60, 96, 100)
PENTA = [(0, 0), (W, 0), (W, EAVE), (W / 2, RIDGE), (0, EAVE)]


def part(name, lines, outline, at, holes=(), traces=(), notes=()):
    return dict(name=name, lines=lines, outline=outline, at=at, holes=holes, traces=traces, notes=notes)


A = part("A - FAÇADE AVANT", ["100 × 265", "égout à 220"],
         [(0, 0), (40, 0), (40, 32), (80, 32), (80, 0)] + PENTA[1:], (50, 238),
         holes=WIN, traces=[BRICK, [(1, 103), (99, 103)]] + SHUTTERS,
         notes=[(50, 84, "parement brique H"), (50, 106, "auvent I"), (60, 37, "sortie d'eau 40 × 32"),
                (50, 50, "turquoise jusqu'à 60"), (35, 201, "fenêtre 14 × 30"), (71, 154, "fenêtre 14 × 30")])
B = part("B - FAÇADE ARRIÈRE", ["100 × 265"], PENTA, (50, 238),
         traces=[rect(25, 0, 75, 60)], notes=[(50, 64, "trappe d'accès 50 × 60"), (50, 30, "(facultative)")])
C = part("C - CÔTÉ GAUCHE", ["74 × 220", "vu de l'extérieur,", "avant à droite"], rect(0, 0, 74, EAVE), (42, 110),
         traces=[rect(7.5, 132, 24.5, 166)], notes=[(16, 169, "porte K")])
Dp = part("D - CÔTÉ DROIT", ["74 × 220"], rect(0, 0, 74, EAVE), (37, 110))
E = part("E - PAN DE TOIT", ["85 × 100", "recouvre F au faîtage"], rect(0, 0, 85, 100), (42.5, 55))
F = part("F - PAN DE TOIT", ["82 × 100"], rect(0, 0, 82, 100), (41, 55))
G = part("G - RAIDISSEUR", ["74 × 94 (× 2)", "collé à plat", "à l'intérieur"], rect(0, 0, 74, 94), (37, 55),
         traces=[[(20 + 7 * math.cos(a * math.pi / 18), 20 + 7 * math.sin(a * math.pi / 18)) for a in range(36)]],
         notes=[(37, 7, "G du bas : trou Ø 14 pour le câble LED,"), (37, 3, "à percer au montage, à l'aplomb du trou du socle")])
H = part("H - BRIQUE", ["92 × 40"], rect(0, 0, 92, 40), (72, 24), holes=[rect(39, 17, 49, 34)], notes=[(44, 11, "niche")])
I = part("I - AUVENT", ["98 × 35"], rect(0, 0, 98, 35), (49, 21))
J = part("J", [], rect(0, 0, 11, 30), (5.5, 14))
K = part("K", [], rect(0, 0, 17, 34), (8.5, 16))
L = part("L", [], [(0, 0), (30, 0), (30, 2.5), (0, 10)], (9, 3.5))


def draw(cv, p, px, py):
    h = max(y for _, y in p["outline"])
    T = lambda x, y: (px + x, py + h - y)
    for tr in p["traces"]:
        cv.poly([T(*q) for q in tr], TRACE, len(tr) > 2)
    for x, y, s in p["notes"]:
        tx, ty = T(x, y)
        cv.text(tx, ty, s, 2.5, BLUE, anchor="middle")
    cv.poly([T(*q) for q in p["outline"]], CUT, True)
    for hole in p["holes"]:
        cv.poly([T(*q) for q in hole], CUT, True)
    tx, ty = T(*p["at"])
    cv.text(tx, ty, p["name"], 3.4, BLACK, True, "middle")
    for i, s in enumerate(p["lines"]):
        cv.text(tx, ty + 4.2 * (i + 1), s, 2.8, anchor="middle")


def sheet(n, what):
    cv = Canvas(PW, PH)
    cv.text(14, 10, "Maison - planche %d/4 - %s - échelle 1" % (n, what), 4, bold=True)
    cv.poly([(14, 290), (114, 290)], CUT)
    for x in (14, 64, 114):
        cv.poly([(x, 288.5), (x, 291.5)], THIN)
    cv.text(118, 291, "Contrôle : 100 mm. Imprimer à 100 %, sans ajustement.", 2.8)
    return cv


def sheets():
    s1 = sheet(1, "contreplaqué 3 mm")
    draw(s1, A, 14, 18)
    draw(s1, C, 122, 18 + RIDGE - EAVE)
    s2 = sheet(2, "contreplaqué 3 mm")
    draw(s2, B, 14, 18)
    draw(s2, Dp, 122, 18 + RIDGE - EAVE)
    s3 = sheet(3, "contreplaqué 3 mm")
    draw(s3, E, 14, 18)
    draw(s3, F, 107, 18)
    draw(s3, G, 14, 128)
    draw(s3, G, 96, 128)
    s4 = sheet(4, "petites pièces, 3 mm")
    draw(s4, H, 14, 18)
    draw(s4, I, 14, 68)
    for i in range(4):
        draw(s4, J, 14 + i * 17, 116)
    s4.text(14, 152, "J - VOLET (× 4), 11 × 30", 2.8)
    draw(s4, K, 96, 112)
    s4.text(96, 152, "K - PORTE, 17 × 34", 2.8)
    for i in range(2):
        draw(s4, L, 14 + i * 40, 166)
    s4.text(14, 182, "L - CONSOLE D'AUVENT (× 2) : le côté haut de 10 mm se colle sur la façade, l'auvent sur la pente.", 2.8)
    s4.poly([(14, 196), (50, 196), (50, 202), (14, 202)], TRACE, True)
    s4.text(54, 200, "Chevron (× 4) : baguette ronde Ø 6, longueur 36 mm. Collé sous l'auvent, il dépasse à l'avant.", 2.8)
    return [s1, s2, s3, s4]


def dim_h(cv, x0, x1, y, s):
    cv.poly([(x0, y), (x1, y)], THIN)
    for x in (x0, x1):
        cv.poly([(x, y - 1.5), (x, y + 1.5)], THIN)
    cv.text((x0 + x1) / 2, y + 4, s, 2.8, anchor="middle")


def dim_v(cv, x, y0, y1, s):
    cv.poly([(x, y0), (x, y1)], THIN)
    for y in (y0, y1):
        cv.poly([(x - 1.5, y), (x + 1.5, y)], THIN)
    cv.text(x + 2, (y0 + y1) / 2 + 1, s, 2.8)


def overview():
    cv = Canvas(PW, PH)
    cv.text(14, 14, "Crèche en liège - étape 3 : la maison", 5.5, bold=True)
    cv.text(14, 20, "Vues d'ensemble à l'échelle 1/2. Les 4 planches suivantes sont à l'échelle 1.", 3)
    k = 0.5

    # --- façade
    ox, oy = 30, 34
    Tf = lambda x, y: (ox + x * k, oy + (275 - y) * k)
    P = lambda pts: [Tf(*q) for q in pts]
    cv.poly(P(A["outline"]), CUT, True)
    for sh in WIN:
        cv.poly(P(sh), CUT, True)
    for sh in SHUTTERS + [BRICK, rect(-1, 101, 101, 106)]:
        cv.poly(P(sh), THIN, True)
    slope = math.hypot(W / 2, RIDGE - EAVE)
    ux, uy = -(W / 2) / slope, -(RIDGE - EAVE) / slope
    for sign, length in ((1, 85), (-1, 82)):
        r = (W / 2, RIDGE + 2)
        e = (r[0] + sign * ux * length, r[1] + uy * length)
        n = (sign * uy * T3 * -1, ux * T3 * -1)
        cv.poly(P([r, e, (e[0] + n[0], e[1] + n[1]), (r[0] + n[0], r[1] + n[1])]), THIN, True)
    cv.text(ox + 50 * k, oy - 2, "FAÇADE", 3, bold=True, anchor="middle")
    x0, y0 = Tf(0, 0)
    x1, y1 = Tf(W, RIDGE)
    dim_h(cv, x0, x1, y0 + 5, "100")
    dim_v(cv, x1 + 9, Tf(0, EAVE)[1], y0, "220")
    dim_v(cv, x1 + 20, y1, y0, "265")
    cv.text(x0 - 3, Tf(0, 80)[1], "brique H", 2.5, BLUE, anchor="end")
    cv.text(x0 - 3, Tf(0, 104)[1], "auvent I", 2.5, BLUE, anchor="end")
    cv.text(x0 - 3, Tf(0, 30)[1], "turquoise", 2.5, BLUE, anchor="end")
    cv.text(x0 - 3, Tf(0, 12)[1], "sortie d'eau", 2.5, BLUE, anchor="end")

    # --- côté gauche (avant à droite)
    ox2 = 135
    Ts = lambda x, y: (ox2 + x * k, oy + (275 - y) * k)
    Q = lambda pts: [Ts(*q) for q in pts]
    cv.poly(Q(rect(0, 0, D, EAVE)), CUT, True)
    cv.poly(Q(rect(-8, 210, D + 12, RIDGE + 4)), THIN, True)
    cv.poly(Q(rect(3 + 7.5, 132, 3 + 24.5, 166)), THIN, True)
    cv.poly(Q(rect(D, 100, D + 34, 106)), THIN, True)
    cv.text(ox2 + 40 * k, oy - 2, "CÔTÉ GAUCHE", 3, bold=True, anchor="middle")
    a0, b0 = Ts(0, 0)
    a1, _ = Ts(D, 0)
    dim_h(cv, a0, a1, b0 + 5, "80")
    cv.text(Ts(19, 0)[0], Ts(0, 124)[1], "porte K", 2.5, BLUE, anchor="middle")
    cv.text(Ts(40, 0)[0], Ts(0, 240)[1], "toit E + F, 100 de long", 2.5, BLUE, anchor="middle")
    cv.text(Ts(D + 4, 0)[0], Ts(0, 92)[1], "auvent", 2.5, BLUE)
    cv.text(Ts(D + 2, 0)[0], Ts(0, 4)[1], "avant", 2.5, BLUE)

    y = 186
    blocks = [
        ("PIÈCES - contreplaqué 3 mm (une plaque de 60 × 30 cm suffit)", [
            "A  façade avant 100 × 265, avec 2 fenêtres et la sortie d'eau",
            "B  façade arrière 100 × 265",
            "C, D  côtés 74 × 220, collés entre les deux façades",
            "E, F  pans de toit 85 × 100 et 82 × 100 (support de l'écorce)",
            "G  2 raidisseurs 74 × 94, à plat à l'intérieur, à 100 et 215 mm du bas",
            "H  parement brique 92 × 40    I  auvent 98 × 35    J  4 volets 11 × 30",
            "K  porte 17 × 34    L  2 consoles d'auvent",
            "Hors plaque : 4 chevrons en baguette ronde Ø 6, longueur 36 mm",
        ]),
        ("MONTAGE", [
            "1. Découper les fenêtres avant le contour : percer, passer la lame, scier.",
            "2. Coller C et D entre A et B, avec les raidisseurs G pour tenir l'équerre.",
            "3. Peindre les murs, puis coller brique, volets, porte, consoles et auvent.",
            "4. Poser le pan F, puis E par-dessus. Le jour au faîtage disparaît sous l'écorce.",
            "5. Ne pas coller la maison sur le socle avant d'avoir posé le tuyau (étape rivière).",
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
    write_pdf(os.path.join(HERE, "03-maison-gabarits-A4.pdf"), [ov] + sheets())
    with open(os.path.join(HERE, "03-maison-apercu.svg"), "w", encoding="utf-8") as f:
        f.write(ov.svg())
    print("ok")
