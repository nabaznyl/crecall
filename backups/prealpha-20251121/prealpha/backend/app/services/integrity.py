"""Integrity signing and verification using HMAC (tamper-evident records).

Uses env `CRECALL_SIGNING_KEY` to sign clip content payloads.
"""
import os
import hmac
import hashlib
import json
from typing import Optional, Dict, Any


class Integrity:
    @staticmethod
    def _key() -> Optional[bytes]:
        key = os.getenv("CRECALL_SIGNING_KEY")
        return key.encode() if key else None

    @staticmethod
    def sign_dict(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        key = Integrity._key()
        if not key:
            return None
        # Stable JSON
        data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        sig = hmac.new(key, data, hashlib.sha256).hexdigest()
        return {"alg": "HS256", "sig": sig}

    @staticmethod
    def verify_dict(payload: Dict[str, Any]) -> bool:
        key = Integrity._key()
        if not key:
            return True  # No key configured; treat as unverifiable but not failing
        integ = payload.get("integrity") if isinstance(payload, dict) else None
        if not isinstance(integ, dict) or "sig" not in integ:
            return False
        expected = Integrity.sign_dict({k: v for k, v in payload.items() if k != "integrity"})
        return bool(expected and expected.get("sig") == integ.get("sig"))
    
    @staticmethod
    def verify_dict(data: dict) -> bool:
        sig = data.get("integrity")
        if not sig:
            return False
        temp = {k: v for k, v in data.items() if k != "integrity"}
        calc = Integrity.sign_dict(temp)
        return sig == calc

    @staticmethod
    def status_dict(data: dict) -> str:
        """Return verification status string."""
        if not data.get("integrity"):
            return "missing"
        return "valid" if Integrity.verify_dict(data) else "invalid"
