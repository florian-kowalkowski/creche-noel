# -*- coding: utf-8 -*-
"""Étape 7 - pièces à imprimer en 3D (Creality K1C, plateau 220 x 220).

Produit des fichiers STL à côté de ce script, chacun déjà posé à plat sur le plateau :
  bac-riviere.stl, bassin-reprise.stl, reservoir.stl, seuil-cascade.stl   (circuit d'eau, PETG)
  rochers.stl, pelle.stl, tuiles-auvent.stl, tuiles-abri-avant.stl, tuiles-abri-arriere.stl   (PLA)
  fenetre-volets.stl (x 2), encadrement-sortie-eau.stl, porte-escalier.stl   (PLA, habillage de la façade)
  moule-4-tuiles.stl, emporte-piece-tuile.stl, reglettes-1,5mm.stl   (PLA, tuiles en argile autodurcissante)
  moule-briques-auvent.stl, moule-briques-escalier.stl   (PLA, parements en briques d'argile)
  apercu-assemblage.stl : les 4 pièces du circuit d'eau à leur place, pour contrôle visuel seulement

Cotes en millimètres. Le tracé de la rivière vient du plan du socle (../plans/generer_plan_socle.py) :
si on le modifie là-bas, relancer ce script.
Dépendances : pip install manifold3d numpy
"""
import math
import os
import struct
import sys

import numpy as np
from manifold3d import CrossSection, FillRule, JoinType, Manifold

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plans"))
from generer_plan_socle import POOL_C, RIVER_AXIS, TRAY_MARGIN, spline  # noqa: E402

# ----------------------------------------------------------------------------- paramètres
TUBE_OD = 10.0       # diamètre EXTÉRIEUR du tuyau (silicone 8 x 10 mm, sur l'embout de 8,4 mm de la pompe)
PLATE = 20.0         # épaisseur du plateau du socle
LIP_W = 12.0         # largeur du bec de la cascade (le lit de la rivière fait environ 27 mm)
V_DROP = 2.0         # descente du bec en V au milieu
TRAY_DEPTH = 9.0     # profondeur du pied du bac sous le dessus du plateau (il pend dans l'évidement)
CAVITY = 55.0        # hauteur libre du caisson (entretoises)
CLEAR = 0.4          # jeu entre une pièce imprimée et le bois
WALL = 2.0           # épaisseur des parois en contact avec l'eau
FLANGE, FLANGE_T = 4.5, 1.6   # collerette qui repose sur le plateau
TRAY_FLOOR = -7.0    # dessus du fond de la rivière (0 = dessus du plateau)
WEIR = -3.0          # crête du déversoir : niveau de l'eau dans la rivière
CUP_LEVEL = -6.0     # haut du trop-plein : niveau de l'eau dans le bassin de reprise
POOL_R = 30.0        # rayon de l'ouverture ronde du plateau
RES = (35, 75, 150, 150)      # emprise du réservoir sur le plan du socle (x0, y0, x1, y1)
ROCKY_BED = True     # fond de rivière en galets (False : fond lisse)
PEBBLES = 340       # nombre de galets tirés sur le fond
CUP_PEBBLES = 110    # nombre de galets au fond du bassin de reprise
PEBBLE_MAX = 2.2    # hauteur maxi d'un galet (l'eau fait 4 mm : au-delà de 4, il sort de l'eau)

# Repère de construction : X = x du plan, Y = -y du plan (pour ne pas imprimer en miroir), Z vers le haut.


def cs(pts):
    return CrossSection([[(x, -y) for x, y in pts]], FillRule.NonZero)


def disc(c, r, n=96):
    return CrossSection.circle(r, n).translate((c[0], -c[1]))


def ext(section, z0, z1):
    return Manifold.extrude(section, z1 - z0).translate((0, 0, z0))


def cyl(c, r, z0, z1, n=64):
    return Manifold.cylinder(z1 - z0, r, r, n).translate((c[0], -c[1], z0))


def box(x0, y0, x1, y1, z0, z1):
    return ext(cs([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), z0, z1)


def river_frame():
    """Points de l'axe de la rivière (repère du plan) : (point, normale, demi-largeur de l'évidement, abscisse)."""
    c = spline(RIVER_AXIS, 12, True)
    n = len(c) - 1
    out, s = [], 0.0
    for i, p in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, n)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        k = math.hypot(tx, ty)
        if i:
            s += math.hypot(p[0] - c[i - 1][0], p[1] - c[i - 1][1])
        out.append((p, (-ty / k, tx / k), 13 + 5 * i / n + TRAY_MARGIN, s))
    return out


def river_polygon():
    f = river_frame()
    left = [(p[0] - n[0] * o, p[1] - n[1] * o) for p, n, o, _ in f]
    right = [(p[0] + n[0] * o, p[1] + n[1] * o) for p, n, o, _ in f]
    return left + right[::-1]


RIVER = cs(river_polygon())

# Point E : là où la rivière débouche dans le bassin ; d = sens du courant à cet endroit.
_dx, _dy = POOL_C[0] - RIVER_AXIS[-1][0], POOL_C[1] - RIVER_AXIS[-1][1]
_k = math.hypot(_dx, _dy)
D = (_dx / _k, _dy / _k)
E = (POOL_C[0] - D[0] * (POOL_R + 0.5), POOL_C[1] - D[1] * (POOL_R + 0.5))


def along(a0, a1, half):
    """Rectangle posé en E : de a0 à a1 dans le sens du courant, de demi-largeur half."""
    nx, ny = -D[1], D[0]
    return cs([(E[0] + D[0] * a + nx * s, E[1] + D[1] * a + ny * s) for a, s in ((a0, -half), (a1, -half), (a1, half), (a0, half))])


# ----------------------------------------------------------------------------- circuit d'eau

def make_tray():
    """Bac de rivière : s'encastre dans l'évidement du plateau, suspendu par sa collerette."""
    foot = (RIVER - disc(POOL_C, POOL_R + 0.5)).offset(-CLEAR)
    behind_house = cs([(-100, -44.2), (400, -44.2), (400, 400), (-100, 400)])     # pas de collerette sous la façade
    flange = (foot.offset(FLANGE) - disc(POOL_C, POOL_R + FLANGE + 0.7)) ^ behind_house
    tray = ext(foot, -TRAY_DEPTH, 0) + ext(flange, 0, FLANGE_T) - ext(foot.offset(-WALL), TRAY_FLOOR, 3)
    tray -= ext(along(-4.5, 0.6, 8), WEIR, 3)                      # échancrure du déversoir
    tray += ext(along(-3, 5, 7), WEIR - 1.2, WEIR)                 # bec qui porte l'eau au-dessus du bassin
    if ROCKY_BED:
        tray = pebble_floor(tray, foot)
    return tray


def _bed_spots(rng, n, margin_of):
    """Tire n emplacements dans le lit, loin des parois, du bout amont et du bassin. Repère du plan."""
    frame, spots = river_frame(), []
    while len(spots) < n:
        p, nrm, o, s = frame[rng.integers(len(frame))]
        r = margin_of(rng)
        half = o - CLEAR - WALL - r - 0.4                          # le galet ne touche pas la paroi
        if half <= 0 or s < r + 4:
            continue
        lat = rng.uniform(-half, half)
        x, y = p[0] + nrm[0] * lat, p[1] + nrm[1] * lat
        if math.hypot(x - POOL_C[0], y - POOL_C[1]) < POOL_R + 0.5 + CLEAR + WALL + r + 0.4:
            continue
        spots.append((x, y, r))
    return spots


def pebble_size(g):
    return 0.9 + 3.8 * g.uniform() ** 1.8                          # beaucoup de gravier, quelques gros galets


def raise_pebbles(solid, z_floor, spots, rng, max_h):
    """Relève le fond plat situé à z_floor en galets aplatis. spots : (x, y, r) dans le repère de construction."""
    peb = []
    for x, y, r in spots:
        e, a = rng.uniform(0.5, 1.0), rng.uniform(0, math.pi)
        peb.append((x, y, r, r * e, math.cos(a), math.sin(a), min(max_h, rng.uniform(0.28, 0.5) * r)))
    P = np.array(peb)

    def raise_floor(v):
        v = np.array(v, dtype=float)
        m = np.abs(v[:, 2] - z_floor) < 1e-4                       # seuls les points du fond bougent
        if m.any():
            dx = v[m, 0][:, None] - P[:, 0]
            dy = v[m, 1][:, None] - P[:, 1]
            u = (dx * P[:, 4] + dy * P[:, 5]) / P[:, 2]
            w = (-dx * P[:, 5] + dy * P[:, 4]) / P[:, 3]
            dome = P[:, 6] * np.clip(1 - u * u - w * w, 0, None) ** 0.6     # galets aplatis
            x, y = v[m, 0], v[m, 1]
            # grain de sable entre les galets, 0 à 0,5 mm : reste sous le premier point de la paroi
            grain = 0.12 * (np.sin(x * 1.7 + np.sin(y * 0.9)) + np.sin(y * 2.3 + np.sin(x * 1.3))) + 0.25
            v[m, 2] += np.maximum(dome.max(axis=1), grain)
        return v

    # 0,7 mm : la paroi est découpée assez fin pour que le grain (0,5 mm maxi) ne retourne aucune face
    return solid.refine_to_length(0.7).warp_batch(raise_floor)


def pebble_floor(tray, foot):
    """Fond de rivière en galets : bosses arrondies sur le fond, gros blocs le long des berges."""
    rng = np.random.default_rng(2611)
    spots = [(x, -y, r) for x, y, r in _bed_spots(rng, PEBBLES, pebble_size)]
    tray = raise_pebbles(tray, TRAY_FLOOR, spots, rng, PEBBLE_MAX)

    # blocs de berge, alternés à gauche et à droite, à moitié pris dans la paroi
    blocks, frame, side = [], river_frame(), 1
    for p, nrm, o, s in frame[2::3]:
        if math.hypot(p[0] - POOL_C[0], p[1] - POOL_C[1]) < POOL_R + 12:
            continue
        r = rng.uniform(2.4, 3.8)
        lat = side * (o - CLEAR - WALL - 0.5 * r)
        side = -side
        rock = make_rock(r, 3.1 * s + 11).rotate((0, 0, rng.uniform(0, 360)))
        blocks.append(rock.translate((p[0] + nrm[0] * lat, -(p[1] + nrm[1] * lat), TRAY_FLOOR - 0.3)))
    inside = ext(foot.offset(-0.4), TRAY_FLOOR - 1, -0.8)          # rien ne dépasse à l'extérieur ni au-dessus
    return tray + (Manifold.compose(blocks) ^ inside)


def make_cup():
    """Bassin de reprise : godet amovible avec trop-plein, posé dans l'ouverture ronde."""
    stand = (POOL_C[0], POOL_C[1] + 12)
    r_up, r_low = POOL_R - CLEAR, POOL_R - 4
    cup = cyl(POOL_C, r_up, max(-PLATE, -18), 0, 96)
    if PLATE < 18:                                                 # plateau mince : le fond dépasse dessous, plus étroit
        cup += cyl(POOL_C, r_low, -18, -PLATE + 0.01, 96)
    # collerette, interrompue franchement du côté où arrive la rivière
    cup += ext(disc(POOL_C, POOL_R + FLANGE) - disc(POOL_C, r_up - 0.5) - along(-10, 16, 24), 0, FLANGE_T)
    cup -= cyl(POOL_C, r_up - WALL, -8, 3, 96) + cyl(POOL_C, r_low - WALL, -16, -7.99, 96)
    cup -= ext(along(-1, 4, 9), WEIR - 1.6, 3)                     # passage du bec de la rivière
    cup += cyl(stand, 6, -18, CUP_LEVEL)                           # trop-plein
    cup -= cyl(stand, 3.5, -19, 1)
    if ROCKY_BED:
        cup = pebble_cup(cup, stand, r_low - WALL)
    return cup


def pebble_cup(cup, stand, r_floor):
    """Fond du bassin en galets, sans toucher la paroi ni le trop-plein."""
    rng = np.random.default_rng(1225)
    c, st = (POOL_C[0], -POOL_C[1]), (stand[0], -stand[1])
    spots = []
    while len(spots) < CUP_PEBBLES:
        r = pebble_size(rng)
        x, y = rng.uniform(-r_floor, r_floor, 2) + c
        if math.hypot(x - c[0], y - c[1]) < r_floor - r - 0.6 and math.hypot(x - st[0], y - st[1]) > 6 + r + 0.5:
            spots.append((x, y, r))
    return raise_pebbles(cup, -16.0, spots, rng, 3.0)


def make_reservoir():
    """Réservoir : bac ouvert posé sur le fond du caisson, sous le bassin. Il reçoit la pompe."""
    x0, y0, x1, y1 = RES
    outer = cs([(x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x1 - 3, y1 - 3), (x0 + 3, y1 - 3)]).offset(3)
    z0, z1 = -(PLATE + CAVITY), -(PLATE + 1)
    res = ext(outer, z0, z1) - ext(outer.offset(-2.4), z0 + 2.4, z1 + 1)
    res -= box(127, y0 - 2, 149, y0 + 5, z1 - 14, z1 + 1)          # passage du tuyau (10 mm) et du câble
    return res


def make_spout():
    """Seuil de cascade : passe par la sortie d'eau de la façade, le tuyau arrive par-dessous."""
    x0, x1, yb, yf, top = 126, 164, -74, -36, 24
    block = box(x0, yb, x1, yf, 0, top)
    # dessous du nez en biseau à 45° : il surplombe le bac sans toucher sa collerette
    wedge2d = CrossSection([[(44.8, -1), (44.8, 3), (36, 11.8), (35, 11.8), (35, -1)]], FillRule.NonZero)
    wedge = Manifold.extrude(wedge2d, 60).transform(np.array([[0, 0, 1, 115.0], [1, 0, 0, 0], [0, 1, 0, 0]], dtype=float))
    block -= wedge
    floor, cx = 18.0, 145.0
    # canal en entonnoir : 30 mm de large au-dessus du tuyau, il se resserre jusqu'au bec de LIP_W mm,
    # plus étroit que le lit de la rivière (environ 27 mm) : l'eau tombe au milieu, sans déborder
    hw = LIP_W / 2
    funnel = [(x0 + 4, yb + 2), (x1 - 4, yb + 2), (x1 - 4, -52), (cx + hw, yf - 3), (cx + hw, yf + 1),
              (cx - hw, yf + 1), (cx - hw, yf - 3), (x0 + 4, -52)]
    block -= ext(cs(funnel), floor, top + 1)
    # bec en V : le fond descend de V_DROP mm au milieu sur les 8 derniers mm, l'eau se concentre au centre
    vy0, vy1 = -(yf - 8), -(yf + 1)                                    # Y de construction (plan inversé)
    pts = []
    for yy in (vy0, vy1):
        pts += [(cx - hw, yy, floor + 0.01), (cx + hw, yy, floor + 0.01), (cx, yy, floor - V_DROP)]
    block -= Manifold.hull_points(pts)
    # brise-jet : un plafond au-dessus de l'arrivée du tuyau. Le jet s'y écrase et ressort calmement
    # vers l'avant par-dessous, au lieu de gicler hors du canal
    block += box(x0 + 3.5, yb + 1.5, x1 - 3.5, -56, floor + 3.6, floor + 5.0)
    block -= cyl((cx, -66), (TUBE_OD + 0.4) / 2, -1, floor + 1)     # logement du tuyau
    return block


# ----------------------------------------------------------------------------- décor

def _hash(i, j, k):
    h = math.sin(i * 127.1 + j * 311.7 + k * 74.7) * 43758.5453
    return h - math.floor(h)


def _noise(x, y, z):
    i, j, k = math.floor(x), math.floor(y), math.floor(z)
    f = lambda t: t * t * (3 - 2 * t)
    u, v, w = f(x - i), f(y - j), f(z - k)
    lerp = lambda a, b, t: a + (b - a) * t
    return lerp(lerp(lerp(_hash(i, j, k), _hash(i + 1, j, k), u), lerp(_hash(i, j + 1, k), _hash(i + 1, j + 1, k), u), v),
                lerp(lerp(_hash(i, j, k + 1), _hash(i + 1, j, k + 1), u), lerp(_hash(i, j + 1, k + 1), _hash(i + 1, j + 1, k + 1), u), v), w)


def make_rock(r, seed):
    def warp(p):
        x, y, z = p
        k = 1 + (_noise(x * 1.6 + seed, y * 1.6, z * 1.6 + seed) - 0.5) * 0.9 + (_noise(x * 4 + seed, y * 4 + 3, z * 4) - 0.5) * 0.25
        return (x * k, y * k, z * k)
    rock = Manifold.sphere(1.0, 14).warp(warp).scale((r * 1.2, r, r * 0.75))
    rock = rock.trim_by_plane((0, 0, 1), -r * 0.22)                # dessous plat, pour l'impression et le collage
    return rock.translate((0, 0, r * 0.22))


def make_rocks():
    radii = [15, 13, 12, 11, 10, 10, 9, 9, 8, 8, 7, 7, 6, 6, 5, 5]
    parts = []
    for i, r in enumerate(radii):
        parts.append(make_rock(r, 7.3 * (i + 1)).rotate((0, 0, 47 * i)).translate((20 + (i % 4) * 42, 18 + (i // 4) * 36, 0)))
    return Manifold.compose(parts)


def make_shovel():
    blade = CrossSection([[(-8.5, 11), (-9, -3), (-7, -12), (0, -14), (7, -12), (9, -3), (8.5, 11)]], FillRule.NonZero)
    shovel = Manifold.extrude(blade, 1.2)
    shovel += Manifold.cube((5, 9, 2.4)).translate((-2.5, 6, 0))                         # douille
    handle = Manifold.cylinder(95, 1.6, 1.6, 24).rotate((-90, 0, 0)).translate((0, 9, 1.2))
    shovel += handle.trim_by_plane((0, 0, 1), 0)                                         # manche à dos plat
    return shovel


def make_tiles(n, pitch, length):
    """Plaque de tuiles canal : onde continue, imprimée debout (sans support)."""
    mid, t = pitch / 2, 1.2
    wave = CrossSection()
    for i in range(n):
        c = (i + 0.5) * pitch
        ring = CrossSection.circle(mid + t / 2, 48) - CrossSection.circle(mid - t / 2, 48)
        half = CrossSection.square((pitch + 4, mid + 2)).translate((-pitch / 2 - 2, -0.15 if i % 2 == 0 else -mid - 2 + 0.15))
        wave += (ring ^ half).translate((c, 0))
    return Manifold.extrude(wave, length)


# ----------------------------------------------------------------------------- export

# ----------------------------------------------------------------------------- habillage de la façade
# Pièces collées sur la façade A pour cacher une découpe imprécise. Repère : celui de la façade vue de
# l'extérieur (X vers la droite, Y vers le haut). Elles s'impriment à plat, face visible en haut.

def poly2d(pts):
    return CrossSection([list(pts)], FillRule.NonZero)


def slab(pts, z0, z1):
    return Manifold.extrude(poly2d(pts), z1 - z0).translate((0, 0, z0))


def rect2d(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def make_window():
    """Fenêtre complète : encadrement, croisillon, appui et volets ouverts.
    L'ouverture de 14 x 30 est à X 0..14, Y 0..30 : on la cale sur le trou de la façade.
    L'encadrement déborde de 3 mm tout autour et cache une découpe jusqu'à 3 mm trop grande."""
    frame = slab(rect2d(-3, -3, 17, 33), 0, 2.4) - slab(rect2d(0, 0, 14, 30), -1, 3)
    frame += slab(rect2d(6.4, 0, 7.6, 30), 0, 1.6) + slab(rect2d(0, 14.4, 14, 15.6), 0, 1.6)   # croisillon
    frame += slab(rect2d(-5, -6, 19, -3), 0, 3.4)                                              # appui
    for side, x0 in ((-1, -14), (1, 17)):                                                      # volets ouverts
        frame += make_shutter(x0, hinge_left=(side > 0), seed=3 + side)
    return frame


def grain_groove(xs, ys, width):
    """Rainure de veinage : un trait ondulé d'épaisseur width, donné par sa ligne médiane."""
    left = [(x - width / 2, y) for x, y in zip(xs, ys)]
    right = [(x + width / 2, y) for x, y in zip(xs, ys)]
    return poly2d(left + right[::-1])


def wood_board(x0, width, height, n_planks, seed, hinge_left, straps, strap_len, top=1.8):
    """Panneau de planches verticales d'épaisseurs inégales, veinage ondulé en creux, un nœud
    sur la planche du milieu, et des pentures de fer en relief côté charnière (Y des pentures : straps)."""
    rng = np.random.default_rng(seed)
    pw, gap = width / n_planks, 0.45
    board = Manifold()
    for i in range(n_planks):
        px0 = x0 + i * pw + (gap / 2 if i else 0)
        px1 = x0 + (i + 1) * pw - (gap / 2 if i < n_planks - 1 else 0)
        h = top + rng.uniform(-0.15, 0.1)
        plank = slab(rect2d(px0, 0, px1, height), 0, h)
        # veinage : 2 rainures ondulées par planche, un peu de travers, qui contournent le nœud
        knot = (rng.uniform(px0 + 1.2, px1 - 1.2), rng.uniform(0.2 * height, 0.8 * height)) if i == n_planks // 2 else None
        grooves = []
        for j in (1, 2):
            base, ph, tilt = px0 + j * (px1 - px0) / 3, rng.uniform(0, 6.3), rng.uniform(-0.012, 0.012)
            ys = [-1 + 0.5 * n for n in range(int(2 * (height + 2)) + 1)]
            xs = []
            for y in ys:
                x = base + 0.22 * math.sin(y * 0.33 + ph) + 0.1 * math.sin(y * 1.3 + 2 * ph) + tilt * (y - height / 2)
                if knot:
                    d = (y - knot[1]) / 2.2
                    x += (0.75 if x > knot[0] else -0.75) * math.exp(-d * d)
                xs.append(x)
            grooves.append(grain_groove(xs, ys, 0.45))
        if knot:
            ring = CrossSection.circle(0.95, 24).scale((0.75, 1.3)) - CrossSection.circle(0.45, 16).scale((0.75, 1.3))
            grooves.append(ring.translate(knot))
        cut = CrossSection()
        for g in grooves:
            cut += g
        plank -= Manifold.extrude(cut, 1).translate((0, 0, h - 0.35))
        board += plank
    # pentures : bandes de fer en relief, du côté de la charnière, terminées par un rond
    hx0, hx1 = (x0, x0 + strap_len) if hinge_left else (x0 + width - strap_len, x0 + width)
    tip = hx1 if hinge_left else hx0
    for y in straps:
        board += slab(rect2d(hx0, y, hx1, y + 0.9), 0, top + 0.45)
        board += Manifold.cylinder(top + 0.45, 0.75, 0.75, 20).translate((tip, y + 0.45, 0))
    return board


def make_shutter(x0, hinge_left, seed):
    """Volet de 11 x 30 en 3 planches."""
    return wood_board(x0, 11, 30, 3, seed, hinge_left, (6.8, 22.6), 9.2)


def make_door():
    """Porte en haut de l'escalier, à coller sur le côté gauche C de la maison (repère porte K).
    Vantail 17 x 34 (X 0..17, Y 0..34) en 4 planches, chambranle en relief, seuil en pierre dessous,
    pentures côté gauche et bouton à droite. Le dessous du seuil (Y -2) se pose sur le palier."""
    leaf = wood_board(0, 17, 34, 4, 11, True, (6, 26.5), 13.5, top=1.7)
    frame = slab(rect2d(-2.2, 0, 19.2, 36.2), 0, 2.6) - slab(rect2d(0, 0, 17, 34), -1, 3)
    sill = slab(rect2d(-3.2, -2, 20.2, 0), 0, 3.2)
    knob = Manifold.cylinder(2.7, 0.8, 0.8, 24).translate((14.6, 16.5, 0))
    plate = slab(rect2d(14.0, 14.2, 15.2, 18.8), 0, 2.1)                      # platine du bouton
    keyhole = slab(rect2d(14.45, 14.6, 14.75, 15.6), 1.7, 3)
    return leaf + frame + sill + plate + knob - keyhole


def make_water_arch():
    """Encadrement en pierre de la sortie d'eau (encoche 40 x 32 en bas de la façade, X 40..80).
    Ouverture 39 x 26 + arc : le seuil (38 x 24) passe dedans. Posé à 2 mm du socle pour
    passer au-dessus de la collerette du bac."""
    y0, xa, xb, ys, top = 2.0, 40.5, 79.5, 26.0, 30.0
    c = (xa + xb) / 2
    half = (xb - xa) / 2
    R = (half ** 2 + (top - ys) ** 2) / (2 * (top - ys))
    cy = top - R
    arc = lambda r, a0, a1, n=24: [(c + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    a_in = math.asin(half / R)
    inner = [(xa, y0 - 1), (xa, ys)] + arc(R, math.pi / 2 + a_in, math.pi / 2 - a_in) + [(xb, ys), (xb, y0 - 1)]
    Ro, xo = R + 8, 6.0
    a_out = math.asin((half + xo) / Ro)
    outer = [(xa - xo, y0)] + arc(Ro, math.pi / 2 + a_out, math.pi / 2 - a_out) + [(xb + xo, y0)]
    stone = slab(outer, 0, 3) - slab(inner, -1, 4)
    joints = []
    for i in range(1, 7):                                                     # voussoirs de l'arc
        a = math.pi / 2 + a_out - i * 2 * a_out / 7
        p0, p1 = (c + (R - 1) * math.cos(a), cy + (R - 1) * math.sin(a)), (c + (Ro + 1) * math.cos(a), cy + (Ro + 1) * math.sin(a))
        nx, ny = -math.sin(a) * 0.3, math.cos(a) * 0.3
        joints.append(slab([(p0[0] - nx, p0[1] - ny), (p1[0] - nx, p1[1] - ny), (p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)], 2.4, 4))
    for y in (9.5, 17.5):                                                     # assises des piédroits
        for x0 in (xa - xo - 1, xb - 1):
            joints.append(slab(rect2d(x0, y - 0.3, x0 + xo + 2, y + 0.3), 2.4, 4))
    return stone - Manifold.compose(joints)


# ----------------------------------------------------------------------------- tuiles en argile
# Tuile canal finie (après séchage) : Ø extérieur 10 mm au gros bout, 8 mm au petit bout, 22 mm de long,
# 1,5 mm d'épaisseur. Le moule et l'emporte-pièce sont agrandis de CLAY_SHRINK pour compenser le retrait.
TILE_D_BIG, TILE_D_SMALL, TILE_LEN, CLAY_T = 10.0, 8.0, 22.0, 1.5
CLAY_SHRINK = 1.03


def _tile_inner():
    """Rayons intérieurs (gros et petit bout) et longueur, côté moule (argile fraîche)."""
    s = CLAY_SHRINK
    return (TILE_D_BIG / 2 - CLAY_T) * s, (TILE_D_SMALL / 2 - CLAY_T) * s, TILE_LEN * s


def make_tile_mold():
    """Moule à draper pour 4 tuiles : 4 demi-cônes couchés sur une semelle. L'argile se pose dessus ;
    la forme conique sert de dépouille : la tuile glisse vers le petit bout pour démouler."""
    r1, r2, L = _tile_inner()
    pitch, margin, base = 17.0, 5.0, 3.0
    W = 4 * pitch
    mold = box(0, -(L + 2 * margin), W, 0, -base, 0)          # box() prend des Y de plan : ici Y = 0..L+2m
    for i in range(4):
        cone = Manifold.cylinder(L, r1, r2, 64).rotate((-90, 0, 0))
        cone = cone.translate((pitch / 2 + i * pitch, margin, 0)).trim_by_plane((0, 0, 1), 0)
        mold += cone
    # petit trait en bout de semelle côté gros bout, pour repérer le sens
    mold -= box(2, -1.6, 6, -0.6, -0.5, 1)
    return mold


def make_tile_cutter():
    """Emporte-pièce : découpe dans la feuille d'argile le flan d'une tuile (demi-cône déroulé)."""
    r1, r2, L = _tile_inner()
    w1, w2 = math.pi * (r1 + CLAY_T / 2), math.pi * (r2 + CLAY_T / 2)
    slant = math.hypot(L, r1 - r2)
    blank = poly2d([(-w1 / 2, 0), (w1 / 2, 0), (w2 / 2, slant), (-w2 / 2, slant)])
    wall = blank.offset(0.8, JoinType.Miter) - blank
    flange = blank.offset(4.0, JoinType.Round) - blank.offset(0.4, JoinType.Miter)
    return Manifold.extrude(wall, 10) + Manifold.extrude(flange, 1.2)


def make_rails():
    """Deux réglettes de 1,5 mm : on étale l'argile au rouleau entre elles pour une épaisseur régulière."""
    return Manifold.compose([slab(rect2d(0, y, 150, y + 10), 0, CLAY_T) for y in (0, 16)])


# ----------------------------------------------------------------------------- briques en argile
# Moule à empreinte : on presse l'argile dans le bac, on arase au ras des bords, on démoule en retournant.
# Le fond du bac donne la face visible des briques ; les nervures donnent les joints en creux.
BRICK_L, BRICK_H, MORTAR = 9.0, 3.0, 0.8     # brique finie (mm) et largeur de joint
BRICK_T = 2.0                                 # épaisseur du parement en argile
JOINT_DEPTH = 0.6


def make_brick_mold(width, height, islands=(), seed=7):
    """Moule pour un parement de width x height (cotes finies, après séchage).
    islands : rectangles (x0, y0, x1, y1) en coordonnées du parement, vu de face, où l'argile doit manquer
    (niche...). Le moule est inversé gauche-droite : une fois démoulé et retourné, le parement est à l'endroit."""
    s = CLAY_SHRINK
    W, H = width * s, height * s
    lx, hy, j = BRICK_L * s, BRICK_H * s, MORTAR * s
    rim = 2.5
    mold = slab(rect2d(-rim, -rim, W + rim, H + rim), -2, BRICK_T) - slab(rect2d(0, 0, W, H), 0, BRICK_T + 1)
    # joints : nervures horizontales entre les rangs, verticales décalées d'une demi-brique un rang sur deux
    ridges = CrossSection()
    pockets = [CrossSection(), CrossSection(), CrossSection()]
    rng = np.random.default_rng(seed)
    row, y = 0, 0.0
    while y < H:
        y1 = min(y + hy, H)
        if y1 < H:
            ridges += poly2d(rect2d(0, y1, W, min(y1 + j, H)))
        x = -(lx + j) / 2 if row % 2 else 0.0
        while x < W:
            x1 = x + lx
            if x1 + j < W:
                ridges += poly2d(rect2d(max(x1, 0), y, x1 + j, y1))
            bx0, bx1 = max(x, 0) + 0.05, min(x1, W) - 0.05
            if bx1 - bx0 > 0.6 and y1 - y > 0.6:
                pockets[int(rng.integers(3))] += poly2d(rect2d(bx0, y + 0.05, bx1, y1 - 0.05))   # briques un peu inégales
            x = x1 + j
        y = y1 + j
        row += 1
    mold += Manifold.extrude(ridges, JOINT_DEPTH)
    for k, pk in enumerate(pockets):
        if k:
            mold -= Manifold.extrude(pk, 0.12 * k + 0.01).translate((0, 0, -0.12 * k))
    for x0, y0, x1, y1 in islands:                                   # inversion gauche-droite du moule
        mold += slab(rect2d((width - x1) * s, y0 * s, (width - x0) * s, y1 * s), 0, BRICK_T)
    mold -= slab([(W / 2 - 3, H + rim + 0.1), (W / 2 + 3, H + rim + 0.1), (W / 2, H + rim - 2.4)], BRICK_T - 0.8, BRICK_T + 1)   # repère HAUT
    return mold


def write_stl(path, solid):
    mesh = solid.to_mesh()
    v = np.asarray(mesh.vert_properties, dtype=np.float32)[:, :3]
    t = np.asarray(mesh.tri_verts)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("a", "<f4", 3), ("b", "<f4", 3), ("c", "<f4", 3), ("attr", "<u2")])
    rec["n"], rec["a"], rec["b"], rec["c"] = n, a, b, c
    with open(path, "wb") as f:
        f.write(b"creche - pieces a imprimer".ljust(80, b" "))
        f.write(struct.pack("<I", len(t)))
        f.write(rec.tobytes())


def on_bed(solid):
    """Pose la pièce sur le plateau d'impression, coin en (0, 0)."""
    lo = solid.bounding_box()[:3]
    return solid.translate((-lo[0], -lo[1], -lo[2]))


def report(name, solid, bodies=1):
    bb = solid.bounding_box()
    size = [bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]]
    n = len(solid.decompose())
    ok = "OK" if (solid.status().name == "NoError" and n == bodies and max(size[:2]) <= 220) else "A VERIFIER"
    print("%-26s %6.1f x %6.1f x %5.1f mm  %6.1f cm3  %d corps  %s" % (name, size[0], size[1], size[2], solid.volume() / 1000, n, ok))


if __name__ == "__main__":
    tray, cup, res, spout = make_tray(), make_cup(), make_reservoir(), make_spout()
    parts = [
        ("bac-riviere.stl", tray, 1), ("bassin-reprise.stl", cup, 1), ("reservoir.stl", res, 1), ("seuil-cascade.stl", spout, 1),
        ("rochers.stl", make_rocks(), 16), ("pelle.stl", make_shovel(), 1),
        ("tuiles-auvent.stl", make_tiles(11, 9.0, 36), 1),
        ("tuiles-abri-avant.stl", make_tiles(8, 9.5, 46), 1),
        ("tuiles-abri-arriere.stl", make_tiles(7, 9.5, 30), 1),
        ("fenetre-volets.stl", make_window(), 1),
        ("encadrement-sortie-eau.stl", make_water_arch(), 1),
        ("porte-escalier.stl", make_door(), 1),
        ("moule-4-tuiles.stl", make_tile_mold(), 1),
        ("emporte-piece-tuile.stl", make_tile_cutter(), 1),
        ("reglettes-1,5mm.stl", make_rails(), 2),
        ("moule-briques-auvent.stl", make_brick_mold(92, 40, [(39, 17, 49, 34)], seed=7), 1),
        ("moule-briques-escalier.stl", make_brick_mold(64, 195, seed=8), 1),
    ]
    for name, solid, bodies in parts:
        solid = on_bed(solid)
        write_stl(os.path.join(HERE, name), solid)
        report(name, solid, bodies)
    write_stl(os.path.join(HERE, "apercu-assemblage.stl"), Manifold.compose([tray, cup, res, spout]))
    inner = (RES[2] - RES[0] - 4.8) * (RES[3] - RES[1] - 4.8) * (CAVITY - 1 - 2.4) / 1000
    print("Réservoir : environ %d mL utiles. Jeu bec/bassin vérifié : %s" % (inner * 0.75, "oui" if (tray ^ cup).is_empty() else "NON, COLLISION"))
    print("Collision bassin/réservoir : %s ; bac/seuil : %s" % ("non" if (cup ^ res).is_empty() else "OUI", "non" if (tray ^ spout).is_empty() else "OUI"))
