"""Peças de layout compartilhadas pelas áreas.

Padrão de cada área (de cima para baixo):
  1. barra de botões (FlowLayout: os botões passam para a linha de baixo se a janela ficar estreita)
  2. texto explicativo da área (com quebra de linha)
  3. linha de confirmação das ações (espaço reservado, que nunca altera o tamanho da janela)
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt, QTimer
from PySide6.QtWidgets import QLabel, QLayout, QSizePolicy, QWidget, QWidgetItem


class FlowLayout(QLayout):
    """Organiza os itens em linha e quebra para a próxima linha quando falta espaço."""

    def __init__(self, parent: QWidget | None = None, spacing: int = 8):
        super().__init__(parent)
        self._items: list = []
        self._spacing = spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item) -> None:
        self._items.append(item)

    def addWidget(self, widget: QWidget) -> None:  # type: ignore[override]
        self.addChildWidget(widget)
        self.addItem(QWidgetItem(widget))

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index: int):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        m = self.contentsMargins()
        area = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y = area.x(), area.y()
        line_height = 0
        for item in self._items:
            if item.isEmpty():
                continue
            hint = item.sizeHint()
            next_x = x + hint.width() + self._spacing
            if next_x - self._spacing > area.right() + 1 and line_height > 0:
                x = area.x()
                y = y + line_height + self._spacing
                next_x = x + hint.width() + self._spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            line_height = max(line_height, hint.height())
        return y + line_height - rect.y() + m.bottom()


def hint_label(text: str) -> QLabel:
    """Texto explicativo da área, com quebra de linha (não força a largura da janela)."""
    label = QLabel(text)
    label.setObjectName("hint")
    label.setWordWrap(True)
    label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    label.setMinimumWidth(50)
    return label


class StatusLine(QLabel):
    """Linha de confirmação das ações ('✔ Texto copiado…'). Some sozinha depois de alguns segundos."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("statusLine")
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.fontMetrics().height() + 6)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(lambda: self.setText(""))

    def flash(self, msg: str, ms: int = 2500) -> None:
        self.setText(msg)
        self._timer.start(ms)

    def show_message(self, msg: str) -> None:
        """Mostra uma mensagem que fica até a próxima (ex.: 'Salvando…')."""
        self._timer.stop()
        self.setText(msg)
