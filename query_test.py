from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import langdetect

# 加载 FAISS 向量数据库
vector_db = FAISS.load_local(
    "vector_db",
    HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    allow_dangerous_deserialization=True
)

# 加载本地 LLaMA 3
llm = Ollama(model="llama3")

while True:
    user_input = input("📢 请输入问题（输入 'exit' 退出）：")
    if user_input.lower() == "exit":
        break

    # 语言检测
    detected_lang = langdetect.detect(user_input)
    print(f"🔍 检测到语言: {detected_lang}")

    # 检索相关数据
    search_results = vector_db.similarity_search(user_input, k=5)

    # 🛠 Debug：打印检索结果
    print("\n🔎 搜索结果（DEBUG）：")
    for doc in search_results:
        print(f"[来源: {doc.metadata.get('来源', '未知')}]\n{doc.page_content}\n")

    context = "\n".join([doc.page_content for doc in search_results])

    if not context.strip():
        print("🤖 AI 回答: 我不知道。")
        continue

    # ✅ 修改 Prompt，强制要求 AI **使用中文回答**
    prompt = f"""
    你是一个精通动漫和萌娘百科的 AI，专门提供详细的动漫角色信息。
    **请使用中文回答**，并尽可能补充细节，如角色背景、性格、相关作品等。

    **背景知识**：
    {context}

    **问题**：
    {user_input}

    **请详细回答，并只基于背景知识，不要编造信息**：
    """
    
    answer = llm.invoke(prompt)
    print(f"\n🤖 AI 回答:\n{answer}\n")
