import os
from langchain_community.vectorstores import FAISS  # FAISS moved to langchain_community
from langchain_community.document_loaders import TextLoader  # Use updated TextLoader
from langchain_huggingface import HuggingFaceEmbeddings  # Use langchain_huggingface
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Text splitter

# 读取动漫百科数据
DATA_PATH = "data/anime_encyclopedia.txt"
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("❌ 请提供 data/anime_encyclopedia.txt 文件")

loader = TextLoader(DATA_PATH)
documents = loader.load()

# 切分文本
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Debugging Step: Print the number of text chunks
print(f"📜 Total Chunks Created: {len(texts)}")

# Check if text chunks are empty
if len(texts) == 0:
    raise ValueError("❌ No text chunks were created! Please check your data file.")

# 使用本地嵌入模型（替换 OpenAI）
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 生成 FAISS 向量数据库
vector_db = FAISS.from_documents(texts, embedding_model)

# 保存向量数据库
os.makedirs("vector_db", exist_ok=True)
vector_db.save_local("vector_db")

print("✅ 动漫百科向量数据库已成功创建！")
