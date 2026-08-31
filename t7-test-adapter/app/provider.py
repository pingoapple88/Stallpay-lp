from __future__ import annotations

import asyncio
import hashlib
import socket
import ssl
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

import httpx

from .signing import ISignatureProvider
from .vault import CredentialMaterial

ALLOWED_PATHS = ("/Machine.aspx", "/Commodity.aspx")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def summarize_json(payload: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {"json_type": type(payload).__name__}
    if isinstance(payload, dict):
        summary["top_level_keys"] = sorted(str(key) for key in payload.keys())
        for key in ("machine", "commodity", "data", "list"):
            value = payload.get(key)
            if isinstance(value, list):
                summary["collection_key"] = key
                summary["record_count"] = len(value)
                if value and isinstance(value[0], dict):
                    summary["record_field_names"] = sorted(str(field) for field in value[0].keys())
                break
        if "state" in payload:
            summary["state"] = payload["state"]
        if "message" in payload:
            summary["message_present"] = bool(payload["message"])
    elif isinstance(payload, list):
        summary["record_count"] = len(payload)
        if payload and isinstance(payload[0], dict):
            summary["record_field_names"] = sorted(str(field) for field in payload[0].keys())
    return summary


class ITianlaiReadOnlyProvider(ABC):
    @abstractmethod
    async def preflight(self, credentials: CredentialMaterial, client_time_utc: str) -> dict[str, Any]:
        """Execute the bounded, read-only connectivity test."""


class TianlaiReadOnlyProvider(ITianlaiReadOnlyProvider):
    def __init__(
        self,
        api_base_url: str,
        signer_factory: type[ISignatureProvider],
        connect_timeout_seconds: float,
        read_timeout_seconds: float,
    ) -> None:
        parts = urlsplit(api_base_url)
        if parts.scheme != "https" or not parts.hostname or parts.path not in ("", "/"):
            raise ValueError("api_base_url must be an HTTPS origin")
        self._base_url = api_base_url.rstrip("/")
        self._host = parts.hostname
        self._signer_factory = signer_factory
        self._connect_timeout = connect_timeout_seconds
        self._read_timeout = read_timeout_seconds

    async def _resolve_dns(self) -> dict[str, Any]:
        started = time.monotonic()
        try:
            records = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: socket.getaddrinfo(self._host, 443, type=socket.SOCK_STREAM),
            )
            addresses = sorted({record[4][0] for record in records})
            return {
                "status": "PASS",
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "address_count": len(addresses),
                "addresses_redacted": True,
            }
        except OSError:
            return {
                "status": "BLOCKED",
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "error": "DNS_RESOLUTION_FAILED",
                "addresses_redacted": True,
            }

    async def _check_tls(self) -> dict[str, Any]:
        started = time.monotonic()
        try:
            context = ssl.create_default_context()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, 443, ssl=context, server_hostname=self._host),
                timeout=self._connect_timeout,
            )
            ssl_object = writer.get_extra_info("ssl_object")
            version = ssl_object.version() if ssl_object else None
            writer.close()
            await writer.wait_closed()
            return {
                "status": "PASS",
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "tls_version": version,
                "certificate_verified": True,
            }
        except (OSError, asyncio.TimeoutError, ssl.SSLError):
            return {
                "status": "BLOCKED",
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "error": "TLS_CONNECTION_FAILED",
                "certificate_verified": False,
            }

    async def _probe_path(
        self,
        client: httpx.AsyncClient,
        path: str,
        credentials: CredentialMaterial,
    ) -> dict[str, Any]:
        if path not in ALLOWED_PATHS:
            raise ValueError("path is outside the read-only allowlist")
        signer = self._signer_factory(credentials.token)
        parameters = {"company": credentials.company}
        signed_parameters = {**parameters, "sign": signer.sign(parameters)}
        started_at = utc_now()
        started = time.monotonic()
        try:
            response = await client.get(path, params=signed_parameters)
            elapsed_ms = round((time.monotonic() - started) * 1000)
            body = response.content
            result: dict[str, Any] = {
                "started_at_utc": started_at,
                "completed_at_utc": utc_now(),
                "method": "GET",
                "path": path,
                "query_redacted": True,
                "http_status": response.status_code,
                "elapsed_ms": elapsed_ms,
                "response_size_bytes": len(body),
                "response_sha256": hashlib.sha256(body).hexdigest(),
                "raw_body_persisted": False,
                "redirect_followed": False,
            }
            try:
                result["response_summary"] = summarize_json(response.json())
                result["json_parse_status"] = "PASS"
            except ValueError:
                result["response_summary"] = {"json_type": "unparseable", "body_redacted": True}
                result["json_parse_status"] = "BLOCKED"
            state_ok = result["response_summary"].get("state") in (0, "0", None)
            result["status"] = (
                "PASS"
                if response.status_code == 200 and result["json_parse_status"] == "PASS" and state_ok
                else "BLOCKED"
            )
            return result
        except httpx.HTTPError:
            return {
                "started_at_utc": started_at,
                "completed_at_utc": utc_now(),
                "method": "GET",
                "path": path,
                "query_redacted": True,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "status": "BLOCKED",
                "error": "UPSTREAM_CONNECTION_FAILED",
                "raw_body_persisted": False,
                "redirect_followed": False,
            }

    async def preflight(self, credentials: CredentialMaterial, client_time_utc: str) -> dict[str, Any]:
        server_started = datetime.now(timezone.utc)
        try:
            client_time = datetime.fromisoformat(client_time_utc.replace("Z", "+00:00"))
            if client_time.tzinfo is None:
                raise ValueError
            clock_skew_seconds = round(abs((server_started - client_time.astimezone(timezone.utc)).total_seconds()), 3)
            clock_status = "PASS" if clock_skew_seconds <= 300 else "ATTENTION"
        except ValueError:
            clock_skew_seconds = None
            clock_status = "BLOCKED"

        dns_result, tls_result = await asyncio.gather(self._resolve_dns(), self._check_tls())
        timeout = httpx.Timeout(self._read_timeout, connect=self._connect_timeout)
        async with httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            follow_redirects=False,
            headers={"Accept": "application/json", "User-Agent": "MerchCore-T7-ReadOnly-Adapter/1.0"},
        ) as client:
            api_results = []
            for path in ALLOWED_PATHS:
                api_results.append(await self._probe_path(client, path, credentials))

        checks = [dns_result["status"], tls_result["status"], clock_status] + [item["status"] for item in api_results]
        overall = "PASS" if all(item == "PASS" for item in checks) else "ATTENTION" if "BLOCKED" not in checks else "BLOCKED"
        return {
            "status": overall,
            "server_time_utc": server_started.isoformat().replace("+00:00", "Z"),
            "client_time_utc": client_time_utc,
            "clock": {"status": clock_status, "skew_seconds": clock_skew_seconds, "allowed_skew_seconds": 300},
            "dns": dns_result,
            "tls": tls_result,
            "upstream_host": self._host,
            "credential_version_id": credentials.version_id,
            "credentials_redacted": True,
            "api_results": api_results,
            "formal_device_control": False,
            "formal_inventory_write": False,
            "direct_refund": False,
            "unknown_auto_resend": False,
            "test_device_verified": False,
            "completion_signal": False,
            "gate_06": "BLOCKED",
        }
