"""paperforge i18n strings."""

from typing import Final

STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "title": "PaperForge",
        "section.summary": "Summary",
        "section.context": "Context",
        "section.decisions": "Key decisions",
        "section.open_questions": "Open questions",
        "section.next_steps": "Next steps",
        "section.body": "Details",
        "label.project": "Project",
        "label.created": "Created",
        "label.format": "Format",
        "label.file_path": "File saved to",
        "label.size": "Size",
        "label.sections": "Sections",
        "label.decisions": "Decisions",
        "label.questions": "Open questions",
        "label.steps": "Next steps",
        "label.tags": "Tags",
        "decision.chose": "Chose",
        "decision.why": "Why",
        "decision.rejected": "Rejected",
        "decision.when": "When",
        "footer.note": (
            "This document was synthesized by an AI agent through paperforge. "
            "Edit it freely — Markdown is portable and Obsidian-friendly."
        ),
        "error.empty_title": (
            "title is required - synthesize one from the user's request, "
            "do not use placeholders like 'Untitled'."
        ),
        "error.empty_summary": (
            "summary could not be derived from sections - provide a summary "
            "or at least one section with non-empty content."
        ),
        "error.no_content": (
            "Provide either a `body` string (simplest) or a `sections` list with content. "
            "The tool will not fabricate content from nothing."
        ),
        "error.invalid_format": "format must be one of: md, html, docx, pdf.",
        "error.write_failed": "Failed to write the document file.",
        "error.docx_missing": "python-docx is not installed.",
        "error.pdf_missing": "weasyprint (or another PDF engine) is not available.",
        "hint.install_docx": "Install with `pip install python-docx`.",
        "hint.install_pdf": (
            "Install with `pip install weasyprint`. On Linux, weasyprint also "
            "needs Cairo/Pango: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`."
        ),
    },
    "tr": {
        "title": "PaperForge",
        "section.summary": "Özet",
        "section.context": "Bağlam",
        "section.decisions": "Önemli kararlar",
        "section.open_questions": "Açık sorular",
        "section.next_steps": "Sonraki adımlar",
        "section.body": "Detaylar",
        "label.project": "Proje",
        "label.created": "Oluşturulma",
        "label.format": "Biçim",
        "label.file_path": "Dosya konumu",
        "label.size": "Boyut",
        "label.sections": "Bölüm",
        "label.decisions": "Karar",
        "label.questions": "Açık soru",
        "label.steps": "Sonraki adım",
        "label.tags": "Etiketler",
        "decision.chose": "Seçilen",
        "decision.why": "Neden",
        "decision.rejected": "Vazgeçilen",
        "decision.when": "Ne zaman",
        "footer.note": (
            "Bu doküman bir AI agent tarafından paperforge üzerinden sentezlendi. "
            "Serbestçe düzenleyin — Markdown taşınabilir ve Obsidian uyumludur."
        ),
        "error.empty_title": (
            "title zorunlu - kullanıcının isteğinden gerçek bir başlık türet, "
            "'Untitled' gibi yer-tutucu kullanma."
        ),
        "error.empty_summary": (
            "summary bölümlerden türetilemedi - bir summary gir veya içerikli "
            "en az bir bölüm sağla."
        ),
        "error.no_content": (
            "Ya bir `body` stringi (en basit yol) ya da içerikli bir `sections` listesi gir. "
            "Araç boştan içerik uydurmaz."
        ),
        "error.invalid_format": "format şunlardan biri olmalı: md, html, docx, pdf.",
        "error.write_failed": "Dosya yazma başarısız oldu.",
        "error.docx_missing": "python-docx yüklü değil.",
        "error.pdf_missing": "weasyprint (veya başka bir PDF motoru) bulunamadı.",
        "hint.install_docx": "Kurulum: `pip install python-docx`.",
        "hint.install_pdf": (
            "Kurulum: `pip install weasyprint`. Linux'ta Cairo/Pango da gerekir: "
            "`sudo apt install libpango-1.0-0 libpangoft2-1.0-0`."
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
