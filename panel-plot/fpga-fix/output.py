import csv
import math
import os

def export_units(sector_paths, order_map, neo_pixel, mlcc):
    neo_rows = []
    mlcc_rows = []
    for sector, points in sorted(sector_paths.items()):
        # Sectorの値を "Sector0" のような文字列と仮定し、数字部分から文字を生成
        letter = chr(65 + sector)
        sector_counter = 0
        for r, theta in points:
            order = order_map.get((r, theta))
            rotation = theta + math.pi if order == "ascending" else theta
            rotation_degrees = math.degrees(rotation)
            np_x = (r + neo_pixel["offset"]) * math.cos(theta)
            np_y = (r + neo_pixel["offset"]) * math.sin(theta)
            # ラベルは例: "A0", "A1", ... または "B0", "B1", ...
            sector_label = f"{letter}{sector_counter}"
            sector_counter += 1
            neo_rows.append([np_x, -np_y, rotation_degrees+90, sector_label])
            mlcc_x = (r + mlcc["offset"]) * math.cos(theta)
            mlcc_y = (r + mlcc["offset"]) * math.sin(theta)
            mlcc_rows.append([mlcc_x, -mlcc_y, rotation_degrees+270, sector_label])
    # CSV出力: NeoPixel用
    output_file_np = os.path.join(os.path.dirname(__file__), 'units_neopixel.csv')
    with open(output_file_np, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Part Number', 'x', 'y', 'rotation', 'sector'])
        id_counter = 1
        for row in neo_rows:
            part_number = f"D{id_counter}"
            writer.writerow([id_counter, part_number] + row)
            id_counter += 1
    # CSV出力: MLCC用
    output_file_mlcc = os.path.join(os.path.dirname(__file__), 'units_mlcc.csv')
    with open(output_file_mlcc, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Part Number', 'x', 'y', 'rotation', 'sector'])
        id_counter = 1
        for row in mlcc_rows:
            part_number = f"C{id_counter}"
            writer.writerow([id_counter, part_number] + row)
            id_counter += 1

def export_neopixel_c_header(sector_paths, order_map, neo_pixel):
    """NeoPixelの座標とIDを統合されたC言語ヘッダーファイルとして出力（int16_t形式）"""
    neo_data = []
    
    # スケーリング係数（浮動小数点から整数への変換用）
    COORDINATE_SCALE = 100  # 0.01mm精度
    ROTATION_SCALE = 10     # 0.1度精度
    
    for sector, points in sorted(sector_paths.items()):
        letter = chr(65 + sector)
        sector_counter = 0
        for r, theta in points:
            order = order_map.get((r, theta))
            rotation = theta + math.pi if order == "ascending" else theta
            rotation_degrees = math.degrees(rotation)
            np_x = (r + neo_pixel["offset"]) * math.cos(theta)
            np_y = (r + neo_pixel["offset"]) * math.sin(theta)
            sector_label = f"{letter}{sector_counter}"
            
            neo_data.append({
                'id': len(neo_data),        # 0から始まるIDに変更
                'x': int(round(np_x * COORDINATE_SCALE)),        # int16_t形式
                'y': int(round(-np_y * COORDINATE_SCALE)),       # int16_t形式、Y座標を反転
                'rotation': int(round((rotation_degrees + 90) * ROTATION_SCALE)), # int16_t形式
                'sector': sector,
                'sector_label': sector_label,
                'r': int(round(r * COORDINATE_SCALE)),           # int16_t形式
                'theta_deg': int(round(math.degrees(theta) * ROTATION_SCALE)) # int16_t形式
            })
            sector_counter += 1
    
    # 範囲を計算
    if neo_data:
        x_values = [data['x'] for data in neo_data]
        y_values = [data['y'] for data in neo_data]
        r_values = [data['r'] for data in neo_data]
        theta_values = [data['theta_deg'] for data in neo_data]
        
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        r_min, r_max = min(r_values), max(r_values)
        theta_min, theta_max = min(theta_values), max(theta_values)
    
    # C言語の統合ヘッダーファイルとして出力
    output_file_h = os.path.join(os.path.dirname(__file__), 'neopixel_coordinates.h')
    with open(output_file_h, 'w') as f:
        f.write("#ifndef NEOPIXEL_COORDINATES_H\n")
        f.write("#define NEOPIXEL_COORDINATES_H\n\n")
        f.write("#include <stdint.h>\n")
        f.write("#include <stddef.h>\n\n")
        f.write("// NeoPixel座標データ（整数形式）\n")
        f.write("// 自動生成されたファイル - 手動で編集しないでください\n")
        f.write("// 座標値は0.01mm単位、回転角度は0.1度単位で格納\n")
        f.write("//\n")
        f.write("// データ範囲とスケーリング情報:\n")
        f.write(f"//   ID: 0 ~ {len(neo_data)-1} (total: {len(neo_data)} NeoPixels)\n")
        f.write(f"//   X座標: {x_min} ~ {x_max} (実値: {x_min/COORDINATE_SCALE:.2f}mm ~ {x_max/COORDINATE_SCALE:.2f}mm)\n")
        f.write(f"//   Y座標: {y_min} ~ {y_max} (実値: {y_min/COORDINATE_SCALE:.2f}mm ~ {y_max/COORDINATE_SCALE:.2f}mm)\n")
        f.write(f"//   半径: {r_min} ~ {r_max} (実値: {r_min/COORDINATE_SCALE:.2f}mm ~ {r_max/COORDINATE_SCALE:.2f}mm)\n")
        f.write(f"//   角度: {theta_min} ~ {theta_max} (実値: {theta_min/ROTATION_SCALE:.1f}° ~ {theta_max/ROTATION_SCALE:.1f}°)\n")
        f.write("//\n")
        f.write("// スケーリング係数:\n")
        f.write(f"//   COORDINATE_SCALE = {COORDINATE_SCALE} (座標値を{COORDINATE_SCALE}倍してint16_tに格納)\n")
        f.write(f"//   ROTATION_SCALE = {ROTATION_SCALE} (角度値を{ROTATION_SCALE}倍してint16_tに格納)\n")
        f.write("//\n")
        f.write("// 変換式:\n")
        f.write("//   実座標値[mm] = int16_t値 / COORDINATE_SCALE\n")
        f.write("//   実角度値[°] = int16_t値 / ROTATION_SCALE\n")
        f.write("//   int16_t値 = 実値 * スケール\n\n")
        
        f.write(f"#define NEOPIXEL_COUNT {len(neo_data)}\n")
        f.write("#define COORDINATE_SCALE 100  // 座標値のスケーリング係数（0.01mm単位）\n")
        f.write("#define ROTATION_SCALE 10     // 回転角度のスケーリング係数（0.1度単位）\n\n")
        
        f.write("typedef struct {\n")
        f.write("    int16_t id;\n")
        f.write("    int16_t x;          // X座標 (0.01mm単位)\n")
        f.write("    int16_t y;          // Y座標 (0.01mm単位)\n")
        f.write("    int16_t r;          // 半径 (0.01mm単位)\n")
        f.write("    int16_t theta_deg;  // 角度 (0.1度単位)\n")
        f.write("} NeoPixelCoord;\n\n")
        
        f.write("static const NeoPixelCoord neopixel_coords[NEOPIXEL_COUNT] = {\n")
        for i, data in enumerate(neo_data):
            comma = "," if i < len(neo_data) - 1 else ""
            f.write(f"    {{ {data['id']:3d}, {data['x']:6d}, {data['y']:6d}, "
                   f"{data['r']:6d}, {data['theta_deg']:5d} }}{comma}  // {data['sector_label']}\n")
        f.write("};\n\n")
        
        # 座標変換用のヘルパーマクロ
        f.write("// 座標変換用のヘルパーマクロ\n")
        f.write("#define COORD_TO_FLOAT(coord) ((float)(coord) / COORDINATE_SCALE)\n")
        f.write("#define ROTATION_TO_FLOAT(rot) ((float)(rot) / ROTATION_SCALE)\n")
        f.write("#define FLOAT_TO_COORD(val) ((int16_t)((val) * COORDINATE_SCALE))\n")
        f.write("#define FLOAT_TO_ROTATION(val) ((int16_t)((val) * ROTATION_SCALE))\n\n")
        
        # インライン関数
        f.write("// ユーティリティ関数\n")
        f.write("static inline const NeoPixelCoord* get_neopixel_coord(int16_t id) {\n")
        f.write("    if (id < 0 || id >= NEOPIXEL_COUNT) {\n")
        f.write("        return NULL;\n")
        f.write("    }\n")
        f.write("    return &neopixel_coords[id];\n")
        f.write("}\n\n")
        
        f.write("static inline int16_t get_neopixel_count(void) {\n")
        f.write("    return NEOPIXEL_COUNT;\n")
        f.write("}\n\n")
        
        f.write("#endif // NEOPIXEL_COORDINATES_H\n")
    
    print(f"統合C言語ヘッダーファイル（int16_t形式）を出力しました: {output_file_h}")
    return neo_data

def export_neopixel_c_source(neo_data):
    """NeoPixel用のC言語ソースファイルを出力（便利な関数の実装、int16_t形式）"""
    output_file_c = os.path.join(os.path.dirname(__file__), 'neopixel_coordinates.c')
    with open(output_file_c, 'w') as f:
        f.write('#include "neopixel_coordinates.h"\n')
        f.write('#include <stddef.h>\n')
        f.write('#include <stdint.h>\n\n')
        
        f.write("// IDからNeoPixel座標を取得\n")
        f.write("const NeoPixelCoord* get_neopixel_coord(int16_t id) {\n")
        f.write("    if (id < 0 || id >= NEOPIXEL_COUNT) {\n")
        f.write("        return NULL;\n")
        f.write("    }\n")
        f.write("    return &neopixel_coords[id];\n")
        f.write("}\n\n")
        
        f.write("// NeoPixelの総数を取得\n")
        f.write("int16_t get_neopixel_count(void) {\n")
        f.write("    return NEOPIXEL_COUNT;\n")
        f.write("}\n")
    
    print(f"C言語ソースファイル（int16_t形式）を出力しました: {output_file_c}")

def export_neopixel_c_arrays(sector_paths, order_map, neo_pixel):
    """NeoPixelの座標をC言語の配列形式で出力（int16_t形式）"""
    neo_data = []
    
    # スケーリング係数（浮動小数点から整数への変換用）
    COORDINATE_SCALE = 100  # 0.01mm精度
    ROTATION_SCALE = 10     # 0.1度精度
    
    for sector, points in sorted(sector_paths.items()):
        letter = chr(65 + sector)
        sector_counter = 0
        for r, theta in points:
            order = order_map.get((r, theta))
            rotation = theta + math.pi if order == "ascending" else theta
            rotation_degrees = math.degrees(rotation)
            np_x = (r + neo_pixel["offset"]) * math.cos(theta)
            np_y = (r + neo_pixel["offset"]) * math.sin(theta)
            sector_label = f"{letter}{sector_counter}"
            
            neo_data.append({
                'id': len(neo_data),        # 0から始まるIDに変更
                'x': int(round(np_x * COORDINATE_SCALE)),
                'y': int(round(-np_y * COORDINATE_SCALE)),
                'rotation': int(round((rotation_degrees + 90) * ROTATION_SCALE)),
                'sector': sector,
                'sector_label': sector_label
            })
            sector_counter += 1
    
    # C言語の配列として出力
    output_file_arrays = os.path.join(os.path.dirname(__file__), 'neopixel_arrays.c')
    with open(output_file_arrays, 'w') as f:
        f.write("// NeoPixel座標データ - C言語配列形式（int16_t）\n")
        f.write("// 自動生成されたファイル - 手動で編集しないでください\n")
        f.write("// 座標値は0.01mm単位、回転角度は0.1度単位で格納\n\n")
        f.write("#include <stdint.h>\n\n")
        
        f.write(f"#define NEOPIXEL_COUNT {len(neo_data)}\n")
        f.write("#define COORDINATE_SCALE 100  // 座標値のスケーリング係数（0.01mm単位）\n")
        f.write("#define ROTATION_SCALE 10     // 回転角度のスケーリング係数（0.1度単位）\n\n")
        
        # ID配列
        f.write("const int16_t neopixel_ids[NEOPIXEL_COUNT] = {\n    ")
        ids = [str(data['id']) for data in neo_data]
        f.write(", ".join(ids))
        f.write("\n};\n\n")
        
        # X座標配列
        f.write("const int16_t neopixel_x[NEOPIXEL_COUNT] = {\n    ")
        xs = [f"{data['x']:6d}" for data in neo_data]
        # 20個ずつで改行
        for i in range(0, len(xs), 20):
            if i > 0:
                f.write(",\n    ")
            f.write(", ".join(xs[i:i+20]))
        f.write("\n};\n\n")
        
        # Y座標配列
        f.write("const int16_t neopixel_y[NEOPIXEL_COUNT] = {\n    ")
        ys = [f"{data['y']:6d}" for data in neo_data]
        for i in range(0, len(ys), 20):
            if i > 0:
                f.write(",\n    ")
            f.write(", ".join(ys[i:i+20]))
        f.write("\n};\n\n")
        
        # ラベル配列（文字列）
        f.write("const char* neopixel_labels[NEOPIXEL_COUNT] = {\n    ")
        labels = [f'"{data["sector_label"]}"' for data in neo_data]
        for i in range(0, len(labels), 10):
            if i > 0:
                f.write(",\n    ")
            f.write(", ".join(labels[i:i+10]))
        f.write("\n};\n\n")
        
        # 変換用のヘルパーマクロ
        f.write("// 座標変換用のヘルパーマクロ\n")
        f.write("#define COORD_TO_FLOAT(coord) ((float)(coord) / COORDINATE_SCALE)\n")
        f.write("#define ROTATION_TO_FLOAT(rot) ((float)(rot) / ROTATION_SCALE)\n")
        f.write("#define FLOAT_TO_COORD(val) ((int16_t)((val) * COORDINATE_SCALE))\n")
        f.write("#define FLOAT_TO_ROTATION(val) ((int16_t)((val) * ROTATION_SCALE))\n")
    
    print(f"C言語配列ファイル（int16_t形式）を出力しました: {output_file_arrays}")
    return neo_data

if __name__ == '__main__':
    # テスト用コード
    export_units({}, {}, {}, {})
