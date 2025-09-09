import os
import subprocess
import ollama

class DeepSeekR1:
    def __init__(self):
        # Используем точное имя скачанной модели
        self.model_name = "deepseek-r1:8b"
        if not self._model_exists():
            print(f"Модель {self.model_name} не найдена. Запускаем installer.sh ...")
            self._run_installer()
            if not self._model_exists():
                raise RuntimeError(f"Не удалось скачать модель {self.model_name}.")

    def _model_exists(self) -> bool:
        try:
            models = ollama.list()
            # Проверяем, встречается ли имя модели в любом элементе кортежа
            return any(self.model_name in str(m) for m in models)
        except Exception as e:
            print(f"Ошибка при проверке модели: {e}")
            return False

    def _run_installer(self):
        try:
            # Делаем скрипт исполняемым
            os.chmod("./installer.sh", 0o755)
            subprocess.run(["./installer.sh"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при запуске installer.sh: {e}")

    def response(self, prompt: str) -> str:
        try:
            result = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return result['message']['content']
        except Exception as e:
            return f"Ошибка при генерации ответа: {e}"

