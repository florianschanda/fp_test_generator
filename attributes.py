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

import mpf.floats
import validation_mpfr

class FP_Attributes:
    def __init__(self, arity, function, mpfr_fn=None, rounding=True, returns="float"):
        assert isinstance(arity, int)
        assert arity >= 1
        assert callable(function)
        assert isinstance(rounding, bool)
        assert returns in ("bool", "float")

        self.arity         = arity
        self.function      = function
        self.mpfr_function = mpfr_fn
        self.rounding      = rounding
        self.returns       = returns

op_attr = {
    "fp.abs"  : FP_Attributes(1,
                              lambda x: abs(x),
                              validation_mpfr.mpfr_abs,
                              rounding=False),
    "fp.neg"  : FP_Attributes(1,
                              lambda x: -x,
                              validation_mpfr.mpfr_neg,
                              rounding=False),
    "fp.add"  : FP_Attributes(2,
                              mpf.floats.fp_add,
                              validation_mpfr.mpfr_add),
    "fp.sub"  : FP_Attributes(2,
                              mpf.floats.fp_sub,
                              validation_mpfr.mpfr_sub),
    "fp.mul"  : FP_Attributes(2,
                              mpf.floats.fp_mul,
                              validation_mpfr.mpfr_mul),
    "fp.div"  : FP_Attributes(2,
                              mpf.floats.fp_div,
                              validation_mpfr.mpfr_div),
    "fp.fma"  : FP_Attributes(3,
                              mpf.floats.fp_fma,
                              validation_mpfr.mpfr_fma),
    "fp.sqrt" : FP_Attributes(1,
                              mpf.floats.fp_sqrt,
                              validation_mpfr.mpfr_sqrt),
    "fp.rem"  : FP_Attributes(2,
                              mpf.floats.fp_rem,
                              validation_mpfr.mpfr_rem,
                              rounding=False),
    "fp.roundToIntegral" : FP_Attributes(1,
                                         mpf.floats.fp_roundToIntegral,
                                         validation_mpfr.mpfr_roundToIntegral),
    "fp.min"  : FP_Attributes(2,
                              mpf.floats.fp_min,
                              validation_mpfr.mpfr_min,
                              rounding=False),
    "fp.max"  : FP_Attributes(2,
                              mpf.floats.fp_max,
                              validation_mpfr.mpfr_max,
                              rounding=False),
    "fp.leq"  : FP_Attributes(2, lambda x, y: x <= y,
                              rounding=False,
                              returns="bool"),
    "fp.lt"  : FP_Attributes(2, lambda x, y: x < y,
                             rounding=False,
                             returns="bool"),
    "fp.geq"  : FP_Attributes(2, lambda x, y: x >= y,
                              rounding=False,
                              returns="bool"),
    "fp.gt"  : FP_Attributes(2, lambda x, y: x > y,
                             rounding=False,
                             returns="bool"),
    "fp.eq"  : FP_Attributes(2, lambda x, y: x == y,
                             rounding=False,
                             returns="bool"),
    "fp.isNormal"  : FP_Attributes(1, lambda x: x.isNormal(),
                                   rounding=False,
                                   returns="bool"),
    "fp.isSubnormal"  : FP_Attributes(1, lambda x: x.isSubnormal(),
                                      rounding=False,
                                      returns="bool"),
    "fp.isZero"  : FP_Attributes(1, lambda x: x.isZero(),
                                 rounding=False,
                                 returns="bool"),
    "fp.isInfinite"  : FP_Attributes(1, lambda x: x.isInfinite(),
                                     rounding=False,
                                     returns="bool"),
    "fp.isNaN"  : FP_Attributes(1, lambda x: x.isNaN(),
                                rounding=False,
                                returns="bool"),
}


def get_simple(op):
    assert op in op_attr

    return op_attr[op]
