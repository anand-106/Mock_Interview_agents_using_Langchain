"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.askGeminiRAG = askGeminiRAG;
const google_genai_1 = require("@langchain/google-genai");
const huggingface_transformers_1 = require("@langchain/community/embeddings/huggingface_transformers");
const memory_1 = require("langchain/vectorstores/memory");
const retrieval_1 = require("langchain/chains/retrieval");
const combine_documents_1 = require("langchain/chains/combine_documents");
const prompts_1 = require("@langchain/core/prompts");
const pdf_1 = require("@langchain/community/document_loaders/fs/pdf");
function askGeminiRAG(query) {
    return __awaiter(this, void 0, void 0, function* () {
        const pdfPath = "C:/Users/gamin/Documents/projects/Mock_Interview_agents_using_Langchain/backend/assets/Anand-S-Resume.pdf";
        const loader = new pdf_1.PDFLoader(pdfPath);
        const docs = yield loader.load();
        //   const docs = [
        //     "LangChain enables LLMs to access tools, memory, and external data.",
        //     "RAG combines retrieval with generation to answer questions using context.",
        //     "Anand lives in Alappuzha.",
        //   ];
        const embeddings = new huggingface_transformers_1.HuggingFaceTransformersEmbeddings({
            model: "BAAI/bge-base-en-v1.5",
        });
        const vectorStore = yield memory_1.MemoryVectorStore.fromDocuments(docs, embeddings);
        const retriever = vectorStore.asRetriever();
        const llm = new google_genai_1.ChatGoogleGenerativeAI({
            model: "gemini-2.0-flash",
            apiKey: process.env.GOOGLE_API_KEY,
            temperature: 0.3,
        });
        const prompt = prompts_1.ChatPromptTemplate.fromTemplate(`
You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question:
{input}
`);
        const combineDocsChain = yield (0, combine_documents_1.createStuffDocumentsChain)({
            llm,
            prompt,
        });
        const chain = yield (0, retrieval_1.createRetrievalChain)({
            retriever,
            combineDocsChain,
        });
        const result = yield chain.invoke({
            input: query,
        });
        return result;
    });
}
