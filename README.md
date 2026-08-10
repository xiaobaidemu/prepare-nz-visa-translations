# prepare-nz-visa-translations

面向 AI 编程代理的可复用 Skill：将中国身份证、户口本、银行流水、在职证明、房产和其他签证材料，重建为清晰、独立、可校验的新西兰签证英文翻译 PDF。

Skill 采用标准 `SKILL.md` 目录结构，可通过 npm 提供的 [`skills`](https://www.npmjs.com/package/skills) CLI 安装到 Codex 等兼容代理；仓库同时提供 PDF 组装、HTML 打印和交付校验脚本。

> 本项目用于文档翻译与排版辅助，不构成移民或法律意见。提交前请核对[新西兰移民局最新翻译要求](https://www.immigration.govt.nz/process-to-apply/applying-for-a-visa/providing-evidence-and-documents-to-support-your-visa-application/providing-english-translations-of-supporting-documents/)。

## 能力

- 按原始页面尺寸、字段顺序、表格和视觉层级重建英文页面。
- 翻译标题、字段、正文、印章、盖章和可辨认的手写内容。
- 生成独立英文译本，并在末页加入四行简洁译者信息。
- 保持原件空白字段为空，不使用 `Not stated`、`Unknown` 等占位文本。
- 校验页数、文件大小、英文文本层、禁用措辞和译者资料。
- 将每页渲染为 PNG，便于在整页视图和 100% 缩放下检查。
- 不依赖 Canva，不在扫描件上涂抹中文后覆盖英文。

## 安装

### 推荐：通过 npm / npx 安装 Skill

```bash
npx skills add xiaobaidemu/prepare-nz-visa-translations \
  --skill prepare-nz-visa-translations \
  -g -a codex -y
```

查看是否安装成功：

```bash
npx skills list -g -a codex
```

更新已安装版本：

```bash
npx skills update prepare-nz-visa-translations -g -y
```

### 仅下载 npm 包内容

```bash
npm install github:xiaobaidemu/prepare-nz-visa-translations
```

此方式只把仓库下载到 `node_modules`，不会自动注册到代理。日常使用建议采用上面的 `npx skills add`。

## 环境要求

- Python 3.10 或更高版本。
- Chrome、Chromium 或 Microsoft Edge，用于把 HTML/CSS 重建页打印为 PDF。
- Python 依赖：`pypdf`、`reportlab`；使用 PNG 视觉校验时还需要 `pypdfium2`。

安装 Python 依赖：

```bash
python3 -m pip install -r skills/prepare-nz-visa-translations/requirements.txt
```

## 配置译者资料

公共仓库不包含任何真实译者的电话或住址。复制示例文件到任务工作目录，再填写真实资料：

```bash
cp skills/prepare-nz-visa-translations/assets/translator-profile.example.json \
  ./translator-profile.json
```

文件包含以下字段：

```json
{
  "name": "Translator Full Name",
  "telephone": "+00 000 0000 0000",
  "address": "Translator's full postal address",
  "qualification": "Relevant qualifications and language experience."
}
```

请勿把真实 `translator-profile.json` 提交到公共仓库。

## 使用方式

在 Codex 中附上原始 PDF 或图片，然后调用：

```text
请使用 $prepare-nz-visa-translations，将这份中文材料重建为独立英文翻译 PDF，
保持原始版式，翻译全部印章，空白字段保持空白，并使用我提供的译者资料。
```

Skill 会先盘点原件、建立抄录清单和术语映射，再重建英文页面、追加译者页、进行文字与视觉校验，最后将文件放入用户指定目录。

## 脚本

以下命令假设当前目录为 Skill 目录。

### HTML 转 PDF

```bash
python3 scripts/render_html_to_pdf.py input.html translated-pages.pdf
```

### 合并译文并追加译者页

```bash
python3 scripts/assemble_translation_pdf.py translated-pages.pdf \
  --output Document_English_Translation.pdf \
  --profile /absolute/path/to/translator-profile.json \
  --title "Document - English Translation"
```

### 最终校验与逐页渲染

```bash
python3 scripts/validate_translation_pdf.py Document_English_Translation.pdf \
  --profile /absolute/path/to/translator-profile.json \
  --expected-pages 2 \
  --english-only \
  --forbid-certified \
  --render-dir ./rendered-pages
```

## 输出约定

- 原件：`<Document_Type>_Original.pdf`
- 译本：`<Document_Type>_English_Translation.pdf`
- 默认交付独立英文译本；只有网站或用户明确要求时才与原件合并。
- 姓名采用用户或护照确认的英文拼写，并在全部材料中保持一致。
- 译文页面匹配原始页面尺寸；最后追加一页简洁译者资料。
- 单个最终文件默认不超过 10 MB。

## 仓库结构

```text
skills/prepare-nz-visa-translations/
├── SKILL.md
├── agents/openai.yaml
├── assets/
│   ├── translator-profile.example.json
│   └── vector-page-template.html
├── references/
│   ├── document-patterns.md
│   ├── layout-reconstruction.md
│   └── translation-and-qa.md
├── scripts/
│   ├── assemble_translation_pdf.py
│   ├── render_html_to_pdf.py
│   └── validate_translation_pdf.py
└── requirements.txt
```

## 开发与验证

```bash
npm run validate
npm run pack:check
```

`npm run validate` 检查 Skill 元数据、必要资源、私密译者资料和脚本语法；`npm run pack:check` 展示 npm 安装包将包含的文件。

## 隐私与安全

- 不要把申请人的护照、身份证、银行流水或户口本样本提交到仓库。
- 不要把真实译者电话和住址写入公共 Skill。
- 以用户提供的原件为唯一事实依据，不推测模糊、遮挡或裁切内容。
- 对外提交前必须人工核对姓名、号码、日期、金额、地址和印章。

## License

[MIT](LICENSE)
