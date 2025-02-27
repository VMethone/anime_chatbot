import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.llms import Ollama
import langdetect

# 加载 FAISS 和 LLaMA 3
vector_db = FAISS.load_local(
    "vector_db",
    HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    allow_dangerous_deserialization=True
)
llm = Ollama(model="llama3")

# Streamlit UI
st.title("动漫百科 Chatbot")
st.write("输入你的问题，我会基于 Wikipedia 数据回答！")

user_input = st.text_input("请输入问题（支持中英文）")

if user_input:
    detected_lang = langdetect.detect(user_input)
    search_results = vector_db.similarity_search(user_input, k=5)
    context = "\n".join([doc.page_content for doc in search_results])

    if not context.strip():
        st.write("我不知道。")
    else:
        prompt = f"请使用{ '中文' if detected_lang.startswith('zh') else '英文' }回答以下问题，并且只能基于提供的背景知识，不要编造答案。\n\n背景知识：\n{context}\n\n问题：{user_input}\n\n请简洁回答："
        answer = llm.invoke(prompt)
        st.write(f"AI 回答：\n{answer}")
