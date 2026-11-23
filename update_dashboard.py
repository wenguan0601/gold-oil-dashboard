import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_data():
    # 模拟数据，后续可替换真实接口
    return "2,650.00", "75.20"

def generate_html(gold, oil):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>金价油价自动看板</title>
    <style>
        body {{ font-family: sans-serif; background: #f4f6f8; padding: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        .price {{ font-size: 24px; color: #f1c40f; font-weight: bold; }}
        .time {{ color: #888; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>📊 每日金价油价看板</h1>
        <p>伦敦金: <span class="price">{gold}</span> USD/oz</p>
        <p>WTI原油: <span class="price">{oil}</span> USD/bbl</p>
        <p class="time">最后更新: {today}</p>
    </div>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    g, o = fetch_data()
    generate_html(g, o)
