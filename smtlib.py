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

def write_header(fd, seed):
    fd.write(";; Random floating-point test generated by fp_test_generator\n")
    fd.write(";;\n")
    fd.write(";; Seed information:\n")
    for key in sorted(seed.keys):
        fd.write(";;    %s = %s\n" % (key, seed.keys[key]))
    fd.write("\n")
    set_info(fd, "smt-lib-version", "2.6")
    set_info(fd, "license", "https://www.gnu.org/licenses/gpl-3.0.html")
    set_info(fd, "category", "random")
    set_info(fd,
             "source",
             "https://github.com/florianschanda/fp_test_generator")

def write_footer(fd):
    fd.write("\n")
    fd.write("(check-sat)\n")
    fd.write("(exit)\n")

def set_info(fd, key, value):
    if ":" in value:
        fd.write("(set-info :%s |%s|)\n" % (key, value))
    else:
        fd.write("(set-info :%s %s)\n" % (key, value))

def set_logic(fd, logic):
    fd.write("(set-logic %s)\n" % logic)

def set_status(fd, status):
    assert status in ("sat", "unsat")
    set_info(fd, "status", status)

def define_fp_const(fd, name, value):
    fd.write("\n")
    fd.write("(define-const %s %s %s)\n" % (name,
                                            value.smtlib_sort(),
                                            value.smtlib_literal()))
    if value.isFinite():
        fd.write(";; should be %s\n" % value.to_python_string())
    fd.write(";;   isZero      : %s\n" % value.isZero())
    fd.write(";;   isSubnormal : %s\n" % value.isSubnormal())
    fd.write(";;   isNormal    : %s\n" % value.isNormal())
    fd.write(";;   isInfinite  : %s\n" % value.isInfinite())
    fd.write(";;   isNan       : %s\n" % value.isNaN())
    fd.write(";;   isNegative  : %s\n" % value.isNegative())
    fd.write(";;   isPositive  : %s\n" % value.isPositive())
    fd.write(";;   isFinite    : %s\n" % value.isFinite())
    fd.write(";;   isIntegral  : %s\n" % value.isIntegral())

def define_const(fd, name, sort, value):
    fd.write("\n")
    fd.write("(define-const %s %s %s)\n" % (name,
                                            sort,
                                            value))

def goal_eq(fd, a, b, expecting_unsat):
    fd.write("\n")
    if expecting_unsat:
        fd.write(";; goal\n")
        fd.write("(assert (not (= %s %s)))\n" % (a, b))
    else:
        fd.write(";; goal\n")
        fd.write("(assert (= %s %s))\n" % (a, b))

def comment(fd, c):
    fd.write(";; %s\n" % c)
