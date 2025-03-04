import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import quote, urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class MoegirlScraper:
    def __init__(self, base_url="https://moegirl.uk/", data_dir="moegirl_data"):
        self.base_url = base_url
        self.data_dir = data_dir
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        
        # 配置重试机制
        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_page(self, title):
        """带重试机制的页面请求"""
        encoded_title = quote(title)
        url = f"{self.base_url}{encoded_title}"
        print(f"🔍 正在访问: {url}")

        try:
            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            return None

    def parse_article(self, html, url):
        """完整内容解析引擎"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 解析基础信息
        article_data = {
            "名称": self._get_title(soup),
            "来源": url,
            "章节内容": [],
            "角色信息": []
        }

        # 解析章节结构
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if content_div:
            current_section = None
            for element in content_div.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'table', 'div']):
                if element.name in ['h2', 'h3']:
                    if current_section:
                        article_data["章节内容"].append(current_section)
                    current_section = self._create_section(element)
                elif current_section:
                    self._process_element(element, current_section)
            
            if current_section:
                article_data["章节内容"].append(current_section)

        # 解析角色信息
        article_data["角色信息"] = self.extract_characters(soup)

        # 清理空章节
        article_data["章节内容"] = [s for s in article_data["章节内容"] if s["content"] or s["title"] in ["注释与外部链接"]]

        self._save_data(article_data)
        return article_data

    def _create_section(self, element):
        """创建新章节"""
        title_span = element.find('span', class_='mw-headline')
        return {
            "level": element.name,
            "title": title_span.get_text(strip=True) if title_span else "无标题",
            "content": []
        }

    def _get_title(self, soup):
        """获取页面标题"""
        title_tag = soup.find("h1", {"id": "firstHeading"})
        return title_tag.text.strip() if title_tag else "未知标题"

    def _process_element(self, element, section):
        """处理各种内容元素"""
        # 跳过导航栏等无关内容
        if 'navbox' in element.get('class', []):
            return

        # 内容处理器映射
        handlers = {
            'p': self._parse_paragraph,
            'ul': self._parse_list,
            'ol': self._parse_list,
            'table': self._parse_table,
            'div': self._parse_special_div
        }

        if element.name in handlers:
            content = handlers[element.name](element)
            if content:
                section["content"].append(content)

    def _parse_paragraph(self, p):
        """解析段落"""
        text = p.get_text(' ', strip=True)
        text = text.replace('（）', '').replace('()', '')  # 清理空括号
        if len(text) > 30:  # 过滤短文本
            return {"type": "paragraph", "text": text}
        return None

    def _parse_list(self, ul):
        """解析列表"""
        items = [li.get_text(' ', strip=True) for li in ul.find_all('li')]
        return {"type": "list", "items": items}

    def _parse_table(self, table):
        """解析表格数据"""
        if 'wikitable' not in table.get('class', []):
            return None

        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for td in tr.find_all(['th', 'td']):
                # 清理单元格内容
                cell_text = td.get_text(' ', strip=True)
                cell_text = cell_text.replace('\xa0', ' ')  # 替换不间断空格
                cells.append(cell_text)
            if cells:
                rows.append(cells)

        if not rows:
            return None

        return {
            "type": "table",
            "header": rows[0] if len(rows) > 1 else [],
            "rows": rows[1:] if len(rows) > 1 else rows
        }

    def _parse_special_div(self, div):
        """解析特殊div内容"""
        # 处理带图片的说明框
        if 'thumb' in div.get('class', []):
            img_tag = div.find('img')
            caption = div.find('div', class_='thumbcaption')
            return {
                "type": "image_box",
                "image": urljoin(self.base_url, img_tag['src']) if img_tag else None,
                "caption": caption.get_text(strip=True) if caption else None
            }
        return None

    def extract_characters(self, soup):
        """角色信息解析"""
        characters = []
        for card in soup.select('.role-list-item'):
            # 解析角色名称
            name_tag = card.select_one('.role-name a')
            if not name_tag:
                continue

            # 中日文名称处理
            ch_name = name_tag.get_text(strip=True)
            jp_name = self._parse_japanese_name(card)
            full_name = f"{ch_name}（{jp_name}）" if jp_name else ch_name

            # 构建角色信息
            role_info = {
                "角色名": full_name,
                "图片": self._parse_character_image(card),
                "详细信息": self._parse_character_details(card)
            }
            characters.append(role_info)

        return characters

    def _parse_japanese_name(self, card):
        """解析日文名称"""
        jp_div = card.select_one('.role-name span[lang="ja"]')
        if not jp_div:
            return None

        name_parts = []
        for ruby in jp_div.find_all('ruby'):
            kanji = ''.join([rb.get_text(strip=True) for rb in ruby.find_all('rb')])
            kana = ruby.find('rt').get_text(strip=True) if ruby.find('rt') else ""
            name_parts.append(f"{kanji}({kana})" if kana else kanji)
        
        return ' '.join(name_parts)

    def _parse_character_image(self, card):
        """解析角色图片"""
        img_tag = card.find('img')
        if img_tag and 'src' in img_tag.attrs:
            return urljoin(self.base_url, img_tag['src'])
        return None

    def _parse_character_details(self, card):
        """解析详细信息"""
        details = {}
        info_div = card.select_one('.role-info-inner')
        if not info_div:
            return details

        # 解析键值对
        current_key = None
        for element in info_div.children:
            if element.name == 'p':
                text = element.get_text(' ', strip=True)
                if '：' in text:
                    key, val = text.split('：', 1)
                    details[key.strip()] = val.strip()
                    current_key = key.strip()
                elif current_key:
                    details[current_key] += " " + text.strip()
            
            # 解析补充说明
            elif element.name == 'dl':
                details.setdefault('补充说明', []).extend(
                    [dd.get_text(' ', strip=True) for dd in element.find_all('dd')]
                )

        return details

    def _save_data(self, data):
        """保存数据"""
        safe_title = ''.join(c for c in data["名称"] if c.isalnum() or c in ' _-')
        filename = os.path.join(self.data_dir, f"{safe_title}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已保存至: {filename}")

    def crawl_article(self, title):
        """执行爬取任务"""
        html = self.fetch_page(title)
        if not html:
            return None
        return self.parse_article(html, f"{self.base_url}{quote(title)}")

if __name__ == "__main__":
    scraper = MoegirlScraper()
    name = input("📢 请输入要爬取的条目名称: ")
    
    start_time = time.time()
    result = scraper.crawl_article(name)
    
    if result:
        print(f"⏱️ 爬取完成，耗时 {time.time()-start_time:.2f}秒")
        print(f"🏷️ 发现 {len(result['章节内容'])} 个章节")
        print(f"👥 解析到 {len(result['角色信息'])} 个角色信息")