from fastapi import FastAPI,WebSocket,UploadFile,File,Form
from fastapi.middleware.cors import CORSMiddleware
import webrtcvad
import audioop
from collections import deque
from stt import speech_to_text
from rag import resume_rag_chain,resume_rag_embed
from tts import text_to_speech
from agent import interview_graph
from uuid import uuid4
from pprint import pprint
import os 
import tempfile
import warnings
import asyncio
from starlette.websockets import WebSocketState
warnings.filterwarnings("ignore", category=UserWarning, module="webrtcvad")



app =FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"], 
                    allow_credentials=True,
                    allow_methods=["*"],  
                    allow_headers=["*"], 
                   )

vad =  webrtcvad.Vad(2)
SAMPLE_RATE = 16000
FRAME_DURATION = 20
FRAME_SIZE = int(SAMPLE_RATE*FRAME_DURATION/1000)*2
SCILENCE_LIMIT = 80
CHUNK_SILENCE_LIMIT= 30

user_data = {

}




def is_speech(frame: bytes)->bool:
    rms = audioop.rms(frame, 2)  # 2 bytes/sample for 16-bit audio
    if rms < 500:  # below this, assume it's silence
        return False
    return vad.is_speech(frame,SAMPLE_RATE)

async def listen_for_speech(websocket:WebSocket):

    await asyncio.sleep(1.0)

    sclience_window = deque(maxlen=SCILENCE_LIMIT)
    buffer =b""
    speech_chunks=0
    silence_chunks = 0
    sclience_window.clear()
    
    print("Talk Now")
    
    speech_started =False
    first_speech = False
    
    while True:

        if websocket.client_state != WebSocketState.CONNECTED:
                print("WebSocket closed by client")
                break
        
        chunk = await websocket.receive_bytes()
    

        # print(f"Received {len(chunk)} bytes of audio.")
        
        
        
        for i in range(0,len(chunk),FRAME_SIZE):
            frame = chunk[i:i+FRAME_SIZE]
            
            if len(frame)<FRAME_SIZE:
                continue
            
            speech = is_speech(frame)
            
            sclience_window.append(speech)

            
            if speech:
                silence_chunks=0
                speech_chunks+=1
                if speech_chunks ==1:
                    print("Speech Started")
                    speech_started=True
                    first_speech =True
            
            if speech_started:
                buffer +=frame
            # print("speaking" if speech else "silence")
            
            if speech_chunks > 25 and not speech:
                silence_chunks +=1
            
            if silence_chunks > CHUNK_SILENCE_LIMIT and speech_chunks>25:
                
                yield buffer
                buffer =b""
                speech_chunks=0
                silence_chunks = 0
                sclience_window.clear()
                speech_started = False
            
            if len(sclience_window) == SCILENCE_LIMIT and not any(sclience_window) and first_speech:
                print("end of speech")
                yield buffer
                return
    


@app.websocket("/ws/{session_id}")
async def audio_ws(websocket:WebSocket,session_id:str):

    try:
    
        print("Trying to accept websocket...")
        
        await websocket.accept()
        print("websocket Connected")
        
        retriever = resume_rag_embed(
            user_data[session_id]["path"]
        )
        
        graph = interview_graph()

        state = {
            "messages": [],
            "turns": 0,
            "last_msg": "",
            "retriever": retriever,
            "job_role": user_data[session_id]["role"],
            "company": user_data[session_id]["company"], 
            "job_details": user_data[session_id]["details"]
        }

        stream = graph.stream(state) 
        
        buffer = b""
        
        
        while True:
            if websocket.client_state != WebSocketState.CONNECTED:
                print("WebSocket closed by client")
                break
            try:
                data = await websocket.receive_text()
                if data == "START":
                    print("Interview Starting...")
                    while True:
                        try:
                            step = next(stream)
                            current_node, current_state = list(step.items())[0]
                            state = current_state  
                            
                            if "messages" not in state or not state["messages"]:
                                print("\n⚠️ No message returned. Skipping.")
                                continue
                            
                            last_msg = state["messages"][-1]["text"]


                            
                            if current_node in {"HR", "TECH", "MANAGER","start","END"}:
                                print(f"\n👤 {current_node} says: {last_msg}")
                                audio_bytes = await text_to_speech(last_msg)
                                await websocket.send_text(current_node)
                                await websocket.send_bytes(audio_bytes)
                                
                            
                                
                                if state.get("next_interviewer") == "CLOSED":
                                    await websocket.send_text(state["report"])
                                    print("Interview Ended By the System")
                                    break
                                
                                if current_node in {"HR", "TECH", "MANAGER","start"}:
                                    
                                    await websocket.send_text("START_LISTENING")
                                    print("listening Started")
                                    
                                    transcription = ""
                                    
                                    async for chunk in listen_for_speech(websocket=websocket):
                                        partial_transcription = speech_to_text(chunk)
                                        
                                        transcription += partial_transcription
                                        print(f"→ {partial_transcription}")
                                        
                                    
                                    print(f"Me: {transcription}")
                                    

                                    await websocket.send_text("STOP_LISTENING")
                                    
                                        
                                    state["messages"].append({"role": "candidate", "text": transcription})
                                    state["last_msg"] = transcription
                                
                        except StopIteration:
                            print("Interview Completed")
                            if "report" in state:
                                await websocket.send_text(state["report"])
                            break
                                
                        except Exception as e:
                            print(e)
                            
                            break
                    
                    break
                elif data == "END":
                    print("Interview stopped by user")
                    break
            except Exception as e:
                print(f'Error recieveing Data {e}')
    
    except Exception as e:
        print(f'error connecting to websocket {e}')
    finally:
        try:
            await websocket.close()
            if os.path.exists(user_data[session_id]["path"]):
                os.remove(user_data[session_id]["path"])
                print("PDF removed")
        except :
            pass

@app.post("/upload_resume/")
async def upload_resume(file:UploadFile =File(...),role:str=Form(...),company:str=Form(),details:str=Form()):

    session_id = str(uuid4())

    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir,f"{session_id}.pdf")

    with open(file_path,"wb") as f:
        f.write(await file.read())

    user_data[session_id]={
        "role":role,
        "company":company,
        "details":details,
        "path":file_path
    }



    # pprint(user_data)

    return {"id":session_id}


    

    

        
        