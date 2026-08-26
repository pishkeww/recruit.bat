from core.pipeline import Pipeline
from core.llm.ollama_client import OllamaClient
from app.config import OLLAMA_URL, MODEL_NAME


class Container:
    def __init__(self):
        self.llm = OllamaClient(OLLAMA_URL, MODEL_NAME)
        self.pipeline = Pipeline(self.llm)


def build_container():
    return Container()