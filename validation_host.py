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
import subprocess

from mpf.floats import MPF, RM_RNE, fp_max
from mpf.rationals import Rational

import validation

def get_cpuinfo():
    info = {}
    with open("/proc/cpuinfo", "r") as fd:
        for raw_line in fd:
            if raw_line.strip():
                k, v = raw_line.split(":", 1)
                info[k.strip()] = v.strip()
            else:
                break

    return "Host (%s)" % info["model name"]

NAME = get_cpuinfo()

def to_bits(f):
    bits = "{0:b}".format(f.bv)
    assert len(bits) <= f.k
    bits = "0" * (f.k - len(bits)) + bits
    return bits

def get_binary_name(fp_op, arg):
    if arg.w == 8 and arg.p == 24:
        prec = 32
    elif arg.w == 11 and arg.p == 53:
        prec = 64
    else:
        raise validation.Unsupported("only single and double work")

    name = os.path.join("host_validation",
                        "%s.float%s.val" % (fp_op, prec))

    if os.path.isfile(name):
        return name

    else:
        raise validation.Unsupported("no validation binary exists")

def call_validator(fp_op, args, rm=None):
    assert len(args) >= 1
    p = subprocess.Popen([],
                         executable=get_binary_name(fp_op, args[0]),
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         encoding="utf-8")
    if rm:
        in_str = rm + "\n"
    else:
        in_str = ""

    for arg in args:
        in_str += to_bits(arg) + "\n"

    stdout, stderr = p.communicate(in_str)

    if p.returncode != 0:
        raise validation.Unsupported("calling validator failed")

    assert stdout.startswith("result: ")
    bits = stdout.split(": ", 1)[1].strip()

    rv = args[0].new_mpf()
    rv.bv = int(bits, 2)

    return rv

def host_abs(a):
    return call_validator("fp.abs", [a])

def host_neg(a):
    return call_validator("fp.neg", [a])

def host_add(rm, a, b):
    return call_validator("fp.add", [a, b], rm)

def host_sub(rm, a, b):
    return call_validator("fp.sub", [a, b], rm)

def host_mul(rm, a, b):
    return call_validator("fp.mul", [a, b], rm)

def host_div(rm, a, b):
    return call_validator("fp.div", [a, b], rm)

def host_sqrt(rm, a):
    return call_validator("fp.sqrt", [a], rm)

def host_fma(rm, a, b, c):
    return call_validator("fp.fma", [a, b, c], rm)

def host_rem(a, b):
    return call_validator("fp.rem", [a, b])

def host_min(a, b):
    raise validation.Unsupported("see issue #23")
    return call_validator("fp.min", [a, b])

def host_max(a, b):
    raise validation.Unsupported("see issue #23")
    return call_validator("fp.max", [a, b])

def host_roundToIntegral(rm, a):
    return call_validator("fp.roundToIntegral", [a], rm)

def sanity_test():
    x = MPF(8, 24, 4286578688)
    y = MPF(8, 24, 2142026366)
    print(x)
    print(y)
    print(host_fma(RM_RNE, x, y, x))
    print(fp_max(x, y))


if __name__ == "__main__":
    sanity_test()
