from fastapi import FastAPI,WebSocket
import webrtcvad
import audioop
from collections import deque
from stt import speech_to_text
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="webrtcvad")



app =FastAPI()

vad =  webrtcvad.Vad(2)
SAMPLE_RATE = 16000
FRAME_DURATION = 20
FRAME_SIZE = int(SAMPLE_RATE*FRAME_DURATION/1000)*2
SCILENCE_LIMIT = 50




def is_speech(frame: bytes)->bool:
    rms = audioop.rms(frame, 2)  # 2 bytes/sample for 16-bit audio
    if rms < 300:  # below this, assume it's silence
        return False
    return vad.is_speech(frame,SAMPLE_RATE)


@app.websocket("/ws/audio")
async def audio_ws(websocket:WebSocket):
    
    await websocket.accept()
    print("websocket Connected")
    
    buffer = b""
    sclience_window = deque(maxlen=SCILENCE_LIMIT)
    
    speech_chunks = 0
    
    while True:
        try:
            chunk = await websocket.receive_bytes()
            

            print(f"Received {len(chunk)} bytes of audio.")
            
            buffer += chunk
            
            for i in range(0,len(chunk),FRAME_SIZE):
                frame = chunk[i:i+FRAME_SIZE]
                
                if len(frame)<FRAME_SIZE:
                    continue
                
                speech = is_speech(frame)
                
                sclience_window.append(speech)
                
                if speech:
                    speech_chunks+=1
                
                print("speaking" if speech else "silence")
                
                if len(sclience_window) == SCILENCE_LIMIT and not any(sclience_window) and speech_chunks>10:
                    print("end of speech")
                    print("processing Audio")
                    
                    transcription = speech_to_text(buffer)
                    
                    print(transcription)
                    
                    buffer =b""
                    sclience_window.clear()
                    
                    return
                    
                    
        
        except Exception as e:
            print(e)
            break
    
    await websocket.close()
        
        