# Extracted OCR & Personal Information Anonymizer (PII Guard)

This toolkit contains the extracted and standalone versions of the **OCR & Document Ingestion Engine** and the **Multi-Layer Personal Information Anonymizer** from **Vexis-Law**.

---

## 📁 Toolkit Contents

| File | Purpose |
| :--- | :--- |
| `ocr_engine.py` | Standalone document ingestion & OCR engine (PDF, Images, Tesseract C++ integration, Indian scripts). |
| `pii_anonymizer.py` | Standalone, pure-Python multi-layer PII scrubber & single-pass de-anonymizer. |
| `extract_and_anonymize.py` | Unified end-to-end CLI to extract text from a file, mask PII, and de-anonymize. |
| `names_dict.jsonl` | Bundled database of 2,622 Indian personal names for high-precision Aho-Corasick/Trie matching. |
| `gazetteer.jsonl` | Gazetteer of known enterprise and party entities. |
| `sample_legal_document.txt` | Sample legal document for testing and verification. |

---

## 🔍 1. OCR Engine Architecture (`ocr_engine.py`)

Derived from `backend/ingestion/extract_pdf.py` and the bundled C++ Tesseract engine.

### Capabilities:
- **Hybrid Extraction**:
  - **Native Text Layer**: Uses PyMuPDF (`fitz`) for digitally created PDFs (instant, millisecond extraction).
  - **OCR Layer**: For scanned PDFs, photos, or images (`.png`, `.jpg`, `.tif`, `.webp`, `.heic`), rasterizes at **300 DPI** and feeds to **Tesseract C++ Engine**.
- **Preprocessing Pipeline**:
  - **EXIF Auto-Orientation**: Handles phone camera orientation tags.
  - **Illumination Flattening**: Gaussian background-division filter that removes lighting variations, shadows, and camera glare.
  - **Dynamic Otsu Thresholding & Deskewing**: Re-aligns skewed pages and maximizes ink-to-paper separation.
- **Multilingual Indian Script Support**:
  - Ships with `eng` and `hin` (Devanagari) models.
  - Maps all 22 Eighth Schedule Indian languages to their native or script fallbacks.
- **Structured Quality Confidence**:
  - Flags low-confidence pages (<70%) to prevent hallucination or missed PII.

### Usage:
```bash
# Extract text as JSON
python ocr_engine.py sample_scan.pdf

# Extract raw text directly
python ocr_engine.py document.png --raw
```

---

## 🛡️ 2. Personal Information Anonymizer (`pii_anonymizer.py`)

Derived from `backend/anonymiser/` (Rust crate) and `backend/deanonymiser/`.

### Capabilities:
- **Layer 2: Structured PII Detection**:
  - **Aadhaar**: 12-digit grouped runs (with `rejects_year_run` to prevent masking year sequences).
  - **PAN Card**: 10-character alphanumeric Indian Tax IDs (`AAAAA0000A`).
  - **Phone / Mobile**: 10-digit numbers, +91 prefixes, spaced formats (with amount-pair guards).
  - **Email Addresses**: Standard RFC email addresses.
  - **Voter ID / EPIC**: Indian voter registration IDs.
  - **Vehicle Registration**: Indian number plates (`DL 01 AB 1234`).
  - **Bank Accounts / Cards**: 16-digit card numbers and account runs.
  - **FIR / Case Numbers**: FIR/Crime case markers.
  - **Honorific Names**: Names introduced by `Mr.`, `Mrs.`, `Shri`, `Smt.`, `Dr.`, `Prof.`.
- **Layer 2: Dictionary Matching**:
  - High-speed dictionary lookups across 2,622 Indian given names and surnames.
- **Layer 3: Contextual Indian Legal Rules**:
  - **Relational Cues**: `S/o`, `D/o`, `W/o`, `C/o`, `son of`, `daughter of`, `wife of` + Name.
  - **Party Roles**: `Petitioner`, `Respondent`, `Complainant`, `Accused`, `Appellant`, `Defendant`.
  - **Aliases**: `alias`, `@`, `known as`, `also known as`.
  - **Address Cues**: `resident of`, `residing at`, `House No.`, `Flat No.`, `Plot No.`.
- **Must-Not-Mask Exclusions (Critical Legal Shield)**:
  - **Presiding Judicial Officers**: `Hon'ble Mr. Justice <Name>`, `Chief Judicial Magistrate <Name>`, `<Name>, J.` are **strictly preserved**.
  - **Legal Statutes**: `Indian Penal Code`, `CrPC`, `BNS`, `Constitution of India` are **strictly preserved**.
  - **Designation Trimming**: Professional titles (e.g. `Forensic Auditor`, `Advocate`, `Inspector`) are trimmed so they are never masked as part of a name.
- **Identity Resolution & Deduplication**:
  - Repeated mentions of the same entity map to the exact same token (`<<Person_1>>`, `<<Aadhaar_1>>`).
- **Single-Pass De-anonymizer**:
  - Safely substitutes tokens back in one left-to-right pass without recursive cascading leaks.

### Usage:
```bash
# Anonymize text
python pii_anonymizer.py --anonymize input.txt -o anonymized.txt -m variable_map.json

# De-anonymize (restore) text
python pii_anonymizer.py --deanonymize anonymized.txt -m variable_map.json -o restored.txt
```

---

## 🚀 3. End-to-End Pipeline (`extract_and_anonymize.py`)

Run OCR extraction and PII scrubbing in a single command:

```bash
# Run OCR + PII Anonymization on any PDF or Image
python extract_and_anonymize.py document.pdf

# Restore the original text from the anonymized output
python extract_and_anonymize.py --deanonymize document.anonymized.txt --map-in document.variable_map.json
```

---

## 🦀 4. Compiling the Standalone Rust Anonymiser Crate

If you prefer running the ultra-high performance native Rust crate (`backend/anonymiser`):

1. Navigate to the backend directory:
   ```bash
   cd Vexis-Law-main/backend
   ```
2. Build the anonymiser crate:
   ```bash
   cargo build --release -p anonymiser --bin suggest_labels
   ```
3. Run test suites:
   ```bash
   cargo test -p anonymiser
   ```
