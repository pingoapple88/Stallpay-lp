from __future__ import annotations

import base64
import json
import os
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, padding as symmetric_padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def build_encrypted_request(payload: dict[str, Any], public_key_pem: str, aes_iv: bytes, aes_key: bytes | None = None) -> tuple[dict[str, str], bytes]:
    if len(aes_iv) != 16:
        raise ValueError("Intella AES IV must be 16 bytes")
    key = aes_key or os.urandom(16)
    if len(key) != 16:
        raise ValueError("Intella AES key must be 16 bytes")
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    padder = symmetric_padding.PKCS7(128).padder()
    padded = padder.update(raw) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(aes_iv)).encryptor()
    encrypted_request = encryptor.update(padded) + encryptor.finalize()
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    encrypted_key = public_key.encrypt(base64.b64encode(key), asymmetric_padding.PKCS1v15())
    return {
        "Request": base64.b64encode(encrypted_request).decode("ascii"),
        "ApiKey": base64.b64encode(encrypted_key).decode("ascii"),
    }, key


def decrypt_response(response_b64: str, aes_key: bytes, aes_iv: bytes) -> dict[str, Any]:
    normalized = response_b64.replace("\\n", "").replace("\\u003d", "=")
    decryptor = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv)).decryptor()
    padded = decryptor.update(base64.b64decode(normalized)) + decryptor.finalize()
    unpadder = symmetric_padding.PKCS7(128).unpadder()
    raw = unpadder.update(padded) + unpadder.finalize()
    return json.loads(raw.decode("utf-8"))


def verify_callback_signature(payload: dict[str, Any], signature_b64: str, public_key_pem: str) -> bool:
    unsigned = dict(payload)
    unsigned.pop("Sign", None)
    raw = json.dumps(unsigned, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    signature = base64.b64decode(signature_b64.replace("\\u003d", "="))
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    try:
        public_key.verify(signature, raw, asymmetric_padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature:
        return False
    return True
