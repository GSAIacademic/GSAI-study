import os
import yaml
from pathlib import Path

def get_nav_item(path: Path, root: Path) -> dict:
    """递归生成导航项"""
    if path.is_file():
        # 如果是文件，返回文件名和相对路径
        if path.name == 'index.md':
            return str(path.relative_to(root)).replace('\\', '/')
        return {path.stem: str(path.relative_to(root)).replace('\\', '/')}
    
    # 如果是目录，递归处理其中的文件和子目录
    items = []
    # 优先处理 index.md
    index_file = path / 'index.md'
    if index_file.exists():
        items.append(get_nav_item(index_file, root))
    
    # 处理其他文件和目录
    for item in sorted(path.iterdir()):
        if item.name != 'index.md' and not item.name.startswith('.'):
            if item.is_file() and item.suffix == '.md':
                items.append(get_nav_item(item, root))
            elif item.is_dir():
                subitems = get_nav_item(item, root)
                if subitems:  # 只有当子目录非空时才添加
                    items.append({item.name: subitems})
    
    return items if path == root else {path.name: items}

def generate_nav():
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
            nav_item = get_nav_item(dir_path, docs_path)
            if nav_item:
                nav.append(nav_item)
    
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
