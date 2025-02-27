import os
import wikipediaapi

# 确保 `data/` 目录存在
os.makedirs("data", exist_ok=True)
DATA_FILE = "data/anime_encyclopedia.txt"

# 设置 Wikipedia API（添加 `contact` 信息）
user_agent = "AnimeRAGBot/1.0 (contact: yixiang.vic@gmail.com)"
wiki_en = wikipediaapi.Wikipedia(language="en", user_agent=user_agent)
wiki_zh = wikipediaapi.Wikipedia(language="zh", user_agent=user_agent)  # ✅ 确保 `zh` 正确

# 目标爬取的动漫列表
anime_list = ["Naruto", "One Piece", "Attack on Titan", "Eren Yeager", "艾伦·耶格尔"]

def get_wikipedia_summary(title):
    """ 获取 Wikipedia 页面摘要（中英双语） """
    print(f"🔍 正在查找 {title} 的 Wikipedia 页面...")

    # 先尝试英文 Wikipedia
    page_en = wiki_en.page(title)
    en_text = page_en.text if page_en.exists() else None

    # 获取 Wikipedia 简体内容
    page_zh = wiki_zh.page(title)
    zh_text = page_zh.text if page_zh.exists() else None

    # 合并中英数据
    if en_text and zh_text:
        return f"[English Wikipedia]\n{en_text}\n\n[简体中文 Wikipedia]\n{zh_text}"
    elif en_text:
        return f"[English Wikipedia]\n{en_text}"
    elif zh_text:
        return f"[简体中文 Wikipedia]\n{zh_text}"
    else:
        print(f"❌ 未找到 {title} 的 Wikipedia 页面")
        return None

# 处理数据
with open(DATA_FILE, "w", encoding="utf-8") as f:
    for anime in anime_list:
        summary = get_wikipedia_summary(anime)
        if summary:
            f.write(f"Anime: {anime}\n")
            f.write(f"Description: {summary}\n\n")
            print(f"✅ {anime} 已写入文件")
        else:
            print(f"⚠️ 无法获取 {anime} 的 Wikipedia 数据")

print("🎉 动漫数据爬取完成！")
