# Reading Tools

PDF 阅读辅助工具，帮助你借助 AI 系统性阅读计算机书籍。

- 按章节切分 PDF
- 将 PDF 转换为 LLM 友好的 Markdown

## 安装

```bash
uv sync
```

## 使用方法

### 查看 PDF 信息

```bash
uv run python main.py info book.pdf
```

### 切分 PDF

按页码范围提取 PDF：

```bash
uv run python main.py split book.pdf chapter1.pdf --start 19 --end 30
# 或简写
uv run python main.py split book.pdf chapter1.pdf -s 19 -e 30
```

### 转换为 Markdown

```bash
# 转换整本书
uv run python main.py convert book.pdf

# 转换指定页码范围
uv run python main.py convert book.pdf -p "19-30"

# 指定输出文件
uv run python main.py convert book.pdf output.md -p "1-10"
```

### 批量处理（推荐）

1. 创建配置文件 `chapters.json`：

```json
{
  "input": "book.pdf",
  "output_dir": "chapters",
  "chapters": [
    {"name": "01-introduction", "start": 1, "end": 15},
    {"name": "02-basics", "start": 16, "end": 45},
    {"name": "03-advanced", "start": 46, "end": 80}
  ]
}
```

2. 运行批量处理：

```bash
uv run python main.py batch chapters.json
```

这会在 `chapters/` 目录下生成：
- 每章的 PDF 文件（`01-introduction.pdf`, `02-basics.pdf`, ...）
- 每章的 Markdown 文件（`01-introduction.md`, `02-basics.md`, ...）

如果只需要切分 PDF 不转换 Markdown：

```bash
uv run python main.py batch chapters.json --no-convert
```

## 工作流建议

1. 用 `info` 命令查看 PDF 总页数
2. 翻阅 PDF 目录，记录每章的起止页码
3. 创建 `chapters.json` 配置文件
4. 运行 `batch` 命令批量处理
5. 将生成的 Markdown 文件逐章喂给 LLM 学习
