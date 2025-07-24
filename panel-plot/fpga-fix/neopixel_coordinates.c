#include "neopixel_coordinates.h"
#include <stddef.h>
#include <stdint.h>

// IDからNeoPixel座標を取得
const NeoPixelCoord* get_neopixel_coord(int16_t id) {
    if (id < 0 || id >= NEOPIXEL_COUNT) {
        return NULL;
    }
    return &neopixel_coords[id];
}

// NeoPixelの総数を取得
int16_t get_neopixel_count(void) {
    return NEOPIXEL_COUNT;
}
