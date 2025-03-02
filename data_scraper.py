import os
import json
from moegirl_scraper import MoegirlWikiScraper  # 导入萌娘百科爬虫
import wikipediaapi

class AnimeDataFetcher:
    def __init__(self, language="zh"):
        self.moegirl_scraper = MoegirlWikiScraper()  # 创建萌娘百科爬虫实例
        self.wiki_api = wikipediaapi.Wikipedia(
            language=language,
            user_agent="AnimeBot/1.0 (https://yourwebsite.com; contact@yourwebsite.com)"
        )
        self.data_dir = "anime_data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_data(self, anime_name):
        """先尝试从萌娘百科爬取，失败则改用 Wikipedia"""
        print(f"🔍 先尝试从萌娘百科获取 {anime_name} ...")
        anime_data = self.moegirl_scraper.crawl_article(anime_name)

        if not anime_data:
            print(f"⚠️ 未在萌娘百科找到 {anime_name}，改用 Wikipedia ...")
            anime_data = self.fetch_from_wikipedia(anime_name)
        else:
            print(f"✅ 萌娘百科爬取成功: {anime_name}")

        if anime_data:
            self.save_data(anime_name, anime_data)
            return anime_data
        else:
            print(f"❌ 未能找到 {anime_name} 的相关信息。")
            return None

    def fetch_from_wikipedia(self, title):
        """从 Wikipedia 爬取数据"""
        page = self.wiki_api.page(title)
        if page.exists():
            return {
                "名称": page.title,
                "来源": page.fullurl,
                "内容": page.summary
            }
        return None

    def save_data(self, anime_name, data):
        """保存数据为 JSON 文件"""
        filename = os.path.join(self.data_dir, f"{anime_name}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已保存: {filename}")

if __name__ == "__main__":
    anime_name = input("📢 请输入要查询的动漫词条: ").strip()
    fetcher = AnimeDataFetcher()
    fetcher.fetch_data(anime_name)
