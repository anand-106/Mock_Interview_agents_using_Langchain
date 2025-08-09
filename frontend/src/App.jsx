import { HomePage } from "./pages/home"
import {BrowserRouter,Route,Routes} from "react-router-dom"
import { InterviewReport } from "./pages/interviewReport"
import { UploadPage } from "./pages/uploadPage"

function App() {
  return <BrowserRouter>
  <Routes>
    <Route path="/" element={<UploadPage/>} /> 
    <Route path="/interview" element={<HomePage/>} />
    <Route path="/report" element={<InterviewReport />} />
  </Routes>
  </BrowserRouter>
}

export default App
