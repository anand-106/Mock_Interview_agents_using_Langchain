import { useRef, useState } from "react"
import { IoMdCloudUpload } from "react-icons/io";
import axios from "axios"
import { useNavigate } from "react-router-dom"



export function UploadPage(){

    const [file,setFile] = useState(null)
    const [jobRole,setJobrole] = useState("")
    const [companyName,setCompanyName] = useState("")
    const [jobDetails,setJobDetails] = useState("")
    const navigate = useNavigate()
    const fileInputRef = useRef(null)
    const [filename, setFileName] = useState("Upload Resume")

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


    return <div className="w-full h-screen flex flex-col bg-[#030617] text-white justify-center items-center">
        <div className="w-full mb-7 flex flex-col gap-3 justify-center items-center">
        <h1 className='font-bold text-5xl'>Mockcruiter</h1>
        <h1>Your personal AI interviewer — anytime, anywhere.</h1>
        </div>
        <div className="flex justify-start items-center gap-2 flex-col bg-slate-800/50 border border-white/20 p-4  w-[500px] rounded-2xl">
        <div className="bg-white/10 w-full h-[100px] flex flex-col justify-center items-center outline-0 rounded-lg cursor-pointer"
        onClick={()=>fileInputRef.current.click()}
        >


        <IoMdCloudUpload size={25} />
        <label>{filename}</label>
        <input type="file" accept="application/pdf" 
        className="cursor-pointer mr-[-100px] hidden"
        ref={fileInputRef}
        onChange={(e)=>{
            setFile(e.target.files[0])
            setFileName(e.target.files[0].name)
        }}
        
        />
        </div>
        <input 
        className="bg-white/10 w-full h-[44px] outline-0 rounded-lg  pl-3"
        placeholder="Job Role" value={jobRole} onChange={(e)=>{
            setJobrole(e.target.value)
        }}/>
        
        <input 
        className="bg-white/10 w-full h-[44px] outline-0 rounded-lg  pl-3"

        placeholder="Company Name" value={companyName} onChange={(e)=>{
            setCompanyName(e.target.value)
        }}/>

        <textarea
        className="bg-white/10 w-full h-[150px] outline-0 resize-none rounded-lg  p-3"
        placeholder="Enter other details" onChange={(e=>{
            setJobDetails(e.target.value)
        })}
        value={jobDetails}
        />

        <button 
        className="bg-white text-black font-semibold text-[17px] cursor-pointer  w-full h-[44px] outline-0 rounded-lg  pl-3"
        
        onClick={handleFileUpload} >Start Interview</button>
        </div>
    </div>
}