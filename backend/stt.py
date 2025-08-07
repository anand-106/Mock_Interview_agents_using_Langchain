from faster_whisper import WhisperModel
import numpy as np

model = WhisperModel("base", device="cpu",compute_type="int8")

def speech_to_text(buffer:bytes) -> str:
    
    
    audio_array = np.frombuffer(buffer, dtype=np.int16).astype(np.float32) / 32768.0  # normalize to [-1, 1]
    
    
    
    segments, _ = model.transcribe(audio_array, language="en")
    text = "".join(segment.text for segment in segments)
    
    return text