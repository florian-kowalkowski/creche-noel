# -*- coding: utf-8 -*-
"""Lecture minimale d'une police TrueType (.ttf) pour en tirer le contour des lettres, sans dépendance.

Gère les tables cmap (format 4), loca, glyf (glyphes simples et composés, pour les lettres accentuées)
et hmtx (chasse de chaque lettre). Pas de crénage : suffisant pour graver quelques lignes de texte.
"""
import struct


class Police:
    def __init__(self, path):
        d = self.d = open(path, "rb").read()
        n = struct.unpack(">H", d[4:6])[0]
        self.tab = {}
        for i in range(n):
            tag, _, off, ln = struct.unpack(">4sIII", d[12 + 16 * i:28 + 16 * i])
            self.tab[tag.decode("latin-1")] = off
        head, maxp, hhea = self.tab["head"], self.tab["maxp"], self.tab["hhea"]
        self.upm = self._u16(head + 18)
        long_loca = struct.unpack(">h", d[head + 50:head + 52])[0]
        ng = self._u16(maxp + 4)
        self.n_hmtx = self._u16(hhea + 34)
        lo = self.tab["loca"]
        if long_loca:
            self.loca = list(struct.unpack(">%dI" % (ng + 1), d[lo:lo + 4 * (ng + 1)]))
        else:
            self.loca = [2 * x for x in struct.unpack(">%dH" % (ng + 1), d[lo:lo + 2 * (ng + 1)])]
        self.cmap = self._cmap()

    def _u16(self, o):
        return struct.unpack(">H", self.d[o:o + 2])[0]

    def _i16(self, o):
        return struct.unpack(">h", self.d[o:o + 2])[0]

    def _cmap(self):
        d, cm = self.d, self.tab["cmap"]
        for i in range(self._u16(cm + 2)):
            pid, eid, off = struct.unpack(">HHI", d[cm + 4 + 8 * i:cm + 12 + 8 * i])
            o = cm + off
            if pid == 3 and eid in (0, 1) and self._u16(o) == 4:
                seg = self._u16(o + 6) // 2
                ends, starts = o + 14, o + 16 + 2 * seg
                deltas, ranges = starts + 2 * seg, starts + 4 * seg
                out = {}
                for s in range(seg):
                    a, b = self._u16(starts + 2 * s), self._u16(ends + 2 * s)
                    delta, ro = self._u16(deltas + 2 * s), self._u16(ranges + 2 * s)
                    for c in range(a, min(b, 0x2FF) + 1):
                        if ro == 0:
                            g = (c + delta) & 0xFFFF
                        else:
                            g = self._u16(ranges + 2 * s + ro + 2 * (c - a))
                            g = (g + delta) & 0xFFFF if g else 0
                        out[c] = g
                return out
        raise ValueError("table cmap format 4 introuvable")

    def advance(self, gid):
        h = self.tab["hmtx"]
        return self._u16(h + 4 * min(gid, self.n_hmtx - 1))

    def contours(self, gid):
        """Contours du glyphe : listes de (x, y, sur_la_courbe), en unités de la police."""
        g0, g1 = self.loca[gid], self.loca[gid + 1]
        if g1 == g0:
            return []
        o = self.tab["glyf"] + g0
        nc = self._i16(o)
        if nc >= 0:
            return self._simple(o, nc)
        out, p = [], o + 10
        while True:                                                     # glyphe composé (lettre + accent)
            flags, sub = self._u16(p), self._u16(p + 2)
            p += 4
            if flags & 1:
                dx, dy = self._i16(p), self._i16(p + 2)
                p += 4
            else:
                dx, dy = struct.unpack(">bb", self.d[p:p + 2])
                p += 2
            a, b, c, e = 1.0, 0.0, 0.0, 1.0
            if flags & 8:
                a = e = self._i16(p) / 16384.0
                p += 2
            elif flags & 0x40:
                a, e = self._i16(p) / 16384.0, self._i16(p + 2) / 16384.0
                p += 4
            elif flags & 0x80:
                a, b, c, e = [self._i16(p + 2 * k) / 16384.0 for k in range(4)]
                p += 8
            for ct in self.contours(sub):
                out.append([(a * x + c * y + dx, b * x + e * y + dy, on) for x, y, on in ct])
            if not flags & 0x20:
                return out

    def _simple(self, o, nc):
        d = self.d
        ends = [self._u16(o + 10 + 2 * i) for i in range(nc)]
        n = ends[-1] + 1 if ends else 0
        p = o + 10 + 2 * nc
        p += 2 + self._u16(p)
        flags = []
        while len(flags) < n:
            f = d[p]
            p += 1
            flags.append(f)
            if f & 8:
                flags += [f] * d[p]
                p += 1
        coords = []
        for short, same in ((2, 16), (4, 32)):
            v, vals = 0, []
            for f in flags:
                if f & short:
                    dv = d[p]
                    p += 1
                    v += dv if f & same else -dv
                elif not f & same:
                    v += self._i16(p)
                    p += 2
                vals.append(v)
            coords.append(vals)
        pts = [(coords[0][i], coords[1][i], bool(flags[i] & 1)) for i in range(n)]
        out, s = [], 0
        for e in ends:
            out.append(pts[s:e + 1])
            s = e + 1
        return out


def polyligne(contour, pas=6):
    """Aplatit un contour TrueType (courbes quadratiques) en polygone."""
    pts = list(contour)
    if not pts:
        return []
    full = []                                                           # ajoute les points implicites
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        full.append(p)
        if not p[2] and not q[2]:
            full.append(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, True))
    k = next(i for i, p in enumerate(full) if p[2])
    full = full[k:] + full[:k]
    out, i, m = [], 0, len(full)
    while i < m:
        p, q = full[i], full[(i + 1) % m]
        if q[2]:
            out.append((p[0], p[1]))
            i += 1
        else:
            r = full[(i + 2) % m]
            for j in range(pas):
                t = j / pas
                out.append(((1 - t) ** 2 * p[0] + 2 * t * (1 - t) * q[0] + t * t * r[0],
                            (1 - t) ** 2 * p[1] + 2 * t * (1 - t) * q[1] + t * t * r[1]))
            i += 2
    return out
