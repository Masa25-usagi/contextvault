#!/usr/bin/env python3
"""ContextVaultの軽量メンテナンス確認。"""

from __future__ import annotations

from pathlib import Path
import re


VAULT = Path(__file__).resolve().parents[1]
MAX_WORDS = 1200


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def wiki_links(text: str) -> list[str]:
    return re.findall(r"\[\[([^\]|#]+)", text)


def main() -> None:
    notes = [p for p in VAULT.rglob("*.md") if ".obsidian" not in p.parts]
    note_stems = {p.stem for p in notes}

    large = []
    broken = []
    for path in notes:
        text = path.read_text(encoding="utf-8")
        count = word_count(text)
        if count > MAX_WORDS:
            large.append((path, count))
        for link in wiki_links(text):
            if link not in note_stems:
                broken.append((path, link))

    print("# ContextVault 週次メンテナンス")
    print("")
    print("## 大きすぎるノート")
    if large:
        for path, count in large:
            print(f"- {path.relative_to(VAULT)}: {count} words")
    else:
        print("- なし")

    print("")
    print("## 壊れたWikiリンク")
    if broken:
        for path, link in broken:
            print(f"- {path.relative_to(VAULT)} -> [[{link}]]")
    else:
        print("- なし")


if __name__ == "__main__":
    main()
