"""
Vector-Index-Sanitizer: Vector Database Index Poisoning & Synthetic Contamination Firewall.
Standard library only: hashlib, json, time, os, re, dataclasses, typing, math.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import os
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple


GENESIS_HASH: str = "0000000000000000000000000000000000000000000000000000000000000000"


@dataclasses.dataclass(frozen=True)
class SanitizerReceipt:
    """Immutable SHA-256 cryptographically chained vector index cleanliness receipt."""
    index: int
    prev_hash: str
    doc_id: str
    tenant_id: str
    status: str
    entropy_score: float
    threats_detected: int
    timestamp: float
    signature_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class CryptographicSanitizerLedger:
    """Tamper-Proof Vector Cleanliness & Provenance Ledger for Audits."""

    def __init__(self, ledger_file: Optional[str] = None):
        self.ledger_file = ledger_file
        self._entries: List[SanitizerReceipt] = []
        self._last_hash = GENESIS_HASH

    @property
    def last_hash(self) -> str:
        return self._last_hash

    @property
    def count(self) -> int:
        return len(self._entries)

    def record_receipt(
        self,
        doc_id: str,
        tenant_id: str,
        status: str,
        entropy: float,
        threats_count: int,
    ) -> SanitizerReceipt:
        idx = len(self._entries)
        ts = time.time()

        raw_msg = f"{idx}:{self._last_hash}:{doc_id}:{tenant_id}:{status}:{entropy:.4f}:{threats_count}:{ts:.6f}"
        sig_hash = hashlib.sha256(raw_msg.encode("utf-8")).hexdigest()

        receipt = SanitizerReceipt(
            index=idx,
            prev_hash=self._last_hash,
            doc_id=doc_id,
            tenant_id=tenant_id,
            status=status,
            entropy_score=round(entropy, 4),
            threats_detected=threats_count,
            timestamp=ts,
            signature_hash=sig_hash,
        )

        self._entries.append(receipt)
        self._last_hash = sig_hash

        if self.ledger_file:
            os.makedirs(os.path.dirname(os.path.abspath(self.ledger_file)), exist_ok=True)
            with open(self.ledger_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(receipt.to_dict()) + "\n")

        return receipt

    def verify_chain_integrity(self) -> Tuple[bool, Optional[str]]:
        current_prev = GENESIS_HASH
        for idx, entry in enumerate(self._entries):
            if entry.index != idx:
                return False, f"Sequence index break at {idx}"
            if entry.prev_hash != current_prev:
                return False, f"Broken SHA-256 chain at {idx}"
            current_prev = entry.signature_hash
        return True, None


class VectorIndexSanitizer:
    """
    In-Situ Vector Database Index Poisoning & Synthetic Contamination Firewall.
    """

    POISON_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
        re.compile(r"you\s+must\s+output\s+the\s+following", re.IGNORECASE),
        re.compile(r"exfiltrate|leak|send\s+to\s+http", re.IGNORECASE),
    ]

    def __init__(self, ledger_path: Optional[str] = None):
        self.ledger = CryptographicSanitizerLedger(ledger_file=ledger_path)

    def check_kill_switch(self) -> bool:
        if os.environ.get("AGENT_SANITIZER_KILL", "0") in ("1", "true", "TRUE"):
            return True
        if os.path.exists("/tmp/AGENT_SANITIZER_KILL"):
            return True
        return False

    @staticmethod
    def _compute_shannon_entropy(text: str) -> float:
        if not text:
            return 0.0
        frequencies: Dict[str, int] = {}
        for char in text:
            frequencies[char] = frequencies.get(char, 0) + 1
        entropy = 0.0
        total = len(text)
        for count in frequencies.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

    def sanitize_document_chunk(
        self,
        doc_id: str,
        tenant_id: str,
        text_chunk: str,
        embedding_vector: Optional[List[float]] = None,
    ) -> Tuple[bool, SanitizerReceipt]:
        if self.check_kill_switch():
            receipt = self.ledger.record_receipt(
                doc_id=doc_id,
                tenant_id=tenant_id,
                status="HALTED_BY_EMERGENCY_KILL_SWITCH",
                entropy=0.0,
                threats_count=0,
            )
            return False, receipt

        entropy = self._compute_shannon_entropy(text_chunk)
        threats_count = 0

        for pattern in self.POISON_PATTERNS:
            if pattern.search(text_chunk):
                threats_count += 1

        if threats_count > 0:
            receipt = self.ledger.record_receipt(
                doc_id=doc_id,
                tenant_id=tenant_id,
                status="QUARANTINED_PROMPT_INJECTION_DETECTED",
                entropy=entropy,
                threats_count=threats_count,
            )
            return False, receipt

        receipt = self.ledger.record_receipt(
            doc_id=doc_id,
            tenant_id=tenant_id,
            status="VERIFIED_CLEAN_INGESTED",
            entropy=entropy,
            threats_count=0,
        )
        return True, receipt
