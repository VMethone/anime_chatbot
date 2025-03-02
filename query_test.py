from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM  # ✅ 更新 Ollama 导入
import langdetect  # 语言检测

# ✅ 确保 FAISS 向量数据库正确加载
vector_db = FAISS.load_local(
    "vector_db",
    HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    allow_dangerous_deserialization=True  # ✅ 解决加载问题
)

# ✅ 使用本地 LLaMA 3 模型
llm = OllamaLLM(model="llama3")  # `ollama pull llama3` 确保下载了模型

while True:
    user_input = input("📢 请输入问题（输入 'exit' 退出）：")
    if user_input.lower() == "exit":
        break

    # **1️⃣ 语言检测**
    detected_lang = langdetect.detect(user_input)
    print(f"🔍 检测到语言: {detected_lang}")

    # **2️⃣ 进行 FAISS 语义搜索**
    search_results = vector_db.similarity_search(user_input, k=8)
    context = "\n".join([doc.page_content for doc in search_results])

    # **3️⃣ 如果没有匹配结果，避免 AI 乱答**
    if not context.strip():
        print("🤖 AI 回答: 抱歉，我没有找到相关信息。")
        continue

    # **4️⃣ 生成 AI 回答**
    prompt = f"""请用 {'中文' if detected_lang.startswith('zh') else '英文'} 回答问题，基于以下背景知识：
{context}

问题：{user_input}

请提供准确、详细的回答："""
    answer = llm.invoke(prompt)

    print(f"🤖 AI 回答:\n{answer}")
