import express from "express";
import { askGeminiRAG } from "./rag";

const app = express();

app.use(express.json());

const port = 3000;

app.get("/", (req, res) => {
  res.json({ message: "Hello World" });
});

app.post("/rag", async (req, res) => {
  const { message }: { message: string } = req.body;

  try {
    const output = await askGeminiRAG(message);
    res.json(output);
  } catch (e) {
    console.log(e);
  }
});

app.listen(port, () => {
  console.log(`server listening on port ${port}`);
});
