import subprocess
from ollama import Ollama

class Llama3:
    def __init__(self):
        self.ollama = Ollama()
        self.model_name = "llama3:latest"
        if not self._model_exists():
            print(f"Модель {self.model_name} не найдена. Запускаем installer.sh ...")
            self._run_installer()
            if not self._model_exists():
                raise RuntimeError(f"Не удалось скачать модель {self.model_name}.")

    def _model_exists(self) -> bool:
        try:
            models = self.ollama.list()
            model_names = [m.name for m in models]
            return self.model_name in model_names
        except Exception:
            return False

    def _run_installer(self):
        try:
            subprocess.run(["./installer.sh"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при запуске installer.sh: {e}")

    def response(self, prompt: str) -> str:
        try:
            result = self.ollama.chat(model=self.model_name, prompt=prompt)
            return result.text if hasattr(result, "text") else str(result)
        except Exception as e:
            return f"Ошибка при генерации ответа: {e}"
