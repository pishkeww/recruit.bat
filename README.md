# recruit.bat

A desktop resume screening tool that scores resumes against job descriptions using ATS-style scoring, semantic similarity, and optional LLM-powered analysis.

## Features

### Scoring (Works Offline, No LLM Required)

- **Keyword matching** — extracts technical keywords from the resume and job description, then computes overlap with weighted scoring
- **Semantic similarity** — uses Sentence Transformers (`all-MiniLM-L6-v2`) to compute cosine similarity between the resume and job description
- **Recency scoring** — detects years in the resume and scores experience based on how recent it is
- **Education matching** — compares the candidate's degree level against job requirements (B.Tech, M.Tech, PhD, etc.)
- **Text cleaning** — strips emails, phone numbers, LinkedIn/GitHub URLs, section headings, and names before matching to reduce false positives

### LLM-Powered Features (Requires Ollama)

- **Cover letter generation** — generates a tailored cover letter aligned with the job description
- **Resume improvement suggestions** — identifies missing keywords, suggests rewritten bullet points, and provides actionable improvements
- **Skills extraction** — extracts technical skills from the resume
- **Structured data extraction** — extracts name, email, phone number, experience timeline, and education details

### Batch Processing

- Upload a folder of PDFs and score all resumes against a single job description
- Results are displayed in a ranked table with color-coded scores (green ≥ 75, orange ≥ 50, red < 50)
- Double-click any row to view extracted structured data
- Export results to CSV or JSON

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) *(optional, required for cover letter generation, suggestions, skills extraction, and structured data extraction)*

Recommended Ollama model:

```bash
llama3.1:8b
```

## Installation

```bash
git clone https://github.com/pishkeww/recruit.bat.git
cd recruit.bat

# Create virtual environment
python -m venv .venv

# Activate it

# Windows
.venv\Scripts\activate

# Linux/macOS
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: pull the Ollama model
ollama pull llama3.1:8b
```

## Usage

```bash
python main.py
```

### Single Resume Mode

1. Click **Upload Resume (PDF)** to load a resume
2. Paste the job description in the **Job Description** field
3. Click **Analyze** to score the resume
4. Toggle keyword chips on or off to refine scoring
5. Use **Clear Resume**, **Clear JD**, or **Clear All** to reset

### Batch Mode

1. Switch to **Batch (Folder)** mode
2. Paste the job description
3. Click **Select Folder of PDFs** to choose a folder containing resumes
4. Click **Analyze All** to process all resumes
5. Results appear in a ranked table sorted by score
6. Double-click a row to view detailed structured data
7. Click **Export CSV** or **Export JSON** to save results

### Without Ollama

The application works without Ollama. You still get:

- Full ATS scoring (keyword, semantic, recency, and education)
- Keyword extraction and matching
- A red **"Ollama: Not connected"** indicator

The following features are unavailable:

- Cover letter generation
- Resume improvement suggestions
- Skills extraction
- Structured data extraction (name, experience, and education)

## Project Structure

```text
recruit.bat/
├── main.py                     # Entry point
├── requirements.txt
├── app/
│   ├── config.py               # Ollama URL and model name
│   └── dependencies.py         # Dependency injection container
├── core/
│   ├── pipeline.py             # Main scoring + LLM pipeline
│   ├── pipeline_worker.py      # QThread worker for single resume processing
│   ├── batch_worker.py         # QThread worker for batch processing
│   ├── prompts.py              # LLM prompt templates
│   ├── export.py               # CSV/JSON export
│   ├── llm/
│   │   └── ollama_client.py    # Ollama HTTP client
│   ├── processing/
│   │   ├── resume_parser.py    # PDF text extraction using PyMuPDF
│   │   ├── keyword_extractor.py # Keyword extraction with tech-term boosting
│   │   ├── text_cleaner.py     # Removes emails, URLs, and headings before matching
│   │   └── embedder.py         # Sentence Transformer embeddings
│   └── scoring/
│       ├── ats_scorer.py       # ATS score computation
│       ├── education_matcher.py # Degree-level matching
│       └── skill_matcher.py    # Skill presence detection
├── services/
│   └── pdf/
│       └── generator.py        # PDF generation for cover letter export
├── ui/
│   ├── main_window.py          # Main GUI window
│   └── components/
│       └── file_upload.py      # Reusable file upload component
└── tests/
    └── test_core.py            # Core unit tests
```

## Running Tests

```bash
python -m pytest tests/test_core.py -v
```

The project currently includes **32 unit tests** covering core processing and scoring functionality.

## How Scoring Works

The final ATS score is a weighted combination of four components:

| Component | Weight | Method |
|---|---:|---|
| Keyword match | 40% | Set overlap between resume and job keywords, with a saturation curve |
| Semantic similarity | 25% | Cosine similarity using Sentence Transformers |
| Recency | 20% | Year-based decay from the most recent date found in the resume |
| Education | 15% | Degree hierarchy comparison (PhD > Master's > Bachelor's > Diploma) |

Keywords are extracted using a custom extractor that boosts technical terms such as Python, Docker, and AWS while filtering stopwords, names, emails, and section headings.

## License

This project is licensed under the MIT License.
