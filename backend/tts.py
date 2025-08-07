from TTS.api import TTS
import sounddevice as sd
import asyncio

tts = TTS("tts_models/en/vctk/vits")


async def text_to_speech(text:str):

    speaker = tts.speakers[0]
    audio = tts.tts(text=text, speaker=speaker)

    sd.play(audio, samplerate=22050)


    sd.wait()
    
    return audio
