import math
import re
from datetime import datetime

ALPHA = 0.40
BETA = 0.25
GAMMA = 0.20
DELTA = 0.15


def keyword_score(resume_keywords, job_keywords):
    if not job_keywords:
        return 0.0

    intersection = set(resume_keywords) & set(job_keywords)
    coverage = len(intersection) / len(job_keywords)
    saturation = 1 - math.exp(-2 * len(intersection))
    score = 0.6 * coverage + 0.4 * saturation

    return min(1.0, score)


def compute_recency(resume_text):
    years = re.findall(r'\b20\d{2}\b', resume_text)

    if not years:
        return 0.6

    latest = max(map(int, years))
    current_year = datetime.now().year
    t = max(0, current_year - latest)

    if t <= 1:
        return 1.0
    elif t <= 3:
        return 0.85
    elif t <= 5:
        return 0.7
    else:
        return 0.5


def compute_ats_score(
    resume_text,
    resume_keywords,
    job_keywords,
    semantic_sim,
    edu_score
):
    kw = keyword_score(resume_keywords, job_keywords)
    recency = compute_recency(resume_text)
    semantic_sim = max(0.3, semantic_sim)

    final = (
        ALPHA * kw +
        BETA * semantic_sim +
        GAMMA * recency +
        DELTA * edu_score
    )

    score = max(0, min(1, final)) * 100

    return {
        "score": round(score, 2),
        "keyword": round(kw * 100, 2),
        "semantic": round(semantic_sim * 100, 2),
        "recency": round(recency * 100, 2),
        "education": round(edu_score * 100, 2)
    }
