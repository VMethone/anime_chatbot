import os
import wikipediaapi
from moegirl_crawler import getfrommoegirl  # 确保导入正确

# 确保 `data/` 目录存在
os.makedirs("data", exist_ok=True)
DATA_FILE = "data/anime_encyclopedia.txt"

# 设置 Wikipedia API
user_agent = "AnimeRAGBot/1.0 (contact: yixiang.vic@gmail.com)"
wiki_en = wikipediaapi.Wikipedia(language="en", user_agent=user_agent)
wiki_zh = wikipediaapi.Wikipedia(language="zh", user_agent=user_agent)

# 目标爬取的动漫列表
anime_list = ["Naruto", "One Piece", "Attack on Titan", "Eren Yeager", "艾伦·耶格尔"]

def get_wikipedia_summary(title):
    """ 获取 Wikipedia 页面摘要 """
    print(f"正在查找 {title} 的 Wikipedia 页面...")

    page_en = wiki_en.page(title)
    en_text = page_en.text if page_en.exists() else None

    page_zh = wiki_zh.page(title)
    zh_text = page_zh.text if page_zh.exists() else None

    if en_text and zh_text:
        return f"[English Wikipedia]\n{en_text}\n\n[中文 Wikipedia]\n{zh_text}"
    elif en_text:
        return f"[English Wikipedia]\n{en_text}"
    elif zh_text:
        return f"[中文 Wikipedia]\n{zh_text}"
    else:
        print(f"Wikipedia 未找到 {title}，尝试萌娘百科...")
        return None

def get_moegirl_summary(title):
    """ 强制爬取萌娘百科 """
    print(f"尝试从萌娘百科获取 {title} 的数据...")
    for year in range(2000, 2025):
        anime_list = getfrommoegirl(year)
        if anime_list:
            for anime in anime_list:
                if title in anime.name:  # 允许部分匹配
                    print(f"从萌娘百科获取到 {title} 的内容")
                    return f"[萌娘百科]\n{anime.name} ({anime.ani_type}, {anime.season}季, {anime.country})"
    print(f"萌娘百科没有找到 {title}")
    return None

# 处理数据
with open(DATA_FILE, "w", encoding="utf-8") as f:
    for anime in anime_list:
        summary = get_wikipedia_summary(anime)

        # **强制爬取萌娘百科，即使 Wikipedia 已找到数据**
        moe_summary = get_moegirl_summary(anime)
        if moe_summary:
            summary = f"{summary}\n\n{moe_summary}" if summary else moe_summary

        if summary:
            f.write(f"Anime: {anime}\n")
            f.write(f"Description: {summary}\n\n")
            print(f"{anime} 已写入文件")
        else:
            print(f"无法获取 {anime} 的数据")

print("动漫数据爬取完成")
