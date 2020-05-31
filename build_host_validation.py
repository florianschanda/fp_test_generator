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

import attributes

simple_op = {
    "fp.add" : "%s + %s",
    "fp.sub" : "%s - %s",
    "fp.mul" : "%s * %s",
    "fp.div" : "%s / %s",
    "fp.neg" : "-%s",
}

special_op = {
    "fp.sqrt" : {"float" : "sqrtf(%s)",
                 "double" : "sqrt(%s)",
                 "long double": "sqrtl(%s)",
                 "__float128": "sqrtq(%s)"},
    "fp.abs" : {"float": "fabsf(%s)",
                "double": "fabs(%s)",
                "long double": "fabsl(%s)",
                "__float128": "fabsq(%s)"},
    "fp.fma" : {"float": "fmaf(%s,%s,%s)",
                "double": "fma(%s,%s,%s)",
                "long double": "fmal(%s,%s,%s)",
                "__float128": "fmaq(%s,%s,%s)"},
    "fp.rem" : {"float": "remainderf(%s,%s)",
                "double": "remainder(%s,%s)",
                "long double": "remainderl(%s,%s)",
                "__float128": "remainderq(%s,%s)"},
    "fp.min" : {"float": "fminf(%s,%s)",
                "double": "fmin(%s,%s)",
                "long double": "fminl(%s,%s)",
                "__float128": "fminq(%s,%s)"},
    "fp.max" : {"float": "__builtin_fmaxf(%s,%s)",
                "double": "fmax(%s,%s)",
                "long double": "fmaxl(%s,%s)",
                "__float128": "fmaxq(%s,%s)"},
}


def build_validator(precision, fp_op):
    assert precision in (32, 64, 80, 128)
    assert fp_op in attributes.op_attr

    attr = attributes.op_attr[fp_op]
    prec = "float%u" % precision
    c_prec = {32: "float",
              64: "double",
              80: "long double",
              128: "__float128"}[precision]
    name = "%s.%s.val" % (fp_op, prec)

    if fp_op in simple_op:
        c_op = simple_op[fp_op]
    elif fp_op in special_op:
        c_op = special_op[fp_op][c_prec]
    elif fp_op == "fp.roundToIntegral":
        if precision == 32:
            c_rti_rna = "roundf"
            c_rti     = "nearbyintf"
        elif precision == 64:
            c_rti_rna = "round"
            c_rti     = "nearbyint"
        elif precision == 80:
            c_rti_rna = "roundl"
            c_rti     = "nearbyintl"
        else:
            c_rti_rna = "roundq"
            c_rti     = "nearbyintq"
    else:
        assert False

    fd = open(os.path.join("host_validation", "%s.c" % name), "w")

    if precision < 128:
        fd.write("#include <math.h>\n")
    else:
        fd.write("#include <quadmath.h>\n")
    fd.write("#include \"vlib.h\"\n")

    fd.write("int main() {\n")

    if fp_op == "fp.roundToIntegral":
        fd.write("  enum rounding_mode rm = parse_rm();\n")
        for i in range(attr.arity):
            fd.write("  %s input_%u = parse_%s();\n" % (c_prec, i, prec))
        fd.write("  %s result;\n" % c_prec)
        fd.write("  if (rm == RNA) {\n")
        fd.write("    result = %s(input_0);\n" % c_rti_rna)
        fd.write("  } else {\n")
        fd.write("    set_rm(rm);\n")
        fd.write("    result = %s(input_0);\n" % c_rti)
        fd.write("  }\n")
    else:
        if attr.rounding:
            fd.write("  enum rounding_mode rm = parse_rm();\n")
            fd.write("  set_rm(rm);\n")
        for i in range(attr.arity):
            fd.write("  %s input_%u = parse_%s();\n" % (c_prec, i, prec))
        fd.write("  %s result = %s;\n" % (
            c_prec,
            c_op % tuple("input_%u" % i for i in range(attr.arity))))

    fd.write("  print_%s(result);\n" % prec)
    fd.write("  return 0;\n")
    fd.write("}\n")
    fd.close()

    return name


def main():
    names = set()
    for prec in (32, 64, 80):
        for op in simple_op:
            names.add(build_validator(prec, op))
        for op in special_op:
            names.add(build_validator(prec, op))
        names.add(build_validator(prec, "fp.roundToIntegral"))

    os.system("make -j8 -C host_validation %s" % " ".join(names))


if __name__ == "__main__":
    main()
