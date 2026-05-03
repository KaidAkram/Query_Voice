import os
import time
import torch
import sounddevice as sd
import soundfile as sf
from transformers import pipeline

# Set cache directory and suppress unnecessary HF hub checks
os.environ["HF_HOME"] = "D:/huggingface_cache"
# os.environ["TRANSFORMERS_OFFLINE"] = "1"  # Uncomment if you want to force offline

_asr_pipeline = None

def get_asr_pipeline():
    global _asr_pipeline
    if _asr_pipeline is not None:
        return _asr_pipeline
        
    print("[INFO] Initializing Whisper pipeline...")
    device = 0 if torch.cuda.is_available() else -1
    try:
        # Load high-accuracy model (requires ~1GB VRAM)
        _asr_pipeline = pipeline(
            "automatic-speech-recognition", 
            model="openai/whisper-small",
            device=device,
            torch_dtype=torch.float16 if device == 0 else torch.float32,
            generate_kwargs={
                "language": "en", 
                "task": "transcribe",
                "repetition_penalty": 1.2,
                "no_repeat_ngram_size": 3
            }
        )
        print(f"[SUCCESS] Model loaded on: {'GPU (CUDA)' if device == 0 else 'CPU'}")
    except Exception as e:
        print(f"[WARNING] GPU Initialization failed, falling back to CPU: {e}")
        _asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-small")
    return _asr_pipeline

def record_audio(filename="test_recording.wav", duration=5, fs=16000):
    print(f"[RECORD] Recording for {duration} seconds... Speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    print("[RECORD] Recording finished.")
    sf.write(filename, recording, fs)
    print(f"[FILE] Saved audio to {filename}")
    return filename

def test_whisper_transcription(audio_path):
    print("[ASR] Transcribing audio...")
    start_time = time.time()
    
    # Load audio data
    audio_data, samplerate = sf.read(audio_path)
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)
        
    # Perform inference
    asr_pipeline = get_asr_pipeline()
    result = asr_pipeline(audio_data)
    end_time = time.time()
    
    transcription = result.get("text", "").strip()
    
    print("\n" + "="*50)
    print("FINAL TRANSCRIPTION:")
    print(f"'{transcription}'")
    print("="*50)
    print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    print("--- LIVE VOICE TEST (WHISPER OPTIMIZED) ---")
    try:
        audio_file = record_audio(duration=7)
        test_whisper_transcription(audio_file)
    except Exception as e:
        print(f"\n[ERROR] Error during test: {e}")
        print("Please ensure you have a microphone connected and necessary libraries installed.")
