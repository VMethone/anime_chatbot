from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.llms import Ollama  # 本地 LLaMA 3
import langdetect  # 语言检测

# 允许 FAISS 反序列化（确保数据库文件是自己生成的）
vector_db = FAISS.load_local(
    "vector_db",
    HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    allow_dangerous_deserialization=True
)

# 加载本地 LLaMA 3
llm = Ollama(model="llama3")  # 确保你已下载 `ollama pull llama3`

while True:
    user_input = input("📢 请输入问题（输入 'exit' 退出）：")
    if user_input.lower() == "exit":
        break

    # 检测输入语言
    detected_lang = langdetect.detect(user_input)
    print(f"🔍 检测到语言: {detected_lang}")

    # 进行 FAISS 相似性搜索（增加 `k=8` 获取更多背景信息）
    search_results = vector_db.similarity_search(user_input, k=8)
    context = "\n".join([doc.page_content for doc in search_results])

    # 如果 `FAISS` 结果为空，直接回答 "我不知道"
    if not context.strip():
        print("🤖 AI 回答: 我不知道。")
        continue

    # 让 AI 生成详细回答
    prompt = f"""请使用{ '中文' if detected_lang.startswith('zh') else '英文' }详细回答以下问题。
你的回答必须基于提供的背景知识，不要编造内容。请尽可能提供完整的信息，包括人物背景、剧情相关内容等。要包括尽可能多的细节。

背景知识：
{context}

问题：{user_input}

请提供详细回答：
"""

    answer = llm.invoke(prompt)

    print(f"🤖 AI 回答:\n{answer}")
