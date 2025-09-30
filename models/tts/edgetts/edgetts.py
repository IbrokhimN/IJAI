import asyncio
import threading
import queue
import os
import uuid
from pathlib import Path
import edge_tts

# Default voice for Russian speech. Change if you like suffering with accents.
VOICE = "ru-RU-DmitryNeural"

# Simple ffmpeg player command. We don't want GUI crap, just sound.
PLAYER_CMD = "ffplay -nodisp -autoexit -loglevel quiet"

# Temp directory for mp3 chunks. We nuke files after playback anyway.
TMP_DIR = Path(__file__).parent / "tts_tmp"
TMP_DIR.mkdir(exist_ok=True)

# Queue of text chunks waiting for TTS.
speech_queue = queue.Queue()

async def speak(text: str):
    """
    Synthesize and play a single text chunk.
    Generates an mp3, plays it, and removes it immediately after.
    """
    filename = TMP_DIR / f"tts_{uuid.uuid4().hex}.mp3"
    tts = edge_tts.Communicate(text, voice=VOICE)
    await tts.save(str(filename))
    os.system(f"{PLAYER_CMD} {filename.resolve()}")
    # Clean up like an adult. Ignore if already gone.
    try:
        filename.unlink()
    except FileNotFoundError:
        pass

def tts_worker():
    """
    Background thread:
    - Pull text from the queue
    - Call TTS coroutine inside its own event loop
    - Stop when None is received
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        text = speech_queue.get()
        if text is None:  # Shutdown signal
            break
        loop.run_until_complete(speak(text))
        speech_queue.task_done()

def start_tts():
    """
    Spin up the TTS worker in a daemon thread.
    Fire and forget—this process dies with the main thread anyway.
    """
    threading.Thread(target=tts_worker, daemon=True).start()
