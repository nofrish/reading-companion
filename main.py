#!/usr/bin/env python3
"""
PDF 阅读辅助工具
- 按章节切分 PDF
- 将 PDF 转换为 LLM 友好的 Markdown
"""

import json
from pathlib import Path

import pymupdf4llm
import typer
from pypdf import PdfReader, PdfWriter
from rich import print as rprint
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="PDF 阅读辅助工具")
console = Console()


@app.command()
def split(
    input_pdf: Path = typer.Argument(..., help="输入 PDF 文件路径"),
    output_pdf: Path = typer.Argument(..., help="输出 PDF 文件路径"),
    start: int = typer.Option(..., "--start", "-s", help="起始页码（从1开始）"),
    end: int = typer.Option(..., "--end", "-e", help="结束页码（包含）"),
):
    """按页码范围切分 PDF"""
    if not input_pdf.exists():
        rprint(f"[red]错误：文件不存在 {input_pdf}[/red]")
        raise typer.Exit(1)

    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)

    if start < 1 or end > total_pages or start > end:
        rprint(f"[red]错误：页码范围无效（总页数：{total_pages}）[/red]")
        raise typer.Exit(1)

    writer = PdfWriter()
    for i in range(start - 1, end):
        writer.add_page(reader.pages[i])

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with open(output_pdf, "wb") as f:
        writer.write(f)

    rprint(f"[green]成功：已提取第 {start}-{end} 页到 {output_pdf}[/green]")


@app.command()
def convert(
    input_pdf: Path = typer.Argument(..., help="输入 PDF 文件路径"),
    output_md: Path = typer.Argument(None, help="输出 Markdown 文件路径（默认同名.md）"),
    pages: str = typer.Option(None, "--pages", "-p", help="指定页码范围，如 '1-10' 或 '1,3,5-8'"),
):
    """将 PDF 转换为 LLM 友好的 Markdown"""
    if not input_pdf.exists():
        rprint(f"[red]错误：文件不存在 {input_pdf}[/red]")
        raise typer.Exit(1)

    if output_md is None:
        output_md = input_pdf.with_suffix(".md")

    page_list = None
    if pages:
        page_list = _parse_page_range(pages)

    rprint(f"[blue]正在转换 {input_pdf}...[/blue]")

    md_text = pymupdf4llm.to_markdown(str(input_pdf), pages=page_list)

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(md_text, encoding="utf-8")

    rprint(f"[green]成功：已转换为 {output_md}[/green]")


@app.command()
def info(
    input_pdf: Path = typer.Argument(..., help="输入 PDF 文件路径"),
):
    """查看 PDF 基本信息"""
    if not input_pdf.exists():
        rprint(f"[red]错误：文件不存在 {input_pdf}[/red]")
        raise typer.Exit(1)

    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    metadata = reader.metadata

    table = Table(title=f"PDF 信息: {input_pdf.name}")
    table.add_column("属性", style="cyan")
    table.add_column("值", style="green")

    table.add_row("总页数", str(total_pages))
    if metadata:
        if metadata.title:
            table.add_row("标题", metadata.title)
        if metadata.author:
            table.add_row("作者", metadata.author)
        if metadata.subject:
            table.add_row("主题", metadata.subject)

    console.print(table)


@app.command()
def batch(
    config_file: Path = typer.Argument(..., help="配置文件路径 (JSON)"),
    convert_to_md: bool = typer.Option(True, "--convert/--no-convert", help="是否同时转换为 Markdown"),
):
    """
    根据配置文件批量切分 PDF 并转换

    配置文件格式示例 (chapters.json):
    {
        "input": "book.pdf",
        "output_dir": "chapters",
        "chapters": [
            {"name": "01-introduction", "start": 1, "end": 15},
            {"name": "02-basics", "start": 16, "end": 45}
        ]
    }
    """
    if not config_file.exists():
        rprint(f"[red]错误：配置文件不存在 {config_file}[/red]")
        raise typer.Exit(1)

    config = json.loads(config_file.read_text(encoding="utf-8"))
    input_pdf = Path(config["input"])
    output_dir = Path(config.get("output_dir", "chapters"))
    chapters = config["chapters"]

    if not input_pdf.is_absolute():
        input_pdf = config_file.parent / input_pdf

    if not input_pdf.exists():
        rprint(f"[red]错误：PDF 文件不存在 {input_pdf}[/red]")
        raise typer.Exit(1)

    output_dir = config_file.parent / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)

    rprint(f"[blue]开始处理 {input_pdf.name}，共 {total_pages} 页，{len(chapters)} 个章节[/blue]")

    for chapter in chapters:
        name = chapter["name"]
        start = chapter["start"]
        end = chapter["end"]

        output_pdf = output_dir / f"{name}.pdf"

        writer = PdfWriter()
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])

        with open(output_pdf, "wb") as f:
            writer.write(f)

        rprint(f"  [green]✓[/green] {name}.pdf (第 {start}-{end} 页)")

        if convert_to_md:
            output_md = output_dir / f"{name}.md"
            page_list = list(range(start - 1, end))
            md_text = pymupdf4llm.to_markdown(str(input_pdf), pages=page_list)
            output_md.write_text(md_text, encoding="utf-8")
            rprint(f"  [green]✓[/green] {name}.md")

    rprint(f"\n[green]完成！输出目录：{output_dir}[/green]")


def _parse_page_range(pages_str: str) -> list[int]:
    """解析页码范围字符串，如 '1-10' 或 '1,3,5-8'"""
    result = []
    parts = pages_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            result.extend(range(int(start) - 1, int(end)))
        else:
            result.append(int(part) - 1)
    return result


if __name__ == "__main__":
    app()
