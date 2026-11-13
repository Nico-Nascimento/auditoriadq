"""Teste automático do programa (sem abrir janela).

Uso:  python testes/teste_rapido.py
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

if "--janela" not in sys.argv:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QPixmap  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app import theme  # noqa: E402
from app.editor import TEMPLATE  # noqa: E402
from app.main_window import MainWindow, apply_style  # noqa: E402
from app.store import SnippetStore  # noqa: E402

ok = 0


def check(cond: bool, msg: str) -> None:
    global ok
    if not cond:
        raise AssertionError(msg)
    ok += 1
    print("  ✔", msg)


def shot(win, name: str) -> None:
    QTest.qWait(80)
    win.grab().save(str(Path(os.environ.get("SCREENSHOT_DIR", tempfile.gettempdir())) / f"tela-{name}.png"))


def main() -> None:
    app = QApplication(sys.argv)
    apply_style(app)
    tmp = Path(tempfile.mkdtemp()) / "snippets.json"
    store = SnippetStore(path=tmp)
    win = MainWindow(store)
    win.resize(1300, 850)
    win.show()
    QTest.qWaitForWindowExposed(win)

    print("Auditoria")
    ed = win.audit.editor
    ed.setFocus()
    check(ed.toPlainText() == TEMPLATE, "editor abre com o modelo padrão")
    check(ed.textCursor().position() == len("Roi: "), "cursor começa depois de 'Roi: '")

    QTest.keyClicks(ed, "cr")
    check(ed.popup.isVisible(), "lista de sugestões aparece ao digitar 'cr'")
    QTest.keyClick(ed, Qt.Key.Key_Tab)
    check(ed.toPlainText().startswith("Roi: Correto.\n"), "Tab insere 'Correto.'")

    c = ed.textCursor()
    c.setPosition(ed.toPlainText().index("Produtos: ") + len("Produtos: "))
    ed.setTextCursor(c)
    QTest.keyClicks(ed, "dp1")
    check(ed.popup.isVisible() and ed.popup.count() == 1, "'dp1' mostra 1 sugestão")
    QTest.keyClick(ed, Qt.Key.Key_Tab)
    check(ed.textCursor().selectedText() == "id", "primeiro campo 'id' fica selecionado")
    QTest.keyClicks(ed, "12")
    QTest.keyClick(ed, Qt.Key.Key_Tab)
    check(ed.textCursor().selectedText() == "ele não aparece até 40%", "Tab vai para o segundo campo")
    QTest.keyClick(ed, Qt.Key.Key_Backtab)
    check(ed.textCursor().selectedText() == "12", "Shift+Tab volta para o primeiro campo")
    QTest.keyClick(ed, Qt.Key.Key_Tab)
    QTest.keyClick(ed, Qt.Key.Key_Tab)
    check(ed.session is None, "Tab depois do último campo encerra o preenchimento")
    check(
        ed.toPlainText().endswith("Produtos: Desmarcar o produto de número 12, ele não aparece até 40%."),
        "frase final correta",
    )
    QTest.keyClick(ed, Qt.Key.Key_Return)
    QTest.keyClicks(ed, "mp1")
    check(ed.popup.count() == 2, "prefixo repetido 'mp1' mostra as 2 opções")
    shot(win, "sugestoes")
    QTest.keyClick(ed, Qt.Key.Key_Down)
    QTest.keyClick(ed, Qt.Key.Key_Return)
    check("ele também entra no escopo" in ed.toPlainText(), "seta para baixo + Enter escolhe a 2ª opção")
    QTest.keyClicks(ed, "Arroz")
    QTest.keyClick(ed, Qt.Key.Key_Tab)
    check(ed.textCursor().selectedText() == "identificação", "dentro de um campo, Tab vai para o próximo campo")
    QTest.keyClick(ed, Qt.Key.Key_Escape)
    check(ed.session is None, "Esc encerra o preenchimento")

    ed.reset_template()
    check(ed.toPlainText() == TEMPLATE, "Resetar formato volta ao modelo")

    print("Calculadora 40%")
    win.tabs.setCurrentWidget(win.calc)
    view = win.calc.view
    for color in ("#ff0000", "#00aa00"):
        pix = QPixmap(400, 300)
        pix.fill(QColor(color))
        view.add_pixmap(pix, color)
    check(len(view.images) == 2, "duas imagens adicionadas")
    a, b = view.images
    check(b.x() == a.x() + 400 + 40, "segunda imagem entra ao lado da primeira")
    check(view.selected is b, "imagem nova fica selecionada")

    def vp(item, x, y) -> QPoint:
        return view.mapFromScene(item.mapToScene(QPointF(x, y)))

    QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, vp(a, 50, 50))
    QTest.mouseMove(view.viewport(), vp(a, 150, 120))
    QTest.mouseMove(view.viewport(), vp(a, 250, 200))
    QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, vp(a, 250, 200))
    m = a.mark
    check(m is not None and abs(m.w - 200) < 2 and abs(m.h - 150) < 2, "botão esquerdo desenha o retângulo")
    check(view.selected is a and b.mark is None, "marcação pertence só à imagem clicada")
    QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, vp(b, 100, 60))
    QTest.mouseMove(view.viewport(), vp(b, 200, 150))
    QTest.mouseMove(view.viewport(), vp(b, 300, 260))
    QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, vp(b, 300, 260))
    win.calc.h_group.buttons()[1].click()
    win.calc.v_group.buttons()[1].click()
    check(b.h_side == "right" and b.v_side == "bottom" and a.h_side == "left", "lados das faixas valem por imagem")
    shot(win, "marcacao")
    view.select(a)

    win.calc.btn_reset.click()
    check(a.mark is None, "Resetar Seleção apaga a marcação da imagem selecionada")

    old = a.pos()
    QTest.mousePress(view.viewport(), Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier, vp(a, 10, 10))
    QTest.mouseMove(view.viewport(), vp(a, 40, 30))
    QTest.mouseRelease(view.viewport(), Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier, vp(a, 40, 30))
    check(a.pos() != old and a.mark is None, "botão direito arrasta a imagem sem marcar")

    win.calc.btn_remove.click()
    check(len(view.images) == 1, "Remover imagem tira só a selecionada")

    print("Anotações")
    win.tabs.setCurrentWidget(win.notes)
    check(win.nav.checkedId() == win.tabs.indexOf(win.notes), "menu lateral acompanha a área aberta")
    QTest.keyClicks(win.notes.editor, "Lembrar de revisar a loja 15")
    win.notes.save_now()
    notes_file = tmp.parent / "anotacoes.txt"
    check(notes_file.read_text(encoding="utf-8") == "Lembrar de revisar a loja 15", "anotações são salvas no arquivo")

    print("Snippets e Ajuda")
    old_dir = Path(tempfile.mkdtemp())
    shutil.copyfile(Path(__file__).with_name("snippets_padrao_v1.json"), old_dir / "snippets.json")
    upgraded = SnippetStore(path=old_dir / "snippets.json")
    check(upgraded.updated_defaults and len(upgraded.snippets) == 25, "arquivo com o padrão antigo é atualizado")
    edited_dir = Path(tempfile.mkdtemp())
    (edited_dir / "snippets.json").write_text('{"Meu": {"prefix": "x", "body": ["y"]}}', encoding="utf-8")
    kept = SnippetStore(path=edited_dir / "snippets.json")
    check(not kept.updated_defaults and len(kept.snippets) == 1, "arquivo editado pela pessoa é mantido")
    win.tabs.setCurrentWidget(win.snippets)
    check(win.snippets.list.count() == len(store.snippets) == 25, "aba Snippets lista os 25 snippets")
    win.tabs.setCurrentWidget(win.help)
    check(len(win.help.items) > 10, "aba Ajuda tem as perguntas")

    names = ["auditoria", "calculadora", "anotacoes", "snippets", "ajuda"]
    for i, name in enumerate(names):
        win.nav.button(i).click()
        shot(win, name)

    print("Modo escuro")
    win.theme_button.click()
    check(theme.current_name() == "escuro", "botão troca para o modo escuro")
    for i, name in enumerate(names):
        win.nav.button(i).click()
        shot(win, f"escuro-{name}")
    check(win.settings.value("tema") == "escuro", "escolha do tema fica salva")
    win.theme_button.click()
    check(theme.current_name() == "claro", "botão volta para o modo claro")

    print(f"\nTudo certo: {ok} verificações passaram.")
    win.close()
    app.quit()


if __name__ == "__main__":
    main()
