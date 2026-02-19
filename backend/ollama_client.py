import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "phi3"


class OllamaClient:

    def __init__(self, model=DEFAULT_MODEL):
        self.model = model

    def is_server_running(self):
        try:
            response = requests.get("http://localhost:11434")
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

        except Exception as e:
            return f"Ollama error: {str(e)}"
