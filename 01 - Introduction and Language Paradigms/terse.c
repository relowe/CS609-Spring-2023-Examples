#include <stdio.h>

int main()
{
    char const* str = "Hello, World\n";
    char const* ptr = str;

    /* Old-style terse c loop */
    while(*ptr) putchar(*(ptr++));

    /* More Intent-Obvious Code */
    ptr = str;
    while(*ptr != '\0') {
        putchar(*ptr);
        ptr = ptr + 1;
    }

}