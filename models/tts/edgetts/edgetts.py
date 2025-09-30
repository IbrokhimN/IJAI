import asyncio
import edge_tts
import threading
import queue
import os
import uuid
import sys
from pathlib import Path

# === Настройки ===
VOICE = "ru-RU-DmitryNeural"   # голос (ru-RU-SvetlanaNeural, en-US-AriaNeural, ...)
PLAYER_CMD = "mpg123 -q"       # любой CLI-плеер (mpg123, ffplay -nodisp -autoexit ...)
TMP_DIR = Path("tts_tmp")      # папка для временных файлов
TMP_DIR.mkdir(exist_ok=True)

# Очередь для озвучки
speech_queue = queue.Queue()

async def speak(text: str):
    """Генерируем mp3 и проигрываем"""
    filename = TMP_DIR / f"tts_{uuid.uuid4().hex}.mp3"
    tts = edge_tts.Communicate(text, voice=VOICE)
    await tts.save(str(filename))
    os.system(f"{PLAYER_CMD} {filename}")
    try:
        filename.unlink()
    except FileNotFoundError:
        pass

def tts_worker():
    """Фоновый поток: берёт текст из очереди и озвучивает"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        text = speech_queue.get()
        if text is None:
            break
        loop.run_until_complete(speak(text))
        speech_queue.task_done()

# Запуск фонового потока
threading.Thread(target=tts_worker, daemon=True).start()

# === Пример генерации текста ===
# Здесь вместо модели просто читаем текст из stdin по кускам,
# но можно подключить llm.create_chat_completion(stream=True)
def main():
    print("🔊 Edge-TTS Demo (вводите текст, exit для выхода)")
    buffer = ""
    for line in sys.stdin:
        line = line.strip()
        if line.lower() in {"exit", "quit"}:
            speech_queue.put(None)
            break
        # эмуляция "стрима": выводим по словам
        for word in line.split():
            print(word, end=" ", flush=True)
            buffer += word + " "
            # когда есть завершение предложения — шлём в TTS
            if any(buffer.endswith(end + " ") for end in [". ", "? ", "! "]):
                speech_queue.put(buffer.strip())
                buffer = ""
        print()
        if buffer.strip():
            # остаток в конце строки
            speech_queue.put(buffer.strip())
            buffer = ""

if __name__ == "__main__":
    try:
        main()
    finally:
        speech_queue.put(None)

