from __future__ import annotations


def extract_json_text(content: str) -> str:
    """Strip markdown code fences and return the inner JSON text."""
    text = content.strip()
    if text.startswith('```'):
        lines = text.splitlines()
        if lines and lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        text = '\n'.join(lines).strip()
    if text and not text.startswith('{'):
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1].strip()
    return text


def parse_bracket_code(value: str) -> list[str]:
    """Parse values like '[GROUP] [CODE]' into ['GROUP', 'CODE']."""
    parts: list[str] = []
    current = ''
    inside = False
    for char in value:
        if char == '[':
            inside = True
            current = ''
            continue
        if char == ']' and inside:
            inside = False
            if current.strip():
                parts.append(current.strip())
            current = ''
            continue
        if inside:
            current += char
    if not parts and value.strip():
        parts.append(value.strip())
    return parts
