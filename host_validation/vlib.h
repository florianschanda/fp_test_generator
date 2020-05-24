/*****************************************************************************
**                                                                          **
**                          FP_TEST_GENERATOR                               **
**                                                                          **
**              Copyright (C) 2020, Florian Schanda                         **
**                                                                          **
**  This file is part of FP_Test_Generator.                                 **
**                                                                          **
**  FP_Test_Generator is free software: you can redistribute it and/or      **
**  modify it under the terms of the GNU General Public License as          **
**  published by the Free Software Foundation, either version 3 of the      **
**  License, or (at your option) any later version.                         **
**                                                                          **
**  FP_Test_Generator is distributed in the hope that it will be useful,    **
**  but WITHOUT ANY WARRANTY; without even the implied warranty of          **
**  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           **
**  GNU General Public License for more details.                            **
**                                                                          **
**  You should have received a copy of the GNU General Public License       **
**  along with FP_Test_Generator. If not, see                               **
**  <http://www.gnu.org/licenses/>.                                         **
**                                                                          **
*****************************************************************************/

#ifndef _VLIB_H_
#define _VLIB_H_

enum rounding_mode { RNE, RNA, RTP, RTN, RTZ };

enum rounding_mode parse_rm();
void set_rm(enum rounding_mode rm);

float parse_float();

void print_float(float f);

#endif
