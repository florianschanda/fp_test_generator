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

import os
import multiprocessing

from mpf.floats import fp_from_float

import smtlib

from core import Seed, Work_Package
from float_vectors import fp_test_points, Float_Vector_With_RM
from precision_vectors import Precision_Vector, precision_test_points


class Float_To_Float_WP(Work_Package):
    def __init__(self,
                 source_precision, p_source,
                 target_precision, p_target,
                 vec):

        self.source_precision = source_precision
        self.p_source = p_source
        # Source precision kind and actual numbers

        self.target_precision = target_precision
        self.p_target = p_target
        # Target precision kind and actual numbers

        self.rm = vec.rm
        # Rounding mode for operation

        self.input_kind = vec.vec[0]
        # Input kind


def execute(wp):
    assert isinstance(wp, Float_To_Float_WP)

    # Create seed
    seed = Seed()
    seed.set_key("operation", "float_to_float")
    seed.set_key("precision_source", wp.source_precision)
    seed.set_key("precision_target", wp.target_precision)
    seed.set_key("input_kind", wp.input_kind)
    seed.set_key("rounding_mode", wp.rm)

    # Create RNG
    rng = seed.get_rng()

    # Create random instances
    input_value = fp_test_points[wp.input_kind](wp.p_source[0], wp.p_source[1],
                                                rng)

    # Decide if this test should be sat or unsat
    expect_unsat = rng.random_bool()

    # Compute result
    expected_result = fp_from_float(wp.p_target[0], wp.p_target[1],
                                    wp.rm,
                                    input_value)
    validators = set(["PyMPF"])

    # Decide on filename
    prefix = os.path.join("fptg_testsuite",
                          "tests",
                          wp.source_precision,
                          "to_fp")
    filename = "to_%s_%s_%s.smt2" % (wp.target_precision,
                                     wp.rm,
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
                            (wp.p_target[0], wp.p_target[1],
                             wp.rm))

        # Emit goal
        smtlib.goal_eq(fd, "expected_result", "computed_result",
                       expect_unsat)

        # Finish
        smtlib.write_footer(fd)


def build_wp(reduced):
    seed = Seed()
    seed.set_key("operation", "float_to_float")

    old_target = None

    for p_vec in Precision_Vector.generate(size=2):
        seed.set_key("precision_source", p_vec.vec[0])
        seed.set_key("precision_target", p_vec.vec[1])

        if old_target != p_vec.vec[1]:
            old_target = p_vec.vec[1]
            print("  to %s" % p_vec.vec[1])

        # Create RNG
        rng = seed.get_rng()

        p_source = precision_test_points[p_vec.vec[0]](rng)
        p_target = precision_test_points[p_vec.vec[1]](rng)

        for i_vec in Float_Vector_With_RM.generate(p_source[0], p_source[1],
                                                   1, reduced):
            yield Float_To_Float_WP(p_vec.vec[0], p_source,
                                    p_vec.vec[1], p_target,
                                    i_vec)


def create(reduced):
    print("Generating float -> float tests")

    pool = multiprocessing.Pool()
    for _ in pool.imap_unordered(execute, build_wp(reduced), 5):
        pass
