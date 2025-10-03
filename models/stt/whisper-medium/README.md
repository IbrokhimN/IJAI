# Whisper Live Transcription

This Python script allows you to record audio from a selected input device and transcribe it in real-time using OpenAI's Whisper model.  
It continuously listens in short intervals and converts your speech to text automatically.

**Key Features:**
- Lists all available audio input devices so you can pick the right one.
- Records audio in 5-second chunks from the selected device.
- Transcribes speech using Whisper (`medium` model by default).
- Automatically handles temporary audio files to keep your system clean.
- Simple setup with minimal dependencies (`whisper`, `sounddevice`, `numpy`, `soundfile`).

This is a lightweight, no-frills tool for real-time speech-to-text transcription.
