Anime RAG Chatbot

**Anime RAG Chatbot** 是一个基于本地 LLaMA 3 + FAISS 向量数据库的 AI 机器人，能够回答关于动漫的百科问题。它支持 本地推理，不依赖 OpenAI API，并能够自动爬取 Wikipedia 数据构建知识库。

---

## 📌 1. 功能介绍

✅ **自动爬取 Wikipedia 动漫数据**（剧情、角色设定等）  
✅ **本地运行 LLaMA 3 / Mistral 7B**（通过 Ollama 实现）  
✅ **RAG（检索增强生成）+ FAISS 向量数据库**  
✅ **FastAPI 提供 REST API**，可用于 Web、聊天机器人等  
✅ **终端直接交互（query_test.py）**

---

## 📂 2. 目录结构

\`\`\`
📂 anime-rag-chatbot
├── 📂 data                    # 存储动漫百科数据
│   ├── anime_encyclopedia.txt
├── 📂 vector_db               # FAISS 向量数据库
├── main.py                    # FastAPI 服务器
├── process_data.py             # 处理数据并存入 FAISS
├── query_test.py               # 终端问答测试
├── data_scraper.py             # 爬取 Wikipedia 数据
├── requirements.txt            # 依赖文件
└── README.md                   # 说明文档
\`\`\`

---

## 📥 3. 安装依赖

首先，安装 Python 依赖：
\`\`\`bash
pip install -r requirements.txt
\`\`\`

如果你还没有安装 **Ollama**，请运行：
\`\`\`bash
curl -fsSL https://ollama.com/install.sh | sh
\`\`\`
然后下载 **LLaMA 3 模型**：
\`\`\`bash
ollama pull llama3
\`\`\`

---

## 🔍 4. 爬取动漫百科数据

**运行爬虫，自动爬取 Wikipedia 动漫百科数据**
\`\`\`bash
python data_scraper.py
\`\`\`
成功后，\`data/anime_encyclopedia.txt\` 将包含类似的数据：
\`\`\`
Anime: Naruto
Description: Naruto Uzumaki is a young ninja striving to become the Hokage...
Main Characters: Naruto Uzumaki, Sasuke Uchiha, Sakura Haruno, Kakashi Hatake
\`\`\`

---

## 📂 5. 处理数据并生成 FAISS 向量数据库

\`\`\`bash
python process_data.py
\`\`\`
这将：
- 读取 \`data/anime_encyclopedia.txt\`
- 使用 \`sentence-transformers\` 进行向量化
- 存储到 FAISS 向量数据库 \`vector_db/\`

---

## 🤖 6. 运行 Chatbot

### **6.1 运行 API**
\`\`\`bash
python main.py
\`\`\`
成功后，访问：
\`\`\`
http://127.0.0.1:8000/docs
\`\`\`
然后可以发送测试请求：
\`\`\`json
{
  "question": "火影忍者的主角是谁？"
}
\`\`\`
返回示例：
\`\`\`json
{
  "question": "火影忍者的主角是谁？",
  "answer": "火影忍者的主角是漩涡鸣人（Uzumaki Naruto）。"
}
\`\`\`

---

### **6.2 直接在终端交互**
\`\`\`bash
python query_test.py
\`\`\`
然后输入：
\`\`\`
📢 请输入问题：进击的巨人的主角是谁？
🤖 AI 回答：艾伦·耶格尔（Eren Yeager）是《进击的巨人》的主角。
\`\`\`

---


