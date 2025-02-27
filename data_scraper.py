from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.llms import Ollama  # ✅ 本地 LLaMA 3
import langdetect  # ✅ 语言检测

# ✅ 允许 FAISS 反序列化（确保数据库文件是自己生成的）
vector_db = FAISS.load_local(
    "vector_db",
    HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    allow_dangerous_deserialization=True
)

# ✅ 加载本地 LLaMA 3
llm = Ollama(model="llama3")  # 确保你已下载 `ollama pull llama3`

while True:
    user_input = input("📢 请输入问题（输入 'exit' 退出）：")
    if user_input.lower() == "exit":
        break

    # ✅ 检测输入语言
    detected_lang = langdetect.detect(user_input)
    print(f"🔍 检测到语言: {detected_lang}")

    # ✅ 进行 FAISS 相似性搜索（调整 k=5 获取更多上下文）
    search_results = vector_db.similarity_search(user_input, k=5)
    context = "\n".join([doc.page_content for doc in search_results])

    # ✅ 如果 `FAISS` 没有找到相关内容，直接回答 "我不知道"
    if not context.strip():
        print("🤖 AI 回答: 我不知道。")
        continue

    # ✅ 让 AI 只基于 FAISS 结果回答，并明确要求 **不能编造答案**
    if detected_lang.startswith("zh"):
        prompt = f"""请使用中文回答以下问题，并且只能基于提供的背景知识，不要编造答案。
如果背景知识中找不到答案，请回答 "我不知道"。

背景知识：
{context}

问题：{user_input}

请用中文简洁回答：
"""
    else:
        prompt = f"""Please answer the following question in English.
You must only use the given context. Do not make up any information.
If the answer is not found in the context, respond with "I don't know."

Context:
{context}

Question: {user_input}

Provide a concise answer in English:
"""

    answer = llm.invoke(prompt)

    print(f"🤖 AI 回答:\n{answer}")