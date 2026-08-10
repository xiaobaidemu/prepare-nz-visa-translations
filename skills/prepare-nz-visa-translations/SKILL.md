---
name: prepare-nz-visa-translations
description: 将中国身份证、户口本、婚姻与民事证明、银行与资产证明、在职证明、房产材料等扫描图片或 PDF，重新制作成适用于新西兰签证申请的清晰英文翻译 PDF。用于需要识别原件、逐项翻译、按原始版式重建英文页面、翻译印章或盖章、生成独立英文译本、添加译者信息、使用英文文件名整理材料或校验签证翻译件的任务。不使用 Canva。
---

# 制作新西兰签证英文翻译件

生成忠实、清晰、可提交的英文重建件，不做内容摘要，也不在中文扫描件上涂抹后覆盖英文。始终保留原件，并确保签证官在 100% 缩放下可以直接阅读译文。

本 Skill 自包含完成任务所需的签证翻译、PDF 生成、版式重建和质量校验逻辑。不要引用其他 Skill 的说明文件来替代本 Skill 内的规则。

## 核心规则

1. 以原始文件为唯一事实依据。不得猜测模糊、折叠、裁切或被印章遮挡的文字。
2. 从零生成 HTML/CSS 或矢量 PDF 英文页面。不得擦除扫描页上的中文，再用色块或英文覆盖。
3. 尽量严格保持原始页面尺寸、比例、章节顺序、表格、边框、对齐、照片、印章和视觉层级。
4. 翻译所有有意义的中文内容，包括标题、字段名、说明、小字、手写内容、钢印、印章和盖章文字。确实无法辨认时写 `[illegible]`；只有文字真实受到遮挡时才能写 `(partly obscured)`。
5. 原件为空的字段必须直接留空。不得填写 `Not stated`、`Not provided`、`Unknown`、横线或其他占位文字。
6. 姓名、号码、日期、地址、金额、证件编号和签发机关必须逐项核对。相同信息在不同材料中必须保持一致。
7. 保证可读性。正文和字段值通常使用 9-11 pt，字段标签使用 8-9 pt；只有无法避免的微型说明可降至 7 pt，不得更小。
8. 不生成 Canva 文件，不加入装饰性水印，也不添加原件中不存在或无法解释的小红字。

## 选择交付形式

- 签证网站提供单独的翻译文件上传栏时，生成纯英文翻译 PDF；中文原件上传至原件栏。
- 用户或网站要求单一合并文件时，按“原件页后接对应英文页”的顺序合并，或制作明确分区的左侧原件、右侧译文版本。
- 用户明确要求独立翻译文件时，默认生成纯英文 PDF，不把中文原件嵌入译本。
- 除非用户要求删除，否则保留既有 HTML、PDF 和中间版本。

## 完整流程

### 1. 盘点并检查原件

- 找出全部源文件和页面，确认文件类型、页数与顺序。
- 记录页面尺寸、方向、旋转、裁切、照片位置、表格结构、印章、手写内容和空白字段。
- 扫描 PDF 必须先渲染成图片进行视觉检查；图片先应用 EXIF 方向修正，再执行 OCR 或嵌入。
- 优先读取 PDF 文字层；只有扫描页、缺失区域或乱码区域才使用 OCR。
- 翻译前建立逐项抄录清单，不能遗漏小字和印章文字。

### 2. 抄录并翻译

- 按原件字段顺序逐项处理，保持原有层级。
- 使用正式、清晰的行政英文；同一中文术语在全部材料中使用同一译法。
- 中国人名优先采用用户或护照提供的拼写，不得擅自更换姓名顺序。
- 地址需翻译行政区划，同时对小区、道路等专名使用稳定一致的拼音或用户确认拼写。
- 日期优先使用 `日 月份 年` 的英文形式，但不得改变原意。
- 印章必须根据实际文字翻译，只有原件明确支持时才能标注为官方印章或专用章。
- 具体术语、空白和校验规则见 [references/translation-and-qa.md](references/translation-and-qa.md)。

### 3. 重建英文页面

- 不规则表格、合并单元格和密集文本优先使用 HTML/CSS；使用明确的毫米尺寸和 `@page` 控制打印尺寸。
- 精确边框、固定坐标、圆形印章和稳定矢量输出优先使用 ReportLab。
- 只有原件照片或无法合理重绘的防伪背景可以使用位图。照片必须从最高质量原件裁切，并保持宽高比。
- 页面顶部可以低调标注 `ENGLISH TRANSLATION`，但不能破坏原件的层级结构。
- 纯英文译本的最终文本层不得包含中文；仅在官方专名确有必要时保留原文形式。
- 新建页面前阅读 [references/layout-reconstruction.md](references/layout-reconstruction.md)。
- 身份证、户口本和其他证件的结构规则见 [references/document-patterns.md](references/document-patterns.md)。

### 4. 生成并组装 PDF

- 使用 `scripts/render_html_to_pdf.py` 将 HTML 转成 PDF；页面尺寸由 HTML 的 `@page` 控制。
- 使用 `scripts/assemble_translation_pdf.py` 合并一页或多页英文译文，并在末页加入简洁译者信息。
- 首次使用时，将 `assets/translator-profile.example.json` 复制为任务目录中的私有资料文件，填写真实译者信息后通过 `--profile` 传入。不得把含电话、住址的真实资料提交到公共仓库。
- 除非交付形式明确要求合并，否则中文原件和英文译本必须保持为两个独立文件。

### 5. 添加译者信息

末页仅使用简洁标题和以下四条英文信息，并从用户提供的译者资料文件读取具体值：

- `Translator: <full name>`
- `Telephone: <phone number>`
- `Address: <full postal address>`
- `Qualification: <relevant qualifications and language experience>`

不得使用表格。默认不得添加准确性声明、签名线、源语言、目标语言、制作日期或解释性页脚。除非译者确实提供适用认证，不得把译本称为 `certified translation`。翻译者姓名使用其确认的英文拼写并在全部译文中保持一致；默认采用 Given name 在前、Surname 在后的显示顺序，除非译者证件或用户明确要求其他顺序。

### 6. 使用英文文件名并放入对应目录

- 用户要求英文文件名时，将保留的原件命名为 `<Document_Type>_Original.pdf`。
- 将最终译本命名为 `<Document_Type>_English_Translation.pdf`。
- 推荐名称包括 `Household_Register_Original.pdf`、`Household_Register_English_Translation.pdf`、`PRC_Resident_Identity_Card_Original.pdf` 和 `PRC_Resident_Identity_Card_English_Translation.pdf`。
- 将原件与译本放入签证材料目录中对应的证件子目录。
- 写入前必须解析并确认确切路径。未经用户明确要求，不得删除旧版本。

### 7. 交付前校验

- 使用 `scripts/validate_translation_pdf.py --english-only --profile ... --render-dir ...` 校验。
- 确认 PDF 可以打开、页数正确，且单个文件不超过 10 MB。
- 检查文本层中没有中文、占位文字、旧译者姓名或未经要求的认证表述。
- 将每一页渲染成 PNG，并分别在整页视图和 100% 缩放下检查。
- 检查照片裁切、页面尺寸、字号、表格对齐、自动换行、印章位置、空白单元格和页面顺序。
- 复制到最终签证目录后重新读取文件，并确认校验和与已验证输出一致。

## 内部资源

- 版式和技术选择：`references/layout-reconstruction.md`
- 翻译、空白、印章与校验规则：`references/translation-and-qa.md`
- 身份证、户口本等证件结构：`references/document-patterns.md`
- HTML 重建起点：`assets/vector-page-template.html`
- 译者资料示例：`assets/translator-profile.example.json`
- PDF 组装、HTML 打印和校验：`scripts/`

优先复用本 Skill 自带脚本，不要重复编写 PDF 组装和校验代码。
