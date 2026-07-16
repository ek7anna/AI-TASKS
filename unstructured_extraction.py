"""
unstructured_extraction.py
----------------------------
Unified multi-format extraction using the `unstructured` library
(https://unstructured.io). Automatically detects file type and partitions
it into a list of typed "elements" (Title, NarrativeText, Table, ListItem,
Image, etc.) — useful as a single entry point covering PDF, DOCX, PPTX,
HTML, XML, CSV/XLSX, TXT, EML and more with one consistent API.

This script scans ALL supported files across the sibling format folders
(../data/pdf, ../data/docx, ../data/pptx, ../data/html, ../data/xml,
../data/excel) plus any files directly under ../data/, and partitions
each with `unstructured.partition.auto.partition`.

Output (per file):
    ../output/json/<name>_unstructured.json     (full element list, RAG-ready chunks)
    ../output/dataframes/<name>_unstructured_tables.csv  (extracted tables, if any)
    ../output/key_value/<name>_unstructured.txt (element type counts + metadata)

Install:
    pip install "unstructured[all-docs]" pandas
    # Some formats (pdf/docx/pptx) additionally need poppler/libreoffice
    # system dependencies - see unstructured.io docs for your OS.
"""

import json
from pathlib import Path

import pandas as pd
from unstructured.partition.auto import partition

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_JSON_DIR = BASE_DIR / "output" / "json"
OUTPUT_DF_DIR = BASE_DIR / "output" / "dataframes"
OUTPUT_KV_DIR = BASE_DIR / "output" / "key_value"

for d in (OUTPUT_JSON_DIR, OUTPUT_DF_DIR, OUTPUT_KV_DIR):
    d.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".html", ".htm",
    ".xml", ".xlsx", ".xls", ".csv", ".txt", ".eml", ".msg",
}


def find_all_supported_files():
    """Recursively find every supported file under ../data/ (all format subfolders)."""
    files = []
    for path in DATA_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
    return files


def element_to_dict(element):
    """Convert an unstructured Element object into a plain JSON-serializable dict."""
    return {
        "type": element.category,
        "text": str(element),
        "metadata": element.metadata.to_dict() if element.metadata else {},
    }


def process_file(filepath: Path):
    elements = partition(filename=str(filepath))
    element_dicts = [element_to_dict(e) for e in elements]

    # Count element types (useful quick summary / key-value output)
    type_counts = {}
    for e in element_dicts:
        type_counts[e["type"]] = type_counts.get(e["type"], 0) + 1

    # Collect any table-type elements into DataFrames (unstructured stores
    # table HTML in metadata.text_as_html when available)
    table_rows = []
    for e in element_dicts:
        if e["type"] == "Table":
            html_table = e["metadata"].get("text_as_html")
            if html_table:
                try:
                    dfs = pd.read_html(html_table)
                    table_rows.extend(dfs)
                except ValueError:
                    pass

    structured = {
        "source_file": filepath.name,
        "source_relative_path": str(filepath.relative_to(DATA_DIR)),
        "num_elements": len(element_dicts),
        "element_type_counts": type_counts,
        "elements": element_dicts,
    }

    # ---- Save JSON ----
    json_path = OUTPUT_JSON_DIR / f"{filepath.stem}_unstructured.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # ---- Save extracted tables, if any ----
    for i, df in enumerate(table_rows):
        df_path = OUTPUT_DF_DIR / f"{filepath.stem}_unstructured_table{i}.csv"
        df.to_csv(df_path, index=False)

    # ---- Save key-value summary ----
    kv_path = OUTPUT_KV_DIR / f"{filepath.stem}_unstructured.txt"
    with open(kv_path, "w", encoding="utf-8") as f:
        f.write(f"source_file: {filepath.name}\n")
        f.write(f"num_elements: {len(element_dicts)}\n")
        for k, v in type_counts.items():
            f.write(f"element_type::{k}: {v}\n")

    print(f"[OK] Processed {filepath.relative_to(DATA_DIR)} -> {json_path.name}")
    return structured


def main():
    files = find_all_supported_files()
    if not files:
        print(f"No supported files found under {DATA_DIR}")
        return

    for filepath in files:
        try:
            process_file(filepath)
        except Exception as e:
            print(f"[ERROR] Failed to process {filepath}: {e}")


if __name__ == "__main__":
    main()