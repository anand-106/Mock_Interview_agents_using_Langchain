import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/huggingface_transformers";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { createRetrievalChain } from "langchain/chains/retrieval";
import { createStuffDocumentsChain } from "langchain/chains/combine_documents";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

export async function askGeminiRAG(query: string) {
  const pdfPath =
    "C:/Users/gamin/Documents/projects/Mock_Interview_agents_using_Langchain/backend/assets/Anand-S-Resume.pdf";

  const loader = new PDFLoader(pdfPath);

  const docs = await loader.load();

  //   const docs = [
  //     "LangChain enables LLMs to access tools, memory, and external data.",
  //     "RAG combines retrieval with generation to answer questions using context.",
  //     "Anand lives in Alappuzha.",
  //   ];

  const embeddings = new HuggingFaceTransformersEmbeddings({
    model: "BAAI/bge-base-en-v1.5",
  });

  const vectorStore = await MemoryVectorStore.fromDocuments(docs, embeddings);

  const retriever = vectorStore.asRetriever();

  const llm = new ChatGoogleGenerativeAI({
    model: "gemini-2.0-flash",
    apiKey: process.env.GOOGLE_API_KEY,
    temperature: 0.3,
  });

  const prompt = ChatPromptTemplate.fromTemplate(`
You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question:
{input}
`);

  const combineDocsChain = await createStuffDocumentsChain({
    llm,
    prompt,
  });

  const chain = await createRetrievalChain({
    retriever,
    combineDocsChain,
  });

  const result = await chain.invoke({
    input: query,
  });

  return result;
}
