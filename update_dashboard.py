import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_data():
    # 模拟获取数据（后续可替换为真实接口）
    gold_price = "2,650.00"
    oil_price = "75.20"
    return gold_price, oil_price

def generate_html(gold, oil):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_str = datetime.now().strftime("%Y年%m月%d日 %A")
    
    # 模拟涨跌状态
    gold_trend = "↑ 涨 0.5%"
    oil_trend = "↓ 跌 0.2%"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金价油价自动看板</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f8; padding: 20px; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; font-size: 28px; }}
        .header p {{ color: #7f8c8d; font-size: 14px; }}
        .card {{ background: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }}
        .card-info h2 {{ margin: 0 0 10px 0; font-size: 18px; color: #7f8c8d; }}
        .card-info .price {{ font-size: 32px; font-weight: bold; color: #f39c12; margin-bottom: 5px; }}
        .card-info .trend {{ font-size: 14px; color: #27ae60; }}
        .card-icon {{ font-size: 40px; }}
        .footer {{ text-align: center; color: #95a5a6; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 每日金价油价看板</h1>
            <p>{date_str}</p>
        </div>
        
        <div class="card">
            <div class="card-info">
                <h2>伦敦金 (XAU/USD)</h2>
                <div class="price">{gold}</div>
                <div class="trend">{gold_trend}</div>
            </div>
            <div class="card-icon">🥇</div>
        </div>
        
        <div class="card">
            <div class="card-info">
                <h2>WTI原油 (USD/bbl)</h2>
                <div class="price">{oil}</div>
                <div class="trend">{oil_trend}</div>
            </div>
            <div class="card-icon">🛢️</div>
        </div>
        
        <div class="footer">
            最后更新时间: {today} | 自动抓取自 GitHub Actions
        </div>
    </div>
</body>
</html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    g, o = fetch_data()
    generate_html(g, o)
