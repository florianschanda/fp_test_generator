CC=gcc
CFLAGS=-std=c99 -frounding-math -fsignaling-nans -ffp-contract=off -mfma -mno-fma4 -Wall -W -Werror -O2
X87_FLAGS=-mfpmath=386
SSE_FLAGS=-msse2 -mfpmath=sse

vlib.o: vlib.c vlib.h
	$(CC) -c $(CFLAGS) $(SSE_FLAGS) vlib.c

sizes: sizes.c vlib.o
	$(CC) -c $(CFLAGS) $(SSE_FLAGS) sizes.c
	$(CC) sizes.o vlib.o -o sizes -lm -lquadmath

%.val: vlib.o %.val.c
	$(CC) -c $(CFLAGS) $(SSE_FLAGS) $*.val.c
	$(CC) $*.val.o vlib.o -o $*.val -lm -lquadmath
