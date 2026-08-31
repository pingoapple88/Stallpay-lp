from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from collections.abc import Mapping


class ISignatureProvider(ABC):
    @abstractmethod
    def sign(self, parameters: Mapping[str, str]) -> str:
        """Return the vendor signature without mutating the input."""


class AsciiSortedSha256SignatureProvider(ISignatureProvider):
    """Implements the signature rule documented by the Tianlai sample PDF."""

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("token is required")
        self._token = token

    @staticmethod
    def canonical_string(parameters: Mapping[str, str], token: str) -> str:
        if not token:
            raise ValueError("token is required")
        if "sign" in parameters:
            raise ValueError("sign must not be included in parameters")
        normalized: list[tuple[str, str]] = []
        for key, value in parameters.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError("signature parameters must be strings")
            if not key:
                raise ValueError("signature parameter names must not be empty")
            normalized.append((key, value))
        normalized.sort(key=lambda item: item[0].encode("ascii"))
        query = "&".join(f"{key}={value}" for key, value in normalized)
        return query + token

    def sign(self, parameters: Mapping[str, str]) -> str:
        canonical = self.canonical_string(parameters, self._token)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
