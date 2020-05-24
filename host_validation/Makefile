CC=gcc
CFLAGS=-std=c99 -frounding-math -fsignaling-nans -ffp-contract=off -mfma -mno-fma4 -pedantic -Wall -W
X87_FLAGS=-mfpmath=386
SSE_FLAGS=-msse2 -mfpmath=sse

vlib.o: vlib.c vlib.h
	$(CC) -c $(CFLAGS) $(SSE_FLAGS) vlib.c

%.val: vlib.o %.val.c
	$(CC) -c $(CFLAGS) $(SSE_FLAGS) $*.val.c
	$(CC) $*.val.o vlib.o -o $*.val -lm
