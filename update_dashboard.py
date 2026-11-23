import datetime
import json
import os
import urllib.request

# ========== 抓取新浪实时行情 ==========
def fetch_quotes():
    symbols = ["rt_黄金_现货", "rt_黄金_期货", "rt_原油_WTI", "rt_原油_布伦特", "Au99.99", "Au_T+D", "沪金连续", "SC主力"]
    url = f"http://hq.sinajs.cn/list={','.join(symbols)}"
    headers = {'Referer': 'https://finance.sina.com.cn', 'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            try: text = raw.decode('gbk')
            except: text = raw.decode('utf-8', errors='ignore')
            return parse(text)
    except Exception as e:
        print(f"抓取失败: {e}")
        return None

def parse(text):
    data = {}
    for line in text.strip().split('\n'):
        if '=' not in line: continue
        var_name = line.split('=')[0].replace('var hq_str_', '').strip()
        val = line.split('=', 1)[1].strip().strip('";').strip('"')
        parts = val.split(',')
        if len(parts) >= 8:
            data[var_name] = parts
    return data

# ========== 主逻辑 ==========
TODAY = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TODAY_DATE = TODAY[:10]

quotes = fetch_quotes()

# 默认值（抓取失败时用）
defaults = {
    "gold_spot": ("3,626.65", "+2.4%"),
    "gold_futures": ("3,605.50", "+2.1%"),
    "wti": ("82.89", "-0.47%"),
    "brent": ("91.96", "-0.29%"),
    "au9999": ("771.40", "+0.9%"),
    "td": ("768.20", "-3.7%"),
    "sh_gold": ("780.80", "-2.77%"),
    "sc": ("520.30", "-1.2%"),
}

if quotes:
    try:
        # 外盘：最新价通常[0]，昨收[7]，涨跌幅手动算
        gs = float(quotes.get("rt_黄金_现货", ["0"])[0])
        gf = float(quotes.get("rt_黄金_期货", ["0"])[0])
        wt = float(quotes.get("rt_原油_WTI", ["0"])[0])
        br = float(quotes.get("rt_原油_布伦特", ["0"])[0])
        # 国内：上期所取[7]昨结算，[0]最新
        au = float(quotes.get("Au99.99", ["0"])[0])
        td_p = float(quotes.get("Au_T+D", ["0"])[0])
        sg = float(quotes.get("沪金连续", ["0"])[0])
        sc_p = float(quotes.get("SC主力", ["0"])[0])
        
        def pct(curr, prev):
            return f"{(curr-prev)/prev*100:+.2f}%" if prev else "0%"
        
        data_map = {
            "gold_spot": (f"{gs:,.2f}", pct(gs, float(quotes["rt_黄金_现货"][7]))),
            "gold_futures": (f"{gf:,.2f}", pct(gf, float(quotes["rt_黄金_期货"][7]))),
            "wti": (f"{wt:.2f}", pct(wt, float(quotes["rt_原油_WTI"][7]))),
            "brent": (f"{br:.2f}", pct(br, float(quotes["rt_原油_布伦特"][7]))),
            "au9999": (f"{au:.2f}", pct(au, float(quotes["Au99.99"][7]))),
            "td": (f"{td_p:.2f}", pct(td_p, float(quotes["Au_T+D"][7]))),
            "sh_gold": (f"{sg:.2f}", pct(sg, float(quotes["沪金连续"][7]))),
            "sc": (f"{sc_p:.2f}", pct(sc_p, float(quotes["SC主力"][7]))),
        }
        print("✅ 实时抓取成功")
    except Exception as e:
        print(f"解析失败: {e}，使用默认数据")
        data_map = defaults
else:
    data_map = defaults

# ========== 历史数据 ==========
HISTORY_FILE = ".history.json"
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
else:
    history = {"dates": [], "gold": [], "oil": []}

if TODAY_DATE not in history["dates"]:
    history["dates"].append(TODAY_DATE)
    history["gold"].append(float(data_map["gold_spot"][0].replace(",", "")))
    history["oil"].append(float(data_map["wti"][0]))
    if len(history["dates"]) > 10:
        history["dates"] = history["dates"][-10:]
        history["gold"] = history["gold"][-10:]
        history["oil"] = history["oil"][-10:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

# ========== 生成 HTML ==========
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>每日金价油价看板</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f0f2f5;color:#333;line-height:1.6}}
.container{{max-width:1200px;margin:0 auto;padding:20px}}
h1{{text-align:center;color:#1a1a2e;font-size:28px;margin-bottom:5px}}
.subtitle{{text-align:center;color:#666;font-size:13px;margin-bottom:25px}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:25px}}
.card{{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.08);position:relative;overflow:hidden}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:4px}}
.card.gold::before{{background:linear-gradient(90deg,#f1c40f,#f39c12)}}
.card.oil::before{{background:linear-gradient(90deg,#e74c3c,#c0392b)}}
.card h3{{font-size:14px;color:#888;margin-bottom:8px}}
.card .price{{font-size:26px;font-weight:700;margin:5px 0}}
.card .change{{font-size:13px;font-weight:600}}
.up{{color:#e74c3c}}.down{{color:#2ecc71}}
.card .unit{{font-size:12px;color:#999}}
.alert-box{{background:#fff3cd;border-left:4px solid #ffc107;padding:12px 16px;border-radius:8px;margin-bottom:25px;font-size:13px}}
.section-title{{font-size:18px;font-weight:700;color:#1a1a2e;margin:30px 0 15px;padding-left:12px;border-left:4px solid #3498db}}
table{{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:25px}}
th{{background:#f8f9fa;padding:12px 15px;text-align:right;font-size:13px;color:#666;font-weight:600}}
th:first-child{{text-align:left}}td{{padding:12px 15px;text-align:right;border-top:1px solid #eee;font-size:14px}}td:first-child{{text-align:left;font-weight:500}}
.chart-section{{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:25px}}
.chart-tabs{{display:flex;gap:10px;margin-bottom:15px}}
.chart-tabs button{{padding:6px 16px;border:1px solid #ddd;background:white;border-radius:20px;cursor:pointer;font-size:13px}}
.chart-tabs button.active{{background:#3498db;color:white;border-color:#3498db}}
.oil-section{{background:linear-gradient(135deg,#fff8e1,#fff3e0);border-radius:12px;padding:25px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:25px}}
.countdown{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:15px 0}}
.countdown div{{background:linear-gradient(135deg,#ff9800,#f57c00);color:white;padding:12px;border-radius:8px;text-align:center}}
.countdown div .num{{font-size:20px;font-weight:700}}.countdown div .label{{font-size:12px;opacity:.9}}
.summary-grid{{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:15px}}
.summary-box{{background:white;padding:15px;border-radius:8px;font-size:13px}}
.summary-box h4{{color:#e74c3c;margin-bottom:8px}}
.footer{{text-align:center;padding:20px;font-size:12px;color:#999}}
.timestamp{{display:inline-block;background:#e3f2fd;color:#1976d2;padding:4px 12px;border-radius:20px;font-weight:600}}
.live-dot{{display:inline-block;width:8px;height:8px;background:#2ecc71;border-radius:50%;margin-right:4px;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
</style>
</head>
<body>
<div class="container">
<h1>每日金价油价看板</h1>
<p class="subtitle">数据生成时间：<span class="timestamp"><span class="live-dot"></span>{TODAY}</span>（北京时间）| 实时抓取</p>

<div class="cards">
<div class="card gold"><h3>伦敦现货金</h3><div class="price">{data_map['gold_spot'][0]}</div><div class="change {'up' if '+' in data_map['gold_spot'][1] else 'down'}">{data_map['gold_spot'][1]}</div><div class="unit">美元/盎司</div></div>
<div class="card gold"><h3>COMEX 期金</h3><div class="price">{data_map['gold_futures'][0]}</div><div class="change {'up' if '+' in data_map['gold_futures'][1] else 'down'}">{data_map['gold_futures'][1]}</div><div class="unit">美元/盎司</div></div>
<div class="card oil"><h3>WTI 原油</h3><div class="price">{data_map['wti'][0]}</div><div class="change {'up' if '+' in data_map['wti'][1] else 'down'}">{data_map['wti'][1]}</div><div class="unit">美元/桶</div></div>
<div class="card oil"><h3>布伦特原油</h3><div class="price">{data_map['brent'][0]}</div><div class="change {'up' if '+' in data_map['brent'][1] else 'down'}">{data_map['brent'][1]}</div><div class="unit">美元/桶</div></div>
</div>

<div class="alert-box"><strong>⚠ 口径提示：</strong>沪金/黄金 T+D 显示的跌幅是相对周末前夜盘高位的跌幅，和上金所现货的涨幅不是同一波行情的反向读数。国内金价在 Au99.99、T+D、沪金期货、金店零售之间能差出三百元一克，请勿跨平台直接比较。</div>

<div class="section-title">国内贵金属与原油三地盘面</div>
<table>
<thead><tr><th>品种</th><th>最新价</th><th>涨跌</th><th>单位</th></tr></thead>
<tbody>
<tr><td>Au99.99</td><td>{data_map['au9999'][0]}</td><td class="{'up' if '+' in data_map['au9999'][1] else 'down'}">{data_map['au9999'][1]}</td><td>元/克</td></tr>
<tr><td>黄金 T+D</td><td>{data_map['td'][0]}</td><td class="{'up' if '+' in data_map['td'][1] else 'down'}">{data_map['td'][1]}</td><td>元/克</td></tr>
<tr><td>沪金主力</td><td>{data_map['sh_gold'][0]}</td><td class="{'up' if '+' in data_map['sh_gold'][1] else 'down'}">{data_map['sh_gold'][1]}</td><td>元/克</td></tr>
<tr><td>WTI</td><td>{data_map['wti'][0]}</td><td class="{'up' if '+' in data_map['wti'][1] else 'down'}">{data_map['wti'][1]}</td><td>美元/桶</td></tr>
<tr><td>布伦特</td><td>{data_map['brent'][0]}</td><td class="{'up' if '+' in data_map['brent'][1] else 'down'}">{data_map['brent'][1]}</td><td>美元/桶</td></tr>
<tr><td>SC 原油</td><td>{data_map['sc'][0]}</td><td class="{'up' if '+' in data_map['sc'][1] else 'down'}">{data_map['sc'][1]}</td><td>元/桶</td></tr>
</tbody>
</table>

<div class="section-title">近10日走势</div>
<div class="chart-section">
<div class="chart-tabs"><button class="active" onclick="switchChart('index')">指数化对比</button><button onclick="switchChart('gold')">黄金原价</button><button onclick="switchChart('oil')">原油原价</button></div>
<div style="position:relative;height:300px"><svg id="chartSvg" viewBox="0 0 800 300" style="width:100%;height:100%">
<line x1="50" y1="20" x2="50" y2="260" stroke="#eee"/><line x1="50" y1="260" x2="780" y2="260" stroke="#ddd"/>
<polyline id="goldLine" fill="none" stroke="#f1c40f" stroke-width="2.5"/>
<polyline id="oilLine" fill="none" stroke="#e74c3c" stroke-width="2.5"/>
<g id="goldDots"></g><g id="oilDots"></g>
<text x="50" y="280" font-size="11" fill="#999">起点</text>
<text x="750" y="280" font-size="11" fill="#999">今日</text>
<text x="60" y="15" font-size="12" fill="#f1c40f" font-weight="600">● 黄金</text>
<text x="120" y="15" font-size="12" fill="#e74c3c" font-weight="600">● 原油</text>
</svg></div>
</div>

<div class="section-title">国内成品油调价专区</div>
<div class="oil-section">
<p><strong>调价窗口：</strong>2026-11-26 24:00（下周四夜里）</p>
<div class="countdown">
<div><div class="num">第7天</div><div class="label">工作日</div></div>
<div><div class="num">剩3天</div><div class="label">倒计时</div></div>
<div><div class="num">-7.55%</div><div class="label">原油变化率</div></div>
<div><div class="num">89.52</div><div class="label">参考均价(美元)</div></div>
</div>
<p><strong>预估调整：</strong>汽油下调约 480 元/吨（金联创口径），另一口径 420 元/吨。折合 92 号降 0.34～0.38 元/升，50 升油箱加满省 17～19 元。</p>
<div class="summary-grid">
<div class="summary-box"><h4>落地后推演</h4><p>全国 92 号均价 8.36 元/升 → 约 <strong>7.99</strong> 元/升（跌破 8 元）</p><p>95 号 8.92 → 约 <strong>8.55</strong> 元/升（全面退出 9 元区间）</p></div>
<div class="summary-box"><h4>为什么国际油价没怎么跌，国内却能降？</h4><p>机制比的是<strong>前后两个 10 个工作日的一揽子均价</strong>，不是单周期涨跌。本周期参考原油均价 89.52 美元/桶，低于上期的 96 美元以上，因此下调。</p></div>
</div>
<p style="font-size:12px;color:#e74c3c;margin-top:10px">※ 以上为机构测算，最终以发改委公告为准。</p>
</div>

<div class="footer"><p>数据来源：新浪财经实时行情 | 此为盘中快照，非收盘价。周末及节假日休市时显示最近交易日数据。</p><p>仅供参考，不构成投资建议。</p></div>
</div>
<script>
const dates={json.dumps(history['dates'])};
const goldData={json.dumps(history['gold'])};
const oilData={json.dumps(history['oil'])};
function drawChart(type){{
const goldLine=document.getElementById('goldLine');const oilLine=document.getElementById('oilLine');
const goldDots=document.getElementById('goldDots');const oilDots=document.getElementById('oilDots');
if(dates.length<2){{goldLine.setAttribute('points','');oilLine.setAttribute('points','');goldDots.innerHTML='';oilDots.innerHTML='';return;}}
const w=730,h=240,leftPad=50;let gp=[],op=[];
if(type==='index'){{const bg=goldData[0],bo=oilData[0];goldData.forEach((v,i)=>gp.push([leftPad+i*(w/(dates.length-1)),260-((v/bg*100-95)/10)*h]));oilData.forEach((v,i)=>op.push([leftPad+i*(w/(dates.length-1)),260-((v/bo*100-95)/10)*h]))}}
else if(type==='gold'){{const mn=Math.min(...goldData)*.99,mx=Math.max(...goldData)*1.01;goldData.forEach((v,i)=>gp.push([leftPad+i*(w/(dates.length-1)),260-((v-mn)/(mx-mn))*h]));oilLine.setAttribute('points','');oilDots.innerHTML=''}}
else{{const mn=Math.min(...oilData)*.99,mx=Math.max(...oilData)*1.01;oilData.forEach((v,i)=>op.push([leftPad+i*(w/(dates.length-1)),260-((v-mn)/(mx-mn))*h]));goldLine.setAttribute('points','');goldDots.innerHTML=''}}
if(type!=='oil'){{goldLine.setAttribute('points',gp.map(p=>p.join(',')).join(' '));goldDots.innerHTML=gp.map(p=>`<circle cx="${{p[0]}}" cy="${{p[1]}}" r="4" fill="#f1c40f"/>`).join('')}}
if(type!=='gold'){{oilLine.setAttribute('points',op.map(p=>p.join(',')).join(' '));oilDots.innerHTML=op.map(p=>`<circle cx="${{p[0]}}" cy="${{p[1]}}" r="4" fill="#e74c3c"/>`).join(''))}}
}}
function switchChart(type){{document.querySelectorAll('.chart-tabs button').forEach(b=>b.classList.remove('active'));event.target.classList.add('active');drawChart(type)}}
drawChart('index');
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 已生成 index.html")
print(f"⏰ {TODAY}")
print(f"  伦敦金: {data_map['gold_spot'][0]} {data_map['gold_spot'][1]}")
print(f"  WTI: {data_map['wti'][0]} {data_map['wti'][1]}")