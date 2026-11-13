from pathlib import Path
from html import escape
import re
import markdown
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "profile.md").read_text(encoding="utf-8")
text = re.sub(r"^#\s+[^\n]+\n", "", text, count=1)
soup = BeautifulSoup(markdown.markdown(text, extensions=["tables", "sane_lists"]), "html.parser")


def heading(name, level="h2"):
    return soup.find(level, string=lambda value: value and value.strip() == name)


def siblings_until(node, levels):
    result = []
    for item in node.next_siblings:
        if isinstance(item, Tag) and item.name in levels:
            break
        if isinstance(item, Tag):
            result.append(item)
    return result


def clean_html(node):
    return str(node).replace("<ul>", '<ul class="inline-list">')


def link_html(node, css="text-link"):
    return f'<a class="{css}" href="{escape(node.get("href", ""), quote=True)}" target="_blank" rel="noopener noreferrer">{escape(node.get_text(" ", strip=True))}</a>'


# About
about_nodes = siblings_until(heading("关于我"), {"h2"})
about_html = "".join(clean_html(node) for node in about_nodes if node.name in {"p", "ul"})

# Honors: convert report tables into visitor-friendly cards.
honor_cards = []
honor_root = heading("荣誉与奖项")
for group in siblings_until(honor_root, {"h2"}):
    if group.name != "h3":
        continue
    category = group.get_text(strip=True)
    for node in siblings_until(group, {"h2", "h3"}):
        if node.name == "table":
            for row in node.select("tbody tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
                if len(cells) >= 3:
                    honor_cards.append(
                        f'<article class="honor-card"><div class="honor-meta"><time>{escape(cells[0])}</time><span>{escape(category)}</span></div><h3>{escape(cells[1])}</h3><p>{escape(cells[2])}</p></article>'
                    )
        elif node.name == "ul":
            for item in node.find_all("li", recursive=False):
                honor_cards.append(
                    f'<article class="honor-card"><div class="honor-meta"><span>{escape(category)}</span></div><p>{escape(item.get_text(" ", strip=True))}</p></article>'
                )

# Projects: preserve the writing in profile.md, add category filtering and real covers.
project_settings = {
    "融研智笔·英语写作系列智能体": ("ai", "", ""),
    "卫华短视频流水线": ("ai aigc", "assets/weihua.png", "卫华短视频流水线工作流界面"),
    "智言 TEDify": ("ai", "assets/zhiyan-logo.jpg", "智言 TEDify 品牌标志"),
    "智序·AI 日程助手": ("tools", "", ""),
    "长隆灵犀": ("ai", "assets/changlong.png", "长隆灵犀智慧伴游首页"),
    "《醒春》AI 短片": ("aigc", "", ""),
    "单词精灵闯关": ("game", "", ""),
    "赛脉·升达赛事汇": ("tools", "assets/saimai-dashboard.png", "升达赛事汇系统首页"),
    "竹心一言与长文写作工作流": ("tools", "", ""),
    "AI 影视与开发工具": ("tools aigc", "", ""),
}
project_cards = []
project_root = heading("代表项目")
for project in siblings_until(project_root, {"h2"}):
    if project.name != "h3":
        continue
    title = project.get_text(" ", strip=True)
    nodes = siblings_until(project, {"h2", "h3"})
    paragraphs = [node for node in nodes if node.name == "p"]
    lists = [node for node in nodes if node.name == "ul"]
    description = "".join(clean_html(node) for node in (paragraphs[:1] or lists[:1]))
    extra_list = "" if not paragraphs or not lists else clean_html(lists[0])
    # Inline links become dedicated action buttons below; avoid showing each URL twice.
    description = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', description, flags=re.S)
    extra_list = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', extra_list, flags=re.S)
    links = []
    for node in nodes:
        for anchor in node.find_all("a", href=True):
            links.append(link_html(anchor, "project-link"))
    category, image, alt = project_settings.get(title, ("tools", "", ""))
    media = ""
    if image:
        contain = " contain" if "logo" in image else ""
        media = f'<div class="project-media{contain}"><img src="{image}" alt="{escape(alt, quote=True)}"></div>'
    link_label = f'<div class="project-links">{"".join(dict.fromkeys(links))}</div>' if links else ""
    project_cards.append(
        f'<article class="project-card" data-category="{category}">{media}<div class="project-body"><div class="project-top"><h3>{escape(title)}</h3><span>{category.split()[0].upper()}</span></div>{description}{extra_list}{link_label}</div></article>'
    )

# Lead with the most complete case study so the first large card has a real project cover.
project_cards.sort(key=lambda card: 0 if "卫华短视频流水线" in card else 1)

# A focused case study keeps the activity story without duplicating the full report.
weihua_nodes = siblings_until(heading("卫华黑客松经历"), {"h2"})
weihua_html = "".join(clean_html(node) for node in weihua_nodes if node.name in {"p", "ul"})

# Timeline
timeline_items = []
timeline_table = heading("学习与成长时间线").find_next("table")
for row in timeline_table.select("tbody tr"):
    cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
    if len(cells) >= 2:
        timeline_items.append(f'<div class="timeline-item"><time>{escape(cells[0])}</time><span class="timeline-dot" aria-hidden="true"></span><p>{escape(cells[1])}</p></div>')

# Skills
skill_cards = []
skills_root = heading("技术能力")
skills_table = skills_root.find_next("table")
for row in skills_table.select("tbody tr"):
    cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
    if len(cells) >= 2:
        skill_cards.append(f'<article class="skill-card"><h3>{escape(cells[0])}</h3><p>{escape(cells[1])}</p></article>')
skills_extra = "".join(clean_html(node) for node in siblings_until(skills_root, {"h2"}) if node.name == "p")

# Campus
campus_nodes = siblings_until(heading("校园与志愿服务"), {"h2"})
campus_html = "".join(clean_html(node) for node in campus_nodes if node.name in {"p", "ul"})

page = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="王佳琦（竹心 / YGtemple）的个人作品集：AI 应用、程序设计、AIGC 创作、竞赛荣誉与开源项目。">
<title>王佳琦 · 竹心｜个人作品集</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230f766e'/%3E%3Ctext x='32' y='43' text-anchor='middle' font-size='34' font-family='sans-serif' fill='white'%3E%E7%AB%B9%3C/text%3E%3C/svg%3E">
<style>
:root{--bg:#f3f6f4;--paper:#fff;--ink:#142524;--muted:#5c6c69;--line:#d9e3df;--teal:#0f766e;--teal-dark:#0a4f4b;--teal-soft:#e4f3ef;--gold:#b7791f;--gold-soft:#fff3d6;--sans:'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif;--serif:'STZhongsong','SimSun',serif;--mono:Consolas,'Courier New',monospace}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:82px}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.8;-webkit-font-smoothing:antialiased}a{color:inherit;text-decoration:none}img{display:block;max-width:100%}button{font:inherit}button,a{-webkit-tap-highlight-color:transparent}a:focus-visible,button:focus-visible{outline:3px solid #70c9bc;outline-offset:3px}.progress{position:fixed;inset:0 auto auto 0;width:0;height:3px;background:var(--teal);z-index:100}.container{width:min(1160px,calc(100% - 36px));margin:auto}.nav{position:sticky;top:0;z-index:50;background:#f3f6f4f2;border-bottom:1px solid #d9e3dfcc;backdrop-filter:blur(12px)}.nav-inner{height:66px;display:flex;align-items:center;justify-content:space-between}.brand{display:flex;align-items:center;gap:10px;font-weight:800}.brand-mark{display:grid;place-items:center;width:34px;height:34px;border-radius:9px;background:var(--teal);color:#fff;font-family:var(--serif);font-size:20px}.brand small{display:block;color:var(--muted);font:10px/1.2 var(--mono);letter-spacing:.08em}.nav-links{display:none}.menu-btn{width:44px;height:44px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:var(--ink);cursor:pointer}.menu-btn span{display:block;width:18px;height:2px;margin:4px auto;background:currentColor;transition:.2s}.menu-btn[aria-expanded=true] span:first-child{transform:translateY(3px) rotate(45deg)}.menu-btn[aria-expanded=true] span:last-child{transform:translateY(-3px) rotate(-45deg)}.mobile-menu{padding:0 0 14px}.mobile-menu[hidden]{display:none}.mobile-menu a{display:block;padding:10px 4px;border-top:1px solid var(--line);color:var(--muted)}.hero{padding:50px 0 34px}.hero-grid{display:grid;gap:32px}.kicker{display:flex;align-items:center;gap:10px;color:var(--teal);font:700 12px/1.4 var(--mono);letter-spacing:.08em}.kicker::before{content:'';width:28px;height:2px;background:var(--teal)}h1{margin:18px 0;font-family:var(--serif);font-size:42px;line-height:1.25;font-weight:700;letter-spacing:-.04em}.hero-copy{max-width:690px;color:var(--muted);font-size:16px}.hero-copy strong{color:var(--ink)}.hero-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:10px 18px;border:1px solid var(--line);border-radius:10px;background:var(--paper);font-weight:700;cursor:pointer}.btn.primary{background:var(--teal);border-color:var(--teal);color:#fff}.btn:hover{transform:translateY(-1px)}.profile-panel{position:relative;padding:28px;background:var(--teal-dark);color:#fff;border-radius:20px;overflow:hidden}.profile-panel::after{content:'竹';position:absolute;right:-6px;bottom:-72px;color:#ffffff0c;font:180px/1 var(--serif)}.profile-panel .label{color:#a9d8d0;font:700 11px/1.4 var(--mono);letter-spacing:.1em}.profile-panel h2{position:relative;margin:12px 0 20px;font-size:26px;line-height:1.4;z-index:1}.profile-panel dl{position:relative;margin:0;z-index:1}.profile-panel dt{margin-top:14px;color:#a9d8d0;font-size:12px}.profile-panel dd{margin:2px 0 0;font-weight:700}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:32px}.stat{padding:16px 8px;border-top:1px solid var(--line)}.stat b{display:block;color:var(--teal);font:700 27px/1.2 var(--mono)}.stat span{font-size:12px;color:var(--muted)}.section{padding:54px 0}.section-head{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:24px}.section-head h2{margin:0;font-size:28px;line-height:1.35;letter-spacing:-.03em}.section-head p{margin:6px 0 0;color:var(--muted)}.section-index{color:var(--teal);font:700 12px/1 var(--mono)}.about-grid{display:grid;gap:24px}.about-content{padding:26px;background:var(--paper);border:1px solid var(--line);border-radius:16px}.about-content p{margin:0 0 14px}.about-content ul,.inline-list{margin:12px 0;padding-left:20px}.about-content li,.inline-list li{margin:7px 0}.about-note{padding:24px;border-left:3px solid var(--gold);background:var(--gold-soft);color:#6a4b17}.about-note strong{display:block;margin-bottom:8px;font-size:18px}.filters{display:flex;gap:8px;overflow-x:auto;padding:0 0 14px;margin-bottom:16px;scrollbar-width:none}.filter{flex:0 0 auto;min-height:44px;padding:8px 15px;border:1px solid var(--line);border-radius:999px;background:var(--paper);color:var(--muted);cursor:pointer}.filter.active{background:var(--teal);border-color:var(--teal);color:#fff}.result-count{margin:0 0 18px;color:var(--muted);font-size:12px}.project-grid{display:grid;gap:20px}.project-card{min-width:0;background:var(--paper);border:1px solid var(--line);border-radius:18px;overflow:hidden}.project-card[hidden]{display:none}.project-media{aspect-ratio:16/10;background:#e9efec;border-bottom:1px solid var(--line);overflow:hidden}.project-media img{width:100%;height:100%;object-fit:cover;object-position:top}.project-media.contain{background:#fff}.project-media.contain img{object-fit:contain;padding:28px}.project-body{padding:22px}.project-top{display:flex;align-items:start;justify-content:space-between;gap:12px}.project-top h3{margin:0;font-size:20px;line-height:1.45}.project-top>span{flex:0 0 auto;padding-top:5px;color:var(--teal);font:700 10px/1 var(--mono);letter-spacing:.08em}.project-body p{color:var(--muted)}.project-body .inline-list{color:var(--muted);font-size:13px}.project-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}.project-link{display:inline-flex;align-items:center;min-height:40px;padding:7px 12px;border-radius:8px;background:var(--teal-soft);color:var(--teal-dark);font-size:12px;font-weight:700}.project-link:hover{background:var(--teal);color:#fff}.case-study{display:grid;margin-top:30px;background:var(--teal-dark);color:#fff;border-radius:20px;overflow:hidden}.case-study img{width:100%;height:100%;min-height:280px;object-fit:cover;object-position:top}.case-copy{padding:28px}.case-copy .section-index{color:#8fd4c8}.case-copy h3{margin:10px 0;font-size:26px}.case-copy p,.case-copy li{color:#d3e8e3}.case-copy a{color:#fff;text-decoration:underline;text-underline-offset:4px}.honor-grid{display:grid;gap:14px}.honor-card{padding:20px;background:var(--paper);border:1px solid var(--line);border-radius:14px}.honor-meta{display:flex;align-items:center;justify-content:space-between;gap:12px;color:var(--teal);font:700 11px/1.4 var(--mono)}.honor-meta span{color:var(--muted);font-family:var(--sans);font-weight:400}.honor-card h3{margin:12px 0 7px;font-size:16px;line-height:1.55}.honor-card p{margin:0;color:var(--muted)}.timeline{--axis:16px}.timeline-item{display:grid;grid-template-columns:74px 32px minmax(0,1fr);gap:0;min-height:72px}.timeline-item time{padding-top:1px;color:var(--teal);font:700 12px/1.8 var(--mono)}.timeline-item p{margin:0 0 24px;padding-left:14px}.timeline-dot{position:relative;justify-self:center;width:11px;height:11px;margin-top:7px;border:3px solid var(--bg);border-radius:50%;background:var(--teal);box-shadow:0 0 0 1px var(--teal);z-index:1}.timeline-item{position:relative}.timeline-item::before{content:'';position:absolute;left:90px;top:18px;bottom:0;width:1px;background:var(--line)}.timeline-item:last-child::before{display:none}.skill-grid{display:grid;gap:12px}.skill-card{padding:20px;border-top:2px solid var(--teal);background:var(--paper)}.skill-card h3{margin:0 0 8px;font-size:16px}.skill-card p{margin:0;color:var(--muted);font-size:13px}.skills-extra{margin-top:20px;color:var(--muted)}.campus{margin-top:24px;padding:24px;background:var(--paper);border:1px solid var(--line);border-radius:16px}.contact{padding:46px 0;background:var(--teal-dark);color:#fff}.contact-grid{display:grid;gap:24px}.contact h2{margin:0 0 10px;font-family:var(--serif);font-size:34px}.contact p{color:#c9e3dd}.contact-list{display:grid;gap:10px}.contact-row{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;padding:13px 0;border-bottom:1px solid #ffffff24}.contact-row span{color:#a9d8d0;font-size:12px}.contact-row strong{font-size:15px;word-break:break-word}.copy-btn{min-height:40px;padding:6px 12px;border:1px solid #ffffff55;border-radius:8px;background:transparent;color:#fff;cursor:pointer}.copy-btn:hover{background:#ffffff12}.contact a{text-decoration:underline;text-underline-offset:4px}.footer{padding:24px 0;color:var(--muted);font-size:12px;text-align:center}.toast{position:fixed;left:50%;bottom:24px;z-index:90;padding:10px 16px;border-radius:9px;background:var(--ink);color:#fff;transform:translate(-50%,20px);opacity:0;pointer-events:none;transition:.2s}.toast.show{transform:translate(-50%,0);opacity:1}.text-link{color:var(--teal);text-decoration:underline}
@media(min-width:640px){.container{width:min(1160px,calc(100% - 64px))}.hero{padding:70px 0 44px}h1{font-size:54px}.project-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.honor-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.skill-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.case-copy{padding:38px}.contact-row strong{font-size:16px}}
@media(min-width:900px){.nav-links{display:flex;align-items:center;gap:26px}.nav-links a{color:var(--muted);font-size:13px}.nav-links a:hover,.nav-links a.active{color:var(--teal)}.menu-btn,.mobile-menu{display:none}.hero{padding:86px 0 54px}.hero-grid{grid-template-columns:minmax(0,1.35fr) minmax(300px,.65fr);align-items:center;gap:60px}.section{padding:76px 0}.about-grid{grid-template-columns:minmax(0,1.5fr) minmax(260px,.5fr)}.project-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.project-card:first-child{grid-column:span 2;display:grid;grid-template-columns:1.15fr 1fr}.project-card:first-child .project-media{aspect-ratio:auto;min-height:340px;border-bottom:0;border-right:1px solid var(--line)}.project-card:first-child .project-body{display:flex;flex-direction:column;justify-content:center;padding:34px}.honor-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.case-study{grid-template-columns:1.1fr 1fr}.case-copy{padding:42px}.skill-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.contact-grid{grid-template-columns:1fr 1.2fr;gap:80px}.timeline-item{grid-template-columns:100px 32px minmax(0,1fr)}.timeline-item::before{left:116px}}
@media(min-width:1180px){.project-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.project-card:first-child{grid-column:span 2}.honor-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media print{.nav,.progress,.filters,.hero-actions,.copy-btn,.toast{display:none}.hero,.section{padding:24px 0}.project-card,.honor-card,.skill-card{break-inside:avoid}.project-grid,.honor-grid,.skill-grid{display:block}.project-card,.honor-card,.skill-card{margin-bottom:12px}.case-study,.contact{background:#fff;color:var(--ink)}.case-copy p,.case-copy li,.contact p{color:var(--muted)}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
</style>
</head>
<body>
<div class="progress" id="progress" aria-hidden="true"></div>
<nav class="nav" aria-label="主导航"><div class="container nav-inner"><a class="brand" href="#top"><span class="brand-mark">竹</span><span>王佳琦<small>ZHUXIN · YGTEMPLE</small></span></a><div class="nav-links"><a href="#projects">项目</a><a href="#honors">荣誉</a><a href="#journey">经历</a><a href="#skills">能力</a><a href="#contact">联系</a></div><button class="menu-btn" id="menuBtn" aria-label="打开导航" aria-expanded="false" aria-controls="mobileMenu"><span></span><span></span></button></div><div class="container mobile-menu" id="mobileMenu" hidden><a href="#projects">项目</a><a href="#honors">荣誉</a><a href="#journey">经历</a><a href="#skills">能力</a><a href="#contact">联系</a></div></nav>
<main id="top">
<header class="hero"><div class="container"><div class="hero-grid"><div><div class="kicker">王佳琦 / 竹心 · 个人作品集</div><h1>把语言、代码与 AI，<br>做成真实作品。</h1><p class="hero-copy">郑州升达经贸管理学院外国语学院翻译专业 2024 级本科生。持续实践 <strong>C/C++、Qt、前端、AI 应用与 AIGC 创作</strong》，让技术既有功能，也有清晰的表达。</p><div class="hero-actions"><a class="btn primary" href="#projects">看看我的项目</a><a class="btn" href="https://github.com/YGtemple" target="_blank" rel="noopener noreferrer">GitHub · YGtemple</a></div></div><aside class="profile-panel"><span class="label">CURRENT FOCUS</span><h2>翻译专业背景<br>AI 应用与内容工程实践</h2><dl><dt>目前身份</dt><dd>外国语学院 · 翻译本科大三</dd><dt>主要方向</dt><dd>智能体 / AIGC / 开源工具</dd><dt>近期成果</dt><dd>卫华黑客松内容创作赛道三等奖</dd></dl></aside></div><div class="stats"><div class="stat"><b>52</b><span>GitHub 公开仓库</span></div><div class="stat"><b>3</b><span>程序设计竞赛奖项</span></div><div class="stat"><b>2</b><span>《醒春》WaytoAGI 双奖</span></div></div></div></header>
<section class="section" id="about"><div class="container"><div class="section-head"><div><span class="section-index">01 / ABOUT</span><h2>关于我</h2></div></div><div class="about-grid"><div class="about-content">__ABOUT__</div><div class="about-note"><strong>我的复合优势</strong>语言敏感度、内容组织能力与工程实践结合。既能阅读和设计，也能把想法推进到页面、工作流和可展示的作品。</div></div></div></section>
<section class="section" id="projects"><div class="container"><div class="section-head"><div><span class="section-index">02 / SELECTED WORK</span><h2>代表项目</h2><p>从 AI 应用到内容生产，从网页工具到学习游戏。</p></div></div><div class="filters" role="group" aria-label="项目分类筛选"><button class="filter active" data-filter="all" aria-pressed="true">全部</button><button class="filter" data-filter="ai" aria-pressed="false">AI 应用</button><button class="filter" data-filter="tools" aria-pressed="false">开发工具</button><button class="filter" data-filter="aigc" aria-pressed="false">AIGC</button><button class="filter" data-filter="game" aria-pressed="false">游戏</button></div><p class="result-count" id="resultCount" aria-live="polite"></p><div class="project-grid">__PROJECTS__</div><div class="case-study"><img src="assets/weihua.png" alt="卫华短视频流水线项目画面" loading="lazy"><div class="case-copy"><span class="section-index">CASE STUDY · 2026.11</span><h3>两天一夜，把企业需求做成完整工作流</h3>__WEIHUA__</div></div></div></section>
<section class="section" id="honors"><div class="container"><div class="section-head"><div><span class="section-index">03 / HONORS</span><h2>荣誉与奖项</h2><p>程序设计、AI 创新、AIGC 创作与志愿服务。</p></div></div><div class="honor-grid">__HONORS__</div></div></section>
<section class="section" id="journey"><div class="container"><div class="section-head"><div><span class="section-index">04 / JOURNEY</span><h2>学习与成长</h2><p>从第一行 C++ 代码，到完整的 AI 产品与内容工作流。</p></div></div><div class="timeline">__TIMELINE__</div></div></section>
<section class="section" id="skills"><div class="container"><div class="section-head"><div><span class="section-index">05 / CAPABILITIES</span><h2>我能做什么</h2><p>把技术、内容与展示组织成可交付的作品。</p></div></div><div class="skill-grid">__SKILLS__</div><div class="skills-extra">__SKILLS_EXTRA__</div><div class="campus">__CAMPUS__</div></div></section>
<section class="contact" id="contact"><div class="container contact-grid"><div><span class="section-index">06 / CONTACT</span><h2>一起做点有意思的作品。</h2><p>欢迎交流程序设计、AI 应用、AIGC 创作、开源项目和校园合作。</p><a href="profile.md" class="text-link">查看完整文字版经历</a></div><div class="contact-list"><div class="contact-row"><div><span>邮箱</span><br><strong>1744059451@qq.com</strong></div><button class="copy-btn" data-copy="1744059451@qq.com">复制邮箱</button></div><div class="contact-row"><div><span>电话 / 微信</span><br><strong>15314662965</strong></div><button class="copy-btn" data-copy="15314662965">复制号码</button></div><div class="contact-row"><div><span>GitHub</span><br><strong><a href="https://github.com/YGtemple" target="_blank" rel="noopener noreferrer">github.com/YGtemple</a></strong></div></div><div class="contact-row"><div><span>学校与专业</span><br><strong>郑州升达经贸管理学院 · 翻译专业</strong></div></div></div></div></section>
</main>
<footer class="footer">王佳琦 · 竹心 · YGtemple<br>保持好奇，持续创作，把想法变成作品。</footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>
const menuBtn=document.getElementById('menuBtn'),mobileMenu=document.getElementById('mobileMenu');
function closeMenu(){menuBtn.setAttribute('aria-expanded','false');mobileMenu.hidden=true;}
menuBtn.addEventListener('click',()=>{const open=menuBtn.getAttribute('aria-expanded')==='true';menuBtn.setAttribute('aria-expanded',String(!open));mobileMenu.hidden=open;});
mobileMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
const filterButtons=[...document.querySelectorAll('.filter')],cards=[...document.querySelectorAll('.project-card')],resultCount=document.getElementById('resultCount');
function filterProjects(category){let count=0;cards.forEach(card=>{const show=category==='all'||card.dataset.category.split(' ').includes(category);card.hidden=!show;if(show)count++;});filterButtons.forEach(btn=>{const active=btn.dataset.filter===category;btn.classList.toggle('active',active);btn.setAttribute('aria-pressed',String(active));});resultCount.textContent=`当前显示 ${count} 个项目`;}
filterButtons.forEach(btn=>btn.addEventListener('click',()=>filterProjects(btn.dataset.filter)));filterProjects('all');
const toast=document.getElementById('toast');let toastTimer;
function showToast(message){toast.textContent=message;toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),1800);}
async function copyText(value){try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(value);}else{const area=document.createElement('textarea');area.value=value;area.style.position='fixed';area.style.opacity='0';document.body.appendChild(area);area.select();document.execCommand('copy');area.remove();}showToast('已复制：'+value);}catch{showToast('请手动复制：'+value);}}
document.querySelectorAll('[data-copy]').forEach(btn=>btn.addEventListener('click',()=>copyText(btn.dataset.copy)));
const progress=document.getElementById('progress');function updateProgress(){const max=document.documentElement.scrollHeight-innerHeight;progress.style.width=(max>0?scrollY/max*100:0)+'%';}addEventListener('scroll',updateProgress,{passive:true});updateProgress();
const navLinks=[...document.querySelectorAll('.nav-links a')];const sections=navLinks.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){navLinks.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+entry.target.id));}}),{rootMargin:'-20% 0px -65% 0px'});sections.forEach(s=>observer.observe(s));}
</script>
</body>
</html>
'''

replacements = {
    "__ABOUT__": about_html,
    "__PROJECTS__": "".join(project_cards),
    "__WEIHUA__": weihua_html,
    "__HONORS__": "".join(honor_cards),
    "__TIMELINE__": "".join(timeline_items),
    "__SKILLS__": "".join(skill_cards),
    "__SKILLS_EXTRA__": skills_extra,
    "__CAMPUS__": campus_html,
}
for marker, value in replacements.items():
    page = page.replace(marker, value)

# Correct the Chinese quote in the static hero without relying on Markdown parsing.
page = page.replace("</strong》", "</strong>")
(ROOT / "index.html").write_text(page, encoding="utf-8", newline="\n")
print(f"Generated {ROOT / 'index.html'}: {len(project_cards)} projects, {len(honor_cards)} honors, {len(timeline_items)} timeline items")
