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
from abc import ABCMeta, abstractmethod

try:
    from mpf.floats import *
except ImportError:
    print("This tool requires the python package PyMPF to be installed.")
    print("You can do this via pip3:")
    print("  $ pip3 install PyMPF")
    sys.exit(1)

import smtlib
from rng import RNG

import attributes

class Seed:
    def __init__(self):
        self.keys = {}

    def set_key(self, key, value):
        self.keys[key] = value

    def get_rng(self):
        seed_vector = []
        m = hashlib.md5()
        for key in sorted(self.keys):
            m.update(bytes(self.keys[key], encoding="utf-8"))
        seed_vector.append(int(m.hexdigest(), 16))
        rng = RNG(*seed_vector)
        return rng

    def get_base_filename(self):
        m = hashlib.md5()
        for key in sorted(self.keys):
            m.update(bytes(self.keys[key], encoding="utf-8"))
        return m.hexdigest()

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

class Vector:
    pass

class Float_Vector(Vector):
    def __init__(self):
        self.vec = []

    def add_item(self, kind):
        assert kind in fp_test_points
        self.vec.append(kind)

    def __str__(self):
        return "Float_Vector<%s>" % ", ".join(self.vec)

    @classmethod
    def generate(cls, eb, sb, size):
        assert isinstance(eb, int)
        assert isinstance(sb, int)
        assert isinstance(size, int)
        assert size >= 1

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
    def generate(cls, eb, sb, size):
        assert isinstance(eb, int)
        assert isinstance(sb, int)
        assert isinstance(size, int)
        assert size >= 1

        for fv in Float_Vector.generate(eb, sb, size):
            for rm in MPF.ROUNDING_MODES:
                vec = Float_Vector_With_RM(rm)
                vec.vec = fv.vec
                yield vec

def precision_name(eb, sb):
    assert isinstance(eb, int)
    assert isinstance(sb, int)

    names = {3:  { 5  : "float8"},
             5:  {11  : "float16"},
             8:  { 8  : "bfloat16",
                  11  : "tensorfloat32",
                  24  : "float32"},
             11: {53  : "float64"},
             15: {64  : "x87_extended",
                  115 : "float128"}}
    if eb in names:
        if sb in names[eb]:
            return names[eb][sb]

    return "fp_%u_%u" % (eb, sb)


def basic_test(eb, sb, fp_op):
    prefix = os.path.join("random_fptg",
                          precision_name(eb, sb),
                          fp_op)
    print("Generating %s" % prefix)

    attr = attributes.get_simple(fp_op)

    generator_class = (Float_Vector_With_RM
                       if attr.rounding
                       else Float_Vector)

    seed = Seed()
    seed.set_key("operation", fp_op)

    for vec in generator_class.generate(eb, sb, attr.arity):
        # Setup seed
        for i in range(attr.arity):
            seed.set_key("input_kind_%u" % (i + 1),
                         vec.vec[i])
        if attr.rounding:
            seed.set_key("rounding_mode", vec.rm)

        # Get filename and rng based on seed
        filename = seed.get_base_filename() + ".smt2"
        rng      = seed.get_rng()

        # Build testcase
        os.makedirs(prefix, exist_ok=True)
        with open(os.path.join(prefix, filename), "w") as fd:
            # Create inputs
            inputs = []
            for input_id, input_kind in enumerate(vec.vec, 1):
                inputs.append(("input_%u" % input_id,
                               fp_test_points[input_kind](eb, sb, rng)))

            # Decide if this test should be sat or unsat
            expect_unsat = rng.random_bool()

            # Compute result
            args = []
            if attr.rounding:
                args.append(vec.rm)
            args += [input_value for _, input_value in inputs]
            try:
                expected_result = attr.function(*args)
                unspecified = False
            except Unspecified:
                assert fp_op in ("fp.min", "fp.max")
                if rng.random_bool():
                    expected_result = inputs[0][1]
                else:
                    expected_result = inputs[1][1]
                    expect_unsat = True
                    unspecified = True

            # Create smtlib output for this test
            smtlib.write_header(fd, seed)
            if unspecified:
                smtlib.set_status(fd, "sat")
                smtlib.comment(fd,
                               "this result exploits unspecified behaviour")
            else:
                smtlib.set_status(fd, "unsat" if expect_unsat else "sat")

            smtlib.set_logic(fd, "QF_FP")

            # Emit inputs
            for input_name, input_value in inputs:
                smtlib.define_fp_const(fd, input_name, input_value)

            # Emit expected result
            if attr.returns == "bool":
                assert isinstance(expected_result, bool)
                smtlib.define_const(fd, "expected_result", "Bool",
                                    str(expected_result).lower())
            else:
                assert isinstance(expected_result, MPF)
                smtlib.define_fp_const(fd, "expected_result", expected_result)

            # Emit caluclation
            result_sort = (expected_result.smtlib_sort()
                           if attr.returns == "float"
                           else "Bool")
            args = []
            if attr.rounding:
                args.append(vec.rm)
            args += [input_name for input_name, _ in inputs]
            smtlib.define_const(fd, "computed_result", result_sort,
                                "(%s %s)" % (fp_op, " ".join(args)))

            # Emit goal
            smtlib.goal_eq(fd, "expected_result", "computed_result",
                           expect_unsat)

            # Finish
            smtlib.write_footer(fd)


def main():
    ap = argparse.ArgumentParser()

    options = ap.parse_args()

    for fp_op in attributes.op_attr:
        basic_test(3, 5, fp_op)

if __name__ == "__main__":
    main()
