"""
Consistent & Scoped Pseudonymisation with HMAC for Privacy-Preserving Health RAG.

Supports Scoped HMAC Pseudonyms:
    token = HMAC(secret_key, hospital_id + ":" + patient_identifier)
This ensures tokens:
1. Remain stable and consistent inside one authorized hospital for narrative RAG continuity.
2. Are distinct and unlinkable across different hospitals and external research exports.
3. Cannot be inverted or correlated without the hospital's tenant secret key.
"""

import hmac
import hashlib
from typing import Dict, List, Any, Optional

DEFAULT_SECRET_KEY = "healthguard-hospital-tenant-master-key"


class ConsistentPseudonymizer:
    """Replace PII spans with institutional scoped HMAC or consistent placeholder tags."""

    def __init__(self, hospital_id: str = "HOSP_MAIN", secret_key: str = DEFAULT_SECRET_KEY, use_hmac: bool = True) -> None:
        self.hospital_id = hospital_id
        self.secret_key = secret_key
        self.use_hmac = use_hmac
        self._mapping: Dict[str, str] = {}
        self._reverse: Dict[str, str] = {}
        self._counters: Dict[str, int] = {}

    def pseudonymize(self, text: str, entities: List[Dict[str, Any]]) -> str:
        """Replace detected PII spans in text with scoped placeholder tags."""
        if not entities or not text:
            return text

        sorted_entities = sorted(entities, key=lambda e: e.get("start", 0), reverse=True)

        for entity in sorted_entities:
            start = entity.get("start", 0)
            end = entity.get("end", 0)
            original_value = text[start:end]
            entity_type = entity.get("type", "ENTITY")

            tag = self._get_or_create_tag(original_value, entity_type)
            text = text[:start] + tag + text[end:]

        return text

    def get_mapping(self) -> Dict[str, str]:
        """Return a copy of the current original_value -> tag mapping."""
        return dict(self._mapping)

    def reverse_map(self, text: str) -> str:
        """De-anonymize text by replacing tags back with original values."""
        if not text:
            return ""
        for tag, original_value in self._reverse.items():
            text = text.replace(tag, original_value)
        return text

    def _get_or_create_tag(self, value: str, entity_type: str) -> str:
        """Return the scoped tag for value, creating one if not seen yet."""
        clean_val = value.strip()
        if clean_val in self._mapping:
            return self._mapping[clean_val]

        short_type = self._canonical_entity_type(entity_type)

        if self.use_hmac:
            # Scoped HMAC token: prevents cross-institutional linkability
            h = hmac.new(
                self.secret_key.encode(),
                f"{self.hospital_id}:{short_type}:{clean_val}".encode(),
                hashlib.sha256
            ).hexdigest()[:6].upper()
            tag = f"[{short_type}_{self.hospital_id}_{h}]"
        else:
            count = self._counters.get(short_type, 0) + 1
            self._counters[short_type] = count
            tag = f"[{short_type}_{count}]"

        self._mapping[clean_val] = tag
        self._reverse[tag] = clean_val
        return tag

    @staticmethod
    def _canonical_entity_type(entity_type: str) -> str:
        mapping = {
            "US_SSN": "SSN",
            "PHONE_NUMBER": "PHONE",
            "EMAIL_ADDRESS": "EMAIL",
            "DATE_TIME": "DATE",
            "PAN_NUMBER": "PAN",
            "ABHA_ID": "ABHA",
            "AADHAAR": "AADHAAR",
            "UHID": "UHID",
            "MEDICAL_LICENSE": "MED_ID",
            "LOCATION": "LOC",
        }
        return mapping.get(entity_type, entity_type)
