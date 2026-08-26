import json


def cover_letter_prompt(resume: str, job: str) -> str:
    return f"""
You are an expert career assistant.

TASK:
Write a highly tailored, professional cover letter.

INPUT:

=== RESUME ===
{resume}

=== JOB DESCRIPTION ===
{job}

STRICT REQUIREMENTS:
- Maximum 500 words
- Use ONLY relevant experience from the resume
- Directly align skills with job requirements
- Include concrete achievements (no vague claims)
- Avoid generic phrases (e.g., "passionate", "hardworking")
- No repetition

STRUCTURE (MANDATORY):
1. Opening: role + strong value proposition
2. Experience: direct alignment with job
3. Impact: measurable or specific contributions
4. Closing: concise and confident

OUTPUT RULES:
- Output ONLY the cover letter
- No headings
- No explanations
- No extra text before or after

BEGIN OUTPUT:
"""


def suggestions_prompt(resume: str, job_keywords: list) -> str:
    keywords_str = ", ".join(job_keywords)

    return f"""
You are an ATS optimization expert.

TASK:
Improve the resume to better match job requirements.

INPUT:

=== RESUME ===
{resume}

=== IMPORTANT KEYWORDS ===
{keywords_str}

STRICT REQUIREMENTS:
- Focus on missing or weak keywords
- Provide actionable, specific improvements
- Avoid generic advice
- Strengthen wording using impactful action verbs
- Quantify achievements where possible

OUTPUT FORMAT (STRICT):

MISSING KEYWORDS:
- ...

IMPROVEMENTS:
- ...

REWRITTEN EXAMPLES:
- Before: ...
  After: ...

- Before: ...
  After: ...

OUTPUT RULES:
- Follow format EXACTLY
- No extra commentary
- No explanations outside sections

BEGIN OUTPUT:
"""


def combined_llm_prompt(resume: str, job_text: str, job_keywords: list) -> str:
    keywords_str = ", ".join(job_keywords)
    return f"""
You are an expert career assistant and resume parser.

TASK: Process this resume and return ALL of the following in a SINGLE JSON object.

INPUT:

=== RESUME ===
{resume}

=== JOB DESCRIPTION ===
{job_text}

=== JOB KEYWORDS ===
{keywords_str}

RETURN A SINGLE VALID JSON OBJECT WITH THESE FIELDS:

{{
  "name": "candidate full name",
  "email": "email or empty string",
  "phone": "phone or empty string",
  "location": "city, country or empty string",
  "total_experience_years": 0,
  "experience": [
    {{"role": "title", "company": "name", "start": "date", "end": "date or Present", "duration_months": 0}}
  ],
  "education": [
    {{"degree": "degree name", "institution": "school name", "year": "year", "gpa": "gpa or empty"}}
  ],
  "skills": ["skill1", "skill2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "improvements": ["improvement1", "improvement2"],
  "rewritten_examples": [
    {{"before": "original text", "after": "improved text"}}
  ],
  "cover_letter": "the full cover letter text"
}}

RULES:
- Return ONLY the JSON object
- No explanations, no markdown, no code blocks
- Use empty string for missing fields, 0 for missing numbers
- Skills: concise 1-3 word technical skills only
- Cover letter: max 400 words, tailored to this resume+job
- Missing keywords: important job keywords absent from the resume
- Improvements: 3-5 specific actionable suggestions
- Rewritten examples: 2-3 before/after pairs from the resume

BEGIN JSON:
"""


def parse_combined_output(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            pass

    return {}


def skill_extraction_prompt(text: str) -> str:
    return f"""
You are an expert at extracting professional skills.

TASK:
Extract key skills from the resume.

INPUT:
{text}

RULES:
- Return ONLY comma-separated values
- No explanations
- No duplicates
- Include technical, tools, and domain skills
- Keep skills concise (1-3 words)

OUTPUT:
"""


def structured_extraction_prompt(text: str) -> str:
    return f"""
You are an expert resume parser.

TASK:
Extract structured data from this resume. Return ONLY valid JSON, no other text.

INPUT:
{text}

OUTPUT FORMAT (STRICT JSON):
{{
  "name": "Full Name",
  "email": "email or empty string",
  "phone": "phone number or empty string",
  "location": "city, state/country or empty string",
  "total_experience_years": 0,
  "experience": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "start": "Month Year or Year",
      "end": "Month Year or Year or Present",
      "duration_months": 0
    }}
  ],
  "education": [
    {{
      "degree": "Degree name",
      "institution": "University/College name",
      "year": "Year or empty string",
      "gpa": "GPA or empty string"
    }}
  ],
  "skills": ["skill1", "skill2"]
}}

RULES:
- Return ONLY the JSON object
- No explanations, no markdown, no code blocks
- Use empty string for missing fields
- Use 0 for missing numeric fields
- Keep skill names concise (1-3 words)
- duration_months: estimate from start/end dates

BEGIN OUTPUT:
"""


def parse_structured_output(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            pass

    return {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "total_experience_years": 0,
        "experience": [],
        "education": [],
        "skills": []
    }
