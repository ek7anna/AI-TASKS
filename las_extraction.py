"""
las_extraction.py
-------------------
Extract structured data from .las (Log ASCII Standard, well-log) files using lasio.

Captures:
    - Well header metadata (well name, UWI, location, dates, etc.)
    - Curve/channel definitions (mnemonic, unit, description)
    - Parameter section (if present)
    - Full curve data as a DataFrame (depth-indexed log curves)

Input : ../data/las/*.las
Output:
    ../output/json/<name>_las.json           (metadata + curve definitions)
    ../output/dataframes/<name>_las_curves.csv  (full depth vs curve-value table)
    ../output/key_value/<name>_las.txt       (well header key-value pairs)

Install:
    pip install lasio pandas
"""

import json
from pathlib import Path

import lasio
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "las"
OUTPUT_JSON_DIR = BASE_DIR / "output" / "json"
OUTPUT_DF_DIR = BASE_DIR / "output" / "dataframes"
OUTPUT_KV_DIR = BASE_DIR / "output" / "key_value"

for d in (OUTPUT_JSON_DIR, OUTPUT_DF_DIR, OUTPUT_KV_DIR):
    d.mkdir(parents=True, exist_ok=True)


def extract_header_section(las: lasio.LASFile, section_name: str):
    """Generic extractor for Well/Params/Curves metadata sections."""
    items = {}
    section = getattr(las, section_name, None)
    if section is None:
        return items
    for item in section:
        items[item.mnemonic] = {
            "unit": item.unit,
            "value": str(item.value),
            "descr": item.descr,
        }
    return items


def process_las_file(filepath: Path):
    las = lasio.read(str(filepath))

    well_info = extract_header_section(las, "well")
    curve_info = extract_header_section(las, "curves")
    params_info = extract_header_section(las, "params")

    df = las.df()  # depth-indexed DataFrame of all curves
    df = df.reset_index()  # bring depth index into a normal column

    structured = {
        "source_file": filepath.name,
        "version": {
            v.mnemonic: str(v.value) for v in las.version
        } if las.version else {},
        "well": well_info,
        "curves": curve_info,
        "parameters": params_info,
        "num_data_rows": len(df),
        "num_curves": len(las.curves),
        "curve_mnemonics": [c.mnemonic for c in las.curves],
    }

    # ---- Save JSON (metadata only, data goes to CSV) ----
    json_path = OUTPUT_JSON_DIR / f"{filepath.stem}_las.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # ---- Save curve data as DataFrame/CSV ----
    df_path = OUTPUT_DF_DIR / f"{filepath.stem}_las_curves.csv"
    df.to_csv(df_path, index=False)

    # ---- Save well header as key-value text ----
    kv_path = OUTPUT_KV_DIR / f"{filepath.stem}_las.txt"
    with open(kv_path, "w", encoding="utf-8") as f:
        for k, v in well_info.items():
            f.write(f"{k}: {v['value']} ({v['unit']}) - {v['descr']}\n")

    print(f"[OK] Processed {filepath.name} -> {json_path.name}")
    return structured


def main():
    las_files = list(INPUT_DIR.glob("*.las"))
    if not las_files:
        print(f"No .las files found in {INPUT_DIR}")
        return

    for filepath in las_files:
        try:
            process_las_file(filepath)
        except Exception as e:
            print(f"[ERROR] Failed to process {filepath.name}: {e}")


if __name__ == "__main__":
    main()