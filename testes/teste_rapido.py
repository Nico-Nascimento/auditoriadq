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
from PySide6.QtGui import QColor, QFont, QPixmap, QTextCursor, QTextFormat  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app import theme  # noqa: E402
from app.editor import TEMPLATE, AuditTab  # noqa: E402
from app.notes_tab import NotesTab  # noqa: E402
from app.single_instance import SingleInstance  # noqa: E402
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

    win.audit.save_now()
    saved = (tmp.parent / "auditoria.txt").read_text(encoding="utf-8")
    check(saved == ed.toPlainText(), "texto da auditoria é salvo no arquivo")
    restored = AuditTab(store, tmp.parent / "auditoria.txt")
    check(restored.editor.toPlainText() == saved, "texto da auditoria é recuperado ao abrir")
    restored.deleteLater()

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

    big = QPixmap(3000, 2000)
    big.fill(QColor("#3366cc"))
    view.add_pixmap(big, "grande")
    win.calc.btn_fit.click()
    visible = view.mapToScene(view.viewport().rect()).boundingRect()
    check(all(visible.contains(i.mapRectToScene(i.image_rect())) for i in view.images),
          "Ajustar à tela mostra todas as imagens")
    win.calc.btn_remove.click()
    check(len(view.images) == 2, "Remover imagem tira só a selecionada")

    print("Anotações")
    win.tabs.setCurrentWidget(win.notes)
    check(win.nav.checkedId() == win.tabs.indexOf(win.notes), "menu lateral acompanha a área aberta")
    ne = win.notes.editor
    ne.setFocus()
    QTest.keyClicks(ne, "Lembrar de revisar a loja 15")
    c = ne.textCursor()
    c.setPosition(0)
    c.movePosition(QTextCursor.MoveOperation.EndOfWord, QTextCursor.MoveMode.KeepAnchor)
    ne.setTextCursor(c)
    check(c.selectedText() == "Lembrar", "palavra selecionada nas anotações")
    win.notes.btn_bold.click()
    win.notes.btn_italic.click()
    win.notes.set_text_color("#E53935")

    def fmt_at(editor, pos):
        cur = QTextCursor(editor.document())
        cur.setPosition(pos + 1)
        return cur.charFormat()

    f0 = fmt_at(ne, 0)
    check(f0.fontWeight() >= QFont.Weight.Bold.value and f0.fontItalic(), "negrito e itálico aplicados")
    check(f0.foreground().color().name().lower() == "#e53935", "cor do texto aplicada")
    check(fmt_at(ne, 10).fontWeight() < QFont.Weight.Bold.value, "o resto do texto não foi alterado")
    c = ne.textCursor()
    c.setPosition(len("Lembrar de "))
    c.movePosition(QTextCursor.MoveOperation.EndOfWord, QTextCursor.MoveMode.KeepAnchor)
    ne.setTextCursor(c)
    win.notes.set_highlight("#FFE066")
    check(fmt_at(ne, len("Lembrar de ")).background().color().name().lower() == "#ffe066", "marca-texto aplicado")
    win.notes.save_now()
    notes_file = tmp.parent / "anotacoes.html"
    reopened = NotesTab(notes_file)
    rf = fmt_at(reopened.editor, 0)
    check(reopened.editor.toPlainText() == "Lembrar de revisar a loja 15", "anotações são salvas e recuperadas")
    check(rf.fontWeight() >= QFont.Weight.Bold.value and rf.foreground().color().name().lower() == "#e53935",
          "formatação é mantida ao reabrir")
    reopened.deleteLater()
    shot(win, "anotacoes-formatadas")
    c = ne.textCursor()
    c.select(QTextCursor.SelectionType.Document)
    ne.setTextCursor(c)
    win.notes.clear_formatting()
    f0 = fmt_at(ne, 0)
    check(not f0.hasProperty(QTextFormat.Property.ForegroundBrush.value) and f0.fontWeight() < QFont.Weight.Bold.value,
          "Limpar formatação remove cor e negrito")
    old_dir = Path(tempfile.mkdtemp())
    (old_dir / "anotacoes.txt").write_text("nota antiga", encoding="utf-8")
    migrated = NotesTab(old_dir / "anotacoes.html")
    check(migrated.editor.toPlainText() == "nota antiga", "anotações da versão anterior são carregadas")
    migrated.deleteLater()

    print("Zoom do texto")
    for area in (win.audit, win.notes):
        base = area.zoom.size
        area.zoom.zoom_in()
        area.zoom.zoom_in()
        check(area.editor.font().pointSize() == base + 2, f"zoom aumenta a letra ({area.zoom.key})")
        check(int(win.settings.value(area.zoom.key)) == base + 2, f"tamanho da letra fica salvo ({area.zoom.key})")
        area.zoom.reset()
        check(area.editor.font().pointSize() == 12, f"Ctrl+0 volta a 100% ({area.zoom.key})")

    print("Layout")
    QTest.qWait(50)
    widths = {}
    for i in range(win.tabs.count()):
        win.nav.button(i).click()
        QTest.qWait(30)
        widths[win.nav.button(i).text()] = win.minimumSizeHint().width()
    print("    largura mínima da janela por área:", widths)
    check(max(widths.values()) <= 1000, "janela pode ser reduzida (largura mínima até 1000 px)")
    win.nav.button(0).click()
    before = win.minimumSizeHint().width()
    win.audit._flash("✔ " + "mensagem muito longa " * 30)
    win.notes._flash("✔ " + "mensagem muito longa " * 30)
    win.snippets.status.flash("✔ " + "mensagem muito longa " * 30)
    QTest.qWait(50)
    check(win.minimumSizeHint().width() == before, "mensagens de confirmação não alteram o tamanho da janela")

    print("Snippets e Ajuda")
    old_dir = Path(tempfile.mkdtemp())
    shutil.copyfile(Path(__file__).with_name("snippets_padrao_v1.json"), old_dir / "snippets.json")
    upgraded = SnippetStore(path=old_dir / "snippets.json")
    check(upgraded.updated_defaults and len(upgraded.snippets) == 25, "arquivo com o padrão antigo é atualizado")
    edited_dir = Path(tempfile.mkdtemp())
    (edited_dir / "snippets.json").write_text('{"Meu": {"prefix": "x", "body": ["y"]}}', encoding="utf-8")
    kept = SnippetStore(path=edited_dir / "snippets.json")
    check(not kept.updated_defaults and len(kept.snippets) == 1, "arquivo editado pela pessoa é mantido")
    check(len(kept.missing_defaults()) == 25, "padrões ausentes são identificados")
    upgraded.snippets = [s for s in upgraded.snippets if s.prefixes != ["dpl"]]
    upgraded.snippets[0].body = "frase editada"
    added = upgraded.add_missing_defaults()
    check([s.prefix_text for s in added] == ["dpl"], "só o padrão ausente é adicionado; o editado é mantido")

    print("Janela única")
    name = f"AuditoriaDQ-teste-{os.getpid()}"
    first = SingleInstance(name)
    check(not first.already_running(), "primeira cópia passa a ser a principal")
    pings = []
    first.activated.connect(lambda: pings.append(1))
    second = SingleInstance(name)
    check(second.already_running(), "segunda cópia percebe que já existe uma aberta")
    QTest.qWait(300)
    check(len(pings) == 1, "a cópia principal recebe o pedido para vir à frente")
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
