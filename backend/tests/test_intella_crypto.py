import base64
import json

from cryptography.hazmat.primitives import hashes, padding as symmetric_padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from app.adapters.intella_crypto import build_encrypted_request, decrypt_response, verify_callback_signature


def key_pair() -> tuple[object, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_key, public_pem


def test_intella_request_envelope_can_be_decrypted() -> None:
    private_key, public_pem = key_pair()
    iv = b"0123456789ABCDEF"
    aes_key = b"ABCDEF0123456789"
    payload = {"Header": {"ServiceType": "OLPay"}, "Data": "{\"StoreOrderNo\":\"PAYUAT001\"}"}
    envelope, returned_key = build_encrypted_request(payload, public_pem, iv, aes_key=aes_key)
    decrypted_key_b64 = private_key.decrypt(base64.b64decode(envelope["ApiKey"]), asymmetric_padding.PKCS1v15())
    assert base64.b64decode(decrypted_key_b64) == aes_key == returned_key
    decryptor = Cipher(algorithms.AES(aes_key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(base64.b64decode(envelope["Request"])) + decryptor.finalize()
    unpadder = symmetric_padding.PKCS7(128).unpadder()
    raw = unpadder.update(padded) + unpadder.finalize()
    assert json.loads(raw) == payload


def test_intella_encrypted_response_can_be_decrypted() -> None:
    key = b"ABCDEF0123456789"
    iv = b"0123456789ABCDEF"
    payload = {"Header": {"StatusCode": "0000"}, "Data": {"OrderStatus": "1"}}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    padder = symmetric_padding.PKCS7(128).padder()
    padded = padder.update(raw) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    response = base64.b64encode(encryptor.update(padded) + encryptor.finalize()).decode()
    assert decrypt_response(response, key, iv) == payload


def test_intella_callback_signature_verification() -> None:
    private_key, public_pem = key_pair()
    payload = {"MchId": "synthetic", "Result": "0000", "StoreOrderNo": "PAYUAT001", "TotalFee": "100"}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    signature = private_key.sign(raw, asymmetric_padding.PKCS1v15(), hashes.SHA256())
    signature_b64 = base64.b64encode(signature).decode()
    assert verify_callback_signature(payload, signature_b64, public_pem) is True
    assert verify_callback_signature({**payload, "TotalFee": "101"}, signature_b64, public_pem) is False
