from langchain_community.vectorstores import FAISS  # ✅ Updated FAISS import
from langchain_huggingface import HuggingFaceEmbeddings  # ✅ Updated embeddings import
from langchain_community.llms import Ollama  # ✅ Use local LLaMA 3
from langchain.chains import RetrievalQA  # ✅ RAG pipeline

# 1️⃣ 允许 FAISS 反序列化
vector_db = FAISS.load_local(
    "vector_db",
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    allow_dangerous_deserialization=True  # ✅ 允许加载 FAISS 旧格式
)
retriever = vector_db.as_retriever()

# 2️⃣ 使用本地 LLaMA 3（Ollama 运行）
llm = Ollama(model="llama3")  # 可换成 "mistral"
qa = RetrievalQA.from_chain_type(llm, retriever=retriever)

# 3️⃣ 终端交互模式
print("🎉 动漫百科 AI 已启动！输入 'exit' 退出")
while True:
    question = input("\n📢 请输入问题（输入 'exit' 退出）：")
    if question.lower() == "exit":
        print("👋 再见！")
        break
    answer = qa.run(question)
    print("🤖 AI 回答：", answer)
