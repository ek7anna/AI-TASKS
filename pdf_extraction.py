"""
pdf_extraction.py
-------------------
Extract structured data from .pdf files using FOUR libraries, each suited
to a different job:

    - pdfplumber : text + simple table extraction, per-page, with layout info
    - PyMuPDF (fitz) : fast text extraction, metadata, images, per-page dicts
    - pypdf      : metadata, page count, basic text (lightweight fallback)
    - camelot-py : high-accuracy table extraction (lattice/stream modes)

Input : ../data/pdf/*.pdf
Output:
    ../output/json/<name>_pdf.json
    ../output/dataframes/<name>_pdf_table<i>.csv      (camelot tables)
    ../output/key_value/<name>_pdf.txt                (document metadata)

Install:
    pip install pdfplumber PyMuPDF pypdf camelot-py[cv] pandas
    # camelot-py also needs Ghostscript installed on the system.
"""

import json
from pathlib import Path

import pdfplumber
import fitz  # PyMuPDF
import pypdf
import camelot
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "pdf"
OUTPUT_JSON_DIR = BASE_DIR / "output" / "json"
OUTPUT_DF_DIR = BASE_DIR / "output" / "dataframes"
OUTPUT_KV_DIR = BASE_DIR / "output" / "key_value"

for d in (OUTPUT_JSON_DIR, OUTPUT_DF_DIR, OUTPUT_KV_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# pypdf — lightweight metadata + page count + fallback text
# ---------------------------------------------------------------------------
def extract_metadata_pypdf(filepath: Path):
    reader = pypdf.PdfReader(str(filepath))
    meta = reader.metadata or {}
    return {
        "num_pages": len(reader.pages),
        "title": meta.get("/Title", ""),
        "author": meta.get("/Author", ""),
        "subject": meta.get("/Subject", ""),
        "creator": meta.get("/Creator", ""),
        "producer": meta.get("/Producer", ""),
        "creation_date": str(meta.get("/CreationDate", "")),
        "is_encrypted": reader.is_encrypted,
    }


# ---------------------------------------------------------------------------
# pdfplumber — per-page text + simple tables + layout (word bounding boxes)
# ---------------------------------------------------------------------------
def extract_with_pdfplumber(filepath: Path):
    pages_data = []
    with pdfplumber.open(str(filepath)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables()
            pages_data.append({
                "page_number": i + 1,
                "text": text.strip(),
                "tables": tables,  # list of list-of-rows
                "width": page.width,
                "height": page.height,
            })
    return pages_data


# ---------------------------------------------------------------------------
# PyMuPDF (fitz) — fast text extraction + images + document metadata
# ---------------------------------------------------------------------------
def extract_with_pymupdf(filepath: Path):
    doc = fitz.open(str(filepath))
    pages_data = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        image_list = page.get_images(full=True)
        pages_data.append({
            "page_number": i + 1,
            "text": text.strip(),
            "num_images": len(image_list),
        })
    doc_meta = doc.metadata
    doc.close()
    return pages_data, doc_meta


# ---------------------------------------------------------------------------
# camelot-py — high-accuracy table extraction
# ---------------------------------------------------------------------------
def extract_tables_camelot(filepath: Path):
    tables = []
    for flavor in ("lattice", "stream"):
        try:
            camelot_tables = camelot.read_pdf(str(filepath), pages="all", flavor=flavor)
            for t in camelot_tables:
                tables.append(t.df)  # pandas DataFrame
            if camelot_tables.n > 0:
                break  # stop once one flavor successfully finds tables
        except Exception:
            continue
    return tables


def extract_key_value_pairs(pypdf_meta: dict):
    return {k: v for k, v in pypdf_meta.items() if v not in ("", None)}


def process_pdf_file(filepath: Path):
    pypdf_meta = extract_metadata_pypdf(filepath)
    pdfplumber_pages = extract_with_pdfplumber(filepath)
    pymupdf_pages, pymupdf_meta = extract_with_pymupdf(filepath)
    camelot_tables = extract_tables_camelot(filepath)
    key_values = extract_key_value_pairs(pypdf_meta)

    structured = {
        "source_file": filepath.name,
        "metadata_pypdf": pypdf_meta,
        "metadata_pymupdf": pymupdf_meta,
        "pages_pdfplumber": pdfplumber_pages,
        "pages_pymupdf": pymupdf_pages,
        "num_camelot_tables": len(camelot_tables),
        "key_value_pairs": key_values,
    }

    # ---- Save JSON ----
    json_path = OUTPUT_JSON_DIR / f"{filepath.stem}_pdf.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # ---- Save camelot tables as CSV/DataFrame ----
    for i, df in enumerate(camelot_tables):
        df_path = OUTPUT_DF_DIR / f"{filepath.stem}_pdf_table{i}.csv"
        df.to_csv(df_path, index=False)

    # ---- Also save any pdfplumber tables not caught by camelot ----
    pdfplumber_table_idx = 0
    for page in pdfplumber_pages:
        for table in page["tables"]:
            if not table:
                continue
            df = pd.DataFrame(table[1:], columns=table[0]) if len(table) > 1 else pd.DataFrame(table)
            df_path = OUTPUT_DF_DIR / f"{filepath.stem}_pdf_plumber_table{pdfplumber_table_idx}.csv"
            df.to_csv(df_path, index=False)
            pdfplumber_table_idx += 1

    # ---- Save key-value text ----
    kv_path = OUTPUT_KV_DIR / f"{filepath.stem}_pdf.txt"
    with open(kv_path, "w", encoding="utf-8") as f:
        for k, v in key_values.items():
            f.write(f"{k}: {v}\n")

    print(f"[OK] Processed {filepath.name} -> {json_path.name}")
    return structured


def main():
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No .pdf files found in {INPUT_DIR}")
        return

    for filepath in pdf_files:
        try:
            process_pdf_file(filepath)
        except Exception as e:
            print(f"[ERROR] Failed to process {filepath.name}: {e}")


if __name__ == "__main__":
    main()