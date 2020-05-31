#!/usr/bin/env python3
##############################################################################
##                                                                          ##
##                          FP_TEST_GENERATOR                               ##
##                                                                          ##
##              Copyright (C) 2020, Florian Schanda                         ##
##                                                                          ##
##  This file is part of FP_Test_Generator.                                 ##
##                                                                          ##
##  FP_Test_Generator is free software: you can redistribute it and/or      ##
##  modify it under the terms of the GNU General Public License as          ##
##  published by the Free Software Foundation, either version 3 of the      ##
##  License, or (at your option) any later version.                         ##
##                                                                          ##
##  FP_Test_Generator is distributed in the hope that it will be useful,    ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of          ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           ##
##  GNU General Public License for more details.                            ##
##                                                                          ##
##  You should have received a copy of the GNU General Public License       ##
##  along with FP_Test_Generator. If not, see                               ##
##  <http://www.gnu.org/licenses/>.                                         ##
##                                                                          ##
##############################################################################

from functools import partial

from mpf.floats import MPF, RM_RNE, fp_nextUp, fp_nextDown
from mpf.rationals import Rational

from core import Vector


def build_zero(eb, sb, _, sign):
    rv = MPF(eb, sb)
    rv.set_zero(sign)
    return rv


def build_min_subnormal(eb, sb, _, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 0, 1)
    return rv


def build_rnd_subnormal(eb, sb, rng, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 0, rng.random_int(2, 2 ** rv.t - 2))
    return rv


def build_max_subnormal(eb, sb, _, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 0, 2 ** rv.t - 1)
    return rv


def build_min_normal(eb, sb, _, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 1, 0)
    return rv


def build_rnd_normal_small(eb, sb, rng, sign):
    rv = MPF(eb, sb)
    rv.pack(sign,
            rng.random_int(1, 2 ** (rv.w - 1)),
            rng.random_int(0, 2 ** rv.t - 1))
    return rv


def build_rnd_normal_large(eb, sb, rng, sign):
    rv = MPF(eb, sb)
    rv.pack(sign,
            rng.random_int(2 ** (rv.w - 1), 2 ** rv.w - 2),
            rng.random_int(0, 2 ** rv.t - 1))
    return rv


def build_one(eb, sb, _, sign):
    rv = MPF(eb, sb)
    rv.from_rational(RM_RNE, Rational(1))
    rv.set_sign_bit(sign)
    return rv


def build_one_succ(eb, sb, rng, sign):
    rv = build_one(eb, sb, rng, sign)
    return fp_nextUp(rv)


def build_one_pred(eb, sb, rng, sign):
    rv = build_one(eb, sb, rng, sign)
    return fp_nextDown(rv)


def build_max_normal(eb, sb, _, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 2 ** rv.w - 2, 2 ** rv.t - 1)
    return rv


def build_inf(eb, sb, _, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 2 ** rv.w - 1, 0)
    return rv


def build_nan(eb, sb, rng):
    rv = MPF(eb, sb)
    rv.pack(rng.random_int(0, 1),
            2 ** rv.w - 1,
            rng.random_int(1, 2 ** rv.t - 1))
    return rv


fp_test_points = {
    # Zeros
    "+0" : partial(build_zero, sign=0),
    "-0" : partial(build_zero, sign=1),

    # Subnormals
    "+min_subnormal" : partial(build_min_subnormal, sign=0),
    "+rnd_subnormal" : partial(build_rnd_subnormal, sign=0),
    "+max_subnormal" : partial(build_max_subnormal, sign=0),
    "-min_subnormal" : partial(build_min_subnormal, sign=1),
    "-rnd_subnormal" : partial(build_rnd_subnormal, sign=1),
    "-max_subnormal" : partial(build_max_subnormal, sign=1),

    # Normals
    "+min_normal"       : partial(build_min_normal, sign=0),
    "+rnd_normal_small" : partial(build_rnd_normal_small, sign=0),
    "+rnd_normal_large" : partial(build_rnd_normal_large, sign=0),
    "+max_normal"       : partial(build_max_normal, sign=0),
    "+1"                : partial(build_one, sign=0),
    "nextup(+1)"        : partial(build_one_succ, sign=0),
    "nextdown(+1)"      : partial(build_one_pred, sign=0),
    "-min_normal"       : partial(build_min_normal, sign=1),
    "-rnd_normal_small" : partial(build_rnd_normal_small, sign=1),
    "-rnd_normal_large" : partial(build_rnd_normal_large, sign=1),
    "-max_normal"       : partial(build_max_normal, sign=1),
    "-1"                : partial(build_one, sign=1),
    "nextup(-1)"        : partial(build_one_succ, sign=1),
    "nextdown(-1)"      : partial(build_one_pred, sign=1),

    # Infinities
    "+inf" : partial(build_inf, sign=0),
    "-inf" : partial(build_inf, sign=1),

    # NaN
    "NaN" : build_nan,
}

reduced_set = frozenset(["+0", "-0",
                         "+rnd_subnormal", "-rnd_subnormal",
                         "+rnd_normal_small", "-rnd_normal_small",
                         "+inf", "-inf",
                         "NaN"])


class Float_Vector(Vector):
    def __init__(self):
        self.vec = []

    def add_item(self, kind):
        assert kind in fp_test_points
        self.vec.append(kind)

    def __str__(self):
        return "Float_Vector<%s>" % ", ".join(self.vec)

    @classmethod
    def generate(cls, eb, sb, size, reduced):
        assert isinstance(eb, int)
        assert isinstance(sb, int)
        assert isinstance(size, int)
        assert isinstance(reduced, bool)
        assert size >= 1

        if reduced:
            all_kinds = sorted(reduced_set)
        else:
            all_kinds = list(sorted(fp_test_points))
        kinds = [0] * size

        def increment(p):
            if p == size:
                return False

            kinds[p] += 1
            if kinds[p] == len(all_kinds):
                kinds[p] = 0
                return increment(p + 1)
            else:
                return True

        while True:
            vec = Float_Vector()
            for k in kinds:
                vec.add_item(all_kinds[k])
            yield vec
            if not increment(0):
                return


class Float_Vector_With_RM(Float_Vector):
    def __init__(self, rm):
        super().__init__()

        assert rm in MPF.ROUNDING_MODES
        self.rm = rm

    def __str__(self):
        return "Float_Vector_With_RM<%s,%s>" % (self.rm,
                                                ", ".join(self.vec))

    @classmethod
    def generate(cls, eb, sb, size, reduced):
        assert isinstance(eb, int)
        assert isinstance(sb, int)
        assert isinstance(size, int)
        assert isinstance(reduced, bool)
        assert size >= 1

        for fv in Float_Vector.generate(eb, sb, size, reduced):
            for rm in MPF.ROUNDING_MODES:
                vec = Float_Vector_With_RM(rm)
                vec.vec = fv.vec
                yield vec
