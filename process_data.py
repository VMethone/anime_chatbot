from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# 读取数据文件
data_file = "data/anime_encyclopedia.txt"
with open(data_file, "r", encoding="utf-8") as f:
    raw_data = f.read().split("\n\n")  # 每个动漫数据块之间有一个空行

# 处理数据格式
docs = []
for entry in raw_data:
    if entry.strip():  # 忽略空数据
        docs.append(Document(page_content=entry))

# 选择多语言嵌入模型
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 生成 FAISS 向量数据库
vector_db = FAISS.from_documents(docs, embedding_model)
vector_db.save_local("vector_db")

print("✅ FAISS 向量数据库创建完成（支持中英检索）！")
