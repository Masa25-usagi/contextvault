#!/usr/bin/env python3
"""クイックメモをContextVaultの受信箱へ保存する。"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re


VAULT = Path(__file__).resolve().parents[1]
INBOX = VAULT / "00_Inbox"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9一-龥ぁ-んァ-ンー]+", "-", text.strip()).strip("-")
    return slug[:60] or "note"


def main() -> None:
    parser = argparse.ArgumentParser(description="クイックメモをContextVaultへ保存します。")
    parser.add_argument("text", nargs="+", help="メモ本文")
    parser.add_argument("--source", default="", help="任意の出典URLまたはアプリ名")
    args = parser.parse_args()

    now = datetime.now()
    text = " ".join(args.text).strip()
    filename = f"{now:%Y%m%d-%H%M%S}-{slugify(text)}.md"
    path = INBOX / filename
    path.write_text(
        "\n".join(
            [
                f"# {text[:80]}",
                "",
                f"取得日時: {now:%Y-%m-%d %H:%M}",
                f"出典: {args.source}",
                "タグ: #受信箱",
                "",
                "## 生キャプチャ",
                "",
                text,
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(path)


if __name__ == "__main__":
    main()
