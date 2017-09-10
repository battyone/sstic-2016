#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint8_t fdata[] = {0xcb, 0x6d, 0x71, 0x1e, 0x38, 0x78, 0xb8, 0x24, 0xfe, 0x3f};
    uint32_t i;
    for (i = 0; i < 0xffffffff; i++) {
        *(uint32_t *)(fdata + 4) = i;
        uint16_t ax;
        __asm__ volatile(
            "fclex\n"
            "fldt %[mem]\n"
            "fld %%st(0)\n"
            "fcos\n"
            "fcompp\n"
            "fstsw %%ax\n"
            : "=a"(ax)
            : [mem] "m"(fdata)
            : "cc");
        if ((ax & 0xffdf) == 0x4000) {
            printf("Found %u %#x\n", i, i);
        }
    }
    return 0;
}
