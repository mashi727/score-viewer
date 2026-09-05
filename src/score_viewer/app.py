"""楽譜PDFビューア + 曲名抽出コピー。

  score-viewer <楽譜ディレクトリ>

左は「現在フォルダの一覧」（先頭に `..`＝親フォルダ、続いてサブフォルダ、PDF）。
PDF をシングルクリックで右に表示。選択中の曲名（ファイル名から抽出）を
⌘C / Ctrl+C でクリップボードへコピーする。

  操作:
    `..` をダブルクリック     … 親フォルダへ
    フォルダをダブルクリック   … その中へ
    📂 / ⌘O                 … 任意のフォルダを開く
    ⌘↑                      … 親フォルダへ
    PDF をシングルクリック     … 右に表示
    ⌘C / Ctrl+C             … 曲名をコピー
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView

from .naming import extract_song_name


class ScoreViewer(QMainWindow):
    def __init__(self, directory: str):
        super().__init__()
        self.setWindowTitle("Score Viewer")
        self.resize(1200, 800)
        self._current_song = ""
        self._root = str(Path(directory).resolve())

        # 左: ナビバー + フォルダ一覧
        self._list = QListWidget()
        self._list.itemClicked.connect(self._on_item_clicked)          # 単: PDFを表示
        self._list.itemDoubleClicked.connect(self._on_item_double)     # 双: 移動 or 表示

        open_btn = QToolButton()
        open_btn.setText("📂")
        open_btn.setToolTip("フォルダを開く (⌘O)")
        open_btn.clicked.connect(self._open_folder)
        self._path_label = QLabel()
        self._path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        nav = QHBoxLayout()
        nav.setContentsMargins(2, 2, 2, 0)
        nav.addWidget(open_btn)
        nav.addWidget(self._path_label, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        left_layout.addLayout(nav)
        left_layout.addWidget(self._list)

        # 右: PDF ビュー（複数ページ・幅フィット）
        self._doc = QPdfDocument(self)
        self._pdf = QPdfView()
        self._pdf.setDocument(self._doc)
        self._pdf.setPageMode(QPdfView.PageMode.MultiPage)
        self._pdf.setZoomMode(QPdfView.ZoomMode.FitToWidth)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(self._pdf)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([340, 860])
        self.setCentralWidget(splitter)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("PDF を選択 → ⌘C / Ctrl+C で曲名をコピー")

        # ショートカット
        QShortcut(QKeySequence(QKeySequence.StandardKey.Copy), self).activated.connect(
            self._copy_song_name
        )
        QShortcut(QKeySequence(QKeySequence.StandardKey.Open), self).activated.connect(
            self._open_folder
        )
        QShortcut(QKeySequence("Ctrl+Up"), self).activated.connect(self._go_up)

        self._set_root(self._root)

    # ---- フォルダ一覧の再構築 ----

    def _set_root(self, path: str) -> None:
        path = str(Path(path).resolve())
        if not Path(path).is_dir():
            return
        self._root = path
        self._path_label.setText(Path(path).name or path)
        self._path_label.setToolTip(path)
        self.setWindowTitle(f"{Path(path).name} — Score Viewer")

        self._list.clear()
        style = self.style()
        # 先頭に `..`（親フォルダ）。ファイルシステム最上位では出さない
        parent = str(Path(path).parent)
        if parent != path:
            up = QListWidgetItem(
                style.standardIcon(QStyle.StandardPixmap.SP_FileDialogToParent), ".."
            )
            up.setData(Qt.ItemDataRole.UserRole, parent)
            self._list.addItem(up)

        try:
            entries = list(Path(path).iterdir())
        except OSError:
            entries = []
        dirs = sorted(
            (p for p in entries if p.is_dir() and not p.name.startswith(".")),
            key=lambda p: p.name.lower(),
        )
        pdfs = sorted(
            (p for p in entries if p.is_file() and p.suffix.lower() == ".pdf"),
            key=lambda p: p.name.lower(),
        )
        for p in dirs:
            it = QListWidgetItem(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon), p.name)
            it.setData(Qt.ItemDataRole.UserRole, str(p))
            self._list.addItem(it)
        for p in pdfs:
            it = QListWidgetItem(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), p.name)
            it.setData(Qt.ItemDataRole.UserRole, str(p))
            self._list.addItem(it)

    def _go_up(self) -> None:
        parent = str(Path(self._root).parent)
        if parent and parent != self._root:
            self._set_root(parent)

    def _open_folder(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "フォルダを開く", self._root)
        if chosen:
            self._set_root(chosen)

    # ---- 一覧操作 ----

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and Path(path).is_file() and path.lower().endswith(".pdf"):
            self._view_pdf(path)

    def _on_item_double(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path:
            return
        if Path(path).is_dir():
            self._set_root(path)          # `..` もフォルダも同じ経路で移動
        elif path.lower().endswith(".pdf"):
            self._view_pdf(path)

    def _view_pdf(self, path: str) -> None:
        self._doc.load(path)
        self._current_song = extract_song_name(Path(path).name)
        self.setWindowTitle(f"{self._current_song} — Score Viewer")
        self.statusBar().showMessage(
            f"曲名: {self._current_song}    （⌘C / Ctrl+C でコピー）"
        )

    def _copy_song_name(self) -> None:
        if not self._current_song:
            return
        QApplication.clipboard().setText(self._current_song)
        self.statusBar().showMessage(f"コピーしました: {self._current_song}", 3000)


def main() -> int:
    app = QApplication(sys.argv)
    positional = [a for a in app.arguments()[1:] if not a.startswith("-")]
    directory = positional[0] if positional else QFileDialog.getExistingDirectory(
        None, "楽譜フォルダを選択"
    )
    if not directory:
        print("ディレクトリが指定されていません", file=sys.stderr)
        return 1
    directory = str(Path(directory).expanduser().resolve())
    if not Path(directory).is_dir():
        print(f"ディレクトリではありません: {directory}", file=sys.stderr)
        return 1

    win = ScoreViewer(directory)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
