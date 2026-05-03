"""sitepulse i18n strings."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title": "SitePulse",
        "section.dns": "DNS",
        "section.rdap": "Domain Registration (RDAP)",
        "section.ssl": "TLS Certificate",
        "section.http": "HTTP",
        "section.https": "HTTPS",
        "section.issues": "Issues",
        "label.host": "Host",
        "label.registered_domain": "Registered domain",
        "label.no_records": "no records",
        "label.expires_in": "Expires in",
        "label.days": "days",
        "label.registrar": "Registrar",
        "label.registered_on": "Registered on",
        "label.expires_on": "Expires on",
        "label.name_servers": "Name servers",
        "label.no_data": "no data",
        "error.empty_input": "Domain or URL is required.",
        "error.invalid_input": "Could not parse a valid hostname from the input.",
        "issue.no_a_records": "Domain has no A or AAAA records.",
        "issue.cert_expired": "TLS certificate is expired.",
        "issue.cert_expiring_soon": "TLS certificate expires in {days} days.",
        "issue.https_unreachable": "HTTPS endpoint is unreachable.",
        "issue.no_hsts": "HSTS header is missing.",
        "issue.no_dmarc": "No DMARC record found.",
        "issue.no_spf": "No SPF record found.",
        "note.audit": "For page-level SEO/AI signals see pagesignal.",
    },
    "tr": {
        "title": "SitePulse",
        "section.dns": "DNS",
        "section.rdap": "Alan Adı Kaydı (RDAP)",
        "section.ssl": "TLS Sertifikası",
        "section.http": "HTTP",
        "section.https": "HTTPS",
        "section.issues": "Bulgular",
        "label.host": "Host",
        "label.registered_domain": "Kayıtlı alan",
        "label.no_records": "kayıt yok",
        "label.expires_in": "Süresi",
        "label.days": "gün",
        "label.registrar": "Tescil eden",
        "label.registered_on": "Tescil tarihi",
        "label.expires_on": "Son geçerlilik",
        "label.name_servers": "Ad sunucuları",
        "label.no_data": "veri yok",
        "error.empty_input": "Alan adı veya URL zorunlu.",
        "error.invalid_input": "Girdiden geçerli bir host adı çıkarılamadı.",
        "issue.no_a_records": "Alan adının A/AAAA kaydı yok.",
        "issue.cert_expired": "TLS sertifikası süresi dolmuş.",
        "issue.cert_expiring_soon": "TLS sertifikasının süresi {days} gün içinde dolacak.",
        "issue.https_unreachable": "HTTPS uç noktasına erişilemiyor.",
        "issue.no_hsts": "HSTS başlığı yok.",
        "issue.no_dmarc": "DMARC kaydı bulunamadı.",
        "issue.no_spf": "SPF kaydı bulunamadı.",
        "note.audit": "Sayfa düzeyinde SEO/AI sinyalleri için pagesignal'i kullanın.",
    },
}

SUPPORTED: Final[tuple[str, ...]] = ("en", "tr")
DEFAULT: Final[str] = "en"


def normalize_lang(lang: str | None) -> str:
    if not lang:
        return DEFAULT
    base = lang.lower().split("-")[0]
    return base if base in SUPPORTED else DEFAULT


def t(key: str, lang: str = DEFAULT, **kwargs: object) -> str:
    lang = normalize_lang(lang)
    table = STRINGS.get(lang) or STRINGS[DEFAULT]
    template = table.get(key) or STRINGS[DEFAULT].get(key) or key
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
