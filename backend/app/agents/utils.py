from typing import Optional

def clean_json_text(text: Optional[str]) -> str:
    """Extracts raw JSON content from text that might contain markdown blocks or conversational prefixes/suffixes."""
    if not text:
        return ""
    text = text.strip()
    start_idx = -1
    for i, char in enumerate(text):
        if char in ('{', '['):
            start_idx = i
            break
    end_idx = -1
    for i in range(len(text) - 1, -1, -1):
        if text[i] in ('}', ']'):
            end_idx = i
            break
    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
        return text[start_idx:end_idx + 1]
    return text
