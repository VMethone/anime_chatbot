import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

def extract_sections(soup):
    """ 提取章节结构，包括文本、列表、表格（成员 & 真人乐队）"""
    content = soup.find('div', {'id': 'mw-content-text'})
    sections = []
    current_section = None
    
    # 解析所有章节
    for element in content.find_all(['h2', 'h3', 'p', 'ul', 'table', 'div', 'dl']):
        if element.name in ['h2', 'h3']:
            # 保存前一个章节
            if current_section:
                sections.append(current_section)
            
            # 创建新章节
            title = element.find('span', class_='mw-headline')
            if title:
                current_section = {
                    'level': element.name,
                    'title': title.get_text(strip=True),
                    'content': []
                }
        elif current_section:
            # 处理文本段落
            if element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    current_section['content'].append({'type': 'paragraph', 'text': text})
            
            # 处理无序列表
            elif element.name == 'ul':
                items = [li.get_text(strip=True) for li in element.find_all('li')]
                if items:
                    current_section['content'].append({'type': 'list', 'items': items})

            # 处理“真人乐队”表格
            elif element.name == 'dl':
                members = parse_dl_table(element)
                if members:
                    current_section['content'].append({'type': 'members', 'data': members})

            # 处理“角色形象”列表
            elif element.get('class') and 'role-list-item' in element.get('class', []):
                roles = parse_role_list(element)
                if roles:
                    current_section['content'].append({'type': 'roles', 'data': roles})

    # 添加最后一个章节
    if current_section:
        sections.append(current_section)
    
    return sections

def parse_dl_table(dl_element):
    """ 解析 <dl> 结构中的成员数据 """
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

def parse_role_list(role_element):
    """ 解析 .role-list-item 结构中的角色数据 """
    roles = []
    role_name_element = role_element.find('div', class_='role-name')
    role_image_element = role_element.find('div', class_='role-image')
    
    if role_name_element:
        role_name = role_name_element.get_text(strip=True)
        
        # 提取角色图片
        role_img = None
        img_tag = role_image_element.find('img') if role_image_element else None
        if img_tag and 'src' in img_tag.attrs:
            role_img = "https://moegirl.uk" + img_tag['src']  # 拼接完整URL
            
        roles.append({
            '角色名': role_name,
            '图片': role_img
        })
    
    return roles if roles else None

def enhanced_crawler():
    """ 爬取 MyGO!!!!! 页面并解析内容 """
    target_url = "https://moegirl.uk/MyGO!!!!!"
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')

            # 页面标题
            title = soup.find('h1').text.strip()
            print("页面标题:", title)
            
            # 提取章节内容
            sections = extract_sections(soup)

            # 打印结构化章节数据
            for section in sections:
                print(f"\n{'#' * int(section['level'][1:])} {section['title']}")
                for content in section['content']:
                    if content['type'] == 'paragraph':
                        print(content['text'])
                    elif content['type'] == 'list':
                        print("列表内容：")
                        for item in content['items']:
                            print(f" - {item}")
                    elif content['type'] == 'members':
                        print("成员信息：")
                        for member in content['data']:
                            print(f"姓名: {member['姓名']} - 角色: {member['角色']}")
                    elif content['type'] == 'roles':
                        print("角色形象：")
                        for role in content['data']:
                            print(f"角色名: {role['角色名']} - 图片: {role['图片']}")

            return {'title': title, 'sections': sections}
        
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"爬取失败：{str(e)}")
        return None


if __name__ == "__main__":
    data = enhanced_crawler()
    
    # 保存到 JSON 文件
    with open('mygo_sections.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ 结果已保存到 mygo_sections.json")
