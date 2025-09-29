from llama_cpp import Llama
import asyncio
import edge_tts
import threading
import queue
import os
import uuid

# путь к модели
model_path = "Yi-1.5-6B-Chat-Q4_K_M.gguf"

# загружаем модель
llm = Llama(
    model_path=model_path,
    n_ctx=4096,
    n_threads=8,
    verbose=False
)

# очередь для речи
speech_queue = queue.Queue()

async def speak(text):
    """Озвучка текста через edge-tts"""
    filename = f"tts_{uuid.uuid4().hex}.mp3"
    tts = edge_tts.Communicate(text, voice="ru-RU-DmitryNeural")
    await tts.save(filename)
    os.system(f"mpg123 -q {filename}")  # проигрываем
    os.remove(filename)  # удаляем после воспроизведения

def tts_worker():
    """Фоновый поток: берёт текст из очереди и озвучивает"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        text = speech_queue.get()
        if text is None:  # сигнал выхода
            break
        loop.run_until_complete(speak(text))
        speech_queue.task_done()

# запускаем поток TTS
threading.Thread(target=tts_worker, daemon=True).start()

print("🤖 Yi-1.5 Chat (введи 'exit' чтобы выйти)\n")
messages = [{"role": "system", "content": "You are a helpful assistant."}]

while True:
    user_input = input("👤 You: ")
    if user_input.lower() in {"exit", "quit"}:
        speech_queue.put(None)  # останавливаем TTS поток
        break

    messages.append({"role": "user", "content": user_input})
    print("🤖 Bot: ", end="", flush=True)

    # стримим ответ
    stream = llm.create_chat_completion(
        messages=messages,
        max_tokens=200,
        temperature=0.7,
        stream=True
    )

    reply = ""
    buffer = ""
    for chunk in stream:
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            text = delta["content"]
            reply += text
            buffer += text
            print(text, end="", flush=True)

            # отправляем куски в озвучку по предложениям
            if any(end in buffer for end in [".", "?", "!"]):
                speech_queue.put(buffer.strip())
                buffer = ""

    # остаток дочитать
    if buffer.strip():
        speech_queue.put(buffer.strip())

    print("\n")
    messages.append({"role": "assistant", "content": reply})

