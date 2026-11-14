"""Aba Snippets: cadastro de prefixos e frases."""
from __future__ import annotations

import html
import os
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .snippets import (
    Snippet,
    load_snippets_file,
    parse_body,
    parse_prefix_text,
    same_prefix_conflicts,
    snippets_to_text,
)
from .layout import FlowLayout, StatusLine, hint_label
from .store import SnippetStore
from . import theme


def preview_html(body: str) -> str:
    """Frase expandida, com os campos de preenchimento destacados."""
    t = theme.current()
    parsed = parse_body(body)
    text = parsed.text
    if not text:
        return f"<i style='color:{t['text_muted']}'>(frase vazia)</i>"
    spans = sorted(parsed.tabstops, key=lambda f: f.start)
    parts: list[str] = []
    pos = 0
    for f in spans:
        if f.start < pos:  # campo aninhado dentro de outro: ignora no destaque
            continue
        parts.append(html.escape(text[pos:f.start]))
        inner = html.escape(text[f.start:f.end]) or "&nbsp;&nbsp;&nbsp;"
        if f.choices:  # campo com lista de opções: mostra todas, separadas por "/"
            inner = " / ".join(html.escape(c) for c in f.choices) + " ▾"
        parts.append(
            f"<span style='background-color:{t['field_highlight']}; color:{t['field_highlight_text']};'>{inner}</span>"
            f"<sup style='color:{t['text_soft']}'>{f.index}</sup>"
        )
        pos = f.end
    parts.append(html.escape(text[pos:]))
    return "".join(parts).replace("\n", "<br>")


class SnippetsTab(QWidget):
    def __init__(self, store: SnippetStore, parent: QWidget | None = None):
        super().__init__(parent)
        self.store = store
        self.current: Snippet | None = None
        self._loading = False

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # 1) botões  2) texto explicativo  3) confirmação das ações
        bar = FlowLayout()
        self.btn_new = QPushButton("Novo snippet")
        self.btn_new.clicked.connect(self.new_snippet)
        self.btn_delete = QPushButton("Excluir")
        self.btn_delete.clicked.connect(self.delete_snippet)
        self.btn_import = QPushButton("Importar arquivo…")
        self.btn_import.clicked.connect(self.import_file)
        self.btn_export = QPushButton("Exportar arquivo…")
        self.btn_export.clicked.connect(self.export_file)
        self.btn_defaults = QPushButton("Adicionar padrões ausentes")
        self.btn_defaults.setToolTip(
            "Adiciona os snippets do padrão atual que ainda não existem na sua lista, "
            "sem alterar os que já existem."
        )
        self.btn_defaults.clicked.connect(self.add_missing_defaults)
        self.btn_folder = QPushButton("Abrir pasta do arquivo")
        self.btn_folder.clicked.connect(self.open_folder)
        for b in (self.btn_new, self.btn_delete, self.btn_import, self.btn_export, self.btn_defaults,
                  self.btn_folder):
            bar.addWidget(b)
        root.addLayout(bar)

        self.path_label = hint_label("")
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self.path_label)
        self.status = StatusLine()
        root.addWidget(self.status)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # ---------------- lista ----------------
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 8, 0)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Pesquisar por nome, prefixo ou frase…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh_list)
        lv.addWidget(self.search)

        self.list = QListWidget()
        self.list.currentItemChanged.connect(self._on_select)
        lv.addWidget(self.list, 1)

        splitter.addWidget(left)

        # ---------------- formulário ----------------
        right = QFrame()
        right.setObjectName("card")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(18, 18, 18, 18)
        rv.setSpacing(10)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setVerticalSpacing(10)
        self.ed_name = QLineEdit()
        self.ed_name.setPlaceholderText("Exemplo: Desmarcar produto 40%")
        self.ed_prefix = QLineEdit()
        self.ed_prefix.setPlaceholderText("Exemplo: dp   (para mais de um prefixo, separe-os por vírgula)")
        self.ed_body = QPlainTextEdit()
        self.ed_body.setPlaceholderText("Exemplo: Desmarcar o produto de número ${1:id}, ${2:ele não aparece até 40%}.")
        self.ed_body.setMinimumHeight(110)
        form.addRow("Nome:", self.ed_name)
        form.addRow("Prefixo:", self.ed_prefix)
        form.addRow("Frase:", self.ed_body)
        rv.addLayout(form)

        syntax = QLabel(
            "Campos de preenchimento: <b>${1:texto}</b>, <b>${2:texto}</b>… "
            "O número define a ordem de navegação com Tab, e o texto corresponde ao valor sugerido. "
            "Para oferecer uma lista de opções, utilize <b>${3|direita,esquerda|}</b> (a primeira opção é "
            "a sugerida). Utilize <b>$0</b> para indicar a posição final do cursor."
        )
        syntax.setObjectName("hint")
        syntax.setWordWrap(True)
        rv.addWidget(syntax)

        lbl = QLabel("Prévia:")
        lbl.setObjectName("sectionLabel")
        rv.addWidget(lbl)
        self.preview = QLabel()
        self.preview.setWordWrap(True)
        self.preview.setTextFormat(Qt.TextFormat.RichText)
        self.preview.setObjectName("preview")
        self.preview.setMinimumHeight(48)
        rv.addWidget(self.preview)

        self.warning = QLabel()
        self.warning.setObjectName("warning")
        self.warning.setWordWrap(True)
        self.warning.hide()
        rv.addWidget(self.warning)
        rv.addStretch(1)
        splitter.addWidget(right)
        splitter.setSizes([380, 700])

        self.ed_name.textEdited.connect(self._on_edit)
        self.ed_prefix.textEdited.connect(self._on_edit)
        self.ed_body.textChanged.connect(self._on_edit)


        self.store.changed.connect(self._on_store_changed)
        self.refresh_list()
        self._update_path_label()
        if self.list.count():
            self.list.setCurrentRow(0)
        else:
            self._show(None)

    # ------------------------------------------------------------------
    @staticmethod
    def _item_text(s: Snippet) -> str:
        prefix = s.prefix_text or "(sem prefixo)"
        return f"{prefix}   —   {s.name}"

    def _update_path_label(self) -> None:
        self.path_label.setText(
            "Cadastre os prefixos e as frases utilizados na área Auditoria. As alterações são salvas "
            f"automaticamente em: {self.store.path}"
        )

    def refresh_list(self) -> None:
        query = self.search.text().strip().casefold()
        keep = self.current
        self.list.blockSignals(True)
        self.list.clear()
        select_item = None
        for s in self.store.snippets:
            hay = f"{s.name} {s.prefix_text} {s.body}".casefold()
            if query and query not in hay:
                continue
            item = QListWidgetItem(self._item_text(s))
            item.setData(Qt.ItemDataRole.UserRole, s)
            item.setToolTip(parse_body(s.body).text)
            self.list.addItem(item)
            if s is keep:
                select_item = item
        self.list.blockSignals(False)
        if select_item is not None:
            self.list.setCurrentItem(select_item)

    def _find_item(self, s: Snippet) -> QListWidgetItem | None:
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.data(Qt.ItemDataRole.UserRole) is s:
                return it
        return None

    def _on_select(self, cur: QListWidgetItem | None, _prev=None) -> None:
        self._show(cur.data(Qt.ItemDataRole.UserRole) if cur else None)

    def _show(self, s: Snippet | None) -> None:
        self.current = s
        self._loading = True
        enabled = s is not None
        for w in (self.ed_name, self.ed_prefix, self.ed_body, self.btn_delete):
            w.setEnabled(enabled)
        self.ed_name.setText(s.name if s else "")
        self.ed_prefix.setText(s.prefix_text if s else "")
        self.ed_body.setPlainText(s.body if s else "")
        self._loading = False
        self._update_preview()

    def _on_edit(self) -> None:
        if self._loading or self.current is None:
            return
        s = self.current
        s.name = self.ed_name.text()
        s.prefixes = parse_prefix_text(self.ed_prefix.text())
        s.body = self.ed_body.toPlainText()
        item = self._find_item(s)
        if item:
            item.setText(self._item_text(s))
            item.setToolTip(parse_body(s.body).text)
        self._update_preview()
        self._editing = True
        self.store.schedule_save()
        self._editing = False

    def _on_store_changed(self) -> None:
        if getattr(self, "_editing", False):
            return
        self.refresh_list()

    def apply_theme(self) -> None:
        self._update_preview()

    def _update_preview(self) -> None:
        s = self.current
        if s is None:
            self.preview.setText(f"<i style='color:{theme.current()['text_muted']}'>Selecione um snippet na lista.</i>")
            self.warning.hide()
            return
        self.preview.setText(preview_html(s.body))

        msgs: list[str] = []
        if not s.prefixes:
            msgs.append("⚠ Este snippet não possui prefixo e, portanto, não aparece nas sugestões do editor.")
        for prefix, others in same_prefix_conflicts(self.store.snippets, s).items():
            names = ", ".join(f"“{o.name}”" for o in others)
            msgs.append(
                f"ℹ O prefixo <b>{html.escape(prefix)}</b> também é utilizado por {html.escape(names)}. "
                "Ambos são exibidos na lista de sugestões e a escolha é feita pelo nome."
            )
        name = s.name.strip()
        if not name:
            msgs.append("⚠ Informe um nome para o snippet, pois ele é exibido na lista de sugestões.")
        elif any(o is not s and o.name.strip() == name for o in self.store.snippets):
            msgs.append("⚠ Já existe outro snippet com este nome. Ao salvar, um número será acrescentado ao final do nome.")
        if msgs:
            self.warning.setText("<br>".join(msgs))
            self.warning.show()
        else:
            self.warning.hide()

    # ------------------------------------------------------------------
    def new_snippet(self) -> None:
        s = Snippet(name="Novo snippet", prefixes=[], body="")
        self.search.clear()
        self.store.add(s)
        self.current = s
        self.refresh_list()
        item = self._find_item(s)
        if item:
            self.list.setCurrentItem(item)
            self.list.scrollToItem(item)
        self.ed_name.setFocus()
        self.ed_name.selectAll()

    def delete_snippet(self) -> None:
        s = self.current
        if s is None:
            return
        ans = QMessageBox.question(
            self,
            "Excluir snippet",
            f"Deseja excluir o snippet “{s.name}” ({s.prefix_text or 'sem prefixo'})?",
        )
        if ans != QMessageBox.StandardButton.Yes:
            return
        row = self.list.currentRow()
        self.current = None
        self.store.remove(s)
        self.refresh_list()
        if self.list.count():
            self.list.setCurrentRow(min(row, self.list.count() - 1))
        else:
            self._show(None)

    def import_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar snippets",
            "",
            "Snippets (*.json *.code-snippets *.txt);;Todos os arquivos (*)",
        )
        if not path:
            return
        try:
            imported = load_snippets_file(path)
        except Exception as exc:
            QMessageBox.warning(self, "Importar snippets", f"Não foi possível ler o arquivo:\n{exc}")
            return
        if not imported:
            QMessageBox.information(self, "Importar snippets", "Nenhum snippet foi encontrado no arquivo.")
            return

        box = QMessageBox(self)
        box.setWindowTitle("Importar snippets")
        box.setText(f"Foram encontrados {len(imported)} snippets. Como deseja importá-los?")
        btn_add = box.addButton("Adicionar aos existentes", QMessageBox.ButtonRole.AcceptRole)
        btn_replace = box.addButton("Substituir todos", QMessageBox.ButtonRole.DestructiveRole)
        box.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked is btn_replace:
            self.current = None
            self.store.replace_all(imported)
            self.status.flash(f"✔ Os snippets foram substituídos pelos {len(imported)} do arquivo importado.", 4000)
        elif clicked is btn_add:
            existing = {(s.name, tuple(s.prefixes), s.body) for s in self.store.snippets}
            new = [s for s in imported if (s.name, tuple(s.prefixes), s.body) not in existing]
            self.store.replace_all(self.store.snippets + new)
            self.status.flash(f"✔ {len(new)} snippets foram adicionados ({len(imported) - len(new)} já existiam).", 4000)
        else:
            return
        self.refresh_list()
        if self.current is None and self.list.count():
            self.list.setCurrentRow(0)

    def export_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar snippets",
            "snippets-auditoria.code-snippets",
            "Snippets do VS Code (*.code-snippets);;JSON (*.json)",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(snippets_to_text(self.store.snippets))
        except OSError as exc:
            QMessageBox.warning(self, "Exportar snippets", f"Não foi possível salvar o arquivo:\n{exc}")
            return
        self.status.flash(f"✔ Arquivo exportado para: {path}", 5000)

    def add_missing_defaults(self) -> None:
        missing = self.store.missing_defaults()
        if not missing:
            self.status.flash("✔ Todos os snippets do padrão atual já constam na sua lista.", 4000)
            return
        names = "\n".join(f"• {s.prefix_text} — {s.name}" for s in missing)
        ans = QMessageBox.question(
            self,
            "Padrões ausentes",
            f"Os seguintes snippets do padrão atual não constam na sua lista:\n\n{names}\n\n"
            "Deseja adicioná-los? Os snippets existentes não serão alterados.",
        )
        if ans != QMessageBox.StandardButton.Yes:
            return
        added = self.store.add_missing_defaults()
        self.refresh_list()
        if added:
            item = self._find_item(added[0])
            if item:
                self.list.setCurrentItem(item)
                self.list.scrollToItem(item)
        self.status.flash(f"✔ {len(added)} snippet(s) adicionado(s).", 4000)

    def open_folder(self) -> None:
        folder = str(self.store.path.parent)
        if sys.platform.startswith("win"):
            os.startfile(folder)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", folder])
