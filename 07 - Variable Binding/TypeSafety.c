#include <stdio.h>

int f(int x, int y) {
    return x+y;
}

int main() {
    double d;
    int x;

    x = f(1, 2);
    d = x; //widening happens implicitly
    x = d/2; //narrowing happens implicitly too
    printf("%f, %d\n", d/2, x);
}