#include <stdio.h>



/* This is a simple c function to be called from a python program */

int add(int x, int y) {
    return x + y;
}

int main(void) {
    printf("Hello from a c function!\n");
}