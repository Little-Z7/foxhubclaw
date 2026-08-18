# FoxHubClaw

Windows EXE and web desk for [RedFoxHub](https://redfox.hk) keyword search.

用户自备红狐 API Key，按关键词检索各平台帖子和评论，支持即时查询与每天 / 每周任务，报告在软件内下载 Excel、HTML、PDF。

仓库镜像：

- GitHub：https://github.com/Little-Z7/foxhubclaw
- Gitee：https://gitee.com/tangenzhe/foxhubclaw

发给同事的一页纸和操作说明：

- [项目简介](docs/项目简介.md)
- [使用手册](docs/使用手册.md)

## 能力

| 平台 | 帖子 / 作品 | 评论 |
| --- | --- | --- |
| 抖音 | 是 | 否 |
| 小红书 | 是 | 否 |
| 公众号 | 是 | 否 |
| B站 | 是 | 是 |
| 今日头条 | 是 | 否 |
| 快手 | 是 | 是 |
| 微博 | 是 | 是 |
| TikTok | 否 | 否 |

评论路径是「先搜作品，再拉热门作品评论」。B 站评论接口异步轮询，比其他平台慢。今日头条经常只回少量条目。TikTok 目前没有关键词帖子 / 评论接口。

## 两种模式

- **桌面 / 内部分发：** 不用注册。本地 SQLite。双击 `FoxHubClaw.exe`，或运行 `scripts/run_desktop.ps1`。
- **网页产品：** 邮箱或用户名加密码。第一个注册的用户是管理员，可启用或停用账号。

## 分发包

仓库不收录 EXE（见 `.gitignore`）。打包后把下面三样放进一个文件夹再压缩：

```
FoxHubClaw.exe
docs/项目简介.md
docs/使用手册.md
```

产物路径：`backend/dist/FoxHubClaw.exe`。数据写在 EXE 工作目录下的 `data/`，不要把该目录公开发出去。

## 环境

- Python 3.12
- Node.js 20+
- 红狐 API Key：https://redfox.hk

## 网页开发

```powershell
cd frontend
npm install
npm run build

cd ..\backend
python -m pip install -r requirements.txt
$env:FOXHUB_MODE="web"
python -m foxhubclaw.main --mode web --host 127.0.0.1 --port 8787
```

打开 http://127.0.0.1:8787

热更新：

```powershell
# 终端 1
cd backend
$env:FOXHUB_MODE="web"
python -m foxhubclaw.main --mode web

# 终端 2
cd frontend
npm run dev
```

Vite 在 Windows 上常只监听 `localhost`（有时是 5174）。用 `http://localhost:5173` 或终端里打印的地址，不要死写 `127.0.0.1`。

## 桌面调试

先构建前端，再启动窗口：

```powershell
cd frontend
npm install
npm run build
cd ..\backend
$env:FOXHUB_MODE="desktop"
python -m foxhubclaw.desktop
```

或：`scripts/run_desktop.ps1`（需已有 `frontend/dist`）。

## 打 EXE

```powershell
cd frontend
npm run build
cd ..\backend
python -m pip install pyinstaller
# 若旧 EXE 正在运行，先退出，否则无法覆盖
python -m PyInstaller --noconfirm foxhubclaw.spec
```

产物：`backend/dist/FoxHubClaw.exe`。单文件、无控制台窗口。打包前关掉正在运行的 FoxHubClaw。

## 定时任务

服务或 EXE 运行时每分钟检查到期任务。只跑一次（例如交给系统计划任务）：

```powershell
cd backend
python -m foxhubclaw.worker
```

## 测试

```powershell
cd backend
python -m pytest -v
```

## 注意

- 产品名、窗口标题、仓库名保持英文 **FoxHubClaw**。界面文案默认中文。
- 不要提交 `.env`、真实 Key、`data/`、`*.exe`。
- Key 在库里加密存储，接口和设置页只回掩码。
