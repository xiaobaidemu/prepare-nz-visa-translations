#!/usr/bin/env python3
"""校验签证英文翻译 PDF，并可选择渲染每一页。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = SKILL_DIR / "assets" / "translator-profile.json"
EXAMPLE_PROFILE = SKILL_DIR / "assets" / "translator-profile.example.json"
DEFAULT_FORBIDDEN = (
    "not stated",
    "not provided",
    "unknown",
    "[placeholder]",
    "i declare that this english translation",
    "complete and accurate to the best",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--max-mb", type=float, default=10.0)
    parser.add_argument("--english-only", action="store_true")
    parser.add_argument("--forbid-certified", action="store_true")
    parser.add_argument("--forbid", action="append", default=[])
    parser.add_argument("--render-dir", type=Path)
    args = parser.parse_args()

    path = args.pdf.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size > args.max_mb * 1024 * 1024:
        raise ValueError(f"PDF 超过 {args.max_mb:g} MB")

    reader = PdfReader(str(path))
    if args.expected_pages is not None and len(reader.pages) != args.expected_pages:
        raise ValueError(f"预期 {args.expected_pages} 页，实际 {len(reader.pages)} 页")
    if not reader.pages:
        raise ValueError("PDF 没有页面")

    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    normalized_text = re.sub(r"\s+", " ", text).strip()
    lowered = normalized_text.lower()
    forbidden = [*DEFAULT_FORBIDDEN, *(value.lower() for value in args.forbid)]
    if args.forbid_certified:
        forbidden.append("certified")
    hits = sorted({term for term in forbidden if term and term in lowered})
    if hits:
        raise ValueError(f"发现禁止出现的文字：{', '.join(hits)}")
    if args.english_only and re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text):
        raise ValueError("可提取文本层中仍含中文字符")

    if not args.profile.is_file():
        raise FileNotFoundError(
            f"找不到译者资料：{args.profile}。请复制 {EXAMPLE_PROFILE}，填写真实资料后通过 --profile 传入。"
        )
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    required = [str(profile[key]) for key in ("name", "telephone", "address", "qualification")]
    missing = [
        value
        for value in required
        if re.sub(r"\s+", " ", value).strip() not in normalized_text
    ]
    if missing:
        raise ValueError(f"缺少译者信息：{missing}")

    if args.render_dir:
        try:
            import pypdfium2 as pdfium
        except ImportError as error:
            raise RuntimeError("使用 --render-dir 前需要安装 pypdfium2") from error
        render_dir = args.render_dir.expanduser().resolve()
        render_dir.mkdir(parents=True, exist_ok=True)
        document = pdfium.PdfDocument(str(path))
        for index in range(len(document)):
            output = render_dir / f"{path.stem}-page-{index + 1}.png"
            document[index].render(scale=2).to_pil().save(output)

    print(f"{path} pages={len(reader.pages)} bytes={path.stat().st_size} validated=true")


if __name__ == "__main__":
    main()
