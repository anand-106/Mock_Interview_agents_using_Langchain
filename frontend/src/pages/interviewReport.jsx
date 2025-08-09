import { useEffect } from "react"
import { useLocation } from "react-router-dom"

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

    return <div>
        <h1>Interview Report</h1>
        <p>{report}</p>
    </div>
}