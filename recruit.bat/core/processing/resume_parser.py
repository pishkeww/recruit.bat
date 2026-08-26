import fitz


def parse_resume_pdf(path: str) -> str:
    text = []

    # SAFE: main thread only
    with fitz.open(path) as doc:
        for page in doc:
            text.append(page.get_text())

    return "\n".join(text)