import whisper
import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile
import os

# Listing all input devices because apparently we can't just pick the right one automatically
print("Available input devices:")
devices = sd.query_devices()
input_devices = [i for i, d in enumerate(devices) if d['max_input_channels'] > 0]

for i in input_devices:
    print(f"{i}: {devices[i]['name']}")

# Asking user to do the hard work and pick a device
device_id = int(input("Enter device number: "))

# Getting default sample rate, because every mic apparently likes to be unique
info = sd.query_devices(device_id, 'input')
samplerate = int(info['default_samplerate'])

print(f"\nUsing device: {info['name']} with sample rate {samplerate} Hz")

# Load Whisper model once, because loading it every time would be stupidly slow
model = whisper.load_model("small")

duration = 5  # record 5 seconds at a time because why not

print("Program started. Listening... (Ctrl+C to exit, obviously)")

while True:
    try:
        # Record audio, yes, again, because we need input
        print("\nListening...")
        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype='float32',
            device=device_id
        )
        sd.wait()
        audio = np.squeeze(audio)

        # Writing to a temp WAV file because Whisper refuses to work with numpy arrays directly
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            sf.write(tmpfile.name, audio, samplerate)
            tmp_filename = tmpfile.name

        # Transcribing speech, magically turning sounds into text
        result = model.transcribe(tmp_filename, language="ru")  # auto-detect works too, if you're lazy
        print("You said:", result["text"].strip())

        # Clean up the temporary file, because we don't need more junk on disk
        os.remove(tmp_filename)

    except KeyboardInterrupt:
        print("\nExiting. Go talk to someone in person, maybe.")
        break
