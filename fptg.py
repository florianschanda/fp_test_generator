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

import argparse
import sys
import os
import hashlib

from functools import partial

try:
    from mpf.floats import *
except ImportError:
    print("This tool requires the python package PyMPF to be installed.")
    print("You can do this via pip3:")
    print("  $ pip3 install PyMPF")
    sys.exit(1)

import smtlib
from rng import RNG

class Seed:
    def __init__(self):
        self.keys = {}
        self.seq  = 0

    def set_key(self, key, value):
        self.seq = 0
        self.keys[key] = value

    def next(self):
        self.seq += 1

        seed_vector = []
        m = hashlib.md5()
        for key in sorted(self.keys):
            m.update(bytes(self.keys[key], encoding="utf-8"))
        seed_vector.append(int(m.hexdigest(), 16))
        seed_vector.append(self.seq)

        rng = RNG(*seed_vector)
        return rng

    def __str__(self):
        seed_vector = []
        m = hashlib.md5()
        for key in sorted(self.keys):
            m.update(bytes(self.keys[key], encoding="utf-8"))
        seed_vector.append(int(m.hexdigest(), 16))
        seed_vector.append(self.seq)

        return "%u_%u" % (seed_vector[0],
                          seed_vector[1])

def build_zero(eb, sb, rng, sign):
    rv = MPF(eb, sb)
    rv.set_zero(sign)
    return rv

def build_min_subnormal(eb, sb, rng, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 0, 1)
    return rv

def build_rnd_subnormal(eb, sb, rng, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 0, rng.random_int(2, 2 ** rv.t - 2))
    return rv

def build_max_subnormal(eb, sb, rng, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 0, 2 ** rv.t - 1)
    return rv

def build_min_normal(eb, sb, rng, sign):
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

def build_one(eb, sb, rng, sign):
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

def build_max_normal(eb, sb, rng, sign):
    rv = MPF(eb, sb)
    rv.pack(sign, 2 ** rv.w - 2, 2 ** rv.t - 1)
    return rv

def build_inf(eb, sb, rng, sign):
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


def create_test(op, eb, sb, seed, rm=None):
    if eb == 3 and sb == 5:
        prec = "float8"
    elif eb == 5 and sb == 11:
        prec = "float16"
    elif eb == 8 and sb == 24:
        prec = "float32"
    elif eb == 11 and sb == 53:
        prec = "float64"
    elif eb == 15 and sb == 64:
        prec = "x87_extended"
    elif eb == 15 and sb == 115:
        prec = "float128"
    elif eb == 8 and sb == 8:
        prec = "bfloat16"
    elif eb == 8 and sb == 11:
        prec = "tensorfloat32"
    else:
        prec = "fp_%u_%u" % (eb, sb)

    os.makedirs(os.path.join("random_fptg", prec, op),
                exist_ok=True)

    if rm:
        fn = str(seed) + "_" + rm + ".smt2"
    else:
        fn = str(seed) + ".smt2"
    return open(os.path.join("random_fptg", prec, op, fn), "w")


def unary_arithmetic_without_rounding(eb, sb, op):
    assert isinstance(eb, int)
    assert isinstance(sb, int)
    assert op in ("fp.abs", "fp.neg")

    print("  for %s" % op)

    seed = Seed()
    seed.set_key("operation", op)

    for a_kind in sorted(fp_test_points):
        seed.set_key("a_kind", a_kind)
        rng = seed.next()
        a = fp_test_points[a_kind](eb, sb, rng)

        function = {"fp.abs" : lambda x: abs(x),
                    "fp.neg" : lambda x: -x}[op]

        expecting_unsat = rng.random_bool()

        fd = create_test(op, eb, sb, seed)
        smtlib.write_header(fd, seed)
        smtlib.set_logic(fd, "QF_FP")
        if expecting_unsat:
            smtlib.set_status(fd, "unsat")
        else:
            smtlib.set_status(fd, "sat")

        smtlib.define_fp_const(fd, "a", a)

        result = function(a)
        smtlib.define_fp_const(fd, "r1", result)

        smtlib.define_const(fd, "r2", result.smtlib_sort(),
                            "(%s a)" % op)

        smtlib.goal_eq(fd, "r1", "r2", expecting_unsat)

        smtlib.write_footer(fd)
        fd.close()

def unary_arithmetic_with_rounding(eb, sb, op):
    assert isinstance(eb, int)
    assert isinstance(sb, int)
    assert op in ("fp.sqrt", "fp.roundToIntegral")

    print("  for %s" % op)

    seed = Seed()
    seed.set_key("operation", op)

    for a_kind in sorted(fp_test_points):
        seed.set_key("a_kind", a_kind)
        rng = seed.next()
        a = fp_test_points[a_kind](eb, sb, rng)

        for rm in MPF.ROUNDING_MODES:
            seed.set_key("rounding", rm)
            rng = seed.next()

            function = {"fp.sqrt"            : fp_sqrt,
                        "fp.roundToIntegral" : fp_roundToIntegral}[op]

            expecting_unsat = rng.random_bool()

            fd = create_test(op, eb, sb, seed)
            smtlib.write_header(fd, seed)
            smtlib.set_logic(fd, "QF_FP")
            if expecting_unsat:
                smtlib.set_status(fd, "unsat")
            else:
                smtlib.set_status(fd, "sat")

            smtlib.define_fp_const(fd, "a", a)

            result = function(rm, a)
            smtlib.define_fp_const(fd, "r1", result)

            smtlib.define_const(fd, "r2", result.smtlib_sort(),
                                "(%s %s a)" % (op, rm))

            smtlib.goal_eq(fd, "r1", "r2", expecting_unsat)

            smtlib.write_footer(fd)
            fd.close()


def binary_arithmetic_with_rounding(eb, sb, op):
    assert isinstance(eb, int)
    assert isinstance(sb, int)
    assert op in ("fp.add", "fp.sub", "fp.mul", "fp.div")

    print("  for %s" % op)

    seed = Seed()
    seed.set_key("operation", op)

    for a_kind in sorted(fp_test_points):
        seed.set_key("a_kind", a_kind)
        rng = seed.next()
        a = fp_test_points[a_kind](eb, sb, rng)

        for b_kind in sorted(fp_test_points):
            seed.set_key("b_kind", b_kind)
            rng = seed.next()
            b = fp_test_points[b_kind](eb, sb, rng)

            for rm in MPF.ROUNDING_MODES:
                seed.set_key("rounding", rm)
                rng = seed.next()

                function = {"fp.add" : fp_add,
                            "fp.sub" : fp_sub,
                            "fp.mul" : fp_mul,
                            "fp.div" : fp_div}[op]

                expecting_unsat = rng.random_bool()

                fd = create_test(op, eb, sb, seed)
                smtlib.write_header(fd, seed)
                smtlib.set_logic(fd, "QF_FP")
                if expecting_unsat:
                    smtlib.set_status(fd, "unsat")
                else:
                    smtlib.set_status(fd, "sat")

                smtlib.define_fp_const(fd, "a", a)
                smtlib.define_fp_const(fd, "b", b)

                result = function(rm, a, b)
                smtlib.define_fp_const(fd, "r1", result)

                smtlib.define_const(fd, "r2", result.smtlib_sort(),
                                    "(%s %s a b)" % (op, rm))

                smtlib.goal_eq(fd, "r1", "r2", expecting_unsat)

                smtlib.write_footer(fd)
                fd.close()


def main():
    ap = argparse.ArgumentParser()

    options = ap.parse_args()

    formats = []
    formats.append((3, 5))    # float8
    # formats.append((5, 11))   # float16
    # formats.append((8, 8))    # bfloat16
    # formats.append((8, 11))   # tensorfloat32
    # formats.append((8, 24))   # float32
    # formats.append((11, 53))  # float64
    # formats.append((15, 64))  # x87_extended
    # formats.append((15, 115)) # float128

    for eb, sb in formats:
        print("Generating tests for precision %u %u" % (eb, sb))
        unary_arithmetic_without_rounding(eb, sb, "fp.abs")
        unary_arithmetic_without_rounding(eb, sb, "fp.neg")

        unary_arithmetic_with_rounding(eb, sb, "fp.roundToIntegral")
        unary_arithmetic_with_rounding(eb, sb, "fp.sqrt")

        binary_arithmetic_with_rounding(eb, sb, "fp.add")
        binary_arithmetic_with_rounding(eb, sb, "fp.sub")
        binary_arithmetic_with_rounding(eb, sb, "fp.mul")
        binary_arithmetic_with_rounding(eb, sb, "fp.div")

if __name__ == "__main__":
    main()
