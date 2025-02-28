import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote, urljoin
import re
import time
import random

BASE_URL = "https://zh.moegirl.org.cn"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": BASE_URL + "/Mainpage",
    "DNT": "1"
}

def clean_text(text):
    """增强版文本清理"""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)  # 移除注释
    text = re.sub(r'\[\d+\]', '', text)  # 移除引用标记
    text = re.sub(r'\s+', ' ', text).strip()
    return text.replace('\u200b', '').replace('\xa0', ' ')

def parse_cell_content(cell):
    """深度解析单元格内容"""
    content_parts = []
    
    # 处理特殊元素
    for element in cell.descendants:
        if isinstance(element, str):
            content_parts.append(element.strip())
        elif element.name == 'img':
            alt = element.get('alt', '图片').strip()
            src = urljoin(BASE_URL, element.get('src', ''))
            content_parts.append(f"[图片: {alt}]({src})")
        elif element.name == 'a' and element.get('href'):
            text = element.text.strip()
            link = urljoin(BASE_URL, element['href'])
            content_parts.append(f"{text}（{link}）")
        elif element.name == 'br':
            content_parts.append('\n')
        elif 'heimu' in element.get('class', []):  # 处理黑幕文本
            content_parts.append(f"||{element.text.strip()}||")
    
    # 合并处理结果
    raw_text = ''.join(content_parts)
    return clean_text(raw_text)

def parse_infobox(infobox):
    """完整Infobox解析实现"""
    anime_data = {}
    current_headers = []
    
    try:
        # 排除嵌套表格
        if infobox.find_parent('table'):
            return {}
            
        for row in infobox.find_all('tr'):
            # 解析表头行
            th_list = row.find_all('th')
            if th_list:
                current_headers = []
                for th in th_list:
                    header = clean_text(th.get_text(separator=" "))
                    rowspan = int(th.get('rowspan', 1))
                    current_headers.extend([header] * rowspan)
                continue
                
            # 解析数据行
            td_list = row.find_all('td')
            if not td_list:
                continue
                
            # 处理跨列单元格
            if len(td_list) == 1 and current_headers:
                anime_data[current_headers[0]] = parse_cell_content(td_list[0])
                continue
                
            # 常规键值对处理
            for header, td in zip(current_headers, td_list):
                anime_data[header] = parse_cell_content(td)
                
    except Exception as e:
        print(f"⚠️ Infobox解析异常: {str(e)}")
        
    return anime_data

def get_anime_info(anime_name):
    """完整信息获取流程"""
    session = requests.Session()
    encoded_name = quote(anime_name.strip().replace(' ', '_'), safe='')
    url = f"{BASE_URL}/{encoded_name}"
    
    try:
        # 随机延迟防止封禁
        time.sleep(random.uniform(1, 2))
        
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 强制编码处理
        if response.encoding.lower() != 'utf-8':
            response.encoding = 'utf-8'
            
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 新版Infobox检测
        infobox = soup.find('table', class_=re.compile(r'wikitable|infobox'))
        
        anime_data = {
            "名称": anime_name,
            "来源": url,
            "基本信息": {},
            "剧情简介": ""
        }
        
        if infobox:
            anime_data["基本信息"] = parse_infobox(infobox)
            
        # 增强版简介提取
        content_div = soup.find('div', class_='mw-parser-output')
        if content_div:
            for element in content_div.children:
                if element.name == 'p':
                    text = clean_text(element.get_text())
                    if len(text) > 100 and not re.search(r'^本条目需要', text):
                        anime_data["剧情简介"] = text
                        break
                elif element.name in ['h2', 'div', 'table']:
                    break
                    
        # 数据清洗
        anime_data["基本信息"] = {
            k: v for k, v in anime_data["基本信息"].items() 
            if v and k not in [''] and len(v) < 500
        }
        
        return anime_data
        
    except Exception as e:
        print(f"❌ 获取数据失败: {str(e)}")
        return None

if __name__ == "__main__":
    anime_name = input("📢 请输入动画名称: ").strip()
    if not anime_name:
        print("⚠️ 输入不能为空")
        exit()
        
    result = get_anime_info(anime_name)
    
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ 未能获取有效信息")