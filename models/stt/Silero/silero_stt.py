import torch
import torchaudio
from pathlib import Path


class SileroSTT:
    def __init__(self, model_path: str = None, device: str = None):
        """
        Initialize Silero STT
        :param model_path: path to model.pt (if None — downloads from torch.hub)
        :param device: "cuda" or "cpu"
        """
        # Set device: GPU if available, otherwise CPU
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if model_path and Path(model_path).exists():
            # Load local model using torch.package
            self.model = torch.package.PackageImporter(model_path).load_pickle("asr", "model")
        else:
            # Download the pre-trained Silero STT model from torch.hub
            self.model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_stt',
                language='ru',
                device=self.device
            )

        # Move model to the selected device
        self.model.to(self.device)

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text
        :param audio_path: path to a .wav file (16kHz, mono)
        :return: recognized text as a string
        """
        # Load audio file
        waveform, sample_rate = torchaudio.load(audio_path)

        # Resample to 16kHz if needed
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)

        # Convert to mono if audio has multiple channels
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # Run inference
        with torch.no_grad():
            text = self.model(waveform.to(self.device))[0]

        return text


if __name__ == "__main__":
    # Example usage
    stt = SileroSTT()
    result = stt.transcribe("test.wav")
    print("Recognized text:", result)
