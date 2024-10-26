import os
import yaml
from pathlib import Path
from typing import Union, Dict, List

def get_nav_item(path: Path, root: Path) -> Union[Dict, str]:
    """递归生成导航项"""
    if path.is_file():
        # 如果是 PDF 文件，生成一个对应的 Markdown 文件来显示它
        if path.suffix == '.pdf':
            # 创建与 PDF 同名的目录来存放预览页面
            preview_dir = path.parent / path.stem
            preview_dir.mkdir(exist_ok=True)
            
            # 生成预览页面的内容
            pdf_content = f"""# {path.stem}

<div class="pdf-container">
    <object data="../{path.name}" type="application/pdf" width="100%" height="600px">
        <p>您的浏览器不支持 PDF 预览，请 <a href="../{path.name}">下载 PDF</a> 查看</p>
    </object>
</div>
"""
            # 在预览目录中创建 index.md
            preview_file = preview_dir / 'index.md'
            os.makedirs(preview_file.parent, exist_ok=True)
            with open(preview_file, 'w', encoding='utf-8') as f:
                f.write(pdf_content)
            
            # 返回预览页面的路径
            return {path.stem: str(preview_dir.relative_to(root) / 'index.md').replace('\\', '/')}
        
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
            # 处理所有文件，包括 PDF
            for item in sorted(dir_path.iterdir()):
                if item.is_file() and (item.suffix == '.md' or item.suffix == '.pdf'):
                    sub_items.append({item.stem: str(item.relative_to(root)).replace('\\', '/')})
            if sub_items:
                items.append({dir_name: sub_items})
    
    # 处理其他文件
    for item in sorted(path.iterdir()):
        if (item.is_file() and 
            (item.suffix == '.md' or item.suffix == '.pdf') and 
            item.name.lower() != 'readme.md' and 
            item.name != 'index.md'):
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
