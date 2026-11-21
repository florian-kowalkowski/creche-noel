# -*- coding: utf-8 -*-
"""Gabarits de traçage à imprimer en 3D : des plaques de 2 mm à poser sur le bois pour tracer autour.

Pour les formes longues à reporter à la règle (courbes, marches). Produit dans impression3d/gabarits/ :
  gabarit-evidement-riviere.stl  forme exacte de l'évidement du plateau, 2 trous de repère Ø 3 (R1, R2)
  gabarit-longeron-pont.stl      longeron arqué du pont (à tracer 2 fois)
Chaque gabarit est vu de dessus : le poser à plat, face imprimée en haut, et tracer autour au crayon fin.
Dépendances : pip install manifold3d numpy
"""
import os
import sys

from manifold3d import CrossSection, FillRule, Manifold

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plans"))
import generer_plan_pont as PO  # noqa: E402
import generer_plan_socle as SO  # noqa: E402
from generer_pieces_3d import on_bed, report, write_stl  # noqa: E402
from generer_plans_cotes import gabarit_ref  # noqa: E402

THICK = 2.0
OUT = os.path.join(HERE, "gabarits")


def plate(pts, holes=()):
    shape = CrossSection([list(pts)], FillRule.NonZero)
    for c, r in holes:
        shape -= CrossSection.circle(r, 32).translate(c)
    return Manifold.extrude(shape, THICK)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    flip = lambda pts: [(x, -y) for x, y in pts]                  # plan du socle : y vers l'avant -> vue de dessus
    r1, r2 = SO.POOL_C, gabarit_ref()
    parts = [
        ("gabarit-evidement-riviere.stl", plate(flip(SO.SLOT), [((r1[0], -r1[1]), 1.6), ((r2[0], -r2[1]), 1.6)])),
        ("gabarit-longeron-pont.stl", plate(PO.STRINGER)),
    ]
    for name, solid in parts:
        solid = on_bed(solid)
        write_stl(os.path.join(OUT, name), solid)
        report(name, solid)
