from __future__ import annotations

import sys
import time
import traceback

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QTabWidget, QVBoxLayout, QWidget

from .calculator import CalculatorTab
from .editor import AuditTab
from .help_tab import HelpTab
from .snippets_tab import SnippetsTab
from .store import SnippetStore, user_data_dir
from .theme import STYLESHEET, light_palette

APP_NAME = "AuditoriaDQ"
APP_TITLE = "AuditoriaDQ"
VERSION = "1.0.0"


class MainWindow(QMainWindow):
    def __init__(self, store: SnippetStore):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} v{VERSION}")
        self.resize(1400, 900)

        root = QWidget()
        root.setObjectName("root")
        lay = QVBoxLayout(root)
        lay.setContentsMargins(24, 18, 24, 18)
        lay.setSpacing(10)

        title = QLabel(APP_TITLE)
        title.setObjectName("title")
        subtitle = QLabel("Auditoria, calculadora de 40% e frases prontas em um só lugar.")
        subtitle.setObjectName("subtitle")
        lay.addWidget(title)
        lay.addWidget(subtitle)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)
        self.audit = AuditTab(store)
        self.calc = CalculatorTab()
        self.snippets = SnippetsTab(store)
        self.help = HelpTab()
        self.tabs.addTab(self.audit, "Auditoria")
        self.tabs.addTab(self.calc, "Calculadora 40%")
        self.tabs.addTab(self.snippets, "Snippets")
        self.tabs.addTab(self.help, "Ajuda")
        self.tabs.currentChanged.connect(self._on_tab)
        lay.addWidget(self.tabs, 1)

        self.setCentralWidget(root)
        self.store = store

    def _on_tab(self, index: int) -> None:
        w = self.tabs.widget(index)
        if w is self.audit:
            self.audit.editor.setFocus()
        elif w is self.calc:
            self.calc.view.setFocus()

    def closeEvent(self, e) -> None:
        self.store.save_now()
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
                "Aconteceu um erro inesperado. O programa vai tentar continuar.\n\n"
                f"{exc_type.__name__}: {exc}\n\n"
                + (f"Detalhes salvos em:\n{log}" if log else ""),
            )

    sys.excepthook = handler


def apply_style(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setPalette(light_palette())
    app.setStyleSheet(STYLESHEET)


def run() -> int:
    QCoreApplication.setOrganizationName("")
    QCoreApplication.setApplicationName(APP_NAME)
    QCoreApplication.setApplicationVersion(VERSION)
    _install_error_handler()
    app = QApplication(sys.argv)
    apply_style(app)

    store = SnippetStore()
    win = MainWindow(store)
    win.showMaximized()
    win.audit.editor.setFocus()
    if store.load_warning:
        QMessageBox.warning(win, "Snippets", store.load_warning)
    return app.exec()
