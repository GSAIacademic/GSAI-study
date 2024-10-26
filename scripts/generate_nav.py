import os
import yaml
from pathlib import Path
from typing import Union, Dict, List

def get_nav_item(path: Path, root: Path) -> Union[Dict, str]:
    """递归生成导航项"""
    if path.is_file():
        # 如果是文件，返回文件名和相对路径
        if path.name == 'index.md':
            return str(path.relative_to(root)).replace('\\', '/')
        return {path.stem: str(path.relative_to(root)).replace('\\', '/')}
    
    # 如果是目录，递归处理其中的文件和子目录
    items = []
    
    # 处理 readme.md 文件（如果存在）
    readme_file = path / 'readme.md'
    if readme_file.exists():
        items.append({'概述': str(readme_file.relative_to(root)).replace('\\', '/')})
    
    # 按照固定顺序处理特定目录
    dir_order = ['ebook', 'exam', 'homework', '学习资源', '工具软件']
    
    # 处理特定目录
    for dir_name in dir_order:
        dir_path = path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            sub_items = []
            for item in sorted(dir_path.iterdir()):
                if item.is_file() and item.suffix == '.md':
                    sub_items.append({item.stem: str(item.relative_to(root)).replace('\\', '/')})
            if sub_items:
                items.append({dir_name: sub_items})
    
    # 处理其他文件
    for item in sorted(path.iterdir()):
        if (item.is_file() and item.suffix == '.md' 
            and item.name != 'readme.md' 
            and item.name != 'index.md'):
            items.append({item.stem: str(item.relative_to(root)).replace('\\', '/')})
    
    return {path.name: items} if path != root else items

def generate_nav() -> List[Dict]:
    docs_path = Path('docs')
    nav = [
        {'首页': 'index.md'},
        {'快速开始': 'start.md'}
    ]
    
    # 处理主要课程目录
    main_dirs = ['大一课程', '大二课程', '大三和大四课程']
    for dir_name in main_dirs:
        dir_path = docs_path / dir_name
        if dir_path.exists():
            courses = []
            for course_dir in sorted(dir_path.iterdir()):
                if course_dir.is_dir():
                    course_nav = get_nav_item(course_dir, docs_path)
                    if course_nav:
                        courses.append(course_nav)
            if courses:
                nav.append({dir_name: courses})
    
    return nav

def update_mkdocs_yml():
    # 读取现有配置
    with open('mkdocs.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 更新导航配置
    config['nav'] = generate_nav()
    
    # 写回配置文件
    with open('mkdocs.yml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

if __name__ == '__main__':
    update_mkdocs_yml()
