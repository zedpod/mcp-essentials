"""Per-tool string table for pagesignal."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title": "PageSignal",
        "section.meta": "Meta Tags",
        "section.headings": "Headings",
        "section.readability": "Readability",
        "section.geo": "AI-Answer Signals (GEO)",
        "section.performance": "Performance",
        "section.issues": "Issues",
        "label.url": "URL",
        "label.final_url": "Final URL",
        "label.title": "Title",
        "label.description": "Description",
        "label.canonical": "Canonical",
        "label.robots": "Robots",
        "label.lang": "Language",
        "label.h1_count": "H1 count",
        "label.h2_count": "H2 count",
        "label.word_count": "Word count",
        "label.sentence_count": "Sentence count",
        "label.avg_sentence_length": "Avg sentence length",
        "label.detected_language": "Detected language",
        "label.schema_types": "Schema types",
        "label.question_headings": "Question-style headings",
        "label.bytes": "Bytes",
        "label.response_time": "Response time",
        "label.status": "Status code",
        "label.redirects": "Redirects",
        "label.no_issues": "No issues found.",
        "issue.empty_title": "Title tag is missing or empty.",
        "issue.title_too_short": "Title is shorter than 30 characters.",
        "issue.title_too_long": "Title exceeds 65 characters; may be truncated by search engines.",
        "issue.empty_description": "Meta description is missing.",
        "issue.description_too_short": "Meta description is shorter than 70 characters.",
        "issue.description_too_long": "Meta description exceeds 160 characters.",
        "issue.no_h1": "Page has no H1 heading.",
        "issue.multiple_h1": "Page has multiple H1 headings; pick one canonical title.",
        "issue.skipped_heading_levels": "Heading hierarchy skipped levels: {levels}",
        "issue.no_canonical": "No canonical link element.",
        "issue.no_open_graph": "Open Graph tags are missing - social previews will be generic.",
        "issue.noindex": "Page is marked noindex; it will not be indexed.",
        "issue.no_lang": "<html> has no lang attribute.",
        "issue.no_schema": "No structured data (JSON-LD) detected.",
        "issue.javascript_heavy": "Body contains very little text - looks JS-rendered. AI crawlers may see less.",
        "issue.large_response": "HTML payload exceeds {kb} KB.",
        "issue.slow_response": "Response time {ms} ms exceeds the 1500 ms target.",
        "error.url_required": "URL is required.",
        "error.invalid_url": "URL must include http:// or https://.",
        "error.unreachable": "Could not fetch the page (network or server error).",
        "error.unsupported_content_type": "Unsupported content type: {ct}.",
        "hint.try_https": "Try the https:// variant of the URL.",
        "hint.spa": "Look for a server-rendered route or test with a headless browser.",
        "note.audit": (
            "PageSignal audits a single URL. For domain-level health (DNS, SSL, RDAP) "
            "see sitepulse."
        ),
    },
    "tr": {
        "title": "PageSignal",
        "section.meta": "Meta Etiketleri",
        "section.headings": "Başlıklar",
        "section.readability": "Okunabilirlik",
        "section.geo": "Yapay Zekâ Cevap Sinyalleri (GEO)",
        "section.performance": "Performans",
        "section.issues": "Bulgular",
        "label.url": "URL",
        "label.final_url": "Son URL",
        "label.title": "Başlık",
        "label.description": "Açıklama",
        "label.canonical": "Canonical",
        "label.robots": "Robots",
        "label.lang": "Dil",
        "label.h1_count": "H1 sayısı",
        "label.h2_count": "H2 sayısı",
        "label.word_count": "Kelime",
        "label.sentence_count": "Cümle",
        "label.avg_sentence_length": "Ortalama cümle uzunluğu",
        "label.detected_language": "Tespit edilen dil",
        "label.schema_types": "Schema türleri",
        "label.question_headings": "Soru biçimli başlıklar",
        "label.bytes": "Bayt",
        "label.response_time": "Yanıt süresi",
        "label.status": "Durum kodu",
        "label.redirects": "Yönlendirmeler",
        "label.no_issues": "Bulgu yok.",
        "issue.empty_title": "Başlık etiketi yok veya boş.",
        "issue.title_too_short": "Başlık 30 karakterden kısa.",
        "issue.title_too_long": "Başlık 65 karakteri aşıyor; arama sonucunda kesilebilir.",
        "issue.empty_description": "Meta açıklama yok.",
        "issue.description_too_short": "Meta açıklama 70 karakterden kısa.",
        "issue.description_too_long": "Meta açıklama 160 karakteri aşıyor.",
        "issue.no_h1": "Sayfada H1 başlığı yok.",
        "issue.multiple_h1": "Birden fazla H1 var; tek canonical başlık tercih edin.",
        "issue.skipped_heading_levels": "Başlık seviyeleri atlanmış: {levels}",
        "issue.no_canonical": "Canonical bağlantısı yok.",
        "issue.no_open_graph": "Open Graph etiketleri eksik - sosyal medya önizlemeleri sade olur.",
        "issue.noindex": "Sayfa noindex olarak işaretli; arama motoru indekslemez.",
        "issue.no_lang": "<html> etiketinde lang yok.",
        "issue.no_schema": "Yapılandırılmış veri (JSON-LD) bulunamadı.",
        "issue.javascript_heavy": "Gövdede metin çok az; JS ile render ediliyor olabilir. AI tarayıcılar daha az görür.",
        "issue.large_response": "HTML yükü {kb} KB'yi aşıyor.",
        "issue.slow_response": "Yanıt süresi {ms} ms; 1500 ms hedefini aşıyor.",
        "error.url_required": "URL zorunlu.",
        "error.invalid_url": "URL http:// veya https:// içermeli.",
        "error.unreachable": "Sayfa çekilemedi (ağ veya sunucu hatası).",
        "error.unsupported_content_type": "Desteklenmeyen içerik türü: {ct}.",
        "hint.try_https": "URL'in https:// varyantını deneyin.",
        "hint.spa": "Sunucu render eden bir varyant deneyin veya headless browser kullanın.",
        "note.audit": (
            "PageSignal tek bir URL'i denetler. Alan adı sağlığı (DNS, SSL, RDAP) "
            "için sitepulse'ı kullanın."
        ),
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
