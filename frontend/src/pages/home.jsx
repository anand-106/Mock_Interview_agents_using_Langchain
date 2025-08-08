import { useRef } from 'react';

export function HomePage(){
    const mediaRecorderRef = useRef(null);
    const wsRef = useRef(null);

    const startInterview = ()=>{
        const ws = new WebSocket('ws://localhost:8000/ws/audio')
        wsRef.current = ws;

        ws.onopen = ()=>{
            console.log("WEBSOCKET CONNECTED")
        }

        ws.onmessage = (event)=>{
            if(typeof event.data == "string") {
                if(event.data === "STOP_LISTENING"){
                    console.log("Stopped Audio Listening")
                    stopStreamingAudio();
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
                    startStreamingAudio();
                };

                audio.play().catch(error => {
                    console.error("Play failed:", error);
                    setTimeout(startStreamingAudio, 1000);
                });
            }
        }


        ws.onclose = ()=>{
            console.log("Web Socket Connected")
            stopStreamingAudio();
        }

        const startStreamingAudio = async () => {
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

            mediaRecorderRef.current = { audioContext, source, processor };
        };
        
        const stopStreamingAudio = () => {
            const recorder = mediaRecorderRef.current;
            if (recorder) {
                recorder.processor?.disconnect();
                recorder.source?.disconnect();
                recorder.audioContext?.close();
            }
        };

        ws.onerror = (err) => console.error('WebSocket error:', err);
        ws.onclose = () => console.log('WebSocket closed');
    }


    return <div className="flex flex-col gap-2 justify-center items-center h-screen">
        <div className="" >

        <h1>Interview AI</h1>
        </div>
        <div className="w-full h-4/5 border-2 rounded-2xl ">

        </div>
        <div>
            <button onClick={startInterview} className="cursor-pointer h-10 w-28 rounded-xl bg-black text-white" >Start Interview</button>
        </div>
    </div>
}