#!/usr/bin/env python3
"""受信箱の単純なノートをMarkdown文脈保管庫へ振り分ける。

このスクリプトは意図的に保守的です。LLMは呼び出さず、ファイルも削除しません。
明確なノートだけをキーワードで分類し、簡潔なリソース・プロジェクト・
アイデア・文脈ノートを作り、元の生ノートには処理記録を追記して
処理済みアーカイブへ移動します。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shutil


VAULT = Path(__file__).resolve().parents[1]
INBOX = VAULT / "00_Inbox"
ARCHIVE = VAULT / "90_Archive" / "Processed"

ROUTES = {
    "project": VAULT / "10_Projects",
    "idea": VAULT / "20_Ideas",
    "resource": VAULT / "30_Resources",
    "context": VAULT / "40_Context",
}

KEYWORDS = {
    "project": ["project", "プロジェクト", "案件", "タスク", "締切", "deadline", "milestone"],
    "idea": ["idea", "アイデア", "着想", "仮説", "concept", "思いついた"],
    "resource": ["http", "source", "記事", "動画", "youtube", "transcript", "資料", "reference"],
    "context": ["profile", "自分", "好み", "価値観", "口調", "working style", "context"],
}


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9一-龥ぁ-んァ-ンー]+", "-", text.strip()).strip("-")
    return slug[:70] or "note"


def classify(text: str) -> str:
    lower = text.lower()
    scores = {name: 0 for name in ROUTES}
    for name, words in KEYWORDS.items():
        scores[name] = sum(1 for word in words if word.lower() in lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "idea"


def title_from(text: str, fallback: str) -> str:
    for line in text.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean:
            return clean[:90]
    return fallback


def process_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    route = classify(text)
    target_dir = ROUTES[route]
    title = title_from(text, path.stem)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    target = target_dir / f"{slugify(title)}.md"

    if target.exists():
        with target.open("a", encoding="utf-8") as f:
            f.write("\n\n---\n")
            f.write(f"## Added From Inbox: {now}\n\n")
            f.write(text.strip() + "\n")
    else:
        target.write_text(
            "\n".join(
                [
                    f"# {title}",
                    "",
                    f"作成日時: {now}",
                    f"種類: {route}",
                    f"元受信箱ノート: [[{path.stem}]]",
                    "",
                    "## 要約",
                    "",
                    text.strip(),
                    "",
                    "## リンク",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    archive_path = ARCHIVE / path.name
    if archive_path.exists():
        archive_path = ARCHIVE / f"{path.stem}-{datetime.now():%H%M%S}{path.suffix}"

    with path.open("a", encoding="utf-8") as f:
        f.write("\n\n---\n")
        f.write(f"処理日時: {now}\n")
        f.write(f"振り分け先: {target.relative_to(VAULT)}\n")

    shutil.move(str(path), str(archive_path))
    print(f"{path.name} -> {target.relative_to(VAULT)}")


def main() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    notes = sorted(p for p in INBOX.glob("*.md") if p.is_file())
    if not notes:
        print("受信箱は空です。")
        return
    for path in notes:
        process_file(path)


if __name__ == "__main__":
    main()
