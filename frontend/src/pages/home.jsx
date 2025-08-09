import { useCallback, useEffect, useRef, useState } from 'react';
import { MdCall } from "react-icons/md";
import { MdCallEnd } from "react-icons/md";
import { FaMicrophone } from "react-icons/fa";
import { useLocation, useNavigate } from 'react-router-dom';

export function HomePage(){
    
    const mediaRecorderRef = useRef(null);
    const wsRef = useRef(null);
    const [isMicON,setIsMicON] = useState(false)
    const [HRSpeaking,setHrSpeaking] = useState(false)
    const [TechSpeaking,setTechSpeaking] = useState(false)
    const [ManagerSpeaking,setManagerSpeaking] = useState(false)
    const isConnectedRef = useRef(false)
    const navigate  =  useNavigate()
    const location = useLocation()


    const startStreamingAudio = useCallback(async () => {
        setIsMicON(true)
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new AudioContext({ sampleRate: 16000 });
        const source = audioContext.createMediaStreamSource(stream);
        
        await audioContext.audioWorklet.addModule(
            URL.createObjectURL(new Blob([`
                class AudioProcessor extends AudioWorkletProcessor {
                    constructor() {
                        super();
                        this.buffer = new Float32Array();
                        this.bufferSize = 320; // 20ms at 16kHz = 320 samples
                    }
                    
                    process(inputs, outputs, parameters) {
                        const input = inputs[0];
                        if (input.length > 0) {
                            const inputData = input[0];
                            
                            // Accumulate data until we have 320 samples (20ms)
                            const newBuffer = new Float32Array(this.buffer.length + inputData.length);
                            newBuffer.set(this.buffer);
                            newBuffer.set(inputData, this.buffer.length);
                            this.buffer = newBuffer;
                            
                            // Send 320-sample chunks (640 bytes when converted to int16)
                            while (this.buffer.length >= this.bufferSize) {
                                const chunk = this.buffer.slice(0, this.bufferSize);
                                this.buffer = this.buffer.slice(this.bufferSize);
                                
                                const pcm = new Int16Array(chunk.length);
                                for (let i = 0; i < chunk.length; i++) {
                                    const s = Math.max(-1, Math.min(1, chunk[i]));
                                    pcm[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                                }
                                
                                this.port.postMessage(pcm.buffer);
                            }
                        }
                        return true;
                    }
                }
                registerProcessor('audio-processor', AudioProcessor);
            `], { type: 'application/javascript' }))
        );

        const processor = new AudioWorkletNode(audioContext, 'audio-processor');
        source.connect(processor);
        
        processor.port.onmessage = (event) => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                console.log(`Sending ${event.data.byteLength} bytes`);
                wsRef.current.send(event.data);
            }
        };

        mediaRecorderRef.current = { audioContext, source, processor,stream };
    },[]);

    const stopStreamingAudio = useCallback(() => {
        const recorder = mediaRecorderRef.current;
        if (recorder) {
            recorder.stream?.getTracks().forEach(track => track.stop());
            recorder.processor?.disconnect();
            recorder.source?.disconnect();
            recorder.audioContext?.close();
            setIsMicON(false)
        }
        mediaRecorderRef.current = null;
    },[]);

    useEffect(()=>{

        if(isConnectedRef.current){
            console.log("Websocket Already Connected")
            return
        }

        let ws = null
        const session_id = location.state?.id
         ws = new WebSocket(`ws://localhost:8000/ws/${session_id}`)
        wsRef.current = ws; 
        isConnectedRef.current = true

        ws.onopen = ()=>{
            console.log("WEBSOCKET CONNECTED")
        }

        ws.onmessage = (event)=>{
            if(typeof event.data == "string") {
                if(event.data === "STOP_LISTENING"){
                    console.log("Stopped Audio Listening")
                    stopStreamingAudio();
                }
                else if(event.data == "HR" || event.data == "start"){
                    setHrSpeaking(true)
                }
                else if(event.data == "TECH"){
                    setTechSpeaking(true)
                }
                else if(event.data == "MANAGER"){
                    setManagerSpeaking(true)
                }
                else if(event.data == "END"){
                    console.log("end of interview")
                }
                else if(event.data == "start")
                {

                }
                else if(event.data == "START_LISTENING")
                    {
    
                    }
                else{
                    stopStreamingAudio()

                    navigate("/report",{state:{report:event.data}})
                }
            }
            else if(event.data instanceof Blob){
                const blob = new Blob([event.data], {type:"audio/wav"})
                const url = URL.createObjectURL(blob)
                const audio = new Audio(url)

                
                audio.onerror = (error) => {
                    console.error("Audio playback failed:", error);
                   
                    setTimeout(startStreamingAudio, 1000);
                };

                audio.onended = () => {
                    console.log("Audio finished, starting to listen...");
                    setHrSpeaking(false)
                    setManagerSpeaking(false)
                    setTechSpeaking(false)
                    startStreamingAudio();
                };

                audio.play().catch(error => {
                    console.error("Play failed:", error);
                    setTimeout(startStreamingAudio, 1000);
                });
            }
        }

        ws.onerror = (err) => console.error('WebSocket error:', err);
        ws.onclose = () => console.log('WebSocket closed');

        
        const handleUnload = () => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.close(1000, 'Page refresh');
            }
        };
        
        window.addEventListener('beforeunload', handleUnload);

        return () => {
            console.log("Cleaning up WebSocket connection...");
            stopStreamingAudio();
            
            if (ws) {
                
                ws.onopen = null;
                ws.onmessage = null;
                ws.onerror = null;
                ws.onclose = null;
                
                if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
                    ws.close(1000, 'Component unmounting');
                }
            }
            wsRef.current.close()
            wsRef.current = null;
            isConnectedRef.current = false
            
            window.removeEventListener('beforeunload', handleUnload);
        };
    },[])

    

    const startInterview = useCallback(()=>{
        
        const ws =wsRef.current
        if(ws?.readyState === WebSocket.OPEN){
            ws.send("START")
        }
        

    },[])

    const endInterview = useCallback(()=>{
        const ws =wsRef.current
        if(ws?.readyState === WebSocket.OPEN){
            ws.send("END")
        }
    },[])


    return <div className="flex flex-col gap-2  items-center h-screen bg-[#030617] text-white px-4">
        <Header />
        <div className="w-full h-4/5 border border-white/50 rounded-2xl  flex justify-evenly items-center ">
        <AgentAvatar name={"HR Manager"}  isSpeaking={HRSpeaking}/>
        <AgentAvatar name={"Tech Lead"} isSpeaking={TechSpeaking} />
        <AgentAvatar name={"Hiring Manager"} isSpeaking={ManagerSpeaking} />
        </div>
        <div className='flex justify-center items-center gap-5 mt-2' >

        <div onClick={startInterview} className="cursor-pointer h-10 w-20 rounded-3xl bg-green-500 flex justify-center items-center" >
            <MdCall color='white' size={30} className='h-full' />
        </div>
        <div  className={`cursor-pointer h-10 w-10 rounded-full bg-white/20 flex justify-center items-center ${isMicON?"border-2 border-green-400":""}`} >
            <FaMicrophone color='white' size={12} className='h-full' />
        </div>
        <div  className="cursor-pointer h-10 w-20 rounded-3xl bg-red-500 flex justify-center items-center" >
            <MdCallEnd color='white' size={30} className='h-full' />
        </div>
        </div>
    </div>
}

function Header(){
    return <div className="flex w-full items-center pt-4 pl-2 mb-4" >

    <h1 className='font-bold text-2xl'>Mockcruiter</h1>
    </div>
}

function AgentAvatar({name,isSpeaking}){
return <div className={`bg-white/10 rounded-xl h-[300px] w-[300px] flex justify-center items-center ${isSpeaking?"border-2 border-green-400":""}`}>
<h1 className='font-semibold text-lg'>{name}</h1>
</div>
}