from fastapi import FastAPI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

app = FastAPI()

# 加载 FAISS 向量数据库
vector_db = FAISS.load_local("vector_db", HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"))

@app.post("/query/")
async def query_anime(question: str):
    search_results = vector_db.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in search_results])
    return {"question": question, "answer": context}

# 运行 FastAPI 服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
