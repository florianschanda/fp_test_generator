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

from functools import partial

from core import Vector, precision_names


def specific_precision(eb, sb, _):
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
