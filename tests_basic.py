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

from mpf.floats import MPF, Unspecified, smtlib_eq

import attributes
import smtlib
import validation
import validation_host
import validation_mpfr

from core import Seed, Work_Package, precision_name
from float_vectors import fp_test_points, Float_Vector, Float_Vector_With_RM


class Basic_Test_WP(Work_Package):
    def __init__(self, fp_op, eb, sb, vec):
        self.fp_op = fp_op
        self.eb    = eb
        self.sb    = sb
        self.vec   = vec


def basic_test_build(wp):
    assert isinstance(wp, Basic_Test_WP)

    attr = attributes.get_simple(wp.fp_op)

    # Setup seed
    seed = Seed()
    seed.set_key("operation", wp.fp_op)
    for i in range(attr.arity):
        seed.set_key("input_kind_%u" % (i + 1),
                     wp.vec.vec[i])
    if attr.rounding:
        seed.set_key("rounding_mode", wp.vec.rm)

    # Get rng based on seed
    rng = seed.get_rng()

    # Create inputs
    inputs = []
    for input_id, input_kind in enumerate(wp.vec.vec, 1):
        inputs.append(("input_%u" % input_id,
                       fp_test_points[input_kind](wp.eb, wp.sb, rng)))

    # Decide if this test should be sat or unsat
    expect_unsat = rng.random_bool()

    # Compute result
    args = []
    if attr.rounding:
        args.append(wp.vec.rm)
    args += [input_value for _, input_value in inputs]
    try:
        expected_result = attr.function(*args)
        unspecified = False
    except Unspecified:
        unspecified = True
        if wp.fp_op in ("fp.min", "fp.max"):
            if rng.random_bool():
                expected_result = inputs[0][1]
            else:
                expected_result = inputs[1][1]
                expect_unsat = True
        else:
            assert False

    # Validate, if the answer is not unspecified
    validation_ok = True
    validators = set(["PyMPF"])
    if not unspecified:
        if attr.mpfr_function is not None:
            try:
                mpfr_result = attr.mpfr_function(*args)
                if smtlib_eq(mpfr_result, expected_result):
                    validators.add(validation_mpfr.NAME)
                else:
                    print("Validation failed for %s:" % wp.fp_op)
                    for arg in args:
                        print("  ", arg)
                    print("PyMPF result: %s" % expected_result)
                    print("MPFR result: %s" % mpfr_result)
                    validation_ok = False

            except validation.Unsupported:
                pass

        if attr.host_function is not None:
            try:
                host_result = attr.host_function(*args)
                if smtlib_eq(host_result, expected_result):
                    validators.add(validation_host.NAME)
                else:
                    print("Validation failed for %s:" % wp.fp_op)
                    for arg in args:
                        if isinstance(arg, MPF):
                            print("  ", arg, arg.bv)
                        else:
                            print(arg)
                    print("PyMPF result: %s" % expected_result)
                    print("Host result: %s" % host_result)
                    validation_ok = False

            except validation.Unsupported:
                pass

    # Decide on filename
    if not validation_ok:
        prefix = "controversial"
    elif len(validators) > 1:
        prefix = "tests_validated"
    else:
        prefix = "tests"
    prefix = os.path.join("fptg_testsuite",
                          prefix,
                          precision_name(wp.eb, wp.sb),
                          wp.fp_op)
    if attr.rounding:
        filename = "%s_%s.smt2" % (wp.vec.rm,
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
            args.append(wp.vec.rm)
        args += [input_name for input_name, _ in inputs]
        smtlib.define_const(fd, "computed_result", result_sort,
                            "(%s %s)" % (wp.fp_op, " ".join(args)))

        # Emit goal
        smtlib.goal_eq(fd, "expected_result", "computed_result",
                       expect_unsat)

        # Finish
        smtlib.write_footer(fd)


def create(eb, sb, fp_op, reduced):
    print("Generating %s (%s)" % (fp_op,
                                  precision_name(eb, sb)))

    attr = attributes.get_simple(fp_op)

    generator_class = (Float_Vector_With_RM
                       if attr.rounding
                       else Float_Vector)

    def build_wp():
        for vec in generator_class.generate(eb, sb, attr.arity, reduced):
            yield Basic_Test_WP(fp_op, eb, sb, vec)

    pool = multiprocessing.Pool()
    for _ in pool.imap_unordered(basic_test_build, build_wp(), 5):
        pass
