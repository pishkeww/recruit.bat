import os
import traceback
from PyQt6.QtCore import QObject, pyqtSignal
from core.processing.resume_parser import parse_resume_pdf


class BatchWorker(QObject):
    finished = pyqtSignal(list)
    progress = pyqtSignal(str)
    single_done = pyqtSignal(dict)

    def __init__(self, pipeline, pdf_paths, job_text, keywords_override=None):
        super().__init__()
        self.pipeline = pipeline
        self.pdf_paths = pdf_paths
        self.job_text = job_text
        self.keywords_override = keywords_override

    def run(self):
        results = []
        total = len(self.pdf_paths)

        for i, path in enumerate(self.pdf_paths):
            filename = os.path.basename(path)
            self.progress.emit(f"Processing {i + 1}/{total}: {filename}")

            try:
                resume_text = parse_resume_pdf(path)
                result = self.pipeline.run(
                    resume_text, self.job_text, self.keywords_override
                )
                result["filename"] = filename
                result["filepath"] = path
                results.append(result)
                self.single_done.emit(result)
            except Exception as e:
                error_result = {
                    "filename": filename,
                    "filepath": path,
                    "score": 0,
                    "keyword": 0,
                    "semantic": 0,
                    "recency": 0,
                    "education": 0,
                    "confidence": 0,
                    "skills": {},
                    "cover_letter": "",
                    "suggestions": f"Error: {str(e)}",
                    "job_keywords": [],
                    "structured": {}
                }
                results.append(error_result)
                self.single_done.emit(error_result)

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.progress.emit(f"Done. Processed {total} resumes.")
        self.finished.emit(results)
