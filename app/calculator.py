"""Aba Calculadora 40%: várias imagens, uma marcação por imagem.

Botão esquerdo: marca (desenha, move e redimensiona o retângulo).
Botão direito: arrasta (a imagem embaixo do mouse ou, no fundo vazio, a vista inteira).
Roda do mouse: zoom.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QGuiApplication,
    QImage,
    QKeySequence,
    QPainter,
    QPen,
    QPixmap,
    QShortcut,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFrame,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .geometry import Box, forty, handle_points, normalize, resize
from . import theme
from .theme import AMARELO, AZUL, AZUL_ESCURO

HANDLE_PX = 10  # tamanho das alças na tela (não muda com o zoom)
GAP = 40  # espaço entre imagens novas
MIN_SCALE, MAX_SCALE, ZOOM_STEP = 0.2, 10.0, 1.05
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff"}

COLOR_HEIGHT_BAND = QColor(68, 110, 155, round(0.25 * 255))
COLOR_WIDTH_BAND = QColor(255, 194, 26, round(0.35 * 255))


def _qrect(b: Box) -> QRectF:
    return QRectF(b.x, b.y, b.w, b.h)


class ImageItem(QGraphicsItem):
    """Uma imagem e a sua marcação (o retângulo acompanha a imagem)."""

    def __init__(self, pixmap: QPixmap, name: str = ""):
        super().__init__()
        self.pixmap = pixmap
        self.name = name
        self.mark: Box | None = None
        self.h_side = "left"  # Esquerda / Direita
        self.v_side = "top"  # Superior / Inferior
        self.is_selected = False
        self.view_scale = 1.0

    # ---------------- geometria ----------------
    def image_rect(self) -> QRectF:
        return QRectF(0, 0, self.pixmap.width(), self.pixmap.height())

    def _margin(self) -> float:
        return (HANDLE_PX + 8) / self.view_scale + 4

    def boundingRect(self) -> QRectF:
        r = self.image_rect()
        if self.mark is not None:
            r = r.united(_qrect(self.mark))
        m = self._margin()
        return r.adjusted(-m, -m, m, m)

    def set_view_scale(self, s: float) -> None:
        self.prepareGeometryChange()
        self.view_scale = s

    def set_mark(self, box: Box | None) -> None:
        self.prepareGeometryChange()
        self.mark = box
        self.update()

    def hit(self, p: QPointF) -> bool:
        if self.image_rect().contains(p):
            return True
        if self.mark is not None:
            m = HANDLE_PX / self.view_scale
            return _qrect(self.mark).adjusted(-m, -m, m, m).contains(p)
        return False

    def handle_at(self, p: QPointF) -> str | None:
        if self.mark is None or not self.is_selected:
            return None
        half = (HANDLE_PX / 2 + 3) / self.view_scale
        for name, (hx, hy) in handle_points(self.mark).items():
            if abs(p.x() - hx) <= half and abs(p.y() - hy) <= half:
                return name
        return None

    # ---------------- desenho ----------------
    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self.pixmap)

        if self.is_selected:
            pen = QPen(QColor(AZUL), 2, Qt.PenStyle.DashLine)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            d = 3 / self.view_scale
            painter.drawRect(self.image_rect().adjusted(-d, -d, d, d))

        if self.mark is None:
            return
        r = self.mark
        f = forty(r, self.h_side, self.v_side)

        # faixas de 40%
        painter.fillRect(_qrect(f.vertical_overlay), COLOR_HEIGHT_BAND)
        painter.fillRect(_qrect(f.horizontal_overlay), COLOR_WIDTH_BAND)

        # retângulo principal
        pen = QPen(QColor(AZUL_ESCURO), 3)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(_qrect(r))

        # linhas de divisa dos 40%
        painter.setPen(QPen(QColor(AZUL), 3))
        painter.drawLine(QPointF(r.x, f.horizontal_line_y), QPointF(r.right, f.horizontal_line_y))
        painter.setPen(QPen(QColor(AMARELO), 3))
        painter.drawLine(QPointF(f.vertical_line_x, r.y), QPointF(f.vertical_line_x, r.bottom))

        # alças (só na imagem selecionada)
        if self.is_selected:
            border = QPen(QColor(AZUL), 1)
            border.setCosmetic(True)
            painter.setPen(border)
            painter.drawRect(_qrect(r))
            hp = QPen(QColor("#000000"), 1)
            hp.setCosmetic(True)
            painter.setPen(hp)
            painter.setBrush(QBrush(QColor("#f5ecd4")))
            s = HANDLE_PX / self.view_scale
            for hx, hy in handle_points(r).values():
                painter.drawRect(QRectF(hx - s / 2, hy - s / 2, s, s))


_HANDLE_CURSORS = {
    "tl": Qt.CursorShape.SizeFDiagCursor,
    "br": Qt.CursorShape.SizeFDiagCursor,
    "tr": Qt.CursorShape.SizeBDiagCursor,
    "bl": Qt.CursorShape.SizeBDiagCursor,
    "tc": Qt.CursorShape.SizeVerCursor,
    "bc": Qt.CursorShape.SizeVerCursor,
    "ml": Qt.CursorShape.SizeHorCursor,
    "mr": Qt.CursorShape.SizeHorCursor,
}


class CalcView(QGraphicsView):
    selectionChanged = Signal(object)  # ImageItem | None
    zoomChanged = Signal(float)
    imagesChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        scene = QGraphicsScene(self)
        scene.setSceneRect(-100000, -100000, 200000, 200000)
        self.setScene(scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.apply_theme()
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.images: list[ImageItem] = []
        self.selected: ImageItem | None = None
        self.zoom = 1.0
        self._z = 0
        self._mode: str | None = None
        self._target: ImageItem | None = None
        self._origin = QPointF()
        self._start_pt = QPointF()
        self._start_box: Box | None = None
        self._handle: str | None = None
        self._last_view = QPointF()
        self._last_scene = QPointF()

        self._first_layout_done = False

    def apply_theme(self) -> None:
        self.setBackgroundBrush(QColor(theme.current()["canvas"]))
        self.viewport().update()

    # ------------------------------------------------------------------
    # Imagens
    # ------------------------------------------------------------------
    def add_pixmap(self, pixmap: QPixmap, name: str = "") -> ImageItem:
        item = ImageItem(pixmap, name)
        item.set_view_scale(self.zoom)
        if self.images:
            x = max(i.x() + i.pixmap.width() for i in self.images) + GAP
            y = min(i.y() for i in self.images)
        else:
            x = y = 0.0
        item.setPos(x, y)
        self.scene().addItem(item)
        self.images.append(item)
        self.select(item)
        self._reveal(item)
        self.imagesChanged.emit(len(self.images))
        return item

    def _reveal(self, item: ImageItem) -> None:
        visible = self.mapToScene(self.viewport().rect()).boundingRect()
        img = item.mapRectToScene(item.image_rect())
        if visible.contains(img):
            return
        if img.width() <= visible.width() and img.height() <= visible.height():
            self.centerOn(img.center())
        else:  # imagem maior que a área: mostra a partir do canto superior esquerdo
            margin = 20 / self.zoom
            self.centerOn(img.left() + visible.width() / 2 - margin, img.top() + visible.height() / 2 - margin)

    def remove_selected(self) -> None:
        item = self.selected
        if item is None:
            return
        self.scene().removeItem(item)
        self.images.remove(item)
        self.selected = None
        self.select(max(self.images, key=lambda i: i.zValue()) if self.images else None)
        self.imagesChanged.emit(len(self.images))
        self.viewport().update()

    def reset_selected_mark(self) -> None:
        if self.selected is not None:
            self.selected.set_mark(None)
            self.selectionChanged.emit(self.selected)

    def set_side(self, h_side: str | None = None, v_side: str | None = None) -> None:
        item = self.selected
        if item is None:
            return
        if h_side:
            item.h_side = h_side
        if v_side:
            item.v_side = v_side
        item.update()

    def select(self, item: ImageItem | None) -> None:
        if self.selected is not None and self.selected is not item:
            self.selected.is_selected = False
            self.selected.update()
        self.selected = item
        if item is not None:
            item.is_selected = True
            self._z += 1
            item.setZValue(self._z)  # a selecionada fica por cima das outras
            item.update()
        self.selectionChanged.emit(item)

    def image_at(self, scene_pt: QPointF) -> ImageItem | None:
        for item in sorted(self.images, key=lambda i: i.zValue(), reverse=True):
            if item.hit(item.mapFromScene(scene_pt)):
                return item
        return None

    # ------------------------------------------------------------------
    # Zoom
    # ------------------------------------------------------------------
    def wheelEvent(self, e) -> None:
        dy = e.angleDelta().y()
        if dy == 0:
            return
        new = self.zoom * ZOOM_STEP if dy > 0 else self.zoom / ZOOM_STEP
        new = max(MIN_SCALE, min(new, MAX_SCALE))
        factor = new / self.zoom
        if abs(factor - 1) < 1e-9:
            return
        self.scale(factor, factor)
        self.zoom = new
        for item in self.images:
            item.set_view_scale(new)
        self.zoomChanged.emit(new)

    # ------------------------------------------------------------------
    # Mouse
    # ------------------------------------------------------------------
    def mousePressEvent(self, e) -> None:
        pos = e.position()
        sp = self.mapToScene(pos.toPoint())
        self.setFocus()

        if e.button() == Qt.MouseButton.RightButton:
            item = self.image_at(sp)
            if item is not None:
                self.select(item)
                self._mode = "drag_image"
            else:
                self._mode = "pan"
            self._last_view = pos
            self._last_scene = sp
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            e.accept()
            return

        if e.button() == Qt.MouseButton.LeftButton:
            item = self.image_at(sp)
            if item is None:
                e.accept()
                return
            self.select(item)
            lp = item.mapFromScene(sp)
            self._target = item
            if item.mark is None:
                self._mode = "draw"
                self._origin = lp
                item.set_mark(Box(lp.x(), lp.y(), 0, 0))
            else:
                handle = item.handle_at(lp)
                if handle:
                    self._mode = "resize"
                    self._handle = handle
                elif _qrect(item.mark).contains(lp):
                    self._mode = "move"
                else:
                    self._mode = None
                self._start_box = item.mark
                self._start_pt = lp
            e.accept()
            return

        super().mousePressEvent(e)

    def mouseMoveEvent(self, e) -> None:
        pos = e.position()
        sp = self.mapToScene(pos.toPoint())

        if self._mode == "pan":
            d = pos - self._last_view
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - round(d.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - round(d.y()))
            self._last_view = pos
            return
        if self._mode == "drag_image" and self.selected is not None:
            d = sp - self._last_scene
            self.selected.moveBy(d.x(), d.y())
            self._last_scene = sp
            return
        if self._mode in ("draw", "move", "resize") and self._target is not None:
            item = self._target
            lp = item.mapFromScene(sp)
            if self._mode == "draw":
                item.set_mark(normalize(self._origin.x(), self._origin.y(), lp.x(), lp.y()))
            elif self._mode == "move" and self._start_box is not None:
                b = self._start_box
                d = lp - self._start_pt
                item.set_mark(Box(b.x + d.x(), b.y + d.y(), b.w, b.h))
            elif self._mode == "resize" and self._start_box is not None and self._handle:
                d = lp - self._start_pt
                item.set_mark(resize(self._start_box, self._handle, d.x(), d.y()))
            return

        self._update_hover_cursor(sp)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e) -> None:
        if self._mode == "draw" and self._target is not None:
            m = self._target.mark
            min_size = 4 / self.zoom  # um clique sem arrastar não cria marcação
            if m is not None and (m.w < min_size or m.h < min_size):
                self._target.set_mark(None)
            self.selectionChanged.emit(self._target)
        self._mode = None
        self._target = None
        self._handle = None
        self._update_hover_cursor(self.mapToScene(e.position().toPoint()))
        e.accept()

    def _update_hover_cursor(self, sp: QPointF) -> None:
        item = self.image_at(sp)
        cursor = Qt.CursorShape.ArrowCursor
        if item is not None:
            lp = item.mapFromScene(sp)
            if item.mark is None:
                cursor = Qt.CursorShape.CrossCursor
            else:
                h = item.handle_at(lp)
                if h:
                    cursor = _HANDLE_CURSORS[h]
                elif _qrect(item.mark).contains(lp):
                    cursor = Qt.CursorShape.SizeAllCursor
        self.viewport().setCursor(cursor)

    # ------------------------------------------------------------------
    # Arrastar arquivos do Explorer para a área
    # ------------------------------------------------------------------
    def dragEnterEvent(self, e) -> None:
        if e.mimeData().hasUrls() or e.mimeData().hasImage():
            e.acceptProposedAction()

    def dragMoveEvent(self, e) -> None:
        if e.mimeData().hasUrls() or e.mimeData().hasImage():
            e.acceptProposedAction()

    def dropEvent(self, e) -> None:
        md = e.mimeData()
        self.parent_tab().load_from_mime(md)
        e.acceptProposedAction()

    def parent_tab(self) -> "CalculatorTab":
        w = self.parentWidget()
        while w is not None and not isinstance(w, CalculatorTab):
            w = w.parentWidget()
        return w  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Dica quando não há imagens
    # ------------------------------------------------------------------
    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        if self.images:
            return
        painter.save()
        painter.resetTransform()
        vr = self.viewport().rect()
        font = QFont(self.font())
        font.setPointSize(13)
        painter.setFont(font)
        painter.setPen(QColor(theme.current()["text"]))
        painter.drawText(
            vr,
            int(Qt.AlignmentFlag.AlignCenter),
            "Cole uma captura de tela com CTRL + V\n"
            "ou clique em “Selecionar imagens” (é possível escolher várias).\n\n"
            "Também é possível arrastar arquivos de imagem para esta área.",
        )
        painter.restore()


class CalculatorTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        bar = QHBoxLayout()
        bar.setSpacing(10)
        self.btn_open = QPushButton("Selecionar imagens")
        self.btn_open.clicked.connect(self.open_files)
        self.btn_remove = QPushButton("Remover imagem")
        self.btn_remove.clicked.connect(self._remove)
        self.btn_reset = QPushButton("Resetar Seleção")
        self.btn_reset.clicked.connect(self._reset_mark)
        bar.addWidget(self.btn_open)
        bar.addWidget(self.btn_remove)
        bar.addWidget(self.btn_reset)

        self.zoom_label = QLabel()
        self.zoom_label.setObjectName("chipLabel")
        bar.addWidget(self.zoom_label)

        self.h_group, h_box = self._side_box("Horizontal:", [("Esquerda", "left"), ("Direita", "right")], "h")
        self.v_group, v_box = self._side_box("Vertical:", [("Superior", "top"), ("Inferior", "bottom")], "v")
        bar.addWidget(h_box)
        bar.addWidget(v_box)
        bar.addStretch(1)
        root.addLayout(bar)

        hint = QLabel(
            "<b>Botão esquerdo</b>: marcação · <b>Botão direito</b> (pressionado): move a imagem; sobre o fundo, "
            "move toda a área · <b>Roda do mouse</b>: zoom · As opções acima se aplicam à imagem selecionada "
            "(indicada pela borda tracejada)."
        )
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        root.addWidget(hint)

        # A área cinza fica dentro de um quadro arredondado; a margem interna evita que os
        # cantos retos da área de desenho apareçam por fora da borda arredondada.
        frame = QFrame()
        frame.setObjectName("canvasFrame")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(6, 6, 6, 6)
        self.view = CalcView()
        self.view.setObjectName("canvas")
        self.view.setFrameShape(QFrame.Shape.NoFrame)
        fl.addWidget(self.view)
        root.addWidget(frame, 1)

        self.view.selectionChanged.connect(self._sync_controls)
        self.view.zoomChanged.connect(self._update_zoom)
        self.view.imagesChanged.connect(lambda _n: self._sync_controls(self.view.selected))

        paste = QShortcut(QKeySequence(QKeySequence.StandardKey.Paste), self)
        paste.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        paste.activated.connect(self.paste)
        delete = QShortcut(QKeySequence(QKeySequence.StandardKey.Delete), self)
        delete.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        delete.activated.connect(self._remove)

        self._update_zoom(1.0)
        self._sync_controls(None)

    def _side_box(self, title: str, options: list[tuple[str, str]], axis: str):
        box = QFrame()
        box.setObjectName("card")
        lay = QHBoxLayout(box)
        lay.setContentsMargins(8, 5, 8, 5)
        lay.setSpacing(6)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: 600;")
        lay.addWidget(lbl)
        group = QButtonGroup(box)
        group.setExclusive(True)
        for text, value in options:
            b = QPushButton(text)
            b.setProperty("toggle", True)
            b.setCheckable(True)
            b.setProperty("side", value)
            b.clicked.connect(lambda _c=False, v=value, a=axis: self._set_side(a, v))
            group.addButton(b)
            lay.addWidget(b)
        return group, box

    # ------------------------------------------------------------------
    def _set_side(self, axis: str, value: str) -> None:
        if axis == "h":
            self.view.set_side(h_side=value)
        else:
            self.view.set_side(v_side=value)

    def _sync_controls(self, item) -> None:
        has = item is not None
        self.btn_remove.setEnabled(has)
        self.btn_reset.setEnabled(has and item.mark is not None)
        for group, current in ((self.h_group, item.h_side if has else None),
                               (self.v_group, item.v_side if has else None)):
            group.setExclusive(False)  # permite desmarcar todos quando não há imagem
            for b in group.buttons():
                b.setEnabled(has)
                b.setChecked(b.property("side") == current)
            group.setExclusive(True)

    def _update_zoom(self, z: float) -> None:
        self.zoom_label.setText(f"Zoom: <b>{round(z * 100)}%</b>")

    def _remove(self) -> None:
        self.view.remove_selected()

    def _reset_mark(self) -> None:
        self.view.reset_selected_mark()

    # ------------------------------------------------------------------
    # Entrada de imagens
    # ------------------------------------------------------------------
    def open_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar imagens",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tif *.tiff);;Todos os arquivos (*)",
        )
        self.load_files(paths)

    def load_files(self, paths: list[str]) -> None:
        failed = []
        for p in paths:
            pix = QPixmap(p)
            if pix.isNull():
                failed.append(Path(p).name)
            else:
                self.view.add_pixmap(pix, Path(p).name)
        if failed:
            QMessageBox.warning(self, "Imagens", "Não foi possível abrir os seguintes arquivos:\n" + "\n".join(failed))

    def load_from_mime(self, md) -> None:
        if md.hasUrls():
            files = [u.toLocalFile() for u in md.urls() if u.isLocalFile()]
            images = [f for f in files if Path(f).suffix.lower() in IMAGE_EXTS]
            if images:
                self.load_files(images)
                return
        if md.hasImage():
            img = md.imageData()
            if isinstance(img, QImage) and not img.isNull():
                self.view.add_pixmap(QPixmap.fromImage(img), "print")
            elif isinstance(img, QPixmap) and not img.isNull():
                self.view.add_pixmap(img, "print")

    def paste(self) -> None:
        cb = QGuiApplication.clipboard()
        md = cb.mimeData()
        if md is None:
            return
        if md.hasImage():
            img = cb.image()
            if not img.isNull():
                self.view.add_pixmap(QPixmap.fromImage(img), "print")
                return
        self.load_from_mime(md)

    def showEvent(self, e) -> None:
        super().showEvent(e)
        self.view.setFocus()
