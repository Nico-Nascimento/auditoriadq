"""Área Anotações: bloco de notas com formatação (cor, marca-texto, negrito e itálico).

O conteúdo é salvo automaticamente em anotacoes.html, na pasta de dados do usuário.
"""
from __future__ import annotations

import re
from pathlib import Path

from PySide6.QtCore import QMimeData, QSettings, Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QIcon,
    QKeySequence,
    QPainter,
    QPixmap,
    QShortcut,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .zoom import FontZoom, ZoomControls

# Cores escolhidas para ficarem legíveis no modo claro e no modo escuro
TEXT_COLORS = [
    ("Vermelho", "#E53935"),
    ("Laranja", "#F57C00"),
    ("Verde", "#2E9E44"),
    ("Azul", "#1E88E5"),
    ("Roxo", "#8E24AA"),
]
HIGHLIGHT_COLORS = [
    ("Amarelo", "#FFE066"),
    ("Verde", "#A5E8A0"),
    ("Azul", "#A8D8FF"),
    ("Rosa", "#FFB3D1"),
    ("Laranja", "#FFCC99"),
]
HIGHLIGHT_TEXT = "#1F2430"
BOLD = QFont.Weight.Bold.value


def _pid(prop) -> int:
    """Número da propriedade de formatação (aceito por todas as versões do PySide6)."""
    return prop.value if hasattr(prop, "value") else int(prop)  # texto escuro sobre o marca-texto (legível nos dois modos)


def _swatch(color: str, underline: bool = False) -> QIcon:
    pix = QPixmap(16, 16)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QColor("#7f8a99"))
    p.setBrush(QColor(color))
    if underline:
        p.drawRoundedRect(1, 11, 14, 4, 1, 1)
    else:
        p.drawRoundedRect(1, 1, 14, 14, 3, 3)
    p.end()
    return QIcon(pix)


def clean_html(html: str) -> str:
    """Remove fonte e tamanho fixos do HTML, para o zoom e o tema continuarem valendo."""
    html = re.sub(r"font-family:[^;\"]*;?", "", html)
    html = re.sub(r"font-size:[^;\"]*;?", "", html)
    return html


class NotesEditor(QTextEdit):
    def insertFromMimeData(self, source: QMimeData) -> None:
        # Cola sempre como texto simples, para não trazer fontes e cores de outros programas
        if source.hasText():
            self.textCursor().insertText(source.text())
        else:
            super().insertFromMimeData(source)

    def canInsertFromMimeData(self, source: QMimeData) -> bool:
        return source.hasText() or super().canInsertFromMimeData(source)


class NotesTab(QWidget):
    def __init__(self, path: Path, settings: QSettings | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.path = path

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ---------------- barra superior ----------------
        bar = QHBoxLayout()
        bar.setSpacing(6)
        self.btn_copy = QPushButton("Copiar tudo")
        self.btn_copy.clicked.connect(self.copy_all)
        bar.addWidget(self.btn_copy)
        bar.addSpacing(10)

        self.btn_bold = self._fmt_button("N", "Negrito (Ctrl + N ou Ctrl + B)")
        self.btn_bold.setStyleSheet("font-weight: 800; min-width: 18px;")
        self.btn_bold.clicked.connect(self.toggle_bold)
        self.btn_italic = self._fmt_button("I", "Itálico (Ctrl + I)")
        self.btn_italic.setStyleSheet("font-style: italic; font-family: Georgia, serif; min-width: 18px;")
        self.btn_italic.clicked.connect(self.toggle_italic)
        bar.addWidget(self.btn_bold)
        bar.addWidget(self.btn_italic)

        self.btn_color = self._menu_button("Cor do texto", "#E53935", underline=True)
        menu = QMenu(self.btn_color)
        for name, color in TEXT_COLORS:
            menu.addAction(_swatch(color), name, lambda c=color: self.set_text_color(c))
        menu.addSeparator()
        menu.addAction("Automática (padrão)", lambda: self.set_text_color(None))
        self.btn_color.setMenu(menu)
        bar.addWidget(self.btn_color)

        self.btn_mark = self._menu_button("Marca-texto", "#FFE066")
        menu = QMenu(self.btn_mark)
        for name, color in HIGHLIGHT_COLORS:
            menu.addAction(_swatch(color), name, lambda c=color: self.set_highlight(c))
        menu.addSeparator()
        menu.addAction("Sem marca-texto", lambda: self.set_highlight(None))
        self.btn_mark.setMenu(menu)
        bar.addWidget(self.btn_mark)

        self.btn_clear = self._fmt_button("Limpar formatação", "Remove cor, marca-texto, negrito e itálico do trecho selecionado")
        self.btn_clear.setCheckable(False)
        self.btn_clear.clicked.connect(self.clear_formatting)
        bar.addWidget(self.btn_clear)

        bar.addSpacing(10)
        self.status = QLabel("")
        self.status.setObjectName("hint")
        bar.addWidget(self.status)
        bar.addStretch(1)
        root.addLayout(bar)

        info = QLabel(
            "Espaço livre para anotações. Selecione um trecho para aplicar cor, marca-texto, negrito ou itálico. "
            "O conteúdo é salvo automaticamente neste computador."
        )
        info.setObjectName("hint")
        info.setWordWrap(True)
        root.addWidget(info)

        # ---------------- editor ----------------
        card = QFrame()
        card.setObjectName("card")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(6, 6, 6, 6)
        self.editor = NotesEditor()
        self.editor.setObjectName("bareEditor")
        self.editor.setFrameShape(QFrame.Shape.NoFrame)
        self.editor.setAcceptRichText(True)
        self.editor.setPlaceholderText("Digite suas anotações aqui…")
        cv.addWidget(self.editor)
        root.addWidget(card, 1)

        self.zoom = FontZoom(self.editor, settings, "fonte/anotacoes")
        bar.addWidget(ZoomControls(self.zoom))

        for seq, fn in (("Ctrl+B", self.toggle_bold), ("Ctrl+N", self.toggle_bold), ("Ctrl+I", self.toggle_italic)):
            sc = QShortcut(QKeySequence(seq), self.editor)
            sc.setContext(Qt.ShortcutContext.WidgetShortcut)
            sc.activated.connect(fn)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(600)
        self._save_timer.timeout.connect(self.save_now)

        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self.status.setText(""))

        self._load()
        self.editor.textChanged.connect(self._on_change)
        self.editor.currentCharFormatChanged.connect(self._sync_buttons)
        self._sync_buttons(self.editor.currentCharFormat())

    # ------------------------------------------------------------------
    def _fmt_button(self, text: str, tip: str) -> QPushButton:
        b = QPushButton(text)
        b.setProperty("toggle", True)
        b.setCheckable(True)
        b.setToolTip(tip)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return b

    def _menu_button(self, text: str, color: str, underline: bool = False) -> QToolButton:
        b = QToolButton()
        b.setObjectName("fmtMenu")
        b.setText(text)
        b.setIcon(_swatch(color, underline))
        b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return b

    # ------------------------------------------------------------------
    # Formatação
    # ------------------------------------------------------------------
    def _merge(self, fmt: QTextCharFormat) -> None:
        c = self.editor.textCursor()
        if not c.hasSelection():
            c.select(QTextCursor.SelectionType.WordUnderCursor)
        c.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _clear_props(self, props: list[QTextFormat.Property]) -> None:
        """Remove propriedades de formatação do trecho selecionado (ou da palavra sob o cursor)."""
        c = self.editor.textCursor()
        if not c.hasSelection():
            c.select(QTextCursor.SelectionType.WordUnderCursor)
        start, end = c.selectionStart(), c.selectionEnd()
        if start == end:
            fmt = self.editor.currentCharFormat()
            for p in props:
                fmt.clearProperty(_pid(p))
            self.editor.setCurrentCharFormat(fmt)
            return
        doc = self.editor.document()
        edit = QTextCursor(doc)
        edit.beginEditBlock()
        pos = start
        while pos < end:
            probe = QTextCursor(doc)
            probe.setPosition(pos + 1)
            fmt = probe.charFormat()
            # avança até o fim do trecho com a mesma formatação
            run_end = pos + 1
            while run_end < end:
                nxt = QTextCursor(doc)
                nxt.setPosition(run_end + 1)
                if nxt.charFormat() != fmt:
                    break
                run_end += 1
            for p in props:
                fmt.clearProperty(_pid(p))
            edit.setPosition(pos)
            edit.setPosition(run_end, QTextCursor.MoveMode.KeepAnchor)
            edit.setCharFormat(fmt)
            pos = run_end
        edit.endEditBlock()
        self.editor.setFocus()

    def toggle_bold(self) -> None:
        fmt = QTextCharFormat()
        bold = self.editor.fontWeight() < BOLD
        fmt.setFontWeight(BOLD if bold else QFont.Weight.Normal.value)
        self._merge(fmt)

    def toggle_italic(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self._merge(fmt)

    def set_text_color(self, color: str | None) -> None:
        if color is None:
            self._clear_props([QTextFormat.Property.ForegroundBrush])
        else:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            self._merge(fmt)

    def set_highlight(self, color: str | None) -> None:
        if color is None:
            self._clear_props([QTextFormat.Property.BackgroundBrush])
        else:
            fmt = QTextCharFormat()
            fmt.setBackground(QColor(color))
            # Sem cor própria, o texto fica escuro sobre o marca-texto (legível também no modo escuro)
            if not self.editor.currentCharFormat().hasProperty(_pid(QTextFormat.Property.ForegroundBrush)):
                fmt.setForeground(QColor(HIGHLIGHT_TEXT))
            self._merge(fmt)

    def clear_formatting(self) -> None:
        self._clear_props([
            QTextFormat.Property.ForegroundBrush,
            QTextFormat.Property.BackgroundBrush,
            QTextFormat.Property.FontWeight,
            QTextFormat.Property.FontItalic,
        ])

    def _sync_buttons(self, fmt: QTextCharFormat) -> None:
        self.btn_bold.setChecked(fmt.fontWeight() >= BOLD)
        self.btn_italic.setChecked(fmt.fontItalic())

    # ------------------------------------------------------------------
    # Arquivo
    # ------------------------------------------------------------------
    def _load(self) -> None:
        old_txt = self.path.with_suffix(".txt")
        try:
            if self.path.exists():
                self.editor.setHtml(self.path.read_text(encoding="utf-8"))
            elif old_txt.exists():  # versões anteriores salvavam texto simples
                self.editor.setPlainText(old_txt.read_text(encoding="utf-8"))
        except OSError:
            pass
        self.editor.document().setModified(False)

    def _on_change(self) -> None:
        self.status.setText("Salvando…")
        self._save_timer.start()

    def save_now(self) -> None:
        self._save_timer.stop()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(clean_html(self.editor.toHtml()), encoding="utf-8")
            tmp.replace(self.path)
            self._flash("✔ Salvo")
        except OSError as exc:
            self.status.setText(f"⚠ Não foi possível salvar: {exc}")

    def _flash(self, msg: str) -> None:
        self.status.setText(msg)
        self._status_timer.start(2000)

    def copy_all(self) -> None:
        md = QMimeData()
        md.setHtml(clean_html(self.editor.toHtml()))  # colar no Word mantém as cores
        md.setText(self.editor.toPlainText())
        QGuiApplication.clipboard().setMimeData(md)
        self._flash("✔ Texto copiado para a área de transferência")
