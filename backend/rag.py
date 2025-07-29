from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from pathlib import Path
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)






def resume_rag_embed(path:str):
    
    
    
    
    pdf_path = Path(f"{path}").resolve()

    
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    
    vectorstore = FAISS.from_documents(documents,embeddings)
    
    retriver = vectorstore.as_retriever()
    
    return retriver
    


def resume_rag_llm(retriver,query):
    load_dotenv()
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )
    
    prompt = ChatPromptTemplate.from_template(
        """
    Use the context below to answer the question.

    Context:
    {context}

    Question:
    {input}
    """
    )
    
    rag_chain  =  ({"context":retriver,"input":RunnablePassthrough()} | prompt | llm)
    
    
    
    result = rag_chain.invoke(query)
    
    
    return result.content
    

if __name__ == "__main__":
    
    retriver = resume_rag_embed(r"C:\Users\gamin\Documents\projects\Mock_Interview_agents_using_Langchain\backend\assets\Anand-S-Resume.pdf")
    
    
    while(True):
        
        text = input("Enter the message : ")
        if text  == "end":
            break
        print(resume_rag_llm(retriver,text))
    