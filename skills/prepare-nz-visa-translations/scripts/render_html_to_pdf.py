#!/usr/bin/env python3
"""使用 Chromium 浏览器将本地 HTML 重建页打印为 PDF。"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


MAC_BROWSERS = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
)


def find_browser(explicit: str | None) -> str:
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            return str(path)
        resolved = shutil.which(explicit)
        if resolved:
            return resolved
        raise FileNotFoundError(f"找不到浏览器：{explicit}")
    for path in MAC_BROWSERS:
        if path.is_file():
            return str(path)
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        resolved = shutil.which(name)
        if resolved:
            return resolved
    raise FileNotFoundError("找不到 Chrome、Chromium 或 Edge 可执行文件")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_html", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--browser")
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    source = args.input_html.expanduser().resolve()
    output = args.output_pdf.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    browser = find_browser(args.browser)

    with tempfile.TemporaryDirectory(prefix="nz-visa-browser-") as profile:
        command = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-background-networking",
            "--allow-file-access-from-files",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={output}",
            source.as_uri(),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "浏览器打印 PDF 失败")
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"浏览器没有生成 PDF：{output}")
    print(output)


if __name__ == "__main__":
    main()
