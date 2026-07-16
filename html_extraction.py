"""
html_extraction.py
-------------------
Extract structured data from .html files using:
    - BeautifulSoup (bs4) : forgiving HTML parsing, tag/text extraction
    - lxml                : fast XPath-based extraction (used as bs4's parser
                            and directly for XPath queries)

Captures:
    - title, meta tags
    - headings (h1-h6) with hierarchy
    - paragraphs
    - links (text + href)
    - tables -> DataFrames
    - simple key-value pairs from <dl>/<dt>/<dd> and definition-like tables

Input : ../data/html/*.html (also *.htm)
Output:
    ../output/json/<name>_html.json
    ../output/dataframes/<name>_html_table<i>.csv
    ../output/key_value/<name>_html.txt

Install:
    pip install beautifulsoup4 lxml pandas
"""

import json
from pathlib import Path

from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "html"
OUTPUT_JSON_DIR = BASE_DIR / "output" / "json"
OUTPUT_DF_DIR = BASE_DIR / "output" / "dataframes"
OUTPUT_KV_DIR = BASE_DIR / "output" / "key_value"

for d in (OUTPUT_JSON_DIR, OUTPUT_DF_DIR, OUTPUT_KV_DIR):
    d.mkdir(parents=True, exist_ok=True)


def extract_meta(soup: BeautifulSoup):
    meta = {}
    if soup.title and soup.title.string:
        meta["title"] = soup.title.string.strip()
    for tag in soup.find_all("meta"):
        name = tag.get("name") or tag.get("property")
        content = tag.get("content")
        if name and content:
            meta[name] = content
    return meta


def extract_headings(soup: BeautifulSoup):
    headings = []
    for level in range(1, 7):
        for tag in soup.find_all(f"h{level}"):
            text = tag.get_text(strip=True)
            if text:
                headings.append({"level": level, "text": text})
    return headings


def extract_paragraphs(soup: BeautifulSoup):
    return [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]


def extract_links(soup: BeautifulSoup):
    links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        links.append({"text": text, "href": a["href"]})
    return links


def extract_tables_bs4(soup: BeautifulSoup):
    """Return list of tables as list-of-rows."""
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def extract_definition_lists(soup: BeautifulSoup):
    """<dl><dt>Key</dt><dd>Value</dd></dl> -> key-value pairs."""
    kv_pairs = {}
    for dl in soup.find_all("dl"):
        terms = dl.find_all("dt")
        defs = dl.find_all("dd")
        for dt, dd in zip(terms, defs):
            key = dt.get_text(strip=True)
            value = dd.get_text(strip=True)
            if key and value:
                kv_pairs[key] = value
    return kv_pairs


def extract_with_lxml_xpath(filepath: Path):
    """Demonstrate XPath-based extraction via lxml (e.g. all text under <article>)."""
    parser = etree.HTMLParser()
    tree = etree.parse(str(filepath), parser)
    article_text = tree.xpath("//article//text()")
    article_text = [t.strip() for t in article_text if t.strip()]
    return article_text


def process_html_file(filepath: Path):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "lxml")  # bs4 using lxml parser

    meta = extract_meta(soup)
    headings = extract_headings(soup)
    paragraphs = extract_paragraphs(soup)
    links = extract_links(soup)
    tables = extract_tables_bs4(soup)
    dl_kv = extract_definition_lists(soup)
    article_text_xpath = extract_with_lxml_xpath(filepath)

    structured = {
        "source_file": filepath.name,
        "meta": meta,
        "headings": headings,
        "paragraphs": paragraphs,
        "links": links,
        "num_tables": len(tables),
        "tables": tables,
        "key_value_pairs": dl_kv,
        "article_text_via_xpath": article_text_xpath,
    }

    # ---- Save JSON ----
    json_path = OUTPUT_JSON_DIR / f"{filepath.stem}_html.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # ---- Save DataFrame(s) ----
    for i, table in enumerate(tables):
        if not table:
            continue
        df = pd.DataFrame(table[1:], columns=table[0]) if len(table) > 1 else pd.DataFrame(table)
        df_path = OUTPUT_DF_DIR / f"{filepath.stem}_html_table{i}.csv"
        df.to_csv(df_path, index=False)

    # ---- Save key-value text ----
    kv_path = OUTPUT_KV_DIR / f"{filepath.stem}_html.txt"
    with open(kv_path, "w", encoding="utf-8") as f:
        for k, v in dl_kv.items():
            f.write(f"{k}: {v}\n")

    print(f"[OK] Processed {filepath.name} -> {json_path.name}")
    return structured


def main():
    html_files = list(INPUT_DIR.glob("*.html")) + list(INPUT_DIR.glob("*.htm"))
    if not html_files:
        print(f"No .html/.htm files found in {INPUT_DIR}")
        return

    for filepath in html_files:
        try:
            process_html_file(filepath)
        except Exception as e:
            print(f"[ERROR] Failed to process {filepath.name}: {e}")


if __name__ == "__main__":
    main()