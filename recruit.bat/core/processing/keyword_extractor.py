import re
from collections import Counter

STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "your", "will",
    "each", "their", "them", "they", "been", "have", "were", "some", "more",
    "years", "experience", "work", "team", "role", "company", "clients",
    "to", "in", "of", "or", "on", "at", "is", "an", "be", "as", "by",
    "it", "no", "so", "if", "my", "do", "up", "we", "he", "me",
    "are", "was", "has", "had", "but", "not", "can", "may", "its",
    "who", "which", "than", "then", "also", "into", "over", "such",
    "any", "all", "our", "one", "two", "per", "via", "re",
    "key", "end", "soft", "set", "use", "used", "new", "good",
    "high", "able", "both", "well", "best", "else", "very",
    "strong", "looking", "requirements", "development", "building",
    "deploying", "frameworks", "senior", "remote", "must",
    "including", "etc", "between", "under", "about", "before",
    "after", "through", "during", "above", "below",
    "email", "com", "http", "https", "www", "org",
    "using", "based", "focus", "quality", "technical", "professional",
    "design", "engineer", "technologies", "tools", "specialization",
    "certifications", "achievements", " soft", "skills",
    "rated", "level", "type", "date", "posted", "apply",
    "job", "full", "time", "part", "contract", "intern", "internship",
    "bachelor", "master", "degree", "diploma", "university", "college",
    "gpa", "graduation", "summary", "objective", "references",
    "varma", "aditya", "kerala", "chennai", "bangalore", "mumbai",
    "delhi", "pune", "hyderabad", "india", "linkedin", "github",
    "kochi", "open", "hybrid", "phone", "email",
    "poc", "genai", "tech", "techsol", "innovations",
    "coursera", "deeplearning", "ai",
    "developed", "implemented", "designed", "built", "created",
    "collaborated", "optimized", "reduced", "achieved", "maintained",
    "aspiring", "foundation", "proven", "track", "record",
    "passionate", "first", "analytical", "player", "spirit",
    "advanced", "efficient", "scalable", "automated", "real",
    "time", "high", "resolution", "manual", "entry",
    "retrieval", "dimensional", "embeddings", "testing",
    "deep", "learning", "machine", "model",
    "national", "level", "hackathon", "smart", "city",
    "infrastructure", "winner", "continuous", "learner",
    "latest", "research", "papers", "presenting",
    "non", "technical", "stakeholders", "acted", "peer",
    "mentor", "students", "university", "club",
    "data", "engineers", "schemas", "text", "prompts",
    "spaces", "room", "users", "redesign", "allows",
    "catalogs", "furniture", "visual", "similarity",
    "surfaces", "wood", "glass", "defects", "detect",
    "accuracy", "cameras", "industrial", "handle",
    "pipeline", "surface", "infer", "speed",
    "quantization", "techniques", "interior",
    "inspection", "quality", "automated",
}

EMAIL_URL_PATTERN = re.compile(
    r'[\w\.\-\+]+@[\w\.\-]+|'
    r'linkedin\.com|github\.com|gmail\.com|'
    r'https?://|www\.'
)


def extract_keywords(text: str, top_n=30):
    raw_words = re.findall(r'\b[a-zA-Z0-9\+\#]{2,}\b', text)
    words_lower = [w.lower() for w in raw_words]
    counts = Counter(words_lower)
    scored_keywords = {}

    for original_word in raw_words:
        clean_word = original_word.lower()

        if clean_word in STOPWORDS:
            continue

        if not re.search('[a-zA-Z]', original_word):
            continue

        if clean_word in scored_keywords:
            continue

        count = counts[clean_word]
        score = min(count, 3)

        if original_word.isupper() and len(original_word) <= 5:
            score += 3

        if clean_word.endswith(("api", "ml", "ai", "py", "db")):
            score += 2

        if clean_word in (
            "python", "java", "javascript", "typescript", "golang", "rust",
            "django", "flask", "fastapi", "react", "angular", "vue",
            "docker", "kubernetes", "k8s", "aws", "gcp", "azure",
            "postgresql", "mysql", "mongodb", "redis",
            "tensorflow", "pytorch", "scikit", "pandas", "numpy",
            "git", "jenkins", "terraform", "ansible",
            "rest", "graphql", "grpc", "kafka", "rabbitmq",
            "linux", "bash", "sql", "nosql", "css", "html",
            "devops", "cicd", "ci/cd", "ml", "ai", "nlp", "cv",
            "llm", "rag", "opencv", "langchain", "llama",
            "spark", "hadoop", "airflow", "dbt",
        ):
            score += 4

        scored_keywords[clean_word] = score

    sorted_res = sorted(
        scored_keywords.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [k for k, _ in sorted_res[:top_n]]
