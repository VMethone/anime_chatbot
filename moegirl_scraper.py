import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import quote, urljoin

class MoegirlWikiScraper:
    def __init__(self, base_url="https://moegirl.uk/", save_dir="moegirl_data", timeout=10):
        """ 初始化爬虫 """
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        self.timeout = timeout
        self.save_dir = save_dir
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def get_page(self, title):
        """ 获取页面 HTML """
        encoded_title = quote(title)
        url = urljoin(self.base_url, encoded_title)
        
        print(f"🔍 访问: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                return response.text, url
            else:
                print(f"❌ 页面不存在: {url}（状态码: {response.status_code}）")
                return None, url
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return None, url

    def extract_sections(self, soup):
        """ 解析页面章节 """
        content = soup.find('div', {'id': 'mw-content-text'})
        sections = []
        current_section = None
        
        for element in content.find_all(['h2', 'h3', 'p', 'ul', 'dl']):
            if element.name in ['h2', 'h3']:
                if current_section:
                    sections.append(current_section)
                
                title = element.find('span', class_='mw-headline')
                if title:
                    current_section = {
                        'level': element.name,
                        'title': title.get_text(strip=True),
                        'content': []
                    }
            elif current_section:
                if element.name == 'p':
                    text = element.get_text(strip=True)
                    if text:
                        current_section['content'].append({'type': 'paragraph', 'text': text})
                elif element.name == 'ul':
                    items = [li.get_text(strip=True) for li in element.find_all('li')]
                    if items:
                        current_section['content'].append({'type': 'list', 'items': items})
                elif element.name == 'dl':
                    members = self.parse_dl_table(element)
                    if members:
                        current_section['content'].append({'type': 'members', 'data': members})
        
        if current_section:
            sections.append(current_section)

        return sections

    def parse_dl_table(self, dl_element):
        """ 解析 <dl> 结构（成员列表）"""
        members = []
        dt_elements = dl_element.find_all('dt')
        dd_elements = dl_element.find_all('dd')

        for dt, dd in zip(dt_elements, dd_elements):
            member = {
                '姓名': dt.get_text(strip=True),
                '角色': dd.get_text(strip=True)
            }
            members.append(member)

        return members if members else None

    def parse_article(self, html, url):
        """ 解析百科词条 """
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title_elem = soup.find('h1', {'id': 'firstHeading'})
        title = title_elem.text.strip() if title_elem else "未知标题"

        # 提取章节
        sections = self.extract_sections(soup)

        # 提取图片
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(self.base_url, src)
            images.append(src)

        return {
            '名称': title,
            '来源': url,
            '章节内容': sections,
            '图片': images[:10]  # 限制最多 10 张图片
        }
    
    def save_article(self, article_data):
        """ 保存文章为 JSON """
        if not article_data:
            return
        
        safe_title = article_data['名称'].replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = os.path.join(self.save_dir, f"{safe_title}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 结果已保存: {filename}")

    def crawl_article(self, title):
        """ 根据输入爬取百科词条 """
        html, url = self.get_page(title)
        if not html:
            return
        
        article_data = self.parse_article(html, url)
        self.save_article(article_data)

        return article_data


# **运行爬虫**
if __name__ == "__main__":
    scraper = MoegirlWikiScraper()

    # 用户输入词条名
    title = input("📢 请输入百科词条名称: ").strip()
    scraper.crawl_article(title)
