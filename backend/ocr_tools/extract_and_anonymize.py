#!/usr/bin/env python3
"""
extract_and_anonymize.py — End-to-End OCR & Personal Information Anonymization Pipeline
Combines Vexis-Law's OCR Document Ingestion and Multi-Layer Legal PII Masker into a unified CLI.

Workflow:
1. Ingestion & OCR: Reads native text or scans using bundled Tesseract C++ Engine with 300 DPI preprocessing.
2. PII Anonymization: Scrub personal identifiers (PAN, Aadhaar, Phone, Email, Voter ID, Names, Addresses)
   while strictly preserving Judicial Officers (Judges, Magistrates) and Legal Statutes.
3. Outputs Anonymized Document + Variable Map (token -> real identity).
4. Provides 1-step De-anonymization.

Usage:
    python extract_and_anonymize.py <document_path> [options]
    python extract_and_anonymize.py --deanonymize <anonymized_txt> --map <variable_map.json>
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Local imports from extracted_tools
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_engine import extract_document
from pii_anonymizer import AnonymizerEngine, deanonymise


def process_document(file_path: str, output_txt: str = None, map_path: str = None, langs: str = "eng+hin"):
    path = Path(file_path).resolve()
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[1/3] Ingesting & performing OCR on '{path.name}'...")
    ocr_res = extract_document(str(path), langs=langs)
    if "error" in ocr_res:
        print(f"Extraction error: {ocr_res['error']}", file=sys.stderr)
        sys.exit(1)

    raw_text = ocr_res.get("extracted_text", "")
    pages = ocr_res.get("pages", 1)
    ocr_pages = ocr_res.get("ocr_pages", 0)
    warnings = ocr_res.get("warnings", [])

    print(f"      Extracted {len(raw_text)} characters across {pages} page(s) (OCR used on {ocr_pages} page(s)).")
    if warnings:
        print(f"      Extraction Warnings: {warnings}")

    print(f"[2/3] Running Personal Information Anonymization (PII Scrubbing)...")
    engine = AnonymizerEngine()
    anon_res = engine.anonymize(raw_text)

    anonymized_text = anon_res["anonymised_text"]
    variable_map = anon_res["variable_map"]
    entity_count = anon_res["entity_count"]
    stats = anon_res["stats"]

    print(f"      Masked {entity_count} entities: {stats}")

    # Output paths
    base_name = path.stem
    out_dir = path.parent
    if not output_txt:
        output_txt = str(out_dir / f"{base_name}.anonymized.txt")
    if not map_path:
        map_path = str(out_dir / f"{base_name}.variable_map.json")

    print(f"[3/3] Saving results...")
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(anonymized_text)
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(variable_map, f, indent=2, ensure_ascii=False)

    print(f"\n[DONE] Anonymized document saved to: {output_txt}")
    print(f"       Reversible variable map saved to: {map_path}\n")

    # Quick preview
    preview_len = min(400, len(anonymized_text))
    print("--- ANONYMIZED TEXT PREVIEW ---")
    print(anonymized_text[:preview_len] + ("..." if len(anonymized_text) > preview_len else ""))
    print("--------------------------------\n")


def main():
    parser = argparse.ArgumentParser(description="End-to-End OCR and PII Anonymizer CLI")
    parser.add_argument("file", nargs="?", help="Document file to process (PDF, image, docx, txt)")
    parser.add_argument("--output", "-o", help="Path to save anonymized text file")
    parser.add_argument("--map", "-m", help="Path to save variable map JSON")
    parser.add_argument("--langs", "-l", default="eng+hin", help="OCR languages (default: eng+hin)")
    parser.add_argument("--deanonymize", "-d", action="store_true", help="De-anonymize an existing file")
    parser.add_argument("--map-in", help="Input variable map JSON for de-anonymization")

    args = parser.parse_args()

    if args.deanonymize:
        if not args.file or not args.map_in:
            print("Error: --deanonymize requires an input file and --map-in <variable_map.json>", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            anon_content = f.read()
        with open(args.map_in, "r", encoding="utf-8") as f:
            vmap = json.load(f)
        restored = deanonymise(anon_content, vmap)
        out_path = args.output or str(Path(args.file).with_suffix(".restored.txt"))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(restored)
        print(f"[SUCCESS] De-anonymized document restored to: {out_path}")
    elif args.file:
        process_document(args.file, output_txt=args.output, map_path=args.map, langs=args.langs)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
