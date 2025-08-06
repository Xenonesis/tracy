"""
DNS & WHOIS Utility Module
Provides DNS record lookups and WHOIS info using free libraries.
"""

import socket
from typing import Dict, Any, List

import whois  # python-whois
import dns.resolver  # dnspython


def resolve_dns(domain: str) -> Dict[str, Any]:
    """Resolve common DNS records for a domain."""
    records_to_check = ["A", "AAAA", "MX", "NS", "TXT"]
    out: Dict[str, Any] = {"domain": domain, "records": {}, "errors": {}}
    resolver = dns.resolver.Resolver()

    for rtype in records_to_check:
        try:
            answers = resolver.resolve(domain, rtype, lifetime=5.0)
            values: List[str] = []
            for rdata in answers:
                try:
                    values.append(str(rdata).strip())
                except Exception:
                    values.append(repr(rdata))
            out["records"][rtype] = values
        except Exception as e:
            out["errors"][rtype] = str(e)
    return out


def whois_lookup(domain: str) -> Dict[str, Any]:
    """Perform a WHOIS lookup for a domain."""
    try:
        data = whois.whois(domain)
        # python-whois returns a dict-like object with many fields
        simplified = {
            "domain_name": _safe_str(data.get("domain_name")),
            "registrar": _safe_str(data.get("registrar")),
            "creation_date": _safe_str(data.get("creation_date")),
            "expiration_date": _safe_str(data.get("expiration_date")),
            "updated_date": _safe_str(data.get("updated_date")),
            "status": data.get("status"),
            "name_servers": data.get("name_servers"),
            "emails": data.get("emails"),
            "country": data.get("country"),
            "org": data.get("org"),
        }
        return {"domain": domain, "whois": simplified}
    except Exception as e:
        return {"domain": domain, "error": f"WHOIS failed: {e}"}


def email_domain_from_address(email: str) -> str:
    """Extract domain from email address."""
    try:
        return email.split("@", 1)[1].strip().lower()
    except Exception:
        return ""


def _safe_str(value) -> str:
    """Coerce python-whois possibly-list values to string."""
    if isinstance(value, list):
        return ", ".join([str(v) for v in value])
    return str(value) if value is not None else ""
