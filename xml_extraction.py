"""
xml_extraction.py
-------------------
Extract structured data from .xml files using FOUR different libraries,
each shown separately so you can compare approaches:

    1. xml.etree.ElementTree  : stdlib, simple tree walk -> nested dict
    2. lxml.etree             : fast, supports XPath queries
    3. xmltodict              : XML -> Python dict (mirrors JSON structure) -> JSON
    4. BeautifulSoup (xml)    : forgiving parser, useful for messy/non-strict XML

Input : ../data/xml/*.xml
Output:
    ../output/json/<name>_xml.json                 (xmltodict-based, primary structured output)
    ../output/json/<name>_xml_etree.json            (ElementTree-based nested dict)
    ../output/dataframes/<name>_xml_records.csv     (flattened repeating-record table, if detected)
    ../output/key_value/<name>_xml.txt              (flattened key-value pairs)

Install:
    pip install lxml xmltodict beautifulsoup4 pandas
"""

import json
from pathlib import Path
import xml.etree.ElementTree as ET

from lxml import etree
import xmltodict
from bs4 import BeautifulSoup
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "xml"
OUTPUT_JSON_DIR = BASE_DIR / "output" / "json"
OUTPUT_DF_DIR = BASE_DIR / "output" / "dataframes"
OUTPUT_KV_DIR = BASE_DIR / "output" / "key_value"

for d in (OUTPUT_JSON_DIR, OUTPUT_DF_DIR, OUTPUT_KV_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. xml.etree.ElementTree — nested dict walk
# ---------------------------------------------------------------------------
def etree_element_to_dict(elem: ET.Element):
    node = {}
    if elem.attrib:
        node["@attributes"] = dict(elem.attrib)

    children = list(elem)
    if children:
        child_dict = {}
        for child in children:
            child_data = etree_element_to_dict(child)
            if child.tag not in child_dict:
                child_dict[child.tag] = child_data
            else:
                # Repeated tag -> convert to list
                if not isinstance(child_dict[child.tag], list):
                    child_dict[child.tag] = [child_dict[child.tag]]
                child_dict[child.tag].append(child_data)
        node.update(child_dict)

    text = (elem.text or "").strip()
    if text:
        if children or elem.attrib:
            node["#text"] = text
        else:
            return text  # leaf node with just text

    return node


def extract_with_elementtree(filepath: Path):
    tree = ET.parse(str(filepath))
    root = tree.getroot()
    return {root.tag: etree_element_to_dict(root)}


# ---------------------------------------------------------------------------
# 2. lxml.etree — XPath based extraction (e.g. all leaf text, all attributes)
# ---------------------------------------------------------------------------
def extract_with_lxml_xpath(filepath: Path):
    tree = etree.parse(str(filepath))
    root = tree.getroot()

    all_text_nodes = [t.strip() for t in root.xpath("//text()") if t.strip()]
    all_attributes = []
    for elem in root.iter():
        if elem.attrib:
            all_attributes.append({"tag": elem.tag, "attributes": dict(elem.attrib)})

    return {
        "root_tag": root.tag,
        "all_text_nodes": all_text_nodes,
        "elements_with_attributes": all_attributes,
    }


# ---------------------------------------------------------------------------
# 3. xmltodict — XML -> dict -> JSON (most direct structured mapping)
# ---------------------------------------------------------------------------
def extract_with_xmltodict(filepath: Path):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    data_dict = xmltodict.parse(content)
    return json.loads(json.dumps(data_dict))  # ensure plain JSON-serializable dict


# ---------------------------------------------------------------------------
# 4. BeautifulSoup (xml parser) — forgiving parse for messy XML
# ---------------------------------------------------------------------------
def extract_with_bs4(filepath: Path):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    soup = BeautifulSoup(content, "xml")
    # Grab top-level repeating tags as flat key-value candidates
    kv_pairs = {}
    for tag in soup.find_all():
        if tag.find() is None:  # leaf node
            text = tag.get_text(strip=True)
            if text:
                kv_pairs[tag.name] = text
    return kv_pairs


# ---------------------------------------------------------------------------
# Try to flatten repeating records into a DataFrame (common for feeds/catalogs)
# ---------------------------------------------------------------------------
def try_flatten_records(xmltodict_data: dict):
    """
    Heuristic: find the first list-of-dicts nested anywhere in the structure
    and flatten it into a DataFrame (e.g. RSS <item> elements, catalog <product> entries).
    """
    def find_list_of_dicts(node):
        if isinstance(node, dict):
            for v in node.values():
                if isinstance(v, list) and v and all(isinstance(i, dict) for i in v):
                    return v
                result = find_list_of_dicts(v)
                if result is not None:
                    return result
        return None

    records = find_list_of_dicts(xmltodict_data)
    if records:
        return pd.json_normalize(records)
    return None


def process_xml_file(filepath: Path):
    etree_data = extract_with_elementtree(filepath)
    xpath_data = extract_with_lxml_xpath(filepath)
    xmltodict_data = extract_with_xmltodict(filepath)
    bs4_kv = extract_with_bs4(filepath)

    structured = {
        "source_file": filepath.name,
        "xmltodict_structure": xmltodict_data,
        "lxml_xpath_summary": xpath_data,
        "bs4_leaf_key_values": bs4_kv,
    }

    # ---- Save primary JSON (xmltodict-based) ----
    json_path = OUTPUT_JSON_DIR / f"{filepath.stem}_xml.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # ---- Save ElementTree-based JSON separately ----
    etree_json_path = OUTPUT_JSON_DIR / f"{filepath.stem}_xml_etree.json"
    with open(etree_json_path, "w", encoding="utf-8") as f:
        json.dump(etree_data, f, indent=2, ensure_ascii=False)

    # ---- Save flattened records as DataFrame, if any repeating structure found ----
    df = try_flatten_records(xmltodict_data)
    if df is not None and not df.empty:
        df_path = OUTPUT_DF_DIR / f"{filepath.stem}_xml_records.csv"
        df.to_csv(df_path, index=False)

    # ---- Save key-value text ----
    kv_path = OUTPUT_KV_DIR / f"{filepath.stem}_xml.txt"
    with open(kv_path, "w", encoding="utf-8") as f:
        for k, v in bs4_kv.items():
            f.write(f"{k}: {v}\n")

    print(f"[OK] Processed {filepath.name} -> {json_path.name}")
    return structured


def main():
    xml_files = list(INPUT_DIR.glob("*.xml"))
    if not xml_files:
        print(f"No .xml files found in {INPUT_DIR}")
        return

    for filepath in xml_files:
        try:
            process_xml_file(filepath)
        except Exception as e:
            print(f"[ERROR] Failed to process {filepath.name}: {e}")


if __name__ == "__main__":
    main()