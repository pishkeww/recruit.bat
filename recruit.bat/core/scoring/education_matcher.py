import re

DEGREE_ALIASES = {
    "phd": 4, "doctorate": 4, "d.phil": 4,
    "mtech": 3, "m.tech": 3, "mca": 3, "msc": 3, "m.sc": 3,
    "ms": 3, "m.s": 3, "master": 3, "mba": 3,
    "btech": 2, "b.tech": 2, "be": 2, "b.e": 2,
    "bca": 2, "bsc": 2, "b.sc": 2, "bachelor": 2,
    "diploma": 1
}


def extract_degree(text):
    text = text.lower()

    found = []
    for degree, rank in DEGREE_ALIASES.items():
        pattern = re.escape(degree)
        if re.search(rf'\b{pattern}\b', text):
            found.append((degree, rank))

    if not found:
        return 0, ""

    degree, rank = max(found, key=lambda x: x[1])

    match = re.search(rf'\b{degree}\b.*?(?=\.|\n|,|$)', text)
    return rank, match.group(0) if match else degree


def calculate_edu_score(resume_text, jd_text, embedder=None):
    req_rank, req_str = extract_degree(jd_text)
    cand_rank, cand_str = extract_degree(resume_text)

    if req_rank == 0:
        return 1.0

    hierarchy_score = 1.0 if cand_rank >= req_rank else 0.7

    semantic = 0.5
    if embedder and req_str and cand_str:
        semantic = embedder.similarity(req_str, cand_str)

    score = 0.6 * hierarchy_score + 0.4 * semantic

    return max(0.5, min(1.0, score))
