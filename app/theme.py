"""Cores e estilo (modo claro e modo escuro), com as cores do projeto Produto Assertivo.

As cores da marca (azul #446E9B, azul escuro #2F437F, amarelo #FFC21A e dourado #E9CF7A)
são as mesmas nos dois modos; no escuro mudam só fundos, textos e bordas neutras.
"""
from __future__ import annotations

from PySide6.QtGui import QColor, QPalette

# Cores da marca
AZUL = "#446E9B"
AZUL_ESCURO = "#2F437F"
AMARELO = "#FFC21A"
DOURADO = "#E9CF7A"

# Mantidas para compatibilidade
FUNDO = "#F8F8F8"
CINZA_BOTAO = "#F4F4F4"
FUNDO_CANVAS = "#dfdddd"

THEMES: dict[str, dict[str, str]] = {
    "claro": {
        "window": "#F8F8F8",
        "sidebar": "#FFFFFF",
        "surface": "#FFFFFF",
        "surface_alt": "#FBFBFB",
        "input": "#FFFFFF",
        "text": AZUL_ESCURO,
        "text_soft": AZUL,
        "text_muted": "#8a9bb0",
        "title": AZUL_ESCURO,
        "border": DOURADO,
        "chip": "#F4F4F4",
        "chip_hover": "#e8edf3",
        "chip_text": AZUL,
        "chip_disabled_text": "#b5c0cc",
        "button_disabled": "#aab9ca",
        "button_disabled_text": "#eef2f6",
        "canvas": "#dfdddd",
        "warning_bg": "#FFF6DA",
        "warning_text": "#8a5a00",
        "field_highlight": "#FFEBA8",
        "field_highlight_text": AZUL_ESCURO,
        "scroll": "#d3dae3",
    },
    "escuro": {
        "window": "#151922",
        "sidebar": "#1B2029",
        "surface": "#1E242F",
        "surface_alt": "#232A36",
        "input": "#232A36",
        "text": "#DCE5F2",
        "text_soft": "#9DB6D6",
        "text_muted": "#6F819A",
        "title": "#DCE5F2",
        "border": "#5E5332",  # dourado escurecido, para não ofuscar
        "chip": "#2A3241",
        "chip_hover": "#323C4E",
        "chip_text": "#9DB6D6",
        "chip_disabled_text": "#56637a",
        "button_disabled": "#2f3b4c",
        "button_disabled_text": "#6f819a",
        "canvas": "#2B2F36",
        "warning_bg": "#3A3120",
        "warning_text": "#F2D27A",
        "field_highlight": "#5C4A12",
        "field_highlight_text": "#FFE9A8",
        "scroll": "#3a4456",
    },
}

_current = "claro"


def current_name() -> str:
    return _current


def current() -> dict[str, str]:
    return THEMES[_current]


def set_current(name: str) -> None:
    global _current
    _current = name if name in THEMES else "claro"


def build_stylesheet(t: dict[str, str]) -> str:
    return f"""
/* A fonte padrão vem de app.setFont() (e não daqui), para o zoom dos editores funcionar */
QWidget {{ color: {t['text']}; }}
QMainWindow, QWidget#root, QWidget#page {{ background: {t['window']}; }}
QScrollArea, QScrollArea > QWidget > QWidget#faqContent {{ background: {t['window']}; border: none; }}

/* ---------- menu lateral ---------- */
QFrame#sidebar {{ background: {t['sidebar']}; border-right: 1px solid {t['border']}; }}
QLabel#title {{ font-size: 16pt; font-weight: 700; color: {t['title']}; padding: 0; }}
QPushButton#navButton {{
    text-align: left;
    background: transparent;
    color: {t['chip_text']};
    border: none;
    border-radius: 10px;
    padding: 11px 16px;
    font-size: 10.5pt;
    font-weight: 600;
}}
QPushButton#navButton:hover {{ background: {t['chip_hover']}; }}
QPushButton#navButton:checked {{ background: {AZUL}; color: white; }}
QPushButton#themeButton {{
    background: {t['chip']};
    color: {t['chip_text']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    padding: 9px 12px;
    font-weight: 600;
}}
QPushButton#themeButton:hover {{ background: {t['chip_hover']}; }}
QLabel#version {{ color: {t['text_muted']}; font-size: 8.5pt; padding-left: 6px; }}

QLabel#hint {{ color: {t['text_soft']}; }}
QLabel#statusLine {{ color: {t['text_soft']}; font-weight: 600; }}
QLabel#warning {{
    color: {t['warning_text']};
    background: {t['warning_bg']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 6px 10px;
}}
QLabel#sectionLabel {{ font-weight: 600; }}
QLabel#preview {{ font-size: 11pt; padding: 8px; background: {t['surface_alt']}; border-radius: 8px; }}
QLabel#chipLabel {{
    background: {t['surface']};
    border: 1px solid {DOURADO};
    border-radius: 10px;
    padding: 7px 14px;
    font-weight: 500;
}}

/* ---------- botões ---------- */
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
QPushButton:disabled {{ background: {t['button_disabled']}; color: {t['button_disabled_text']}; }}

QPushButton[toggle="true"] {{
    background: {t['chip']};
    color: {t['chip_text']};
    border: none;
    border-radius: 8px;
    padding: 5px 12px;
}}
QPushButton[toggle="true"]:checked {{ background: {AMARELO}; color: {AZUL_ESCURO}; }}
QPushButton[toggle="true"]:disabled {{ background: {t['chip']}; color: {t['chip_disabled_text']}; }}

/* ---------- cartões e campos ---------- */
QFrame#card {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 12px;
}}
QFrame#card QLabel {{ background: transparent; }}
QFrame#card QLabel#warning {{ background: {t['warning_bg']}; }}
QFrame#card QLabel#preview {{ background: {t['surface_alt']}; }}

QPlainTextEdit, QTextEdit, QLineEdit, QListWidget, QTextBrowser {{
    background: {t['input']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 6px;
    selection-background-color: {AMARELO};
    selection-color: {AZUL_ESCURO};
}}
QPlainTextEdit:focus, QLineEdit:focus {{ border: 1px solid {AZUL}; }}
QFrame#card QPlainTextEdit#bareEditor, QFrame#card QTextEdit#bareEditor {{
    border: none; padding: 10px; background: {t['surface']};
}}
QListWidget::item {{ padding: 5px 4px; border-radius: 6px; }}
QListWidget::item:selected {{ background: {AMARELO}; color: {AZUL_ESCURO}; }}

QToolButton#fmtMenu {{
    background: {t['chip']};
    color: {t['chip_text']};
    border: none;
    border-radius: 8px;
    padding: 5px 10px;
}}
QToolButton#fmtMenu:hover {{ background: {t['chip_hover']}; }}
QToolButton#fmtMenu::menu-indicator {{ image: none; width: 0; }}
QMenu {{
    background: {t['surface']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{ padding: 6px 18px 6px 10px; border-radius: 6px; }}
QMenu::item:selected {{ background: {t['chip_hover']}; }}
QMenu::separator {{ height: 1px; background: {t['border']}; margin: 4px 6px; }}

QListWidget#suggestions {{
    background: #1f2430;
    border: 1px solid #3b4252;
    border-radius: 6px;
    padding: 2px;
}}

/* ---------- ajuda ---------- */
QLabel#faqSection {{ font-size: 14pt; font-weight: 700; color: {t['title']}; padding-top: 10px; }}
QPushButton#faqQuestion {{
    text-align: left;
    background: {t['chip']};
    color: {t['title']};
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    font-weight: 600;
    font-size: 10.5pt;
}}
QPushButton#faqQuestion:hover {{ background: {t['chip_hover']}; }}
QPushButton#faqQuestion:checked {{
    background: {AZUL};
    color: white;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
}}
QLabel#faqAnswer {{
    background: {t['surface']};
    border: 1px solid {t['border']};
    border-top: none;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    padding: 10px 16px;
    font-size: 10.5pt;
}}

QFrame#canvasFrame {{ background: {t['canvas']}; border: 1px solid {t['border']}; border-radius: 12px; }}
QGraphicsView#canvas {{ border: none; background: {t['canvas']}; }}
QSplitter::handle {{ background: transparent; }}
QToolTip {{ color: {t['text']}; background: {t['surface']}; border: 1px solid {t['border']}; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {t['scroll']}; border-radius: 4px; min-height: 30px; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {t['scroll']}; border-radius: 4px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QMessageBox, QDialog {{ background: {t['window']}; }}
"""


def build_palette(t: dict[str, str]) -> QPalette:
    """Paleta do Qt (usada por caixas de diálogo e partes não cobertas pelo estilo)."""
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(t["window"]))
    p.setColor(QPalette.ColorRole.WindowText, QColor(t["text"]))
    p.setColor(QPalette.ColorRole.Base, QColor(t["input"]))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor(t["chip"]))
    p.setColor(QPalette.ColorRole.Text, QColor(t["text"]))
    p.setColor(QPalette.ColorRole.Button, QColor(t["chip"]))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(t["text"]))
    p.setColor(QPalette.ColorRole.Highlight, QColor(AMARELO))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor(AZUL_ESCURO))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor(t["surface"]))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor(t["text"]))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor(t["text_muted"]))
    return p


# Compatibilidade com o código antigo
STYLESHEET = build_stylesheet(THEMES["claro"])


def light_palette() -> QPalette:
    return build_palette(THEMES["claro"])
