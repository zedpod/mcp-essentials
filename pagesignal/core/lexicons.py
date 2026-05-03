"""Multi-language question-word lexicons for GEO signal detection.

Used by `audit.py` to mark a heading as "question-style" — these heading types
correlate with content that AI engines tend to lift directly into answers.
"""

QUESTION_WORDS: dict[str, frozenset[str]] = {
    "en": frozenset(
        {
            "what", "why", "how", "when", "where", "who", "which", "whose",
            "is", "are", "do", "does", "did", "can", "could", "should",
            "would", "will",
        }
    ),
    "tr": frozenset(
        {
            "ne", "nedir", "neden", "niye", "niçin", "nasıl", "nasil", "ne zaman",
            "nerede", "kim", "kimdir", "hangi", "hangisi", "kaç", "kac",
        }
    ),
    "de": frozenset(
        {
            "was", "warum", "wieso", "weshalb", "wie", "wann", "wo", "woher",
            "wohin", "wer", "wessen", "welche", "welcher", "welches",
        }
    ),
    "es": frozenset(
        {
            "qué", "que", "por qué", "porqué", "cómo", "como", "cuándo", "cuando",
            "dónde", "donde", "quién", "quien", "cuál", "cual", "cuáles", "cuales",
        }
    ),
    "fr": frozenset(
        {
            "que", "quoi", "pourquoi", "comment", "quand", "où", "ou", "qui",
            "quel", "quelle", "quels", "quelles",
        }
    ),
    "it": frozenset(
        {
            "che", "cosa", "perché", "perche", "come", "quando", "dove",
            "chi", "quale", "quali",
        }
    ),
    "pt": frozenset(
        {
            "que", "o que", "por que", "porque", "como", "quando", "onde", "quem",
            "qual", "quais",
        }
    ),
    "ar": frozenset(
        {
            "ما", "ماذا", "لماذا", "كيف", "متى", "أين", "اين", "من", "أي", "اي",
        }
    ),
}


def is_question(text: str, language: str) -> bool:
    """True if the text begins with a question-word in the given language, or ends with '?'."""
    if not text:
        return False
    stripped = text.strip()
    if stripped.endswith("?") or stripped.endswith("؟"):
        return True
    lower = stripped.lower()
    words = QUESTION_WORDS.get(language) or set()
    for w in words:
        if lower.startswith(w + " ") or lower == w:
            return True
    return False
