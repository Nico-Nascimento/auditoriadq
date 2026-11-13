"""Aba Anotações: um bloco de notas livre, salvo automaticamente no computador."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QFontMetrics, QGuiApplication
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class NotesTab(QWidget):
    def __init__(self, path: Path, parent: QWidget | None = None):
        super().__init__(parent)
        self.path = path

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        bar = QHBoxLayout()
        self.btn_copy = QPushButton("Copiar tudo")
        self.btn_copy.clicked.connect(self.copy_all)
        bar.addWidget(self.btn_copy)
        bar.addSpacing(12)
        self.status = QLabel("")
        self.status.setObjectName("hint")
        bar.addWidget(self.status)
        bar.addStretch(1)
        info = QLabel("Anote o que quiser: tudo é salvo automaticamente no seu computador.")
        info.setObjectName("hint")
        bar.addWidget(info)
        root.addLayout(bar)

        card = QFrame()
        card.setObjectName("card")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(6, 6, 6, 6)
        self.editor = QPlainTextEdit()
        self.editor.setObjectName("bareEditor")
        self.editor.setFrameShape(QFrame.Shape.NoFrame)
        font = QFont("Segoe UI", 12)
        self.editor.setFont(font)
        self.editor.setTabStopDistance(QFontMetrics(font).horizontalAdvance(" ") * 4)
        self.editor.setPlaceholderText("Escreva suas anotações aqui…")
        cv.addWidget(self.editor)
        root.addWidget(card, 1)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(600)
        self._save_timer.timeout.connect(self.save_now)

        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self.status.setText(""))

        self._load()
        self.editor.textChanged.connect(self._on_change)

    def _load(self) -> None:
        try:
            text = self.path.read_text(encoding="utf-8") if self.path.exists() else ""
        except OSError:
            text = ""
        self.editor.setPlainText(text)

    def _on_change(self) -> None:
        self.status.setText("Salvando…")
        self._save_timer.start()

    def save_now(self) -> None:
        self._save_timer.stop()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(self.editor.toPlainText(), encoding="utf-8")
            tmp.replace(self.path)
            self._flash("✔ Salvo")
        except OSError as exc:
            self.status.setText(f"⚠ Não foi possível salvar: {exc}")

    def _flash(self, msg: str) -> None:
        self.status.setText(msg)
        self._status_timer.start(2000)

    def copy_all(self) -> None:
        QGuiApplication.clipboard().setText(self.editor.toPlainText())
        self._flash("✔ Texto copiado")
