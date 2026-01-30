---
name: reading-companion
description: 阅读伴侣 - 帮助用户阅读和整理书籍。支持 PDF 书籍裁剪、转换为 Markdown、AI 润色优化。当用户提到阅读书籍、整理章节、PDF 转换、读书笔记时使用此 skill。
---

# Reading Companion - 阅读伴侣

帮助用户高效阅读长篇书籍的智能助手。

## 核心理念

**用户只需要说想读什么，其余的交给我来处理。**

```
用户："帮我整理第 50-80 页"
  ↓
Claude 自动完成：裁剪 → 转换 → 分析内容 → 命名 → 润色 → 保存
```

## 必需信息

| 信息 | 是否必需 | 默认值 |
|------|----------|--------|
| **PDF 文件路径** | ✅ 必需 | 无，必须提供 |
| **输出目录** | 可选 | 当前目录下，以书名命名的文件夹 |

### 检查流程

```
用户发起阅读请求
    ↓
检查：是否已知 PDF 路径？ ──否──→ 询问："请提供 PDF 文件路径"
    ↓是
检查：是否指定输出目录？ ──否──→ 使用默认：./{书名}/
    ↓
开始处理
```

### 信息记忆

一旦用户提供了 PDF 路径，在当前会话中会记住，后续操作无需重复提供。

## 会话式工作流

### 初始化示例

```
用户：我要读 ~/Books/design-patterns.pdf
```

Claude 会：
1. 读取 PDF 信息（总页数、书名）
2. 默认输出到 ./design-patterns/ 目录
3. 询问用户想从哪里开始

如果用户想指定输出位置：
```
用户：我要读 ~/Books/design-patterns.pdf，放到 ~/Notes/设计模式
```

### 阅读指令

用户可以用自然语言告诉我要读哪部分：

| 用户说 | 我的理解 |
|--------|----------|
| "整理第 50 到 80 页" | 提取 p.50-80 |
| "帮我看第三章" | 需要先确认第三章的页码范围 |
| "继续下一章" | 根据上次位置推断 |
| "从第 100 页开始，大概 30 页" | 提取 p.100-130 |

### 自动处理步骤

收到指令后，我会自动：

1. **裁剪 PDF** → 提取指定页码范围
2. **转换 Markdown** → 使用 pymupdf4llm 转换
3. **分析内容** → 读取前几页，识别章节标题
4. **智能命名** → 根据内容确定文件名（如 `03-观察者模式`）
5. **润色格式** → 优化为整洁的 Markdown
6. **保存文件** → 放到输出目录

## 工具命令

本 Skill 依赖项目目录的 `main.py`。请确保在插件安装目录下运行命令。

### 命令速查

```bash
# 查看 PDF 信息
uv run python main.py info <pdf_path>

# 裁剪 PDF
uv run python main.py split <input.pdf> <output.pdf> -s <起始页> -e <结束页>

# 转换为 Markdown
uv run python main.py convert <input.pdf> [output.md] [--pages "1-10"]

# 批量处理
uv run python main.py batch <config.json>
```

## 智能章节命名

当用户指定页码范围后，我会：

1. 先将该范围转换为 Markdown
2. 读取内容，寻找：
   - 大标题（Chapter X、第X章）
   - 主题关键词
   - 首个一级/二级标题
3. 生成命名，格式：`序号-简短标题`
   - 例：`03-观察者模式`、`05-dependency-injection`
4. 如果无法判断，询问用户

## 润色原则（严格遵守）

### 核心规则

1. **完整保留原始内容** - 严禁删减任何原有信息，一个字都不能少
2. **仅优化格式** - 修复排版问题，不改动文字表述
3. **保持简洁整齐** - 不添加花哨的格式，专注于可读性
4. **图片路径保持相对路径** - 确保能正确显示

### 格式优化清单

- [ ] 标题层级：从 `#` 开始，层级递进合理
- [ ] 段落分隔：段落之间有空行
- [ ] 列表格式：统一使用 `-` 或 `1.`，缩进正确
- [ ] 代码块：添加语言标记 ` ```python `
- [ ] 表格对齐：修复表格格式
- [ ] 图片引用：检查相对路径是否正确

### 润色示例

**原始输出**（pymupdf4llm 转换结果，格式混乱）：
```markdown
Chapter 3 Observer Pattern
The Observer pattern defines a one-to-many dependency.When state changes, all dependents are notified.
Key participants:
- Subject
- Observer
- ConcreteSubject
```

**润色后**（整洁可读）：
```markdown
# Chapter 3 Observer Pattern

The Observer pattern defines a one-to-many dependency. When state changes, all dependents are notified.

## Key participants

- **Subject** - 被观察的对象
- **Observer** - 观察者接口
- **ConcreteSubject** - 具体的被观察者
```

## 目录结构

```
{output_dir}/
├── 01-introduction/
│   ├── 01-introduction.pdf
│   ├── 01-introduction.md
│   └── 01-introduction_images/
├── 02-basics/
│   ├── 02-basics.pdf
│   ├── 02-basics.md
│   └── 02-basics_images/
└── ...
```

## 完整示例

### 场景：用户开始读一本新书

```
用户：我要读 ~/Downloads/design-patterns.pdf

Claude：
1. 读取 PDF 信息（总页数、元数据）
2. 回复：这本书共 320 页，输出将保存到 ./design-patterns/，你想从哪里开始？

用户：先看第 1 到 30 页

Claude：
1. 创建目录 ./design-patterns/01-introduction/
2. 裁剪 p.1-30 → 01-introduction.pdf
3. 转换为 Markdown
4. 分析内容，发现标题是 "Introduction to Design Patterns"
5. 命名为 01-introduction
6. 润色 Markdown 格式
7. 保存到 ./design-patterns/01-introduction/01-introduction.md
8. 回复：已整理完成 01-introduction (p.1-30)
```

### 场景：继续阅读

```
用户：继续，第 31 到 60 页

Claude：
1. 裁剪 p.31-60
2. 转换、分析内容，发现是 "Chapter 2: Creational Patterns"
3. 命名为 02-creational-patterns
4. 润色并保存到 ./design-patterns/02-creational-patterns/
```

### 场景：指定输出位置

```
用户：我要读 ~/Books/erta.pdf，放到 ~/Notes/编程书籍/ERTA

Claude：
1. 读取 PDF 信息
2. 输出将保存到 ~/Notes/编程书籍/ERTA/
3. 后续章节都保存在这个目录下
```

## 注意事项

1. **首次使用**：只需要提供 PDF 路径，输出目录可选
2. **章节命名**：优先从内容中提取，无法判断时询问用户
3. **大文件**：建议每次处理不超过 50 页，便于润色和阅读
4. **图片处理**：默认提取图片到单独文件夹，使用相对路径引用
