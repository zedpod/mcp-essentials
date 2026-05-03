"""paperforge.core - pure logic for assembling and writing documents."""

from .build import create_document, default_output_dir
from .i18n import DEFAULT, SUPPORTED, normalize_lang, t
from .md_writer import render_markdown
from .render import to_markdown
from .types import (
    Decision,
    DocumentArtifact,
    DocumentFormat,
    ErrorInfo,
    Result,
    Section,
)

__bundle_order__ = [
    "types",
    "i18n",
    "md_writer",
    "html_writer",
    "docx_writer",
    "pdf_writer",
    "build",
    "render",
]

__all__ = [
    "create_document",
    "default_output_dir",
    "render_markdown",
    "to_markdown",
    "Result",
    "Section",
    "Decision",
    "DocumentArtifact",
    "DocumentFormat",
    "ErrorInfo",
    "t",
    "normalize_lang",
    "SUPPORTED",
    "DEFAULT",
]
