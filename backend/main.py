from fastapi import FastAPI,WebSocket
import webrtcvad
import audioop
from collections import deque
from stt import speech_to_text
from rag import resume_rag_chain,resume_rag_embed
from agent import interview_graph
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="webrtcvad")



app =FastAPI()

vad =  webrtcvad.Vad(2)
SAMPLE_RATE = 16000
FRAME_DURATION = 20
FRAME_SIZE = int(SAMPLE_RATE*FRAME_DURATION/1000)*2
SCILENCE_LIMIT = 100




def is_speech(frame: bytes)->bool:
    rms = audioop.rms(frame, 2)  # 2 bytes/sample for 16-bit audio
    if rms < 300:  # below this, assume it's silence
        return False
    return vad.is_speech(frame,SAMPLE_RATE)

async def listen_for_speech(websocket:WebSocket):
    sclience_window = deque(maxlen=SCILENCE_LIMIT)
    buffer =b""
    speech_chunks=0
    sclience_window.clear()
    
    print("Talk Now")
    
    while True:
        chunk = await websocket.receive_bytes()
    

        # print(f"Received {len(chunk)} bytes of audio.")
        
        buffer += chunk
        
        for i in range(0,len(chunk),FRAME_SIZE):
            frame = chunk[i:i+FRAME_SIZE]
            
            if len(frame)<FRAME_SIZE:
                continue
            
            speech = is_speech(frame)
            
            sclience_window.append(speech)
            
            if speech:
                speech_chunks+=1
                if speech_chunks ==1:
                    print("Speech Started")
            
            # print("speaking" if speech else "silence")
            
            if len(sclience_window) == SCILENCE_LIMIT and not any(sclience_window) and speech_chunks>25:
                print("end of speech")
                return buffer
    


@app.websocket("/ws/audio")
async def audio_ws(websocket:WebSocket):
    
    print("Trying to accept websocket...")
    
    await websocket.accept()
    print("websocket Connected")
    
    retriever = resume_rag_embed(
        r"C:\Users\gamin\Documents\projects\Mock_Interview_agents_using_Langchain\backend\assets\Anand-S-Resume.pdf"
    )
    
    graph = interview_graph()

    state = {
        "messages": [],
        "turns": 0,
        "last_msg": "",
        "retriever": retriever,
    }

    stream = graph.stream(state) 
    
    buffer = b""
    
    
    
    
    # step = next(stream)
    # current_node, current_state = list(step.items())[0]
    # state = current_state
    
    # if "messages" not in state or not state["messages"]:
    #     print("\n⚠️ No message returned. Skipping.")
    

    # last_msg = state["messages"][-1]["text"]
    # if current_node in {"HR", "TECH", "MANAGER","start","END"}:
    #     print(f"\n👤 {current_node} says: {last_msg}")
    
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
                
                if state.get("next_interviewer") == "CLOSED":
                    break
                
                if current_node != "END":
                    buffer = await listen_for_speech(websocket=websocket)
                        
                    print("processing Audio")
                    
                    transcription = speech_to_text(buffer)
                    
                    print(f"Me: {transcription}")
                    
                    

                    # Only take user input after interviewer nodes
                    
                        
                    state["messages"].append({"role": "candidate", "text": transcription})
                    state["last_msg"] = transcription
                   
        except Exception as e:
            print(e)
            break
    
    await websocket.close()
        
        