"""Zoom do texto (tamanho da letra) para os editores de Auditoria e Anotações.

Controles: botões A− / A+, clique no percentual para voltar a 100%,
Ctrl + roda do mouse, Ctrl + "+", Ctrl + "−" e Ctrl + 0.
O tamanho escolhido fica salvo em config.ini.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QSettings, Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics, QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

BASE_SIZE = 12
MIN_SIZE = 8
MAX_SIZE = 36


class FontZoom(QObject):
    sizeChanged = Signal(int)

    def __init__(self, editor, settings: QSettings | None, key: str, parent: QObject | None = None):
        super().__init__(parent or editor)
        self.editor = editor
        self.settings = settings
        self.key = key
        size = BASE_SIZE
        if settings is not None:
            try:
                size = int(settings.value(key, BASE_SIZE))
            except (TypeError, ValueError):
                size = BASE_SIZE
        self.size = BASE_SIZE
        self.set_size(size, save=False)

        editor.viewport().installEventFilter(self)
        for seq, fn in (
            ("Ctrl++", self.zoom_in),
            ("Ctrl+=", self.zoom_in),
            ("Ctrl+-", self.zoom_out),
            ("Ctrl+0", self.reset),
        ):
            sc = QShortcut(QKeySequence(seq), editor)
            sc.setContext(Qt.ShortcutContext.WidgetShortcut)
            sc.activated.connect(fn)

    # ------------------------------------------------------------------
    def set_size(self, size: int, save: bool = True) -> None:
        size = max(MIN_SIZE, min(MAX_SIZE, int(size)))
        self.size = size
        font = QFont(self.editor.font())
        font.setFamily("Segoe UI")
        font.setPointSize(size)
        self.editor.setFont(font)
        if hasattr(self.editor, "setTabStopDistance"):
            self.editor.setTabStopDistance(QFontMetrics(font).horizontalAdvance(" ") * 4)
        if save and self.settings is not None:
            self.settings.setValue(self.key, size)
        self.sizeChanged.emit(size)

    def zoom_in(self) -> None:
        self.set_size(self.size + 1)

    def zoom_out(self) -> None:
        self.set_size(self.size - 1)

    def reset(self) -> None:
        self.set_size(BASE_SIZE)

    def percent(self) -> int:
        return round(self.size / BASE_SIZE * 100)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.Wheel and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            dy = event.angleDelta().y()
            if dy > 0:
                self.zoom_in()
            elif dy < 0:
                self.zoom_out()
            return True
        return False


class ZoomControls(QWidget):
    """Botões A− [100%] A+ que controlam um FontZoom."""

    def __init__(self, zoom: FontZoom, parent: QWidget | None = None):
        super().__init__(parent)
        self.zoom = zoom
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        self.btn_out = QPushButton("A−")
        self.btn_out.setToolTip("Diminuir o tamanho do texto (Ctrl + −)")
        self.label = QPushButton()
        self.label.setToolTip("Tamanho do texto. Clique para voltar a 100% (Ctrl + 0)")
        self.btn_in = QPushButton("A+")
        self.btn_in.setToolTip("Aumentar o tamanho do texto (Ctrl + +). Também é possível usar Ctrl + roda do mouse.")
        for b in (self.btn_out, self.label, self.btn_in):
            b.setProperty("toggle", True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            lay.addWidget(b)
        self.label.setMinimumWidth(58)
        self.btn_out.clicked.connect(zoom.zoom_out)
        self.btn_in.clicked.connect(zoom.zoom_in)
        self.label.clicked.connect(zoom.reset)
        zoom.sizeChanged.connect(self._update)
        self._update(zoom.size)

    def _update(self, _size: int) -> None:
        self.label.setText(f"{self.zoom.percent()}%")
        self.btn_out.setEnabled(self.zoom.size > MIN_SIZE)
        self.btn_in.setEnabled(self.zoom.size < MAX_SIZE)
