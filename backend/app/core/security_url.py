"""
URL Security & SSRF Protection Module.

Ensures that user-supplied video URLs only target public web endpoints
and prevents Server-Side Request Forgery (SSRF) attacks targeting
internal services, loopback addresses, or cloud metadata endpoints.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse
import httpx

from app.core import get_logger

logger = get_logger(__name__)

BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


class SSRFValidationError(ValueError):
    """Raised when a URL violates SSRF safety rules."""
    pass


def is_ip_private_or_blocked(ip_str: str) -> bool:
    """Check whether an IP address is private, loopback, link-local, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            return True
        for net in BLOCKED_NETWORKS:
            if ip in net:
                return True
        return False
    except ValueError:
        return True


def validate_url_security(url: str) -> str:
    """
    Validate a URL string for security compliance (SSRF prevention).

    - Must use http or https protocol.
    - Resolves hostname and verifies that IP address is not private/blocked.
    """
    if not url or not isinstance(url, str):
        raise SSRFValidationError("URL không hợp lệ.")

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        raise SSRFValidationError("Giao thức URL phải là http hoặc https.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFValidationError("URL không chứa tên miền hợp lệ.")

    # Check for direct IP host
    try:
        ip = ipaddress.ip_address(hostname)
        if is_ip_private_or_blocked(str(ip)):
            raise SSRFValidationError(f"Địa chỉ IP {hostname} bị chặn do lý do bảo mật (SSRF).")
        return url
    except ValueError:
        pass  # Hostname is a domain name, proceed to DNS resolution

    # DNS Resolution check
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        if not addr_info:
            raise SSRFValidationError(f"Không thể phân giải tên miền: {hostname}")

        for family, socktype, proto, canonname, sockaddr in addr_info:
            resolved_ip = sockaddr[0]
            if is_ip_private_or_blocked(resolved_ip):
                logger.warning("SSRF blocked resolved IP", hostname=hostname, ip=resolved_ip)
                raise SSRFValidationError(
                    f"Tên miền {hostname} phân giải về địa chỉ nội bộ ({resolved_ip}) bị cấm truy cập."
                )
    except socket.gaierror as e:
        raise SSRFValidationError(f"Không thể kết nối đến tên miền {hostname}: {str(e)}")

    return url


async def safe_http_head_or_get(client: httpx.AsyncClient, url: str, max_redirects: int = 5) -> httpx.Response:
    """
    Execute HTTP HEAD or GET request safely, validating IP address on each redirect step.
    """
    current_url = url
    for redirect_count in range(max_redirects + 1):
        validate_url_security(current_url)
        res = await client.get(current_url, follow_redirects=False)
        if res.is_redirect:
            location = res.headers.get("Location")
            if not location:
                raise SSRFValidationError("Redirect response missing Location header.")
            # Resolve relative redirect URLs
            if location.startswith("/"):
                parsed = urlparse(current_url)
                current_url = f"{parsed.scheme}://{parsed.netloc}{location}"
            else:
                current_url = location
        else:
            return res

    raise SSRFValidationError("Vượt quá số lần chuyển hướng (too many redirects).")
