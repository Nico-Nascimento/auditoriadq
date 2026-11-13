from __future__ import annotations

import sys
import time
import traceback

from PySide6.QtCore import QCoreApplication, QSettings, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from . import theme
from .calculator import CalculatorTab
from .editor import AuditTab
from .help_tab import HelpTab
from .notes_tab import NotesTab
from .resources import resource_path
from .single_instance import SingleInstance
from .snippets_tab import SnippetsTab
from .store import SnippetStore, user_data_dir

APP_NAME = "AuditoriaDQ"
APP_TITLE = "AuditoriaDQ"
VERSION = "1.5.0"


class MainWindow(QMainWindow):
    def __init__(self, store: SnippetStore):
        super().__init__()
        self.store = store
        data_dir = store.path.parent  # mesma pasta do arquivo de snippets
        self.settings = QSettings(str(data_dir / "config.ini"), QSettings.Format.IniFormat)

        self.setWindowTitle(f"{APP_TITLE} v{VERSION}")
        self.resize(1400, 900)

        root = QWidget()
        root.setObjectName("root")
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---------------- menu lateral ----------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sv = QVBoxLayout(sidebar)
        sv.setContentsMargins(14, 20, 14, 16)
        sv.setSpacing(6)
        brand = QHBoxLayout()
        brand.setSpacing(8)
        logo = QLabel()
        logo.setPixmap(QIcon(str(resource_path("app", "assets", "icone.png"))).pixmap(34, 34))
        brand.addWidget(logo)
        title = QLabel(APP_TITLE)
        title.setObjectName("title")
        brand.addWidget(title, 1)
        sv.addLayout(brand)
        sv.addSpacing(8)

        # ---------------- páginas ----------------
        self.tabs = QStackedWidget()  # mantém o nome "tabs" (usado pelo teste)
        self.audit = AuditTab(store, data_dir / "auditoria.txt", self.settings)
        self.calc = CalculatorTab()
        self.notes = NotesTab(data_dir / "anotacoes.html", self.settings)
        self.snippets = SnippetsTab(store)
        self.help = HelpTab()
        pages = [
            ("Auditoria", self.audit),
            ("Calculadora 40%", self.calc),
            ("Anotações", self.notes),
            ("Snippets", self.snippets),
            ("Ajuda", self.help),
        ]
        self.nav = QButtonGroup(self)
        self.nav.setExclusive(True)
        for i, (label, page) in enumerate(pages):
            page.setObjectName("page")
            self.tabs.addWidget(page)
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            self.nav.addButton(btn, i)
            sv.addWidget(btn)
        self.nav.idClicked.connect(self.tabs.setCurrentIndex)
        self.tabs.currentChanged.connect(self._on_tab)

        sv.addStretch(1)
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        sv.addWidget(self.theme_button)
        version = QLabel(f"versão {VERSION}")
        version.setObjectName("version")
        sv.addWidget(version)

        outer.addWidget(sidebar)
        content = QWidget()
        content.setObjectName("root")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(8, 8, 8, 8)
        cl.addWidget(self.tabs)
        outer.addWidget(content, 1)
        self.setCentralWidget(root)

        self.set_theme(str(self.settings.value("tema", "claro")))
        self.nav.button(0).setChecked(True)
        self.tabs.setCurrentIndex(0)

    # ------------------------------------------------------------------
    def _on_tab(self, index: int) -> None:
        btn = self.nav.button(index)
        if btn is not None and not btn.isChecked():
            btn.setChecked(True)
        w = self.tabs.widget(index)
        if w is self.audit:
            self.audit.editor.setFocus()
        elif w is self.calc:
            self.calc.view.setFocus()
        elif w is self.notes:
            self.notes.editor.setFocus()

    def set_theme(self, name: str) -> None:
        apply_style(QApplication.instance(), name)
        self.settings.setValue("tema", theme.current_name())
        dark = theme.current_name() == "escuro"
        self.theme_button.setText("☀  Modo claro" if dark else "🌙  Modo escuro")
        self.calc.view.apply_theme()
        self.snippets.apply_theme()

    def toggle_theme(self) -> None:
        self.set_theme("claro" if theme.current_name() == "escuro" else "escuro")

    def bring_to_front(self) -> None:
        state = self.windowState() & ~Qt.WindowState.WindowMinimized
        self.setWindowState(state | Qt.WindowState.WindowActive)
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, e) -> None:
        self.store.save_now()
        self.notes.save_now()
        self.audit.save_now()
        self.settings.sync()
        super().closeEvent(e)


def _install_error_handler() -> None:
    """Mostra erros inesperados numa janela e guarda em erros.log (o .exe não tem console)."""

    def handler(exc_type, exc, tb) -> None:
        text = "".join(traceback.format_exception(exc_type, exc, tb))
        try:
            log = user_data_dir() / "erros.log"
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} (v{VERSION}) ===\n{text}")
        except Exception:
            log = None
        if QApplication.instance() is not None:
            QMessageBox.critical(
                None,
                "Erro inesperado",
                "Ocorreu um erro inesperado. O programa tentará continuar em funcionamento.\n\n"
                f"{exc_type.__name__}: {exc}\n\n"
                + (f"Detalhes salvos em:\n{log}" if log else ""),
            )

    sys.excepthook = handler


def apply_style(app: QApplication, name: str = "claro") -> None:
    theme.set_current(name)
    t = theme.current()
    app.setStyle("Fusion")
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    app.setPalette(theme.build_palette(t))
    app.setStyleSheet(theme.build_stylesheet(t))


def run() -> int:
    QCoreApplication.setOrganizationName("")
    QCoreApplication.setApplicationName(APP_NAME)
    QCoreApplication.setApplicationVersion(VERSION)
    _install_error_handler()
    if sys.platform.startswith("win"):
        # Faz o Windows mostrar o ícone do programa na barra de tarefas (e não o do Python)
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AuditoriaDQ.App")
        except Exception:
            pass
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(resource_path("app", "assets", "icone.ico"))))

    instance = SingleInstance()
    if instance.already_running():
        return 0  # a janela que já estava aberta vem para a frente

    apply_style(app)
    store = SnippetStore()
    win = MainWindow(store)
    instance.activated.connect(win.bring_to_front)
    win.showMaximized()
    win.audit.editor.setFocus()
    if store.load_warning:
        QMessageBox.warning(win, "Snippets", store.load_warning)
    return app.exec()
