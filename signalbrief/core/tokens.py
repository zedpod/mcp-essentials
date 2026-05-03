"""Token-level matching utilities for keyword scoring.

Substring matching is forbidden by the repo conventions (`"ai" in "brain"` is
the canonical bug). We tokenize on Unicode word boundaries and either match
whole tokens or split phrases into adjacent token runs.
"""

import re

WORD_RE = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    return [m.group(0).lower() for m in WORD_RE.finditer(text)]


def keyword_matches(haystack_tokens: list[str], keyword: str) -> int:
    """Count occurrences of `keyword` (potentially multi-word) in tokenized haystack.

    Multi-word keywords match adjacent token runs.
    """
    kw_tokens = tokenize(keyword)
    if not kw_tokens:
        return 0
    if len(kw_tokens) == 1:
        target = kw_tokens[0]
        return sum(1 for tok in haystack_tokens if tok == target)
    n = len(kw_tokens)
    count = 0
    for i in range(len(haystack_tokens) - n + 1):
        if haystack_tokens[i : i + n] == kw_tokens:
            count += 1
    return count
