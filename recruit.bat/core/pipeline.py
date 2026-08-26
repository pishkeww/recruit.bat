from core.prompts import (
    combined_llm_prompt,
    parse_combined_output,
)
from core.processing.keyword_extractor import extract_keywords
from core.processing.text_cleaner import clean_for_matching
from core.processing.embedder import create_embedder
from core.scoring.ats_scorer import compute_ats_score
from core.scoring.education_matcher import calculate_edu_score


class Pipeline:
    def __init__(self, llm=None):
        self.llm = llm
        self.embedder = create_embedder()

    def run(self, resume_text, job_text, keywords_override=None):
        clean_resume = clean_for_matching(resume_text)

        resume_keywords = extract_keywords(clean_resume, top_n=50)

        if keywords_override:
            job_keywords = keywords_override
        else:
            job_keywords = extract_keywords(job_text, top_n=30)

        semantic_sim = 0.5
        if self.embedder:
            try:
                semantic_sim = self.embedder.similarity(
                    clean_resume[:2000], job_text[:2000]
                )
                semantic_sim = max(0.0, min(1.0, semantic_sim))
            except Exception:
                semantic_sim = 0.5

        edu_score = calculate_edu_score(resume_text, job_text, self.embedder)

        scores = compute_ats_score(
            clean_resume, resume_keywords, job_keywords,
            semantic_sim, edu_score
        )

        structured = {}
        cover_letter = ""
        suggestions = ""
        skills = {}

        if self.llm:
            prompt = combined_llm_prompt(
                resume_text[:3000], job_text[:3000], job_keywords
            )
            response = self.llm.generate(prompt)

            if response.get("status") == "success":
                data = parse_combined_output(response["data"])

                structured = {
                    "name": data.get("name", ""),
                    "email": data.get("email", ""),
                    "phone": data.get("phone", ""),
                    "location": data.get("location", ""),
                    "total_experience_years": data.get("total_experience_years", 0),
                    "experience": data.get("experience", []),
                    "education": data.get("education", []),
                    "skills": data.get("skills", []),
                }

                raw_skills = data.get("skills", [])
                if isinstance(raw_skills, list):
                    skills = {s.lower(): "present" for s in raw_skills if len(s) > 2}

                cover_letter = data.get("cover_letter", "")

                missing = data.get("missing_keywords", [])
                improvements = data.get("improvements", [])
                rewrites = data.get("rewritten_examples", [])

                sug_parts = []
                if missing:
                    sug_parts.append("MISSING KEYWORDS:\n" + "\n".join(f"- {k}" for k in missing))
                if improvements:
                    sug_parts.append("IMPROVEMENTS:\n" + "\n".join(f"- {i}" for i in improvements))
                if rewrites:
                    rw_lines = []
                    for r in rewrites:
                        if isinstance(r, dict):
                            rw_lines.append(f"Before: {r.get('before', '')}")
                            rw_lines.append(f"  After: {r.get('after', '')}")
                    sug_parts.append("REWRITTEN EXAMPLES:\n" + "\n".join(rw_lines))

                suggestions = "\n\n".join(sug_parts)

        return {
            "score": scores["score"],
            "keyword": scores["keyword"],
            "semantic": scores["semantic"],
            "recency": scores["recency"],
            "education": scores["education"],
            "confidence": scores["score"],
            "skills": skills,
            "structured": structured,
            "cover_letter": cover_letter,
            "suggestions": suggestions,
            "job_keywords": job_keywords
        }
