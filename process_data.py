import os
import json
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class AnimeVectorDB:
    def __init__(self, data_dir="moegirl_data", vector_db_path="vector_db"):
        self.data_dir = data_dir
        self.vector_db_path = vector_db_path
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        # 检查向量数据库是否已存在
        if os.path.exists(vector_db_path):
            print(f"📂 加载已有向量数据库: {vector_db_path}")
            self.db = FAISS.load_local(vector_db_path, self.embedding_model, allow_dangerous_deserialization=True)
        else:
            print("📂 创建新向量数据库...")
            self.create_vector_db()

    def create_vector_db(self):
        """读取 JSON 数据并创建 FAISS 向量数据库"""
        documents = []

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.data_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # 提取文本内容
                if "章节内容" in data:
                    for section in data["章节内容"]:
                        for content in section["content"]:
                            if content["type"] == "paragraph":
                                documents.append(content["text"])

        # 检查是否有数据
        if not documents:
            print("⚠️ 没有找到可用的 JSON 数据，无法创建向量数据库！")
            return

        print(f"📊 生成 {len(documents)} 条文本的嵌入向量...")

        # ✅ 这里不需要手动生成 `embeddings`，直接传入 `embedding_model`
        index = FAISS.from_texts(texts=documents, embedding=self.embedding_model)

        # 保存向量数据库
        index.save_local(self.vector_db_path)
        print("✅ 向量数据库创建成功！")

# 运行
if __name__ == "__main__":
    vector_db = AnimeVectorDB()
