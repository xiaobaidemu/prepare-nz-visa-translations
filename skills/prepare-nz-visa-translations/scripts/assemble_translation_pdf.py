#!/usr/bin/env python3
"""合并英文译文页，并追加简洁的译者信息页。"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = SKILL_DIR / "assets" / "translator-profile.json"
EXAMPLE_PROFILE = SKILL_DIR / "assets" / "translator-profile.example.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("translation_pages", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--title", default="English Translation")
    parser.add_argument("--max-mb", type=float, default=10.0)
    return parser.parse_args()


def load_profile(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(
            f"找不到译者资料：{path}。请复制 {EXAMPLE_PROFILE}，填写真实资料后通过 --profile 传入。"
        )
    profile = json.loads(path.read_text(encoding="utf-8"))
    required = ("name", "telephone", "address", "qualification")
    missing = [key for key in required if not str(profile.get(key, "")).strip()]
    if missing:
        raise ValueError(f"译者资料缺少字段：{', '.join(missing)}")
    return {key: str(profile[key]).strip() for key in required}


def draw_line(canvas: Canvas, markup: str, x: float, y: float, width: float, style: ParagraphStyle) -> float:
    paragraph = Paragraph(markup, style)
    _, height = paragraph.wrap(width, 1000)
    paragraph.drawOn(canvas, x, y - height)
    return y - height


def build_declaration(path: Path, page_size: tuple[float, float], profile: dict[str, str]) -> None:
    width, height = page_size
    canvas = Canvas(str(path), pagesize=page_size)
    canvas.setTitle("Translator's Declaration")
    canvas.setFillColor(white)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)

    margin = min(42 * mm, width * 0.18)
    x = margin
    content_width = width - 2 * margin
    top = height - min(42 * mm, height * 0.16)

    canvas.setFillColor(HexColor("#173b51"))
    canvas.setFont("Helvetica-Bold", 15 if width >= 560 else 14)
    canvas.drawString(x, top, "TRANSLATOR'S DECLARATION")

    style = ParagraphStyle(
        "translator-line",
        fontName="Helvetica",
        fontSize=10 if width >= 560 else 9,
        leading=15 if width >= 560 else 14,
        leftIndent=11,
        firstLineIndent=-11,
        textColor=HexColor("#142329"),
    )
    lines = [
        f"- Translator: <b>{profile['name']}</b>",
        f"- Telephone: {profile['telephone']}",
        f"- Address: {profile['address']}",
        f"- Qualification: {profile['qualification']}",
    ]
    y = top - 38
    for line in lines:
        y = draw_line(canvas, line, x, y, content_width, style) - 9
    canvas.save()


def main() -> None:
    args = parse_args()
    profile = load_profile(args.profile)
    for path in args.translation_pages:
        if not path.is_file():
            raise FileNotFoundError(path)

    first_reader = PdfReader(str(args.translation_pages[0]))
    if not first_reader.pages:
        raise ValueError("第一份英文译文 PDF 没有页面")
    first_box = first_reader.pages[0].mediabox
    page_size = (float(first_box.width), float(first_box.height))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="nz-visa-translation-") as temp_dir:
        declaration = Path(temp_dir) / "translator-details.pdf"
        build_declaration(declaration, page_size, profile)

        writer = PdfWriter()
        for source in args.translation_pages:
            reader = PdfReader(str(source))
            for page in reader.pages:
                writer.add_page(page)
        writer.add_page(PdfReader(str(declaration)).pages[0])
        writer.add_metadata({
            "/Title": args.title,
            "/Subject": "English visa-document translation",
            "/Author": profile["name"],
        })
        with args.output.open("wb") as stream:
            writer.write(stream)

    limit = int(args.max_mb * 1024 * 1024)
    if args.output.stat().st_size > limit:
        raise ValueError(f"输出文件超过 {args.max_mb:g} MB：{args.output}")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
