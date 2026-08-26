import csv
import json
import os
from datetime import datetime


def export_csv(results, output_path):
    if not results:
        return

    fieldnames = [
        "rank", "filename", "score", "keyword", "semantic",
        "recency", "education", "name", "email", "phone",
        "location", "total_experience_years", "education_degree",
        "education_institution", "skills"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, r in enumerate(results, 1):
            structured = r.get("structured", {})
            exp = structured.get("experience", [])
            total_years = structured.get("total_experience_years", 0)
            edu = structured.get("education", [])
            edu_str = "; ".join(
                f"{e.get('degree', '')} - {e.get('institution', '')}"
                for e in edu
            ) if edu else ""
            skills_list = structured.get("skills", [])

            writer.writerow({
                "rank": i,
                "filename": r.get("filename", ""),
                "score": r.get("score", 0),
                "keyword": r.get("keyword", 0),
                "semantic": r.get("semantic", 0),
                "recency": r.get("recency", 0),
                "education": r.get("education", 0),
                "name": structured.get("name", ""),
                "email": structured.get("email", ""),
                "phone": structured.get("phone", ""),
                "location": structured.get("location", ""),
                "total_experience_years": total_years,
                "education_degree": edu_str,
                "education_institution": "; ".join(
                    e.get("institution", "") for e in edu
                ),
                "skills": "; ".join(skills_list)
            })


def export_json(results, output_path):
    output = []
    for i, r in enumerate(results, 1):
        structured = r.get("structured", {})
        output.append({
            "rank": i,
            "filename": r.get("filename", ""),
            "scores": {
                "final": r.get("score", 0),
                "keyword": r.get("keyword", 0),
                "semantic": r.get("semantic", 0),
                "recency": r.get("recency", 0),
                "education": r.get("education", 0)
            },
            "structured_data": structured,
            "job_keywords": r.get("job_keywords", [])
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
