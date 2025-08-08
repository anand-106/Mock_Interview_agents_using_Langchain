from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import asyncio
import io

tts = TTS("tts_models/en/vctk/vits")


async def text_to_speech(text:str):

    speaker = tts.speakers[0]
    audio = tts.tts(text=text, speaker=speaker)

    with io.BytesIO() as buffer:
        sf.write(buffer,audio,22050,format="WAV")
        return buffer.getvalue()
    
