# 王佳琦（竹心）· 个人主页

王佳琦 / `YGtemple` 的公开个人主页与经历仓库，记录学习历程、代表项目、竞赛荣誉、AIGC 创作、校园实践和联系方式。

## 仓库内容

- `profile.md`：完整个人介绍与经历。
- `index.html`：可直接由 GitHub Pages 托管的静态主页。
- `scripts/build_site.py`：修改 `profile.md` 后重新生成主页。

## 更新主页

```powershell
python -m pip install -r requirements.txt
python scripts/build_site.py
```

## GitHub Pages

仓库使用 `main` 分支根目录发布。进入 `Settings → Pages`，选择 `Deploy from a branch`，分支选择 `main / (root)` 即可。

Pages 启用后的公开主页：<https://ygtemple.github.io/wangjiaqi-profile/>
