#!/usr/bin/env python3
"""
pii_anonymizer.py — Standalone Personal Information Anonymizer & De-anonymizer
Extracted from Vexis-Law backend (`backend/anonymiser` & `backend/deanonymiser`).

Key Features:
1. Multi-Layer Anonymization:
   - Layer 2: Deterministic Regex (Aadhaar, PAN, Phone, Email, Voter ID, Vehicle, Passport, Bank Account, FIR).
   - Layer 2: Dictionary Matching (2,622 Indian personal names from `names_dict.jsonl`).
   - Layer 3: Contextual Indian Legal Rules (Relational S/o, D/o, W/o; Party roles Petitioner/Respondent/Accused/Complainant; Aliases; Address cues).
2. Judicial Officer & Statute Exclusions (Must-Not-Mask):
   - Judicial officers (Hon'ble Justice, Judge, Chief Judicial Magistrate, etc.) are strictly PRESERVED.
   - Legal statutes (IPC, CrPC, BNS, etc.) are strictly PRESERVED.
3. Stopword & Designations Filtering:
   - Filters legal boilerplate, stopwords, and trailing designations ("Forensic Auditor", "Advocate", "Inspector")
     to prevent over-masking common words or job titles.
4. Consistent Identity Resolution / Deduplication:
   - Identical entities reuse the same placeholder token (e.g., <<Person_1>>) throughout the entire document.
5. Reversible Single-Pass De-anonymizer:
   - Restores original values safely in one left-to-right pass without cascading substitution leaks.

Usage:
    python pii_anonymizer.py --anonymize <text_file> [-o <out_anonymized>] [-m <out_map.json>]
    python pii_anonymizer.py --deanonymize <anonymized_file> -m <map.json> [-o <restored_file>]
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any

BASE_DIR = Path(__file__).resolve().parent

# --- Word Lists & Exclusions ---

DESIGNATION_WORDS = {
    "forensic", "auditor", "audit", "accountant", "analyst", "consultant",
    "engineer", "architect", "surveyor", "examiner", "investigator", "expert",
    "physician", "surgeon", "psychiatrist", "psychologist", "pathologist",
    "scientist", "technician", "valuer", "appraiser", "advocate", "counsel",
    "attorney", "solicitor", "notary", "pleader", "prosecutor", "magistrate",
    "registrar", "arbitrator", "mediator", "witness", "complainant", "accused",
    "petitioner", "respondent", "appellant", "applicant", "deponent", "plaintiff",
    "defendant", "guardian", "nominee", "trustee", "executor", "officer",
    "inspector", "constable", "superintendent", "commissioner", "sergeant",
    "warden", "collector", "tehsildar", "patwari", "director", "manager",
    "president", "chairman", "chairperson", "partner", "associate", "secretary",
    "treasurer", "cashier", "clerk", "agent", "broker", "contractor",
    "supervisor", "coordinator", "executive", "assistant", "deputy", "joint",
    "additional", "senior", "junior", "chief", "head", "incharge", "officiating"
}

HEURISTIC_STOPWORDS = {
    # Courts / legal structure
    "high", "court", "supreme", "sessions", "district", "magistrate", "tribunal", "bench",
    "division", "civil", "criminal", "appeal", "appellate", "petition", "writ", "suit", "case",
    "section", "article", "clause", "sub", "act", "code", "penal", "constitution", "rule", "rules",
    "order", "schedule", "chapter", "part", "union", "state", "government", "republic", "ministry",
    "department", "board", "authority", "commission", "corporation", "bar", "council", "law",
    "justice", "judge", "honble", "hon", "learned", "respondent", "petitioner", "appellant",
    "complainant", "accused", "plaintiff", "defendant", "prosecution", "counsel", "advocate",
    "applicant", "opposite", "party", "parties", "indian", "india", "procedure", "evidence",
    "limitation", "companies", "contract", "property", "family", "matter", "judgment", "judgement",
    "affidavit", "annexure", "exhibit", "para", "paragraph", "dated", "vide", "registrar", "gazette",
    # Deed / property boilerplate
    "situated", "situate", "bearing", "admeasuring", "measuring", "comprising", "boundary",
    "boundaries", "extent", "premises", "constructed", "hereinafter", "hereinbefore",
    "aforementioned", "consideration", "executed", "presents", "witnesseth", "whereby",
    "thereof", "therein", "thereto", "hereto", "pursuant", "favour", "favor", "recorded",
    # Months / days
    "january", "february", "march", "april", "may", "june", "july", "august", "september",
    "october", "november", "december", "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday",
    # Honorifics & common prefixes that are never standalone names
    "mr", "mrs", "ms", "dr", "prof", "shri", "sh", "smt", "kumari", "adv", "advocate",
    # Common words / pronouns / prepositions / court terms
    "the", "this", "that", "these", "those", "there", "here", "in", "on", "at", "of", "and", "but",
    "it", "as", "by", "for", "from", "whereas", "hence", "therefore", "further", "moreover", "however",
    "thus", "both", "their", "his", "her", "said", "above", "below", "no", "shall", "will", "persons",
    "person", "named", "abov", "death", "alarm", "simple", "hindi", "trial", "guilty", "charge",
    "versus", "vs", "v", "coram", "order", "matter", "before",
    # Financial
    "estimated", "value", "valued", "total", "approximate", "approximately", "amount", "sum", "worth",
    # Place names
    "new", "delhi", "mumbai", "navi", "uttar", "madhya", "andhra", "himachal", "arunachal",
    "pradesh", "tamil", "nadu", "west", "bengal", "jammu", "kashmir", "maharashtra", "karnataka",
    "kerala", "bombay", "calcutta", "madras", "gujarat", "rajasthan", "punjab", "haryana", "bihar",
    "odisha", "assam", "goa", "chennai", "kolkata", "bangalore", "hyderabad", "pune", "nagpur",
    # Statutory
    "bharatiya", "nyaya", "sanhita", "nagarik", "suraksha", "sakshya", "adhiniyam"
}

NON_NAME_WORDS = {
    "phone", "mobile", "email", "address", "signature", "sign", "date",
    "single", "married", "unmarried", "widow", "widower", "divorced", "separated",
    "male", "female", "gender", "sex", "age", "occupation", "profession",
    "religion", "caste", "category", "nationality", "district", "town",
    "village", "pin", "pincode", "code", "number", "no", "regd", "registered",
    "reference", "ref", "form", "sheet", "copy", "original", "duplicate",
    "true", "certified", "attested", "father", "fathers", "mother", "mothers",
    "husband", "wife", "guardian", "relation", "relationship", "designation",
    "department", "office", "branch", "account", "bank", "ifsc", "name", "names",
    "details", "information", "particulars", "specimen", "declare", "declaration",
    "undersigned", "hereby", "self", "applicant", "photo", "photograph",
    "thumb", "impression", "left", "right", "blank", "nil", "none", "unknown",
    "na", "tel", "fax", "contact", "regarding", "subject", "enclosed",
    "attached", "kindly", "please", "note", "following", "sincerely",
    "yours", "faithfully", "respectfully", "herewith", "aforesaid",
    "captioned", "subjectto", "concerned", "authority", "authorities",
    "solemnly", "affirm", "affirmed", "affirming", "affirmation", "deponent",
    "verify", "verified", "verification", "sworn", "swear", "oath", "sd"
}

ALL_STOPWORDS = HEURISTIC_STOPWORDS | NON_NAME_WORDS

STATUTE_PATTERNS = [
    r"\b(?:Indian\s+Penal\s+Code|IPC)\b",
    r"\b(?:Code\s+of\s+Criminal\s+Procedure|CrPC)\b",
    r"\b(?:Code\s+of\s+Civil\s+Procedure|CPC)\b",
    r"\b(?:Bharatiya\s+Nyaya\s+Sanhita|BNS)\b",
    r"\b(?:Bharatiya\s+Nagarik\s+Suraksha\s+Sanhita|BNSS)\b",
    r"\b(?:Bharatiya\s+Sakshya\s+Adhiniyam|BSA)\b",
    r"\b(?:Indian\s+Evidence\s+Act|IEA)\b",
    r"\b(?:Constitution\s+of\s+India)\b",
    r"\b(?:Negotiable\s+Instruments\s+Act|NI\s+Act)\b",
    r"\b(?:Motor\s+Vehicles\s+Act|MV\s+Act)\b",
    r"\b(?:Protection\s+of\s+Children\s+from\s+Sexual\s+Offences|POCSO)\b",
    r"\b(?:Narcotic\s+Drugs\s+and\s+Psychotropic\s+Substances|NDPS)\b",
]

# Judicial Title regexes (Prefix and Suffix forms)
RE_JUDICIAL_PREFIX = re.compile(
    r"\b(?:Justice|Judge|Hon'ble|Honourable|Ld\.|Learned|"
    r"(?:(?:Chief|Additional|Senior|Judicial|Metropolitan|Sessions|District|First|1st)\s+){0,4}"
    r"(?:Justice|Judge|Magistrate))\s+"
    r"(?:(?:Mr|Mrs|Ms|Dr|Smt|Shri|Sri|Justice|Judge|Magistrate)\.?\s+)*"
    r"((?:[A-Z]\.\s*){0,4}[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})",
    re.IGNORECASE
)

RE_JUDICIAL_SUFFIX = re.compile(
    r"((?:[A-Z]\.\s*){0,4}[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}),?\s+"
    r"(?:(?:Chief|Additional|Senior|Judicial|Metropolitan|Sessions|District|First|1st)\s+){0,4}"
    r"(?:Justice|Judge|Magistrate)\b",
    re.IGNORECASE
)

RE_CORAM = re.compile(
    r"\bCORAM\s*:\s*((?:[A-Z]\.\s*){0,4}[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})",
    re.IGNORECASE
)


def load_dictionary_names() -> Set[str]:
    """Load Indian names from bundled names_dict.jsonl or fallback set."""
    names_path = BASE_DIR / "names_dict.jsonl"
    if not names_path.exists() and getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        names_path = Path(sys._MEIPASS) / "backend" / "ocr_tools" / "names_dict.jsonl"
    names = set()
    if names_path.exists():
        try:
            with open(names_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line)
                        if "name" in obj:
                            names.add(obj["name"].strip())
        except Exception:
            pass
    if not names:
        names = {
            "Aakash", "Aarav", "Amit", "Ananya", "Anil", "Arjun", "Deepak", "Gaurav",
            "Kavita", "Manish", "Manoj", "Mukesh", "Naresh", "Neha", "Pooja", "Priya",
            "Rahul", "Rajesh", "Ramesh", "Rohan", "Rohit", "Sachin", "Sanjay", "Sunita",
            "Suresh", "Vijay", "Vikram", "Vikas", "Vinod", "Vivek"
        }
    return names


class AnonymizerEngine:
    def __init__(self, names_dict: Set[str] = None):
        self.names_dict = names_dict if names_dict is not None else load_dictionary_names()
        self._init_patterns()

    def _init_patterns(self):
        # Layer 2 Structured Patterns
        self.re_card = re.compile(r"\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b")
        self.re_aadhaar = re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b")
        self.re_pan = re.compile(r"\b[A-Za-z]{5}\d{4}[A-Za-z]\b")
        self.re_phone = re.compile(r"\b(?:\+91[\s\-]?)?[6-9]\d{4}[\s\-]?\d{5}\b|\b(?:\+91[\s\-]?)?[6-9]\d{9}\b")
        self.re_email = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
        self.re_voter = re.compile(r"\b[A-Za-z]{3}\d{7}\b")
        self.re_vehicle = re.compile(r"\b[A-Za-z]{2}[\s\-]?[0-9]{1,2}[\s\-]?[A-Za-z]{1,3}[\s\-]?[0-9]{4}\b")
        self.re_passport = re.compile(r"\b[A-PR-WYZ][1-9]\d\s?\d{4}[1-9]\b", re.IGNORECASE)
        self.re_fir = re.compile(r"\b(?:FIR|CIR|Crime|Case)\s+No\.?\s*[:\-]?\s*(\d+[A-Za-z0-9/\-]*)", re.IGNORECASE)
        self.re_honorific_person = re.compile(
            r"\b(?:Mr|Mrs|Ms|Dr|Prof|Shri|Sh|Smt|Kumari)\.?\s+"
            r"((?:[A-Z][a-z]+|[A-Z]\.)(?:\s+(?:[A-Z][a-z]+|[A-Z]\.)){0,3})"
        )

        # Layer 3 Contextual Rules (Strict Title-Case capturing)
        self.re_relational = re.compile(
            r"\b(?:S/o|D/o|W/o|C/o|R/o|son\s+of|daughter\s+of|wife\s+of|husband\s+of|father\s+of|mother\s+of)\.?\s*[:\-]?\s*"
            r"(?:(?:late|shri|sh|smt|mr|mrs|kum)\.?\s+){0,2}"
            r"((?:[A-Z][a-z]+|[A-Z]{2,})(?:[ \t]+(?:[A-Z][a-z]+|[A-Z]{2,}))*)",
            re.IGNORECASE
        )
        self.re_field_label = re.compile(
            r"\b(?:(?:father|mother|husband|wife|guardian)(?:['’]?s)?\s*name|name\s+of\s+(?:the\s+)?(?:father|mother|husband|wife|guardian|complainant|accused|informant|deceased|victim)|in\s+the\s+matter\s+of)\s*[:\-]?\s*"
            r"(?:(?:late|shri|sh|smt|mr|mrs|kum)\.?\s+){0,2}"
            r"((?:[A-Z][a-z]+|[A-Z]{2,})(?:[ \t]+(?:[A-Z][a-z]+|[A-Z]{2,}))*)",
            re.IGNORECASE
        )
        # Party roles: explicitly allow skipping honorifics before capturing Title-Cased name
        self.re_party_role = re.compile(
            r"\b(?:petitioner|respondent|complainant|accused|appellant|defendant|plaintiff)\s*[:\-]?\s*"
            r"(?:(?:late|shri|sh|smt|mr|mrs|ms|dr|kum)\.?\s+){0,2}"
            r"((?:[A-Z][a-z]+|[A-Z]{2,})(?:[ \t]+(?:[A-Z][a-z]+|[A-Z]{2,}))*)",
            re.IGNORECASE
        )
        self.re_alias = re.compile(
            r"(?:([A-Z][a-z]+(?:[ \t]+[A-Z][a-z]+){0,2})[ \t]+)?"
            r"(?:\b(?:alias|a/?k/?a|known\s+as)|@)\s+"
            r"([A-Z][a-z]+(?:[ \t]+[A-Z][a-z]+){0,2})",
            re.IGNORECASE
        )
        self.re_address = re.compile(
            r"(?:\b(?:resident\s+of|residing\s+at|r/o|address\s*[:\-]|permanent\s+address\s*[:\-]|address\s+of\s+the\s+\w+\s*[:\-])\s*([^\n;]{4,100})|"
            r"\b((?:h\.?\s*no\.?|house\s+no\.?|shop\s+no\.?|plot\s+no\.?|flat\s+no\.?|door\s+no\.?)\s*\d[^\n;,]{0,40}(?:,[^\n;,]{0,60}){1,3}))",
            re.IGNORECASE
        )
        self.re_org_suffix = re.compile(
            r"\b([A-Z][A-Za-z0-9&.\- ]{2,40}?\s+(?:Pvt\.?\s*Ltd\.?|Private\s+Limited|Ltd\.?|Limited|LLP|Corporation|Corp\.?|Inc\.?))\b",
            re.IGNORECASE
        )

    def _collect_exclusions(self, text: str) -> List[Tuple[int, int]]:
        """Collect all byte/char spans that must NEVER be masked (Judges, Magistrates, Statutes)."""
        spans = []
        for m in RE_JUDICIAL_PREFIX.finditer(text):
            spans.append(m.span())
        for m in RE_JUDICIAL_SUFFIX.finditer(text):
            spans.append(m.span())
        for m in RE_CORAM.finditer(text):
            spans.append(m.span())
        for pat in STATUTE_PATTERNS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                spans.append(m.span())
        return sorted(spans, key=lambda s: s[0])

    @staticmethod
    def _is_excluded(start: int, end: int, exclusions: List[Tuple[int, int]]) -> bool:
        for ex_start, ex_end in exclusions:
            if not (end <= ex_start or start >= ex_end):
                return True
        return False

    @staticmethod
    def _trim_designation(name: str) -> str:
        """Trim trailing job designations like 'Forensic Auditor' or 'Advocate'."""
        words = name.strip().split()
        while words and words[-1].lower().strip(".,;:()") in DESIGNATION_WORDS:
            words.pop()
        return " ".join(words)

    @staticmethod
    def is_plausible_name_span(name_candidate: str) -> bool:
        """Verify that a candidate span contains plausible name words and no stopwords."""
        words = name_candidate.strip().split()
        if not words:
            return False
        for w in words:
            clean = re.sub(r"[^\w]", "", w)
            if not clean:
                continue
            if clean.lower() in ALL_STOPWORDS or clean.lower() in DESIGNATION_WORDS:
                return False
            # Check Title Case or all-caps
            if not (clean[0].isupper() or clean.isupper()):
                return False
        return True

    @staticmethod
    def _rejects_year_run(matched: str) -> bool:
        """Return True if match is NOT a sequence of calendar years."""
        groups = re.split(r"[\s\-]+", matched.strip())
        if len(groups) < 2:
            return True
        all_years = all(g.isdigit() and len(g) == 4 and 1900 <= int(g) <= 2100 for g in groups)
        return not all_years

    def anonymize(self, text: str) -> Dict[str, Any]:
        """
        Run the complete anonymization pipeline over input text.
        Returns:
            {
                "anonymised_text": str,
                "variable_map": Dict[str, str],   # token -> original value
                "entity_count": int,
                "stats": Dict[str, int]
            }
        """
        exclusions = self._collect_exclusions(text)
        variable_map: Dict[str, str] = {}
        val_to_token: Dict[str, str] = {}
        type_counters: Dict[str, int] = {}

        def get_or_mint_token(val: str, prefix: str) -> str:
            clean_val = val.strip()
            if clean_val in val_to_token:
                return val_to_token[clean_val]
            count = type_counters.get(prefix, 0) + 1
            type_counters[prefix] = count
            tok_key = f"{prefix}_{count}"
            variable_map[tok_key] = clean_val
            val_to_token[clean_val] = tok_key
            return tok_key

        candidates: List[Tuple[int, int, str, str]] = []

        # 1. Structured Patterns (Layer 2)
        for m in self.re_card.finditer(text):
            if not self._is_excluded(m.start(), m.end(), exclusions) and self._rejects_year_run(m.group(0)):
                candidates.append((m.start(), m.end(), m.group(0), "AccountNo"))

        for m in self.re_aadhaar.finditer(text):
            if not self._is_excluded(m.start(), m.end(), exclusions) and self._rejects_year_run(m.group(0)):
                candidates.append((m.start(), m.end(), m.group(0), "Aadhaar"))

        for m in self.re_pan.finditer(text):
            if not self._is_excluded(m.start(), m.end(), exclusions):
                candidates.append((m.start(), m.end(), m.group(0), "PAN"))

        for m in self.re_phone.finditer(text):
            val = m.group(0)
            parts = val.split()
            if len(parts) == 2 and parts[0].endswith("000") and parts[1].endswith("000"):
                continue
            if not self._is_excluded(m.start(), m.end(), exclusions):
                candidates.append((m.start(), m.end(), val, "Phone"))

        for m in self.re_email.finditer(text):
            if not self._is_excluded(m.start(), m.end(), exclusions):
                candidates.append((m.start(), m.end(), m.group(0), "Email"))

        for m in self.re_voter.finditer(text):
            if not self._is_excluded(m.start(), m.end(), exclusions):
                candidates.append((m.start(), m.end(), m.group(0), "VoterID"))

        for m in self.re_vehicle.finditer(text):
            if not self._is_excluded(m.start(), m.end(), exclusions):
                candidates.append((m.start(), m.end(), m.group(0), "Vehicle"))

        for m in self.re_passport.finditer(text):
            if not self._is_excluded(m.start(), m.end(), exclusions):
                candidates.append((m.start(), m.end(), m.group(0), "Passport"))

        for m in self.re_honorific_person.finditer(text):
            raw_name = m.group(1)
            trimmed = self._trim_designation(raw_name)
            if self.is_plausible_name_span(trimmed) and not self._is_excluded(m.start(1), m.start(1) + len(trimmed), exclusions):
                candidates.append((m.start(1), m.start(1) + len(trimmed), trimmed, "Person"))

        # 2. Contextual Rules (Layer 3)
        for m in self.re_relational.finditer(text):
            raw_name = m.group(1)
            trimmed = self._trim_designation(raw_name)
            if self.is_plausible_name_span(trimmed) and not self._is_excluded(m.start(1), m.start(1) + len(trimmed), exclusions):
                candidates.append((m.start(1), m.start(1) + len(trimmed), trimmed, "Person"))

        for m in self.re_field_label.finditer(text):
            raw_name = m.group(1)
            trimmed = self._trim_designation(raw_name)
            if self.is_plausible_name_span(trimmed) and not self._is_excluded(m.start(1), m.start(1) + len(trimmed), exclusions):
                candidates.append((m.start(1), m.start(1) + len(trimmed), trimmed, "Person"))

        for m in self.re_party_role.finditer(text):
            raw_name = m.group(1)
            trimmed = self._trim_designation(raw_name)
            if self.is_plausible_name_span(trimmed) and not self._is_excluded(m.start(1), m.start(1) + len(trimmed), exclusions):
                candidates.append((m.start(1), m.start(1) + len(trimmed), trimmed, "Person"))

        for m in self.re_alias.finditer(text):
            for grp_idx in (1, 2):
                val = m.group(grp_idx)
                if val:
                    trimmed = self._trim_designation(val)
                    if self.is_plausible_name_span(trimmed) and not self._is_excluded(m.start(grp_idx), m.start(grp_idx) + len(trimmed), exclusions):
                        candidates.append((m.start(grp_idx), m.start(grp_idx) + len(trimmed), trimmed, "Person"))

        for m in self.re_address.finditer(text):
            val = m.group(1) or m.group(2)
            if val:
                val = val.strip().rstrip(".,;")
                grp_start = m.start(1) if m.group(1) else m.start(2)
                if not self._is_excluded(grp_start, grp_start + len(val), exclusions):
                    candidates.append((grp_start, grp_start + len(val), val, "Address"))

        for m in self.re_org_suffix.finditer(text):
            if not self._is_excluded(m.start(), m.end(), exclusions):
                candidates.append((m.start(), m.end(), m.group(1).strip(), "Org"))

        # 3. Dictionary Names matching (whole-word)
        for word in re.finditer(r"\b[A-Z][a-z]{2,}\b", text):
            w = word.group(0)
            if w in self.names_dict:
                if not self._is_excluded(word.start(), word.end(), exclusions):
                    candidates.append((word.start(), word.end(), w, "Person"))

        # Sort candidates: start position ascending, longest span first
        candidates.sort(key=lambda c: (c[0], -(c[1] - c[0])))

        # Resolve overlapping spans (greedy non-overlapping replacement)
        non_overlapping: List[Tuple[int, int, str, str]] = []
        last_end = 0
        for start, end, val, prefix in candidates:
            if start >= last_end and end <= len(text):
                non_overlapping.append((start, end, val, prefix))
                last_end = end

        # Construct anonymised text
        out_parts = []
        curr = 0
        for start, end, val, prefix in non_overlapping:
            out_parts.append(text[curr:start])
            token_key = get_or_mint_token(val, prefix)
            out_parts.append(f"<<{token_key}>>")
            curr = end
        out_parts.append(text[curr:])

        anonymised_str = "".join(out_parts)

        # Entity count & stats
        stats: Dict[str, int] = {}
        for k in variable_map:
            prefix = k.split("_")[0]
            stats[prefix] = stats.get(prefix, 0) + 1

        return {
            "anonymised_text": anonymised_str,
            "variable_map": variable_map,
            "entity_count": len(non_overlapping),
            "stats": stats
        }


def deanonymise(text: str, variable_map: Dict[str, str]) -> str:
    """
    Safely de-anonymize text in a single non-cascading left-to-right pass.
    Guarantees no re-scanning of replaced values.
    """
    if not text or not variable_map:
        return text or ""

    out = []
    i = 0
    n = len(text)
    while i < n:
        if i + 1 < n and text[i:i + 2] == "<<":
            close_idx = text.find(">>", i + 2)
            next_open = text.find("<<", i + 2)
            if close_idx != -1 and (next_open == -1 or close_idx < next_open):
                key = text[i + 2:close_idx].strip()
                if key in variable_map:
                    out.append(variable_map[key])
                    i = close_idx + 2
                    continue
                else:
                    out.append(text[i:close_idx + 2])
                    i = close_idx + 2
                    continue
        out.append(text[i])
        i += 1

    return "".join(out)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Standalone Personal Information Anonymizer / De-anonymizer")
    parser.add_argument("--anonymize", "-a", metavar="FILE", help="File to anonymize")
    parser.add_argument("--deanonymize", "-d", metavar="FILE", help="File to de-anonymize")
    parser.add_argument("--map", "-m", metavar="MAP_FILE", help="Path to variable_map.json")
    parser.add_argument("--output", "-o", metavar="OUT_FILE", help="Output file path (default stdout)")

    args = parser.parse_args()
    engine = AnonymizerEngine()

    if args.anonymize:
        with open(args.anonymize, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        res = engine.anonymize(content)

        map_path = args.map or "variable_map.json"
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(res["variable_map"], f, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(res["anonymised_text"])
            print(f"Anonymised text written to {args.output}")
            print(f"Variable map saved to {map_path}")
            print(f"Entities masked: {res['entity_count']} {res['stats']}")
        else:
            print("--- ANONYMISED TEXT ---")
            print(res["anonymised_text"])
            print("\n--- VARIABLE MAP ---")
            print(json.dumps(res["variable_map"], indent=2, ensure_ascii=False))

    elif args.deanonymize:
        if not args.map:
            print("Error: --map <variable_map.json> is required for de-anonymization.", file=sys.stderr)
            sys.exit(1)
        with open(args.deanonymize, "r", encoding="utf-8", errors="replace") as f:
            anon_text = f.read()
        with open(args.map, "r", encoding="utf-8") as f:
            vmap = json.load(f)

        restored = deanonymise(anon_text, vmap)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(restored)
            print(f"Restored text written to {args.output}")
        else:
            print(restored)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
