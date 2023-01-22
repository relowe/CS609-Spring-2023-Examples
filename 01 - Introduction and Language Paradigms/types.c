#include <stdio.h>

int main()
{
    int x=0;
    double d = 1.9999999;

    x = d;
    d = x;
    printf("x: %d, d: %f\n", x, d);
}