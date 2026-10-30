from __future__ import annotations


def evidence_text(value: object) -> list[str]:
    """All text retained in a complete blinded observation."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for child in value.values() for text in evidence_text(child)]
    if isinstance(value, list):
        return [text for child in value for text in evidence_text(child)]
    return []
