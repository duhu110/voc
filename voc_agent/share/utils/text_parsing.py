from __future__ import annotations

import json
import re


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


def parse_json_payload_once(content: str) -> dict:
    """Parse provider text into a JSON object with one extra cleanup attempt."""
    text = extract_json_text(content)
    try:
        return json.loads(text)
    except json.JSONDecodeError as original_error:
        repaired = repair_json_text_once(text)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            raise original_error


def repair_json_text_once(text: str) -> str:
    candidate = text.strip()
    candidate = re.sub(r"^json\s*", "", candidate, flags=re.IGNORECASE)
    candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)
    start = candidate.find("{")
    if start == -1:
        return candidate

    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(candidate[start:], start=start):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return candidate[start : index + 1].strip()
    return candidate


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
