# Mindshield 心盾·Streamlit Cloud 稳定版

这是一个面向香港、澳门及大湾区硕士毕业生的多页面招聘反诈 MVP。

## 页面

- Home 首页
- Verify AI 核验
- Report 风险报告
- Tactics 反诈知识库
- FAQ 使用帮助

## 第一次运行（macOS）

重点：必须打开整个解压后的项目文件夹，不要只打开一个 Python 文件。

1. 先在旧网站的终端按 `Control + C`，停止旧服务。
2. 把新 ZIP 解压成一个全新文件夹；不要直接覆盖旧版本。
3. 打开 VS Code。
4. 点击顶部菜单“文件 → 打开文件夹”。
5. 选择刚刚解压出的 `mindshield_cloud` 文件夹。
6. 点击“终端 → 新建终端”。
7. 确认终端提示符最后是 `mindshield_cloud %`，再逐行执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade -r requirements.txt
python -m streamlit run app.py
```

这些命令的意思：

- 第 1 行：创建一个只属于本项目的 Python 小环境。
- 第 2 行：进入这个小环境。
- 第 3–4 行：安装网页、AI、网页提取和图片识别组件。
- 第 5 行：启动网站。

浏览器没有自动打开时，访问：

```text
http://localhost:8501
```

## 以后再次运行

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

停止网站：回到终端，同时按 `Control + C`。

如果只在自己的电脑上使用，并且还需要图片 OCR，再额外执行：

```bash
python -m pip install -r requirements-local-ocr.txt
```

云端稳定版默认不安装这组大型 OCR 组件，以降低 Streamlit Cloud 构建失败的概率。

## 上传到 GitHub（最简单的方法）

GitHub 用来保存代码，本身不会自动运行这个网站。

1. 登录 GitHub，点击右上角 `+`，选择 `New repository`。
2. 仓库名称填写 `mindshield`，初学阶段可选择 `Public`。
3. 点击 `Create repository`。
4. 在新仓库页面点击 `uploading an existing file`，或者点击 `Add file → Upload files`。
5. 打开本项目文件夹，把里面的文件和文件夹拖入上传区域。必须确保 `app.py` 和
   `requirements.txt` 位于仓库最外层，不能再套一层无关文件夹。
6. 不要上传 `.venv`、API Key 或 `.streamlit/secrets.toml`。
7. 在页面底部点击 `Commit changes` 完成上传。

## 部署为公开网页（Streamlit Community Cloud）

1. 先完成上面的 GitHub 上传。
2. 打开 `https://share.streamlit.io`，使用 GitHub 登录。
3. 点击 `Create app`，选择你的 `mindshield` 仓库。
4. Branch 选择 `main`，Main file path 填写 `app.py`。
5. Python 版本建议选择 `3.12`，然后点击 `Deploy`。
6. 首次安装 OCR 依赖会比普通网页慢，请等待部署日志完成。

当前程序让每个使用者在侧栏输入自己的 DeepSeek API Key，因此不需要把你的密钥
上传到 GitHub 或写进部署设置。

## 如果出现“File does not exist”

这不是 Python 代码错误，而是终端所在的文件夹不对。先用 VS Code 打开整个 `mindshield_fixed` 文件夹，再新建终端。

## 如果浏览器仍显示旧的空白页

1. 确认旧终端已用 `Control + C` 停止。
2. 关闭旧的浏览器标签页。
3. 在新文件夹里重新运行 `python -m streamlit run app.py`。
4. 打开终端显示的新 `Local URL`。
5. 如果页面被浏览器缓存，按 `Command + Shift + R` 强制刷新。

## 使用顺序

1. 点击左上角侧栏按钮，输入 DeepSeek API Key。
2. 在首页点击进入 AI 核验中心。
3. 选择招聘文字、职位链接或聊天截图。
4. 检查提取出的文字。
5. 点击 `RUN AI AUDIT`。
6. 系统会自动打开风险报告页面。

## 职位链接为什么仍可能读不到

新版会依次尝试读取官网的 `JobPosting` 结构化数据、网页正文和普通可见文字，
因此比旧版支持更多公司招聘官网。网站如果要求登录、弹出安全验证码，或必须在
浏览器里运行 JavaScript，程序不会绕过网站保护。这时请把官网上的职位正文复制到
“职位正文”输入框，或切换到图片模式上传截图，AI 审查功能仍然可以正常使用。

## 安全提醒

- 不要把 API Key 写进 Python 文件或上传 GitHub。
- 上传截图前请遮盖身份证、护照、银行卡、验证码和家庭住址。
- AI 结果仅用于风险筛查，不是法律定性。
