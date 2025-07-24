// neopixel_coordinates.h の使用例
#include "neopixel_coordinates.h"
#include <stdio.h>

int main() {
    printf("NeoPixel Total Count: %d\n", get_neopixel_count());
    
    // 最初の数個のNeoPixel座標を表示
    for (int i = 0; i < 5; i++) {
        const NeoPixelCoord* coord = get_neopixel_coord(i);
        if (coord != NULL) {
            printf("NeoPixel %d: x=%d, y=%d, r=%d, theta=%d\n", 
                   coord->id, coord->x, coord->y, coord->r, coord->theta_deg);
            printf("  Float values: x=%.2fmm, y=%.2fmm, r=%.2fmm, theta=%.1f°\n",
                   COORD_TO_FLOAT(coord->x), COORD_TO_FLOAT(coord->y), 
                   COORD_TO_FLOAT(coord->r), ROTATION_TO_FLOAT(coord->theta_deg));
        }
    }
    
    // 範囲外アクセステスト
    const NeoPixelCoord* invalid = get_neopixel_coord(-1);
    printf("Invalid ID test: %s\n", invalid == NULL ? "NULL (正常)" : "Error");
    
    invalid = get_neopixel_coord(NEOPIXEL_COUNT);
    printf("Out of range test: %s\n", invalid == NULL ? "NULL (正常)" : "Error");
    
    return 0;
}
