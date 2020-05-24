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

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fenv.h>
#include <stdint.h>

#include "vlib.h"

enum rounding_mode parse_rm()
{
  char *rm;

  scanf("%ms\n", &rm);
  if (strcmp(rm, "RNE") == 0) {
    return RNE;
  } else if (strcmp(rm, "RTZ") == 0) {
    return RTZ;
  } else if (strcmp(rm, "RTP") == 0) {
    return RTP;
  } else if (strcmp(rm, "RTN") == 0) {
    return RTN;
  } else if (strcmp(rm, "RNA") == 0) {
    return RNA;
  } else {
    printf("Unsupported rounding mode %s", rm);
    exit(1);
  }
}

void set_rm(enum rounding_mode rm)
{
  switch (rm) {
  case RNE:
    fesetround(FE_TONEAREST);
    break;
  case RNA:
    printf("Unsupported rounding mode RNA");
    exit(1);
  case RTP:
    fesetround(FE_UPWARD);
    break;
  case RTN:
    fesetround(FE_DOWNWARD);
    break;
  case RTZ:
    fesetround(FE_TOWARDZERO);
    break;
  }
}

int read_bit(uint32_t bv, int bit)
{
  return (bv & (1 << bit)) > 0;
}

void set_bit(uint32_t *bv, int bit)
{
  *bv = *bv | (1 << bit);
}

float parse_float()
{
  char *bin;
  uint32_t bv = 0;
  scanf("%ms\n", &bin);

  if (strlen(bin) != 32) {
    printf("expected 32 binary digits, got %lu\n", strlen(bin));
    exit(1);
  }

  for (int i=0; i<32; ++i) {
    if (bin[i] == '1') {
      set_bit(&bv, 31 - i);
    } else if (bin[i] == '0') {
      // Do nothing
    } else {
      printf("parse error at digit %u: not 0 or 1\n", i + 1);
      exit(1);
    }
  }

  /*
  fprintf(stderr, "parsed: ");
  for (int i=0; i<32; ++i) {
    fprintf(stderr, "%u", read_bit(bv, 31 - i));
  }
  fprintf(stderr, "\n");
  fprintf(stderr, "parsed: %f\n", *((float*)(&bv)));
  */

  return *((float*)(&bv));
}

void print_float(float f)
{
  uint32_t bv = *((uint32_t*)(&f));
  printf("result: ");
  for (int i=0; i<32; ++i) {
    printf("%u", read_bit(bv, 31 - i));
  }
  printf("\n");
}
