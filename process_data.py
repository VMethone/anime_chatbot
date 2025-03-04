import json
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class AnimeVectorDB:
    def __init__(self, data_dir="moegirl_data"):
        self.data_dir = data_dir
        self.vector_db_path = "vector_db"
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

        if os.path.exists(self.vector_db_path):
            print(f"📂 加载已有向量数据库: {self.vector_db_path}")
            self.db = FAISS.load_local(self.vector_db_path, self.embedding_model, allow_dangerous_deserialization=True)
        else:
            print("📂 创建新向量数据库...")
            self.create_vector_db()

    def load_json_data(self):
        """加载 JSON 数据"""
        documents = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                source = data.get("来源", "未知来源")

                # 处理角色信息
                for char in data.get("角色信息", []):
                    char_text = f"{char['角色名']} - {char.get('担当', '未知角色')}"
                    documents.append((char_text, source))

        return documents

    def create_vector_db(self):
        """创建 FAISS 向量数据库"""
        data = self.load_json_data()
        if not data:
            print("⚠️ 没有找到可用的 JSON 数据，无法创建向量数据库！")
            return

        texts, sources = zip(*data)
        self.db = FAISS.from_texts(texts=texts, embedding=self.embedding_model, metadatas=[{"来源": src} for src in sources])
        self.db.save_local(self.vector_db_path)
        print("✅ 向量数据库已创建并保存！")

if __name__ == "__main__":
    vector_db = AnimeVectorDB()
