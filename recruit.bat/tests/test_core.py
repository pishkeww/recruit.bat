import sys
import os
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestKeywordExtractor(unittest.TestCase):
    def test_extracts_tech_keywords(self):
        from core.processing.keyword_extractor import extract_keywords
        text = "Python Django Flask REST APIs Docker Kubernetes AWS Azure CI/CD"
        kw = extract_keywords(text, top_n=20)
        self.assertIn("python", kw)
        self.assertIn("django", kw)
        self.assertIn("flask", kw)
        self.assertIn("docker", kw)

    def test_filters_stopwords(self):
        from core.processing.keyword_extractor import extract_keywords
        text = "the and for with this that from your will each their"
        kw = extract_keywords(text, top_n=20)
        self.assertEqual(len(kw), 0)

    def test_respects_top_n(self):
        from core.processing.keyword_extractor import extract_keywords
        text = "Python Java JavaScript TypeScript Golang Rust C++ Ruby PHP Swift"
        kw = extract_keywords(text, top_n=5)
        self.assertLessEqual(len(kw), 5)

    def test_tech_terms_get_higher_scores(self):
        from core.processing.keyword_extractor import extract_keywords
        text = "python randomword1 randomword2 randomword3"
        kw = extract_keywords(text, top_n=10)
        self.assertEqual(kw[0], "python")


class TestTextCleaner(unittest.TestCase):
    def test_removes_email(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "Contact me at john@gmail.com for details"
        cleaned = clean_for_matching(text)
        self.assertNotIn("john@gmail.com", cleaned)

    def test_removes_phone(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "Call +91 98765 43210 for info"
        cleaned = clean_for_matching(text)
        self.assertNotIn("+91", cleaned)

    def test_removes_linkedin(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "LinkedIn: linkedin.com/in/johndoe"
        cleaned = clean_for_matching(text)
        self.assertNotIn("linkedin.com", cleaned)

    def test_removes_github(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "GitHub: github.com/johndoe"
        cleaned = clean_for_matching(text)
        self.assertNotIn("github.com", cleaned)

    def test_removes_headings(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "PROFESSIONAL SUMMARY\nPython developer with 5 years\nTECHNICAL SKILLS\nPython, Django"
        cleaned = clean_for_matching(text)
        self.assertNotIn("PROFESSIONAL SUMMARY", cleaned)
        self.assertNotIn("TECHNICAL SKILLS", cleaned)
        self.assertIn("Python developer", cleaned)
        self.assertIn("Python, Django", cleaned)

    def test_removes_mixed_case_headings(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "Professional Summary\nPython developer\nTechnical Skills\nDjango Flask"
        cleaned = clean_for_matching(text)
        self.assertNotIn("Professional Summary", cleaned)
        self.assertNotIn("Technical Skills", cleaned)

    def test_keeps_content(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "Built REST APIs using Django and Flask. Deployed on AWS."
        cleaned = clean_for_matching(text)
        self.assertIn("REST APIs", cleaned)
        self.assertIn("Django", cleaned)

    def test_removes_name_line(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "JOHN DOE\nEmail: john@gmail.com\nPython developer"
        cleaned = clean_for_matching(text)
        self.assertNotIn("JOHN DOE", cleaned)
        self.assertIn("Python developer", cleaned)

    def test_removes_digit_only_lines(self):
        from core.processing.text_cleaner import clean_for_matching
        text = "43210\nPython developer"
        cleaned = clean_for_matching(text)
        self.assertNotIn("43210", cleaned)


class TestScoring(unittest.TestCase):
    def test_keyword_score_perfect_match(self):
        from core.scoring.ats_scorer import keyword_score
        resume_kw = ["python", "django", "flask"]
        job_kw = ["python", "django", "flask"]
        score = keyword_score(resume_kw, job_kw)
        self.assertAlmostEqual(score, 1.0, places=1)

    def test_keyword_score_no_match(self):
        from core.scoring.ats_scorer import keyword_score
        resume_kw = ["java", "spring"]
        job_kw = ["python", "django"]
        score = keyword_score(resume_kw, job_kw)
        self.assertLess(score, 0.3)

    def test_keyword_score_empty_job(self):
        from core.scoring.ats_scorer import keyword_score
        score = keyword_score(["python"], [])
        self.assertEqual(score, 0.0)

    def test_compute_recency_recent(self):
        from core.scoring.ats_scorer import compute_recency
        from datetime import datetime
        year = datetime.now().year
        score = compute_recency(f"Worked at company in {year}")
        self.assertEqual(score, 1.0)

    def test_compute_recency_old(self):
        from core.scoring.ats_scorer import compute_recency
        score = compute_recency("Worked at company in 2015")
        self.assertEqual(score, 0.5)

    def test_compute_recency_no_year(self):
        from core.scoring.ats_scorer import compute_recency
        score = compute_recency("No year mentioned here")
        self.assertEqual(score, 0.6)


class TestEducationMatcher(unittest.TestCase):
    def test_no_requirements(self):
        from core.scoring.education_matcher import calculate_edu_score
        score = calculate_edu_score("B.Tech", "No degree required")
        self.assertEqual(score, 1.0)

    def test_meets_requirement(self):
        from core.scoring.education_matcher import calculate_edu_score
        score = calculate_edu_score("M.Tech in CS", "B.Tech required")
        self.assertGreaterEqual(score, 0.7)

    def test_below_requirement(self):
        from core.scoring.education_matcher import calculate_edu_score
        score = calculate_edu_score("Diploma", "B.Tech required")
        self.assertLess(score, 1.0)


class TestPrompts(unittest.TestCase):
    def test_cover_letter_prompt(self):
        from core.prompts import cover_letter_prompt
        prompt = cover_letter_prompt("resume text", "job text")
        self.assertIn("resume text", prompt)
        self.assertIn("job text", prompt)

    def test_suggestions_prompt(self):
        from core.prompts import suggestions_prompt
        prompt = suggestions_prompt("resume text", ["python", "django"])
        self.assertIn("resume text", prompt)
        self.assertIn("python", prompt)
        self.assertIn("django", prompt)

    def test_skill_extraction_prompt(self):
        from core.prompts import skill_extraction_prompt
        prompt = skill_extraction_prompt("resume text")
        self.assertIn("resume text", prompt)

    def test_structured_extraction_prompt(self):
        from core.prompts import structured_extraction_prompt
        prompt = structured_extraction_prompt("resume text")
        self.assertIn("resume text", prompt)
        self.assertIn("JSON", prompt)

    def test_parse_structured_output_valid_json(self):
        from core.prompts import parse_structured_output
        data = {
            "name": "John Doe",
            "email": "john@test.com",
            "phone": "",
            "location": "",
            "total_experience_years": 3,
            "experience": [],
            "education": [],
            "skills": ["python"]
        }
        result = parse_structured_output(json.dumps(data))
        self.assertEqual(result["name"], "John Doe")
        self.assertEqual(result["skills"], ["python"])

    def test_parse_structured_output_with_markdown(self):
        from core.prompts import parse_structured_output
        raw = '```json\n{"name": "Jane", "skills": ["java"]}\n```'
        result = parse_structured_output(raw)
        self.assertEqual(result["name"], "Jane")

    def test_parse_structured_output_invalid(self):
        from core.prompts import parse_structured_output
        result = parse_structured_output("not json at all")
        self.assertEqual(result["name"], "")
        self.assertEqual(result["skills"], [])


class TestExport(unittest.TestCase):
    def test_export_csv(self):
        from core.export import export_csv
        results = [
            {
                "filename": "resume1.pdf",
                "score": 85.5,
                "keyword": 80.0,
                "semantic": 75.0,
                "recency": 90.0,
                "education": 100.0,
                "structured": {
                    "name": "John",
                    "email": "j@test.com",
                    "phone": "123",
                    "location": "NYC",
                    "total_experience_years": 5,
                    "experience": [],
                    "education": [{"degree": "BS", "institution": "MIT", "year": "2020", "gpa": "3.8"}],
                    "skills": ["python", "django"]
                },
                "job_keywords": ["python"]
            }
        ]
        path = os.path.join(os.path.dirname(__file__), "test_output.csv")
        export_csv(results, path)
        self.assertTrue(os.path.exists(path))
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("John", content)
        self.assertIn("python", content)
        os.remove(path)

    def test_export_json(self):
        from core.export import export_json
        results = [
            {
                "filename": "resume1.pdf",
                "score": 85.5,
                "keyword": 80.0,
                "semantic": 75.0,
                "recency": 90.0,
                "education": 100.0,
                "structured": {"name": "John", "skills": ["python"]},
                "job_keywords": ["python"]
            }
        ]
        path = os.path.join(os.path.dirname(__file__), "test_output.json")
        export_json(results, path)
        self.assertTrue(os.path.exists(path))
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data[0]["rank"], 1)
        self.assertEqual(data[0]["structured_data"]["name"], "John")
        os.remove(path)


class TestResumeParser(unittest.TestCase):
    def test_parse_sample_cv(self):
        from core.processing.resume_parser import parse_resume_pdf
        sample = os.path.join(
            os.path.dirname(__file__), "..", "sample cv.pdf"
        )
        if os.path.exists(sample):
            text = parse_resume_pdf(sample)
            self.assertGreater(len(text), 100)
            self.assertIn("Python", text)


if __name__ == "__main__":
    unittest.main()
