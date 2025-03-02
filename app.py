import streamlit as st
from query_test import query_anime

st.set_page_config(page_title="动漫 AI Chatbot", layout="wide")

st.title("🎌 动漫百科 AI 🤖")

# 用户输入
question = st.text_input("🔎 请输入您的问题:", "")

if st.button("提交"):
    if question:
        with st.spinner("AI 思考中..."):
            answer = query_anime(question)
        st.success(answer)
