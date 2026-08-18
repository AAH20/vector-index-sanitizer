"""
Vector-Index-Sanitizer: Vector Database Index Poisoning & Synthetic Contamination Firewall.
"""

from vectorsanitizer.core import (
    VectorIndexSanitizer,
    SanitizerReceipt,
    CryptographicSanitizerLedger,
    GENESIS_HASH,
)

__all__ = [
    "VectorIndexSanitizer",
    "SanitizerReceipt",
    "CryptographicSanitizerLedger",
    "GENESIS_HASH",
]

__version__ = "1.0.0"
