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

float parse_float32()
{
  char *bin;
  uint32_t bv = 0;
  float rv;
  scanf("%ms\n", &bin);

  if (strlen(bin) != 32) {
    printf("expected 32 binary digits, got %lu\n", strlen(bin));
    exit(1);
  }

  for (int i=0; i<32; ++i) {
    bv = bv << 1;
    if (bin[i] == '1') {
      bv |= 1;
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

  memcpy(&rv, &bv, 4);
  return rv;
}

double parse_float64()
{
  char *bin;
  uint64_t bv = 0;
  double rv;
  scanf("%ms\n", &bin);

  if (strlen(bin) != 64) {
    printf("expected 64 binary digits, got %lu\n", strlen(bin));
    exit(1);
  }

  for (int i=0; i<64; ++i) {
    bv = bv << 1;
    if (bin[i] == '1') {
      bv |= 1;
    } else if (bin[i] == '0') {
      // Do nothing
    } else {
      printf("parse error at digit %u: not 0 or 1\n", i + 1);
      exit(1);
    }
  }

  /* fprintf(stderr, "read: %s\n", bin); */
  /* fprintf(stderr, "parsed: "); */
  /* for (int i=0; i<64; ++i) { */
  /*   fprintf(stderr, "%u", read_bit64(bv, 63 - i)); */
  /* } */
  /* fprintf(stderr, "\n"); */
  /* fprintf(stderr, "parsed: %f\n", *((double*)(&bv))); */

  memcpy(&rv, &bv, 8);
  return rv;
}

long double parse_float80()
{
  union {
    uint64_t bv[2];
    long double rv;
  } data;
  char *bin;
  int idx;
  scanf("%ms\n", &bin);

  if (strlen(bin) != 80) {
    printf("expected 80 binary digits, got %lu\n", strlen(bin));
    exit(1);
  }

  data.bv[0] = 0;
  data.bv[1] = 0;

  for (int i=6*8; i<128; ++i) {
    idx = i < 64;
    data.bv[idx] = data.bv[idx] << 1;
    if (bin[i-6*8] == '1') {
      data.bv[idx] |= 1;
    } else if (bin[i-6*8] == '0') {
      // Do nothing
    } else {
      printf("parse error at digit %u: not 0 or 1\n", i + 1 - 6*8);
      exit(1);
    }
  }

  /*
  fprintf(stderr, "string: %s\n", bin);
  fprintf(stderr, "parsed hi: %016lx\n", data.bv[1]);
  fprintf(stderr, "parsed lo: %016lx\n", data.bv[0]);
  fprintf(stderr, "parsed flt: %Lf\n", data.rv);
  */

  return data.rv;
}

__float128 parse_float128()
{
  union {
    uint64_t bv[2];
    __float128 rv;
  } data;
  char *bin;
  int idx;
  scanf("%ms\n", &bin);

  if (strlen(bin) != 128) {
    printf("expected 128 binary digits, got %lu\n", strlen(bin));
    exit(1);
  }

  data.bv[0] = 0;
  data.bv[1] = 0;

  for (int i=0; i<128; ++i) {
    idx = i < 64;
    data.bv[idx] = data.bv[idx] << 1;
    if (bin[i] == '1') {
      data.bv[idx] |= 1;
    } else if (bin[i] == '0') {
      // Do nothing
    } else {
      printf("parse error at digit %u: not 0 or 1\n", i + 1);
      exit(1);
    }
  }

  return data.rv;
}

void print_float32(float f)
{
  uint8_t bv[sizeof(float)];
  memcpy(bv, &f, sizeof(float));

  printf("result: ");
  for (unsigned int i=0; i<sizeof(float); ++i) {
    printf("%02x", bv[sizeof(float)-1-i]);
  }
  printf("\n");
}

void print_float64(double f)
{
  uint8_t bv[sizeof(double)];
  memcpy(bv, &f, sizeof(double));

  printf("result: ");
  for (unsigned int i=0; i<sizeof(double); ++i) {
    printf("%02x", bv[sizeof(double)-1-i]);
  }
  printf("\n");
}

void print_float80(long double f)
{
  uint8_t bv[sizeof(long double)];
  memcpy(bv, &f, sizeof(long double));

  printf("result: ");
  for (unsigned int i=6; i<sizeof(long double); ++i) {
    printf("%02x", bv[sizeof(long double)-1-i]);
  }
  printf("\n");
}

void print_float128(__float128 f)
{
  uint8_t bv[sizeof(__float128)];
  memcpy(bv, &f, sizeof(__float128));

  printf("result: ");
  for (unsigned int i=0; i<sizeof(__float128); ++i) {
    printf("%02x", bv[sizeof(__float128)-1-i]);
  }
  printf("\n");
}
