import { useEffect } from "react"
import { useLocation } from "react-router-dom"
import Markdown from "react-markdown";

export function InterviewReport(){

    const location = useLocation()

    const report = location.state?.report

    useEffect(()=>{
        navigator.mediaDevices.getUserMedia({audio:true}).then(
            stream=>{
                stream.getTracks().forEach(track=>{
                    track.stop()
                })
            }
        ).catch(()=>{

        })
    })

    return <div className="w-full h-screen bg-[#030617] text-white flex flex-col items-start p-10 gap-4 overflow-y-auto text-start ">
        <div className="flex flex-col w-full flex-1 bg-slate-700/50 rounded-lg p-5">

        <h1 className="text-2xl text-center font-semibold" >Interview Report</h1>
        <Markdown >{report}</Markdown>
        </div>
    </div>
}