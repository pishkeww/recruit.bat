from PyQt6.QtCore import QObject, pyqtSignal


class PipelineWorker(QObject):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    def __init__(self, pipeline, resume, job, keywords_override=None):
        super().__init__()
        self.pipeline = pipeline
        self.resume = resume
        self.job = job
        self.keywords_override = keywords_override

    def run(self):
        try:
            self.progress.emit("Running analysis...")

            result = self.pipeline.run(
                self.resume,
                self.job,
                self.keywords_override
            )

            self.finished.emit(result)

        except Exception as e:
            self.finished.emit({
                "score": 0,
                "keyword": 0,
                "semantic": 0,
                "recency": 0,
                "education": 0,
                "confidence": 0,
                "skills": {},
                "cover_letter": "",
                "suggestions": str(e),
                "job_keywords": []
            })