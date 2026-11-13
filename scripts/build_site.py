from pathlib import Path
import html
import re
import markdown

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "profile.md").read_text(encoding="utf-8")
source = re.sub(r"^#\s+[^\n]+\n", "", source, count=1)

md = markdown.Markdown(
    extensions=["tables", "toc", "fenced_code", "sane_lists"],
    extension_configs={"toc": {"permalink": False}},
    output_format="html5",
)
article = md.convert(source)

# Make source URLs useful without changing their visible text.
def link_code(match):
    url = html.unescape(match.group(1))
    return f'<a class="source-link" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(url)}</a>'

article = re.sub(r"<code>(https?://[^<]+)</code>", link_code, article)

# Explicit column widths keep long Chinese cells readable.
def table_markup(match):
    table = match.group(0)
    header = re.search(r"<tr>(.*?)</tr>", table, flags=re.S)
    count = len(re.findall(r"<th\b", header.group(1))) if header else 0
    widths = {
        2: [24, 76],
        3: [18, 42, 40],
        4: [14, 22, 30, 34],
    }.get(count, [round(100 / count, 2)] * count if count else [])
    colgroup = ""
    if widths:
        colgroup = "<colgroup>" + "".join(f'<col style="width:{w}%">' for w in widths) + "</colgroup>"
    table = table.replace("<table>", '<table class="evidence-table">' + colgroup, 1)
    return '<div class="table-wrap">' + table + "</div>"

article = re.sub(r"<table>.*?</table>", table_markup, article, flags=re.S)

nav_items = []
for token in md.toc_tokens:
    label = re.sub(r"^[一二三四五六七八九十]+、", "", token["name"])
    nav_items.append(f'<a href="#{html.escape(token["id"], quote=True)}">{html.escape(label)}</a>')
nav = "\n".join(nav_items)

page = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="王佳琦（竹心 / YGtemple）的公开个人主页：项目作品、程序设计竞赛、AI 应用、AIGC 创作与校园实践。">
<title>王佳琦 · 竹心｜项目、荣誉与个人主页</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%232563eb'/%3E%3Ctext x='32' y='43' text-anchor='middle' font-size='34' font-family='sans-serif' fill='white'%3E%E7%AB%B9%3C/text%3E%3C/svg%3E">
<style>
:root{--bg:#f6f7f9;--paper:#fff;--ink:#1f2937;--muted:#5f6b7a;--line:#e2e6eb;--blue:#2563eb;--blue-soft:#eaf1ff;--green:#18794e;--green-soft:#e9f6ef;--amber:#925d06;--amber-soft:#fff5dc;--mono:Consolas,'Courier New',monospace;--sans:'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.85;-webkit-font-smoothing:antialiased}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}a:focus-visible,button:focus-visible{outline:3px solid #8db4ff;outline-offset:3px}button{font:inherit}.shell{max-width:1240px;margin:0 auto;padding:0 18px}.hero{margin:18px 0 28px;padding:34px 24px;background:var(--paper);border:1px solid var(--line);border-radius:18px;position:relative;overflow:hidden}.hero::after{content:'YG';position:absolute;right:18px;bottom:-46px;font:900 150px/1 var(--mono);color:#f0f4fa;pointer-events:none}.eyebrow{display:inline-flex;align-items:center;gap:8px;font:600 12px/1.4 var(--mono);color:var(--blue);letter-spacing:.06em}.eyebrow::before{content:'';width:22px;height:2px;background:var(--blue)}h1{position:relative;margin:14px 0 10px;font-size:36px;line-height:1.2;letter-spacing:-.03em;z-index:1}h1 span{color:var(--blue)}.hero-lead{position:relative;max-width:760px;margin:0;color:var(--muted);font-size:16px;z-index:1}.hero-tags{position:relative;display:flex;flex-wrap:wrap;gap:8px;margin-top:20px;z-index:1}.tag{display:inline-block;padding:4px 10px;border:1px solid #cbdcff;border-radius:999px;background:var(--blue-soft);color:#174da9;font-size:12px;font-weight:600}.hero-actions{position:relative;display:flex;flex-wrap:wrap;gap:10px;margin-top:22px;z-index:1}.button{display:inline-flex;align-items:center;min-height:44px;padding:9px 15px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:var(--ink);font-weight:600}.button.primary{background:var(--blue);border-color:var(--blue);color:#fff}.button:hover{text-decoration:none;filter:brightness(.97)}.stats{position:relative;display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:26px;z-index:1}.stat{padding:13px 14px;border-top:2px solid var(--line);background:#fafbfc}.stat b{display:block;font:700 23px/1.2 var(--mono);color:var(--ink)}.stat span{font-size:12px;color:var(--muted)}.notice{padding:13px 16px;margin:0 0 24px;border-left:3px solid var(--blue);background:var(--blue-soft);color:#29466f;font-size:13px}.layout{display:block}.sidebar{display:none}.content{min-width:0}.report{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:22px 18px}.report h2{margin:42px 0 16px;padding-top:14px;border-top:1px solid var(--line);font-size:24px;line-height:1.35;letter-spacing:-.02em}.report h2:first-child{margin-top:0;padding-top:0;border-top:0}.report h3{margin:28px 0 12px;font-size:18px;line-height:1.45}.report p{margin:10px 0}.report ul,.report ol{padding-left:22px}.report li{margin:7px 0}.report strong{font-weight:700}.report code{padding:2px 5px;border-radius:4px;background:#f0f2f5;color:#334155;font:13px/1.5 var(--mono);word-break:break-word}.report blockquote{margin:18px 0;padding:12px 16px;border-left:3px solid #9bb9ef;background:#f7faff;color:#4c5f7a}.report blockquote p{margin:0}.source-link{word-break:break-all;font:12px/1.6 var(--mono)}.table-wrap{margin:16px 0 24px;overflow-x:auto;border:1px solid var(--line);border-radius:10px}.evidence-table{width:100%;min-width:680px;border-collapse:collapse;table-layout:fixed;font-size:13px;line-height:1.7}.evidence-table th{padding:11px 12px;background:#f0f3f7;color:#364152;text-align:left;font-weight:700;vertical-align:middle}.evidence-table td{padding:11px 12px;border-top:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}.evidence-table tr:last-child td{border-bottom:0}.evidence-table td:first-child{font-weight:600;color:#354155}.footer{padding:30px 0 44px;color:var(--muted);font-size:12px;text-align:center}.back-top{position:fixed;right:18px;bottom:18px;width:44px;height:44px;border:1px solid var(--line);border-radius:12px;background:var(--paper);color:var(--blue);box-shadow:0 4px 16px #1f293714;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .2s}.back-top.show{opacity:1;pointer-events:auto}.legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.legend span{padding:3px 9px;border-radius:5px;font-size:12px;font-weight:600}.legend .proved{background:var(--green-soft);color:var(--green)}.legend .self{background:var(--blue-soft);color:#2454a6}.legend .todo{background:var(--amber-soft);color:var(--amber)}
@media(min-width:640px){.shell{padding:0 26px}.hero{padding:44px 40px}.hero h1{font-size:48px}.stats{grid-template-columns:repeat(4,1fr)}.report{padding:34px 38px}}
@media(min-width:1020px){.layout{display:grid;grid-template-columns:210px minmax(0,1fr);gap:26px;align-items:start}.sidebar{display:block;position:sticky;top:22px;max-height:calc(100vh - 44px);overflow:auto;padding:16px 12px;background:var(--paper);border:1px solid var(--line);border-radius:14px}.sidebar-title{padding:0 10px 10px;color:var(--muted);font:600 11px/1.5 var(--mono);letter-spacing:.08em}.sidebar a{display:block;padding:6px 10px;border-radius:7px;color:var(--muted);font-size:12px;line-height:1.5}.sidebar a:hover,.sidebar a.active{background:var(--blue-soft);color:var(--blue);text-decoration:none}.report{padding:40px 46px}}
@media print{body{background:#fff;font-size:11pt}.shell{max-width:none;padding:0}.hero{margin:0;padding:20px 0;border:0;border-bottom:2px solid #222;border-radius:0}.hero::after,.sidebar,.back-top,.hero-actions{display:none}.layout{display:block}.report{padding:0;border:0}.report h2{break-after:avoid}.table-wrap{overflow:visible}.evidence-table{min-width:0;font-size:9pt}.notice{border:1px solid #bbb;background:#fff}.footer{padding:20px 0}.source-link{word-break:break-all}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
</style>
</head>
<body>
<div class="shell">
<header class="hero" id="top">
  <div class="eyebrow">PORTFOLIO · 2026</div>
  <h1>王佳琦 <span>/ 竹心</span></h1>
  <p class="hero-lead">郑州升达经贸管理学院外国语学院翻译专业 2024 级本科生。以翻译专业背景连接程序设计、AI 应用、AIGC 内容生产与开源工具，持续把想法做成可展示、可复用的作品。</p>
  <div class="hero-tags"><span class="tag">C/C++ 与算法</span><span class="tag">Qt 与前端</span><span class="tag">AI 智能体</span><span class="tag">AIGC 影像</span><span class="tag">开源 Skill</span></div>
  <div class="hero-actions"><a class="button primary" href="https://github.com/YGtemple" target="_blank" rel="noopener noreferrer">GitHub · YGtemple</a><a class="button" href="mailto:1744059451@qq.com">1744059451@qq.com</a><a class="button" href="tel:15314662965">电话 / 微信 · 15314662965</a></div>
  <div class="stats"><div class="stat"><b>52</b><span>GitHub 公开仓库</span></div><div class="stat"><b>15</b><span>荣誉与实践记录</span></div><div class="stat"><b>16</b><span>项目与作品方向</span></div><div class="stat"><b>2024</b><span>翻译本科入学年份</span></div></div>
</header>
<div class="notice">翻译专业 × 程序设计 × AI 应用 × AIGC 创作。欢迎浏览我的项目与作品，也欢迎通过邮件、电话或微信交流合作。</div>
<div class="layout">
<aside class="sidebar" aria-label="主页目录"><div class="sidebar-title">主页目录</div>__NAV__</aside>
<main class="content"><article class="report">__ARTICLE__</article></main>
</div>
<footer class="footer">王佳琦 · 竹心 · YGtemple<br>保持好奇，持续创作，把想法变成作品。</footer>
</div>
<button class="back-top" id="backTop" aria-label="返回顶部" title="返回顶部">↑</button>
<script>
const backTop=document.getElementById('backTop');
const updateButton=()=>backTop.classList.toggle('show',window.scrollY>600);
window.addEventListener('scroll',updateButton,{passive:true});updateButton();
backTop.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
const links=[...document.querySelectorAll('.sidebar a')];
const sections=links.map(a=>document.getElementById(decodeURIComponent(a.hash.slice(1)))).filter(Boolean);
if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){links.forEach(a=>a.classList.toggle('active',a.hash==='#'+entry.target.id));}})},{rootMargin:'-15% 0px -72% 0px'});sections.forEach(s=>observer.observe(s));}
</script>
</body>
</html>
'''
page = page.replace("__NAV__", nav).replace("__ARTICLE__", article)
(ROOT / "index.html").write_text(page, encoding="utf-8", newline="\n")
print(f"Generated {ROOT / 'index.html'} ({len(page)} characters)")
