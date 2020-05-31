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

from math import log2

from mpf.floats import MPF, RM_RNE, RM_RNA, RM_RTP, RM_RTN, RM_RTZ
from mpf.rationals import Rational

import gmpy2

from validation import Unsupported


NAME = "%s (via gmpy2 %s)" % (gmpy2.mpfr_version(),
                              gmpy2.version())

MPF_TO_MPFR_RM = {RM_RNE : gmpy2.RoundToNearest,
                  RM_RTP : gmpy2.RoundUp,
                  RM_RTN : gmpy2.RoundDown,
                  RM_RTZ : gmpy2.RoundToZero}
# MPFR in general does not support RM_RNA.
#
# You might be tempted to assume RM_RNA is RoundAwayZero, but this is
# not correct. That rounding mode is really the inverse of
# RoundToZero, i.e. it always does this and not just at half-points.


def mpf_to_mpfr(f):
    assert isinstance(f, MPF)

    if f.isNaN():
        return gmpy2.nan()
    elif f.isInfinite():
        if f.isPositive():
            return gmpy2.inf(1)
        else:
            return gmpy2.inf(-1)
    elif f.isZero():
        if f.isPositive():
            return gmpy2.zero(1)
        else:
            return gmpy2.zero(-1)
    else:
        return gmpy2.mpfr(f.to_python_string())


def mpfr_to_mpf(f):
    ctx = gmpy2.get_context()
    p = ctx.precision
    # emax = ctx.emax - 1
    # emax = (2 ** (w - 1)) - 1
    # emax + 1 = 2 ** (w - 1)
    # ln2(emax + 1) = w - 1
    # w = ln(emax + 1) + 1
    # w = ln(ctx.emax) + 1
    w = log2(ctx.emax) + 1
    assert w.is_integer()
    w = int(w)
    # w = k - p
    # k = w + p
    k = w + p

    eb = k - p
    sb = p

    rv = MPF(eb, sb)
    if gmpy2.is_nan(f):
        rv.set_nan()
    elif gmpy2.is_infinite(f):
        if gmpy2.sign(f) > 0:
            rv.set_infinite(0)
        else:
            rv.set_infinite(1)
    elif gmpy2.is_zero(f):
        if str(f) == "-0.0":
            rv.set_zero(1)
        elif str(f) == "0.0":
            rv.set_zero(0)
        else:
            assert False
    else:
        a, b = f.as_integer_ratio()
        rv.from_rational(RM_RNE, Rational(int(a), int(b)))
        assert mpf_to_mpfr(rv) == f

    return rv


def mpfr_context(a, rm=None):
    assert isinstance(a, MPF)

    # mpfr_precision = a.p
    # mpfr_emax = a.emax + 1
    mpfr_emin = a.emin - a.p + 2

    if mpfr_emin == 0:
        raise Unsupported("mpfr emin would be zero")

    ctx = gmpy2.ieee(32)
    # This is a good place to start from, but we'll overwrite most of
    # the fun stuff.

    ctx.precision = a.p
    ctx.emax      = a.emax + 1
    ctx.emin      = a.emin - a.p + 2

    if rm is not None:
        ctx.round = MPF_TO_MPFR_RM[rm]

    return ctx


def check_rm(rm):
    if rm is not None:
        if rm not in MPF_TO_MPFR_RM:
            raise Unsupported("rounding mode %s not supported" % rm)


def mpfr_abs(a):
    assert isinstance(a, MPF)
    with gmpy2.local_context(mpfr_context(a)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_r = abs(mpfr_a)
        return mpfr_to_mpf(mpfr_r)


def mpfr_neg(a):
    assert isinstance(a, MPF)
    with gmpy2.local_context(mpfr_context(a)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_r = -mpfr_a
        return mpfr_to_mpf(mpfr_r)


def mpfr_sqrt(rm, a):
    assert isinstance(a, MPF)
    check_rm(rm)
    with gmpy2.local_context(mpfr_context(a, rm)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_r = gmpy2.sqrt(mpfr_a)
        return mpfr_to_mpf(mpfr_r)


def mpfr_roundToIntegral(rm, a):
    assert isinstance(a, MPF)
    if rm == RM_RNA:
        with gmpy2.local_context(mpfr_context(a)):
            mpfr_a = mpf_to_mpfr(a)
            mpfr_r = gmpy2.rint_round(mpfr_a)
            return mpfr_to_mpf(mpfr_r)
    else:
        check_rm(rm)
        with gmpy2.local_context(mpfr_context(a, rm)):
            mpfr_a = mpf_to_mpfr(a)
            mpfr_r = gmpy2.rint(mpfr_a)
            return mpfr_to_mpf(mpfr_r)


def mpfr_add(rm, a, b):
    assert isinstance(a, MPF)
    check_rm(rm)
    with gmpy2.local_context(mpfr_context(a, rm)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_b = mpf_to_mpfr(b)
        mpfr_r = mpfr_a + mpfr_b
        return mpfr_to_mpf(mpfr_r)


def mpfr_sub(rm, a, b):
    assert isinstance(a, MPF)
    check_rm(rm)
    with gmpy2.local_context(mpfr_context(a, rm)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_b = mpf_to_mpfr(b)
        mpfr_r = mpfr_a - mpfr_b
        return mpfr_to_mpf(mpfr_r)


def mpfr_mul(rm, a, b):
    assert isinstance(a, MPF)
    check_rm(rm)
    with gmpy2.local_context(mpfr_context(a, rm)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_b = mpf_to_mpfr(b)
        mpfr_r = mpfr_a * mpfr_b
        return mpfr_to_mpf(mpfr_r)


def mpfr_div(rm, a, b):
    assert isinstance(a, MPF)
    check_rm(rm)
    with gmpy2.local_context(mpfr_context(a, rm)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_b = mpf_to_mpfr(b)
        mpfr_r = mpfr_a / mpfr_b
        return mpfr_to_mpf(mpfr_r)


def mpfr_rem(a, b):
    assert isinstance(a, MPF)
    with gmpy2.local_context(mpfr_context(a)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_b = mpf_to_mpfr(b)
        mpfr_r = gmpy2.remainder(mpfr_a, mpfr_b)
        return mpfr_to_mpf(mpfr_r)


def mpfr_min(a, b):
    assert isinstance(a, MPF)
    with gmpy2.local_context(mpfr_context(a)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_b = mpf_to_mpfr(b)
        mpfr_r = gmpy2.min2(mpfr_a, mpfr_b)
        return mpfr_to_mpf(mpfr_r)


def mpfr_max(a, b):
    assert isinstance(a, MPF)
    with gmpy2.local_context(mpfr_context(a)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_b = mpf_to_mpfr(b)
        mpfr_r = gmpy2.max2(mpfr_a, mpfr_b)
        return mpfr_to_mpf(mpfr_r)


def mpfr_fma(rm, a, b, c):
    assert isinstance(a, MPF)
    check_rm(rm)
    with gmpy2.local_context(mpfr_context(a, rm)):
        mpfr_a = mpf_to_mpfr(a)
        mpfr_b = mpf_to_mpfr(b)
        mpfr_c = mpf_to_mpfr(c)
        mpfr_r = gmpy2.fma(mpfr_a, mpfr_b, mpfr_c)
        return mpfr_to_mpf(mpfr_r)
