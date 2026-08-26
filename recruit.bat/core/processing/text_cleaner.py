import re

CONTACT_PATTERNS = re.compile(
    r'[\w\.\-\+]+@[\w\.\-]+'
    r'|linkedin\.com/in/[\w\-]+'
    r'|github\.com/[\w\-]+'
    r'|https?://[^\s]+'
    r'|www\.[^\s]+'
    r'|\+91[\s\d\-]+'
    r'|\+\d{1,3}[\s\d\-]{7,}',
    re.IGNORECASE
)

LABEL_LINE = re.compile(
    r'^(LinkedIn|GitHub|Phone|Email|Tel|Mobile|Address|Portfolio)\s*:',
    re.IGNORECASE
)

BULLET = re.compile(r'^[\s]*[●\-\*\•]\s*', re.MULTILINE)

HEADING_WORDS = {
    "summary", "objective", "profile", "overview", "about",
    "skills", "technical", "technologies", "competencies", "tools",
    "education", "academic", "qualification", "degree",
    "experience", "employment", "positions", "work",
    "projects", "project", "portfolio",
    "certifications", "certification", "achievements", "awards", "honors",
    "soft", "interests", "hobbies", "languages", "references",
    "publications", "patents", "conferences", "presentations",
    "volunteer", "community", "leadership",
}


def _is_heading(line):
    stripped = line.strip().rstrip(":").strip()
    if not stripped:
        return False
    words = stripped.lower().split()
    if len(words) > 5:
        return False
    if any(c in stripped for c in ".;,"):
        return False
    if re.search(r'\d{4}', stripped):
        return False
    match_count = sum(1 for w in words if w in HEADING_WORDS)
    if match_count == 0:
        return False
    if match_count >= len(words) * 0.5:
        return True
    if len(words) <= 2 and match_count >= 1:
        return True
    return False


def _is_name_line(line, prev_line, next_line):
    stripped = line.strip()
    if not stripped:
        return False
    if len(stripped) > 50:
        return False
    if any(c.isdigit() for c in stripped):
        return False
    if any(c in stripped for c in "@./+"):
        return False
    words = stripped.split()
    if len(words) > 4:
        return False
    if not all(w[0].isupper() for w in words if len(w) > 1):
        return False
    next_stripped = (next_line or "").strip().lower()
    has_contact_after = any(k in next_stripped for k in ["email", "phone", "linkedin", "github", "@", "+91"])
    has_location_after = bool(re.match(r'^[A-Za-z\s]+,\s*[A-Za-z\s]+', next_stripped))
    if has_contact_after or has_location_after:
        return True
    prev_stripped = (prev_line or "").strip()
    if not prev_stripped:
        return True
    return False


def clean_for_matching(text):
    lines = text.split("\n")
    result = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            continue

        if CONTACT_PATTERNS.search(stripped):
            continue

        if LABEL_LINE.match(stripped):
            continue

        if re.match(r'^[\d\s\+\-]{4,}$', stripped):
            continue

        if _is_heading(stripped):
            continue

        prev_line = lines[i - 1] if i > 0 else ""
        next_line = lines[i + 1] if i < len(lines) - 1 else ""
        if _is_name_line(stripped, prev_line, next_line):
            continue

        cleaned = BULLET.sub("", stripped)
        if cleaned:
            result.append(cleaned)

    return "\n".join(result)
