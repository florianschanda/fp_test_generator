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

try:
    import mpf.floats
    assert mpf.floats.__name__ == mpf.floats.__name__
except ImportError:
    print("This tool requires the python package PyMPF to be installed.")
    print("You can do this via pip3:")
    print("  $ apt-get install python3-pip")
    print("  $ pip3 install PyMPF")
    sys.exit(1)

try:
    import gmpy2
    assert gmpy2.__name__ == gmpy2.__name__
except ImportError:
    print("This tool requires the python package gmpy2 to be installed.")
    print("You can do this via pip3:")
    print("  $ apt-get install libmpfr-dev libmpc-dev")
    print("  $ pip3 install gmpy2")
    sys.exit(1)

import attributes
import core

import tests_basic
import tests_float_to_float


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reduced-fp-points",
                    action="store_true",
                    help="create way fewer testcases in each category")

    options = ap.parse_args()

    # Build tests

    # for fp_op in attributes.op_attr:
    #     for eb in core.precision_names:
    #         for sb in core.precision_names[eb]:
    #             tests_basic.create(eb, sb, fp_op, options.reduced_fp_points)

    tests_float_to_float.create(options.reduced_fp_points)


if __name__ == "__main__":
    main()
