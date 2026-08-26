def match_skills(resume_text: str, job_keywords: list):
    resume_lower = resume_text.lower()
    results = {}

    for skill in job_keywords:
        count = resume_lower.count(skill.lower())

        if count >= 2:
            results[skill] = "STRONG"
        elif count == 1:
            results[skill] = "WEAK"
        else:
            results[skill] = "MISSING"

    return results