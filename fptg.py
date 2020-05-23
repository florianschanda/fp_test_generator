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
    print("  $ apt-get install python3-pip")
    print("  $ pip3 install PyMPF")
    sys.exit(1)

try:
    import gmpy2
except ImportError:
    print("This tool requires the python package gmpy2 to be installed.")
    print("You can do this via pip3:")
    print("  $ apt-get install libmpfr-dev libmpc-dev")
    print("  $ pip3 install gmpy2")
    sys.exit(1)

from rng import RNG

import smtlib
import attributes
import validation
import validation_mpfr

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

precision_names = {3:  { 5  : "float8"},
                   5:  {11  : "float16"},
                   8:  { 8  : "bfloat16",
                        11  : "tensorfloat32",
                        24  : "float32"},
                   11: {53  : "float64"},
                   15: {64  : "x87_extended",
                        115 : "float128"}
}

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

def specific_precision(eb, sb, rng):
    return (eb, sb)

def random_ordered_precision(rng):
    eb = rng.random_int(3, 10)
    sb = rng.random_int(eb + 1, eb + 7)
    return (eb, sb)

def random_symmetrical_precision(rng):
    eb = rng.random_int(3, 7)
    return (eb, eb)

def random_weird_precision(rng):
    eb = rng.random_int(5, 12)
    sb = rng.random_int(3, eb - 1)
    return (eb, sb)

precision_test_points = {
    precision_names[eb][sb]: partial(specific_precision, eb, sb)
    for eb in precision_names
    for sb in precision_names[eb]
}
precision_test_points["random_ordered"] = random_ordered_precision
precision_test_points["random_symmetrical"] = random_symmetrical_precision
precision_test_points["random_weird"] = random_weird_precision

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

class Precision_Vector(Vector):
    def __init__(self):
        self.vec = []

    def add_item(self, kind):
        assert kind in precision_test_points
        self.vec.append(kind)

    def __str__(self):
        return "Precision_Vector<%s>" % ", ".join(self.vec)

    @classmethod
    def generate(cls, size):
        assert isinstance(size, int)
        assert size >= 1

        all_kinds = list(sorted(precision_test_points))
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
            vec = Precision_Vector()
            for k in kinds:
                vec.add_item(all_kinds[k])
            yield vec
            if not increment(0):
                return


def precision_name(eb, sb):
    assert isinstance(eb, int)
    assert isinstance(sb, int)

    if eb in precision_names:
        if sb in precision_names[eb]:
            return precision_names[eb][sb]

    return "fp_%u_%u" % (eb, sb)


def basic_test(eb, sb, fp_op):
    print("Generating %s (%s)" % (fp_op,
                                  precision_name(eb, sb)))

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

        # Get rng based on seed
        rng = seed.get_rng()

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
            unspecified = True
            if rng.random_bool():
                expected_result = inputs[0][1]
            else:
                expected_result = inputs[1][1]
                expect_unsat = True

        # Validate
        validation_ok = True
        validators = set(["PyMPF"])
        if not unspecified:
            if attr.mpfr_function is not None:
                try:
                    mpfr_result = attr.mpfr_function(*args)
                    if smtlib_eq(mpfr_result, expected_result):
                        validators.add(validation_mpfr.NAME)
                    else:
                        print("Validation failed for %s:" % fp_op)
                        for arg in args:
                            print("  ", arg)
                        print("PyMPF result: %s" % expected_result)
                        print("MPFR result: %s" % mpfr_result)
                        validation_ok = False

                except validation.Unsupported:
                    pass

        # Decide on filename
        if not validation_ok:
            prefix = "random_fptg_controversial"
        elif len(validators) > 1:
            prefix = "random_fptg_validated"
        else:
            prefix = "random_fptg"
        prefix = os.path.join(prefix,
                              precision_name(eb, sb),
                              fp_op)
        if attr.rounding:
            filename = "%s_%s.smt2" % (vec.rm,
                                       seed.get_base_filename())
        else:
            filename = "%s.smt2" % seed.get_base_filename()

        # Build testcase
        os.makedirs(prefix, exist_ok=True)
        with open(os.path.join(prefix, filename), "w") as fd:
            # Create smtlib output for this test
            smtlib.write_header(fd, seed, validators)
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

def float_to_float_test():
    print("Generating float -> float tests")

    seed = Seed()
    seed.set_key("operation", "float_to_float")

    old_tgt = None
    for p_vec in Precision_Vector.generate(size=2):
        # Setup seed
        seed.set_key("precision_source", p_vec.vec[0])
        seed.set_key("precision_target", p_vec.vec[1])
        if old_tgt != p_vec.vec[1]:
            print("  to %s" % p_vec.vec[1])
            old_tgt = p_vec.vec[1]

        rng = seed.get_rng()

        p_source = precision_test_points[p_vec.vec[0]](rng)
        p_target = precision_test_points[p_vec.vec[1]](rng)

        for i_vec in Float_Vector_With_RM.generate(p_source[0], p_source[1],
                                                   size=1):
            seed.set_key("input_kind", i_vec.vec[0])
            seed.set_key("rounding_mode", i_vec.rm)

            # Get RNG based on seed
            rng = seed.get_rng()

            # Create input
            input_value = fp_test_points[i_vec.vec[0]](p_source[0],
                                                       p_source[1],
                                                       rng)

            # Decide if this test should be sat or unsat
            expect_unsat = rng.random_bool()

            # Compute result
            expected_result = fp_from_float(p_target[0], p_target[1],
                                            i_vec.rm,
                                            input_value)
            validators = set(["PyMPF"])

            # Decide on filename
            prefix = os.path.join("random_fptg",
                                  p_vec.vec[1],
                                  "to_fp")

            filename = "to_%s_%s_%s.smt2" % (p_vec.vec[1],
                                             i_vec.rm,
                                             seed.get_base_filename()[:4])

            # Build testcase
            os.makedirs(prefix, exist_ok=True)
            with open(os.path.join(prefix, filename), "w") as fd:
                # Create smtlib output for this test
                smtlib.write_header(fd, seed, validators)
                smtlib.set_status(fd, "unsat" if expect_unsat else "sat")

                smtlib.set_logic(fd, "QF_FP")

                # Emit input
                smtlib.define_fp_const(fd, "potato", input_value)

                # Emit expected result
                smtlib.define_fp_const(fd, "expected_result", expected_result)

                # Emit caluclation
                smtlib.define_const(fd, "computed_result",
                                    expected_result.smtlib_sort(),
                                    "((_ to_fp %u %u) %s potato)" %
                                    (p_target[0], p_target[1],
                                     i_vec.rm))

                # Emit goal
                smtlib.goal_eq(fd, "expected_result", "computed_result",
                               expect_unsat)

                # Finish
                smtlib.write_footer(fd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reduced-fp-points",
                    action="store_true",
                    help="create way fewer testcases in each category")

    options = ap.parse_args()

    # Process options

    if options.reduced_fp_points:
        reduced_set = set(["+0", "-0",
                           "+rnd_subnormal", "-rnd_subnormal",
                           "+rnd_normal_small", "-rnd_normal_small",
                           "+inf", "-inf",
                           "NaN"])

        for name in set(fp_test_points) - reduced_set:
            del fp_test_points[name]

    # Build tests

    for fp_op in attributes.op_attr:
        basic_test(3, 5, fp_op)

    float_to_float_test()

if __name__ == "__main__":
    main()
