#include <gr55xx.h>

int main(void)
{
    // TODO set GPIO mode to output
    GPIO0->ALTFUNCSET = 0x01; // ??? how to do that
    while(1) {
        GPIO0->OUTENSET |= (1 << 3);
        for(volatile int i=0; i < 1000000; i++) {}
        GPIO0->OUTENCLR |= (1 << 3);
        for(volatile int i=0; i < 1000000; i++) {}
    }
    return 0;
}
