import { useState } from "react"

import axios from "axios"
import { useNavigate } from "react-router-dom"


export function UploadPage(){

    const [file,setFile] = useState(null)
    const [jobRole,setJobrole] = useState(null)
    const [companyName,setCompanyName] = useState(null)
    const [jobDetails,setJobDetails] = useState(null)
    const navigate = useNavigate()

    const handleFileUpload = ()=>{
        if(!file){
            alert("Please Select a File")
        }

        const formdata = new FormData();

        formdata.append("file",file)
        formdata.append("role",jobRole)
        formdata.append("company",companyName)
        formdata.append("details",jobDetails)

        axios.post("http://localhost:8000/upload_resume/",formdata,{
            headers:{
                "Content-Type": "multipart/form-data"
            }
        }).then((res)=>{
            console.log("File Upload done",res)
            navigate("/interview",{state:{id:res.data.id}})
        }).catch((err=>{
            console.log(err)
        }))
        
    }


    return <div className="w-full h-full flex flex-col">
        <input type="file" accept="application/pdf" 
        className="cursor-pointer"
        onChange={(e)=>{
            setFile(e.target.files[0])
        }}
        />

        <input placeholder="Job Role" value={jobRole} onChange={(e)=>{
            setJobrole(e.target.value)
        }}/>
        <input placeholder="Company Name" value={companyName} onChange={(e)=>{
            setCompanyName(e.target.value)
        }}/>

        <textarea placeholder="Enter other details" className="h-[300px] w-[500px]" onChange={(e=>{
            setJobDetails(e.target.value)
        })}
        value={jobDetails}
        />

        <button onClick={handleFileUpload} >Start Interview</button>
    </div>
}