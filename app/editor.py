"""Aba Auditoria: editor de texto com modelo padrão e snippets no estilo do VS Code."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QRect, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetrics, QGuiApplication, QPainter, QTextCursor, QTextFormat
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .snippets import Snippet, is_word_char, parse_body
from .store import SnippetStore

TEMPLATE = (
    "Roi: \n"
    "--------------\n"
    "Espaços: \n"
    "--------------\n"
    "Preços: \n"
    "--------------\n"
    "Produtos: "
)

ROW_HEIGHT = 26
MAX_ROWS = 8
POPUP_WIDTH = 440
ROLE_DATA = int(Qt.ItemDataRole.UserRole) + 1
ROLE_TYPED = int(Qt.ItemDataRole.UserRole) + 2


def u16len(text: str) -> int:
    """Tamanho em unidades UTF-16 (é assim que o Qt conta posições no texto)."""
    return len(text.encode("utf-16-le")) // 2


# ---------------------------------------------------------------------------
# Lista de sugestões (parecida com a do VS Code)
# ---------------------------------------------------------------------------
class SuggestionDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index) -> None:
        prefix, name = index.data(ROLE_DATA)
        typed = index.data(ROLE_TYPED) or ""
        r = option.rect
        selected = bool(option.state & QStyle.StateFlag.State_Selected)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if selected:
            painter.setBrush(QColor("#04395E"))
            painter.setPen(QColor("#0E639C"))
            painter.drawRoundedRect(r.adjusted(1, 1, -1, -1), 4, 4)

        base_font = QFont(option.font)
        base_font.setPointSizeF(10.5)
        bold = QFont(base_font)
        bold.setBold(True)

        x = r.left() + 10
        # ícone simples de "snippet"
        painter.setPen(QColor("#C5C5C5"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        icon = QRect(x, r.center().y() - 6, 10, 12)
        painter.drawRect(icon)
        x += 20

        # prefixo: parte digitada em azul/negrito, resto normal
        n = min(len(typed), len(prefix)) if prefix.casefold().startswith(typed.casefold()) else 0
        typed_part, rest = prefix[:n], prefix[n:]
        painter.setFont(bold)
        painter.setPen(QColor("#4FC1FF"))
        painter.drawText(QRect(x, r.top(), r.width(), r.height()), int(Qt.AlignmentFlag.AlignVCenter), typed_part)
        x += QFontMetrics(bold).horizontalAdvance(typed_part)
        painter.setFont(base_font)
        painter.setPen(QColor("#D4D4D4"))
        painter.drawText(QRect(x, r.top(), r.width(), r.height()), int(Qt.AlignmentFlag.AlignVCenter), rest)

        # nome à direita
        painter.setPen(QColor("#CCCCCC") if selected else QColor("#9DA5B4"))
        name_rect = QRect(r.left() + 120, r.top(), r.width() - 132, r.height())
        elided = QFontMetrics(base_font).elidedText(name, Qt.TextElideMode.ElideRight, name_rect.width())
        painter.drawText(name_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight), elided)
        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        return QSize(POPUP_WIDTH - 10, ROW_HEIGHT)


class SuggestionPopup(QListWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("suggestions")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setItemDelegate(SuggestionDelegate(self))
        self.setUniformItemSizes(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self.matches: list[tuple[str, Snippet]] = []
        self.hide()

    def set_matches(self, matches: list[tuple[str, Snippet]], typed: str) -> None:
        self.matches = matches
        self.clear()
        for prefix, snip in matches:
            item = QListWidgetItem()
            item.setData(ROLE_DATA, (prefix, snip.name))
            item.setData(ROLE_TYPED, typed)
            item.setToolTip(parse_body(snip.body).text)
            self.addItem(item)
        self.setCurrentRow(0)
        rows = min(len(matches), MAX_ROWS)
        self.resize(POPUP_WIDTH, rows * ROW_HEIGHT + 8)

    def move_selection(self, delta: int) -> None:
        if not self.count():
            return
        row = (self.currentRow() + delta) % self.count()
        self.setCurrentRow(row)

    def current_match(self) -> tuple[str, Snippet] | None:
        row = self.currentRow()
        if 0 <= row < len(self.matches):
            return self.matches[row]
        return None


# ---------------------------------------------------------------------------
# Sessão de preenchimento dos campos de um snippet
# ---------------------------------------------------------------------------
@dataclass
class SnippetSession:
    fields: list[tuple[QTextCursor, QTextCursor]]  # (início, fim) de cada campo, em ordem de Tab
    start: QTextCursor
    end: QTextCursor  # fim do snippet ($0, se existir)
    index: int = -1


class AuditEditor(QPlainTextEdit):
    def __init__(self, store: SnippetStore, parent: QWidget | None = None):
        super().__init__(parent)
        self.store = store
        self.session: SnippetSession | None = None
        self._moving = False

        font = QFont("Segoe UI", 12)
        self.setFont(font)
        self.setTabStopDistance(QFontMetrics(font).horizontalAdvance(" ") * 4)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

        self.popup = SuggestionPopup(self)
        self.popup.itemClicked.connect(lambda _item: self.accept_suggestion())

        self.cursorPositionChanged.connect(self._on_cursor_moved)
        self.textChanged.connect(self._refresh_highlight)

        self.reset_template(initial=True)

    # ------------------------------------------------------------------
    # Modelo padrão
    # ------------------------------------------------------------------
    def reset_template(self, initial: bool = False) -> None:
        self.end_session()
        self.popup.hide()
        if initial:
            self.setPlainText(TEMPLATE)
        else:
            c = QTextCursor(self.document())
            c.beginEditBlock()
            c.select(QTextCursor.SelectionType.Document)
            c.insertText(TEMPLATE)  # mantém o Ctrl+Z disponível
            c.endEditBlock()
        c = self.textCursor()
        c.setPosition(u16len("Roi: "))
        self.setTextCursor(c)
        self.setFocus()

    def is_template(self) -> bool:
        return self.toPlainText().strip() == TEMPLATE.strip()

    # ------------------------------------------------------------------
    # Palavra digitada antes do cursor
    # ------------------------------------------------------------------
    def _current_word(self) -> tuple[int, str]:
        c = self.textCursor()
        if c.hasSelection():
            return c.position(), ""
        doc = self.document()
        pos = c.position()
        if is_word_char(doc.characterAt(pos)):  # cursor no meio de uma palavra
            return pos, ""
        start = pos
        while start > 0 and is_word_char(doc.characterAt(start - 1)):
            start -= 1
        if start == pos:
            return pos, ""
        w = QTextCursor(doc)
        w.setPosition(start)
        w.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
        return start, w.selectedText()

    # ------------------------------------------------------------------
    # Lista de sugestões
    # ------------------------------------------------------------------
    def _update_popup(self, open_if_hidden: bool) -> None:
        if not open_if_hidden and not self.popup.isVisible():
            return
        _start, word = self._current_word()
        matches = self.store.matches(word) if word else []
        if not matches:
            self.popup.hide()
            return
        self.popup.set_matches(matches, word)
        self._place_popup()
        self.popup.show()
        self.popup.raise_()

    def _place_popup(self) -> None:
        rect = self.cursorRect()
        top_left = self.viewport().mapTo(self, rect.bottomLeft())
        x = top_left.x() - 30
        y = top_left.y() + 4
        h = self.popup.height()
        if y + h > self.height() - 4:  # sem espaço embaixo: abre acima da linha
            y = self.viewport().mapTo(self, rect.topLeft()).y() - h - 4
        x = max(4, min(x, self.width() - self.popup.width() - 4))
        y = max(4, y)
        self.popup.move(x, y)

    def accept_suggestion(self) -> None:
        match = self.popup.current_match()
        self.popup.hide()
        if match is None:
            return
        _prefix, snippet = match
        start, word = self._current_word()
        self.insert_snippet(snippet, replace_from=start)

    # ------------------------------------------------------------------
    # Inserção do snippet e navegação pelos campos
    # ------------------------------------------------------------------
    def _cursor_at(self, pos: int, keep_on_insert: bool) -> QTextCursor:
        c = QTextCursor(self.document())
        c.setPosition(pos)
        c.setKeepPositionOnInsert(keep_on_insert)
        return c

    def insert_snippet(self, snippet: Snippet, replace_from: int | None = None) -> None:
        self.end_session()
        parsed = parse_body(snippet.body)
        text = parsed.text

        c = self.textCursor()
        pos = c.position()
        base = replace_from if replace_from is not None else pos
        c.beginEditBlock()
        c.setPosition(base)
        c.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
        c.insertText(text)
        c.endEditBlock()

        def doc_pos(py_index: int) -> int:
            return base + u16len(text[:py_index])

        end_pos = doc_pos(parsed.final) if parsed.final is not None else doc_pos(len(text))

        if not parsed.tabstops:
            c = self.textCursor()
            c.setPosition(end_pos)
            self.setTextCursor(c)
            return

        fields = [
            (self._cursor_at(doc_pos(f.start), True), self._cursor_at(doc_pos(f.end), False))
            for f in parsed.tabstops
        ]
        self.session = SnippetSession(
            fields=fields,
            start=self._cursor_at(base, True),
            end=self._cursor_at(end_pos, False),
        )
        self.goto_field(+1)

    def goto_field(self, step: int) -> None:
        s = self.session
        if s is None:
            return
        idx = s.index + step
        if idx < 0:
            idx = 0
        if idx >= len(s.fields):  # passou do último campo: vai para o fim do snippet
            end = s.end.position()
            self.end_session()
            c = self.textCursor()
            c.setPosition(end)
            self.setTextCursor(c)
            return
        s.index = idx
        start_c, end_c = s.fields[idx]
        c = self.textCursor()
        c.setPosition(start_c.position())
        c.setPosition(end_c.position(), QTextCursor.MoveMode.KeepAnchor)
        self._moving = True
        self.setTextCursor(c)
        self._moving = False
        self._refresh_highlight()

    def end_session(self) -> None:
        if self.session is not None:
            self.session = None
            self._refresh_highlight()

    def _on_cursor_moved(self) -> None:
        if self.popup.isVisible():
            # mantém a lista só enquanto o cursor continua na palavra digitada
            QTimer.singleShot(0, lambda: self._update_popup(open_if_hidden=False))
        if self.session is None or self._moving:
            return
        p = self.textCursor().position()
        if p < self.session.start.position() or p > self.session.end.position():
            self.end_session()

    def _refresh_highlight(self) -> None:
        selections = []
        s = self.session
        if s is not None:
            for i, (a, b) in enumerate(s.fields):
                sel = QTextEdit.ExtraSelection()
                cur = QTextCursor(self.document())
                cur.setPosition(a.position())
                cur.setPosition(b.position(), QTextCursor.MoveMode.KeepAnchor)
                sel.cursor = cur
                fmt = sel.format
                if i == s.index:
                    fmt.setBackground(QColor(255, 194, 26, 110))
                else:
                    fmt.setBackground(QColor(68, 110, 155, 45))
                fmt.setProperty(QTextFormat.Property.FullWidthSelection, False)
                sel.format = fmt
                selections.append(sel)
        self.setExtraSelections(selections)

    # ------------------------------------------------------------------
    # Teclado e mouse
    # ------------------------------------------------------------------
    def keyPressEvent(self, e) -> None:
        key = e.key()
        mods = e.modifiers()
        shift = bool(mods & Qt.KeyboardModifier.ShiftModifier)
        plain_tab = key == Qt.Key.Key_Tab and not shift and not (mods & Qt.KeyboardModifier.ControlModifier)

        if key == Qt.Key.Key_Space and (mods & Qt.KeyboardModifier.ControlModifier):
            self._update_popup(open_if_hidden=True)  # Ctrl+Espaço abre as sugestões, como no VS Code
            return

        if self.popup.isVisible():
            if key == Qt.Key.Key_Down:
                self.popup.move_selection(+1)
                return
            if key == Qt.Key.Key_Up:
                self.popup.move_selection(-1)
                return
            if key == Qt.Key.Key_Escape:
                self.popup.hide()
                return
            # Enter sempre aceita. Tab aceita quando não há campos sendo preenchidos
            # (dentro de um snippet, o Tab continua indo para o próximo campo).
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) or (plain_tab and self.session is None):
                self.accept_suggestion()
                return

        if self.session is not None:
            if plain_tab:
                self.popup.hide()
                self.goto_field(+1)
                return
            if key == Qt.Key.Key_Backtab or (key == Qt.Key.Key_Tab and shift):
                self.popup.hide()
                self.goto_field(-1)
                return
            if key == Qt.Key.Key_Escape:
                self.end_session()
                return

        super().keyPressEvent(e)

        text = e.text()
        if text and text.isprintable() and is_word_char(text[-1]):
            self._update_popup(open_if_hidden=True)
        elif self.popup.isVisible():
            self._update_popup(open_if_hidden=False)

    def mousePressEvent(self, e) -> None:
        self.popup.hide()
        super().mousePressEvent(e)

    def focusOutEvent(self, e) -> None:
        self.popup.hide()
        super().focusOutEvent(e)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        if self.popup.isVisible():
            self._place_popup()

    def scrollContentsBy(self, dx: int, dy: int) -> None:
        super().scrollContentsBy(dx, dy)
        if self.popup.isVisible():
            self._place_popup()


# ---------------------------------------------------------------------------
# A aba completa
# ---------------------------------------------------------------------------
class AuditTab(QWidget):
    def __init__(self, store: SnippetStore, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        bar = QHBoxLayout()
        self.btn_copy = QPushButton("Copiar tudo")
        self.btn_copy.clicked.connect(self.copy_all)
        self.btn_reset = QPushButton("Resetar formato")
        self.btn_reset.clicked.connect(self.reset_format)
        bar.addWidget(self.btn_copy)
        bar.addWidget(self.btn_reset)
        bar.addSpacing(12)
        self.status = QLabel("")
        self.status.setObjectName("hint")
        bar.addWidget(self.status)
        bar.addStretch(1)
        hint = QLabel("Digite um prefixo (ex.: <b>dp1</b>, <b>cr</b>) e aperte <b>Tab</b> · "
                      "<b>Tab</b>/<b>Shift+Tab</b> navegam pelos campos · <b>Esc</b> sai")
        hint.setObjectName("hint")
        bar.addWidget(hint)
        root.addLayout(bar)

        card = QFrame()
        card.setObjectName("card")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(6, 6, 6, 6)
        self.editor = AuditEditor(store)
        self.editor.setFrameShape(QFrame.Shape.NoFrame)
        self.editor.setStyleSheet("QPlainTextEdit { border: none; padding: 10px; }")
        cv.addWidget(self.editor)
        root.addWidget(card, 1)

        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self.status.setText(""))

    def _flash(self, msg: str) -> None:
        self.status.setText(msg)
        self._status_timer.start(2500)

    def copy_all(self) -> None:
        QGuiApplication.clipboard().setText(self.editor.toPlainText())
        self._flash("✔ Texto copiado")

    def reset_format(self) -> None:
        if not self.editor.is_template():
            ans = QMessageBox.question(
                self,
                "Resetar formato",
                "Isso apaga o texto atual e volta ao modelo padrão.\n"
                "(Se mudar de ideia, use Ctrl+Z no editor.)\n\nContinuar?",
            )
            if ans != QMessageBox.StandardButton.Yes:
                return
        self.editor.reset_template()
        self._flash("✔ Formato restaurado")
