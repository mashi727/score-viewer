# score-viewer

楽譜PDFのフォルダを開き、左のツリーからシングルクリックで右にPDFを表示。
ファイル名から曲名を抽出し、**⌘C / Ctrl+C** でクリップボードへコピーする軽量ビューア。

例: `112_Beethoven's 9th - 4th Horn in F -2024-11-08.pdf` → 曲名 `112_Beethoven's 9th`

PySide6 + QtPdf 製。区切り（`-` / `_` / 空白）、Horn 前後の序数、日付、`のコピー`、
`1,3` のようなパート番号の揺れを吸収して曲名だけを取り出す（曲名側の "9th" や
年 "2025" は保持する）。抽出規則は `src/score_viewer/naming.py`。

## 導入・実行（uv）

CLI として使う（推奨。仮想環境は uv 管理・プロジェクト外）:

```bash
uv tool install --editable .        # score-viewer コマンドを導入（ソース編集が即反映）
score-viewer <楽譜ディレクトリ>       # 引数なしならフォルダ選択ダイアログ
```

開発時にそのまま動かす:

```bash
uv run score-viewer <楽譜ディレクトリ>
uv run pytest                        # 曲名抽出のテスト
```

## 使い方

- 左ペイン: 指定ディレクトリ配下の PDF をツリー表示（PDF 以外は非表示）
- シングルクリック: 右ペインに PDF 表示（複数ページ・幅フィット）
- **⌘C / Ctrl+C**: 選択中の曲名をコピー（曲名はタイトルバーとステータスバーに表示）
