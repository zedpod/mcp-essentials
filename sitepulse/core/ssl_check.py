"""TLS certificate inspection using stdlib socket + cryptography (locale-safe)."""

import socket
import ssl
from datetime import datetime, timezone

from .types import SslCert


def fetch_cert(host: str, port: int = 443, timeout: float = 5.0) -> SslCert:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                der = ssock.getpeercert(binary_form=True)
    except Exception as exc:
        return SslCert(ok=False, error=f"{type(exc).__name__}: {exc}")

    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        cert = x509.load_der_x509_certificate(der)
        issuer_attrs = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        subject_attrs = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        not_before = cert.not_valid_before_utc.replace(tzinfo=timezone.utc) if hasattr(cert, "not_valid_before_utc") else cert.not_valid_before
        not_after = cert.not_valid_after_utc.replace(tzinfo=timezone.utc) if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after
        # Strip any pre-existing tzinfo for the timedelta math then compare in UTC.
        now = datetime.now(timezone.utc)
        days_until = int((not_after - now).total_seconds() // 86400) if not_after else None
        san: list[str] = []
        try:
            ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            san = [str(name) for name in ext.value.get_values_for_type(x509.DNSName)]
        except Exception:
            pass
        return SslCert(
            ok=True,
            issuer=issuer_attrs[0].value if issuer_attrs else None,
            subject=subject_attrs[0].value if subject_attrs else None,
            not_before=not_before,
            not_after=not_after,
            days_until_expiry=days_until,
            san=san,
        )
    except Exception as exc:
        return SslCert(ok=False, error=f"parse: {type(exc).__name__}: {exc}")
