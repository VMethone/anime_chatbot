import wikipedia

# 1️⃣ 设置 Wikipedia API 访问
wikipedia.set_lang("en")  # 设定为英文 Wikipedia
wikipedia.set_user_agent("AnimeRAGBot/1.0 (contact: yixiang.vic@gmail.com)")  # ✅ 设置 User-Agent

# 2️⃣ 自动选择最佳 Wikipedia 词条
def get_best_wikipedia_match(anime_title):
    search_results = wikipedia.search(anime_title, results=5)
    
    if not search_results:
        print(f"❌ 没有找到 {anime_title} 的 Wikipedia 页面")
        return None

    print(f"🔎 {anime_title} 可能的匹配项: {search_results}")

    # **优先选择带 `(manga)` 或 `(anime)` 的结果**
    for result in search_results:
        if "(manga)" in result or "(anime)" in result:
            print(f"✅ 选择最佳匹配: {result}")
            return result

    # **如果没有 `(manga)` 或 `(anime)`，默认选第一个**
    print(f"⚠️ 没有找到带 (manga) 或 (anime) 的结果，默认选择: {search_results[0]}")
    return search_results[0]

# 3️⃣ 获取 Wikipedia **完整** 页面内容
def get_wikipedia_summary(anime_title):
    try:
        best_match = get_best_wikipedia_match(anime_title)
        if not best_match:
            return None

        # **获取 Wikipedia 页面内容**
        page = wikipedia.page(best_match, auto_suggest=True)
        summary = page.content  # ✅ **获取完整页面内容**
        
        print(f"📖 {best_match} 爬取成功，共 {len(summary)} 字")  
        return summary

    except wikipedia.exceptions.DisambiguationError as e:
        print(f"⚠️ {anime_title} 匹配到多个结果，请更具体: {e.options[:5]}")
        return None
    except wikipedia.exceptions.PageError:
        print(f"❌ {anime_title} 页面不存在，尝试 '(manga)' 版本")
        return get_wikipedia_summary(f"{anime_title} (manga)")  # ✅ **自动尝试 "One Piece (manga)"**
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return None

# 4️⃣ 预定义动漫角色列表
anime_characters = {
    "Naruto": "Naruto Uzumaki, Sasuke Uchiha, Sakura Haruno, Kakashi Hatake",
    "One Piece": "Monkey D. Luffy, Roronoa Zoro, Nami, Sanji, Tony Tony Chopper",
    "Attack on Titan": "Eren Yeager, Mikasa Ackerman, Armin Arlert, Levi Ackerman"
}

# 5️⃣ 需要爬取的动漫列表
anime_list = ["Naruto", "One Piece", "Attack on Titan"]

# 6️⃣ 重新写入完整数据
with open("data/anime_encyclopedia.txt", "w", encoding="utf-8") as f:
    for anime in anime_list:
        summary = get_wikipedia_summary(anime)
        if summary:
            characters = anime_characters.get(anime, "No character data available")
            content = f"Anime: {anime}\nDescription: {summary}\nMain Characters: {characters}\n\n"
            f.write(content)
            print(f"✅ {anime} 已写入文件")
        else:
            print(f"⚠️ {anime} 没有爬取到内容，跳过")

print("🎉 动漫数据爬取完成！")
