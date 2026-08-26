import requests
import time


class OllamaClient:
    def __init__(self, url="http://localhost:11434/api/generate", model="llama3"):
        self.url = url
        self.model = model

    def generate(self, prompt: str, retries=1) -> dict:
        for attempt in range(retries + 1):
            try:
                response = requests.post(
                    self.url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=300
                )

                if response.status_code != 200:
                    return {
                        "status": "error",
                        "message": f"Ollama {response.status_code}: {response.text}"
                    }

                data = response.json()

                if "response" not in data:
                    return {
                        "status": "error",
                        "message": f"Invalid response format: {data}"
                    }

                text = data["response"].strip()

                if len(text) > 5000:
                    text = text[:5000] + "\n\n[Truncated]"

                return {
                    "status": "success",
                    "data": text
                }

            except Exception as e:
                if attempt < retries:
                    time.sleep(1)
                    continue

                return {"status": "error", "message": str(e)}