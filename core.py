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

import hashlib

from rng import RNG


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


class Vector:
    pass


precision_names = {
    3: {5: "float8"},
    5: {11: "float16"},
    8: {8: "bfloat16",
        11: "tensorfloat32",
        24: "float32"},
    11: {53: "float64"},
    15: {64: "x87_extended",
         113: "float128"}
}


def precision_name(eb, sb):
    assert isinstance(eb, int)
    assert isinstance(sb, int)

    if eb in precision_names:
        if sb in precision_names[eb]:
            return precision_names[eb][sb]

    return "fp_%u_%u" % (eb, sb)


class Work_Package:
    pass
