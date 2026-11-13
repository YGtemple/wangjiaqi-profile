# 王佳琦 · 个人经历与荣誉档案

这是王佳琦（竹心 / `YGtemple`）的个人资料仓库，用于持续记录学习经历、项目作品、竞赛荣誉、志愿服务与公开技术输出。

## 内容

- `profile.md`：完整核验档案，区分“已证实、个人自述、待核对”。
- `index.html`：由完整档案生成的静态个人主页，可由 GitHub Pages 直接托管。
- `scripts/build_site.py`：修改 `profile.md` 后重新生成主页的脚本。

## 隐私口径

不收录手机号、学号、身份证号、准考证号、账号令牌、家庭困难认定和医疗信息。团队成果不写成个人独立完成；未正式立项、未核实奖项和存在冲突的名单不写成确定事实。

## 本地更新主页

```powershell
python -m pip install -r requirements.txt
python scripts/build_site.py
```

## GitHub Pages

本仓库按 `main` 分支根目录直接发布静态页面设计。启用路径通常为仓库 `Settings → Pages → Deploy from a branch → main / (root)`。

**Pages 是否公开与仓库是否私有是两个独立设置。当前文件准备不代表已启用 Pages；发布前必须确认网站可见范围。**
