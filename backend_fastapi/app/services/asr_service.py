"""
ASR Service — Automatic Speech Recognition
=============================================
Handles audio file processing using Hugging Face Whisper.
"""
from transformers import pipeline
import os
os.environ["HF_HOME"] = "D:/huggingface_cache"
import soundfile as sf
import numpy as np


class ASRService:
    """Whisper-based Automatic Speech Recognition service."""

    def __init__(self, model_name: str = "openai/whisper-base"):
        self.model_name = model_name
        # TODO: Load Whisper model and processor from Hugging Face
        self.model = None
        self.processor = None

    def load_model(self):
        """Load the Whisper model into memory."""
        print(f"--- [ASR_SERVICE] Loading Whisper model: {self.model_name} ---")
        try:
            self.model = pipeline("automatic-speech-recognition", model=self.model_name)
            print("--- [ASR_SERVICE] Model loaded successfully. ---")
        except Exception as e:
            print(f"--- [ASR_SERVICE] Error loading model: {e} ---")
            raise e

    async def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text.

        Args:
            audio_path: Path to the audio file (.wav, .mp3, .webm)

        Returns:
            Transcribed text string
        """
        if self.model is None:
            self.load_model()
            
        print(f"--- [ASR_SERVICE] Transcribing: {audio_path} ---")
        try:
            # Load audio manually to bypass ffmpeg requirement
            audio_data, samplerate = sf.read(audio_path)
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
                
            result = self.model(audio_data)
            text = result.get("text", "").strip()
            print(f"--- [ASR_SERVICE] Transcription result: '{text}' ---")
            return text
        except Exception as e:
            print(f"--- [ASR_SERVICE] Transcription error: {e} ---")
            raise e
