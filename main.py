from fastapi import FastAPI  # 创建 API 服务器
from pydantic import BaseModel  # 处理请求数据格式
from langchain_community.vectorstores import FAISS  # FAISS 向量数据库
from langchain_community.embeddings import HuggingFaceEmbeddings  # 本地嵌入模型
from langchain.llms import Ollama  # 本地 LLaMA 3 语言模型
from langchain.chains import RetrievalQA  # 结合检索（RAG）的问答系统

# 创建 FastAPI 应用
app = FastAPI()

# 加载 FAISS 向量数据库（使用本地嵌入模型）
vector_db = FAISS.load_local("vector_db", HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
retriever = vector_db.as_retriever()

# 使用本地 LLaMA 3（Ollama 运行）
llm = Ollama(model="llama3")  # 可以换成 "mistral"

# 创建 RAG 问答系统
qa = RetrievalQA.from_chain_type(llm, retriever=retriever)

# 定义 API 请求格式
class QueryRequest(BaseModel):
    question: str  # 用户的问题

# 定义 API 路由（前端可以 POST 请求这里进行问答）
@app.post("/query/")
async def query_anime(data: QueryRequest):
    answer = qa.run(data.question)  # 运行 RAG 模型
    return {"question": data.question, "answer": answer}

# 运行 API 服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
