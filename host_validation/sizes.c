#include <stdio.h>
#include "vlib.h"
#include <math.h>
int main()
{
  printf("sizeof(float) = %lu\n", sizeof(float));
  printf("sizeof(double) = %lu\n", sizeof(double));
  printf("sizeof(long double) = %lu\n", sizeof(long double));
  printf("sizeof(__float128) = %lu\n", sizeof(__float128));

  long double f = INFINITY;
  printf("%Lf\n", f);
  print_float80(f);

}
