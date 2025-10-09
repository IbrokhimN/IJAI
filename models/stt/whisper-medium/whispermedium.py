import whisper
import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile
import os
import time
import threading
import sys
import json


class VoiceListener:
    PRIORITY_FILE = "mic_priority.json"

    def __init__(
        self,
        model_size: str = "small",
        silence_threshold: float = 0.01,
        silence_duration: float = 3.0,
        chunk_duration: float = 0.25,
        language: str = "ru",
    ):
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.chunk_duration = chunk_duration
        self.language = language
        self.model = whisper.load_model(model_size)
        self.device_id = self._select_device()
        info = sd.query_devices(self.device_id, "input")
        self.samplerate = int(info["default_samplerate"])
        self._stop_indicator = False
        self._indicator_thread = None

    def _select_device(self):
        """
        Загружает приоритеты микрофонов, пытается выбрать по ним.
        Если не найдено — запрашивает у пользователя и сохраняет.
        """
        priorities = self._load_priorities()
        available_devices = sd.query_devices()

        for device_name in priorities:
            idx = self._find_device_index(device_name, available_devices)
            if idx is not None:
                print(f"🎙 Использую сохранённое устройство: {device_name}")
                return idx

        new_idx, new_name = self._ask_device(available_devices)
        print(f"✅ Устройство '{new_name}' добавлено в приоритеты.\n")
        priorities.append(new_name)
        self._save_priorities(priorities)
        return new_idx

    def _find_device_index(self, name, devices):
        """Ищет устройство по имени (частичное совпадение)"""
        for i, d in enumerate(devices):
            if d["max_input_channels"] > 0 and name.lower() in d["name"].lower():
                return i
        return None

    def _ask_device(self, devices):
        """Просит пользователя выбрать устройство"""
        input_devices = [i for i, d in enumerate(devices) if d["max_input_channels"] > 0]
        print("\n🎤 Доступные устройства ввода:\n")
        for i in input_devices:
            print(f"{i}: {devices[i]['name']}")
        while True:
            try:
                choice = int(input("\n👉 Введи номер устройства: "))
                if choice in input_devices:
                    return choice, devices[choice]["name"]
            except ValueError:
                pass
            print("⚠️ Неверный ввод, попробуй снова.")

    def _load_priorities(self):
        """Загружает список приоритетов из файла"""
        if os.path.exists(self.PRIORITY_FILE):
            try:
                with open(self.PRIORITY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_priorities(self, data):
        """Сохраняет приоритеты в файл"""
        with open(self.PRIORITY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _record_until_silence(self):
        recorded = []
        silent_time = 0.0
        speaking = False
        adaptive_threshold = self.silence_threshold

        self._stop_indicator = False
        self._indicator_thread = threading.Thread(target=self._listening_indicator)
        self._indicator_thread.start()

        while True:
            chunk = sd.rec(
                int(self.chunk_duration * self.samplerate),
                samplerate=self.samplerate,
                channels=1,
                dtype="float32",
                device=self.device_id,
            )
            sd.wait()
            chunk = np.squeeze(chunk)
            recorded.append(chunk)

            rms = np.sqrt(np.mean(chunk**2))
            adaptive_threshold = 0.9 * adaptive_threshold + 0.1 * (rms * 1.5)

            if rms > adaptive_threshold:
                speaking = True
                silent_time = 0.0
            elif speaking:
                silent_time += self.chunk_duration

            if speaking and silent_time >= self.silence_duration:
                break

        self._stop_indicator = True
        self._indicator_thread.join()
        sys.stdout.write("\r" + " " * 10 + "\r")
        sys.stdout.flush()

        return np.concatenate(recorded)

    def _listening_indicator(self):
        while not self._stop_indicator:
            for symbol in [".  ", ".. ", "..."]:
                if self._stop_indicator:
                    break
                sys.stdout.write("\r🎧 Слушаю" + symbol)
                sys.stdout.flush()
                time.sleep(0.4)

    def listen_once(self) -> str:
        audio = self._record_until_silence()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            sf.write(tmpfile.name, audio, self.samplerate)
            tmp_filename = tmpfile.name

        try:
            result = self.model.transcribe(tmp_filename, language=self.language)
            text = result["text"].strip()
        finally:
            os.remove(tmp_filename)

        return text


if __name__ == "__main__":
    listener = VoiceListener()
    print("\nНажми Ctrl+C чтобы выйти\n")

    while True:
        try:
            text = listener.listen_once()
            if text:
                print(f"\r📝 {text}")
            else:
                print("\r(тишина)")
        except KeyboardInterrupt:
            print("\nBye")
            break

