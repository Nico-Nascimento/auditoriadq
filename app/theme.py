"""Cores e estilo, as mesmas do projeto web Produto Assertivo."""
from PySide6.QtGui import QColor, QPalette

AZUL = "#446E9B"
AZUL_ESCURO = "#2F437F"
AMARELO = "#FFC21A"
DOURADO = "#E9CF7A"
FUNDO = "#F8F8F8"
CINZA_BOTAO = "#F4F4F4"
FUNDO_CANVAS = "#dfdddd"

STYLESHEET = f"""
QWidget {{
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
    color: {AZUL_ESCURO};
}}
QMainWindow, QWidget#root {{ background: {FUNDO}; }}

QLabel#title {{ font-size: 22pt; font-weight: 700; color: {AZUL_ESCURO}; }}
QLabel#subtitle {{ color: {AZUL}; }}
QLabel#hint {{ color: {AZUL}; }}
QLabel#warning {{ color: #8a5a00; background: #FFF6DA; border: 1px solid {DOURADO}; border-radius: 8px; padding: 6px 10px; }}
QLabel#sectionLabel {{ font-weight: 600; }}

QPushButton {{
    background: {AZUL};
    color: white;
    border: 1px solid {DOURADO};
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 500;
}}
QPushButton:hover {{ background: #3c6290; }}
QPushButton:pressed {{ background: #345681; }}
QPushButton:disabled {{ background: #aab9ca; color: #eef2f6; }}

QPushButton[toggle="true"] {{
    background: {CINZA_BOTAO};
    color: {AZUL};
    border: none;
    border-radius: 8px;
    padding: 5px 12px;
}}
QPushButton[toggle="true"]:checked {{ background: {AMARELO}; color: {AZUL_ESCURO}; }}
QPushButton[toggle="true"]:disabled {{ background: {CINZA_BOTAO}; color: #b5c0cc; }}

QFrame#card {{
    background: white;
    border: 1px solid {DOURADO};
    border-radius: 12px;
}}
QFrame#card QLabel {{ background: transparent; }}
QFrame#card QLabel#warning {{ background: #FFF6DA; }}

QTabWidget::pane {{
    border: 1px solid {DOURADO};
    border-radius: 12px;
    background: white;
    top: -1px;
}}
QTabBar::tab {{
    background: {CINZA_BOTAO};
    color: {AZUL};
    padding: 9px 20px;
    margin-right: 4px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: 600;
}}
QTabBar::tab:selected {{ background: {AZUL}; color: white; }}
QTabBar::tab:hover:!selected {{ background: #e8edf3; }}

QPlainTextEdit, QLineEdit, QListWidget, QTextBrowser {{
    background: white;
    border: 1px solid {DOURADO};
    border-radius: 8px;
    padding: 6px;
    selection-background-color: {AMARELO};
    selection-color: {AZUL_ESCURO};
}}
QPlainTextEdit:focus, QLineEdit:focus {{ border: 1px solid {AZUL}; }}
QListWidget::item {{ padding: 5px 4px; border-radius: 6px; }}
QListWidget::item:selected {{ background: {AMARELO}; color: {AZUL_ESCURO}; }}

QListWidget#suggestions {{
    background: #1f2430;
    border: 1px solid #3b4252;
    border-radius: 6px;
    padding: 2px;
}}

QGraphicsView {{ border: 1px solid {DOURADO}; border-radius: 12px; }}
QSplitter::handle {{ background: transparent; }}
QToolTip {{ color: {AZUL_ESCURO}; background: white; border: 1px solid {DOURADO}; }}
"""


def light_palette() -> QPalette:
    """Força o tema claro mesmo se o Windows estiver no modo escuro."""
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(FUNDO))
    p.setColor(QPalette.ColorRole.WindowText, QColor(AZUL_ESCURO))
    p.setColor(QPalette.ColorRole.Base, QColor("white"))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor(CINZA_BOTAO))
    p.setColor(QPalette.ColorRole.Text, QColor(AZUL_ESCURO))
    p.setColor(QPalette.ColorRole.Button, QColor(CINZA_BOTAO))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(AZUL_ESCURO))
    p.setColor(QPalette.ColorRole.Highlight, QColor(AMARELO))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor(AZUL_ESCURO))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor("white"))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor(AZUL_ESCURO))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#8a9bb0"))
    return p
