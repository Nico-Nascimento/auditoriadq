"""Aba Ajuda: perguntas frequentes sobre como usar o programa."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget


FAQ: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Visão geral",
        [
            (
                "Para que serve o programa?",
                "Ele junta as ferramentas do dia a dia da auditoria em uma janela só:"
                "<ul>"
                "<li><b>Auditoria</b>: onde você escreve o texto da auditoria, com o modelo padrão já preenchido "
                "e frases prontas (snippets) que aparecem ao digitar um prefixo.</li>"
                "<li><b>Calculadora 40%</b>: onde você cola prints, desenha a marcação e vê as faixas de 40%.</li>"
                "<li><b>Anotações</b>: um bloco de notas livre, salvo automaticamente.</li>"
                "<li><b>Snippets</b>: onde você cadastra e ajusta os prefixos e as frases.</li>"
                "</ul>"
                "Use o menu à esquerda para trocar de área.",
            ),
            (
                "Como troco entre modo claro e modo escuro?",
                "Clique no botão <b>Modo escuro</b> (ou <b>Modo claro</b>) no fim do menu à esquerda. "
                "O programa lembra a sua escolha da próxima vez que abrir.",
            ),
            (
                "Preciso de internet?",
                "Não. Tudo funciona no seu computador, inclusive os seus snippets.",
            ),
        ],
    ),
    (
        "Auditoria",
        [
            (
                "Como funciona o modelo padrão?",
                "O editor sempre abre com as seções <b>Roi</b>, <b>Espaços</b>, <b>Preços</b> e <b>Produtos</b>, "
                "separadas por <code>--------------</code>. Os títulos são texto comum: dá para editar, "
                "apagar ou criar seções direto no editor.",
            ),
            (
                "Onde escrevo cada ajuste?",
                "O primeiro ajuste fica na mesma linha do título, depois dos dois pontos. "
                "Os seguintes vão um por linha, logo abaixo, antes do separador:"
                "<pre>Produtos: Desmarcar o produto de número 12, ele não aparece até 40%.\n"
                "Ajustar a identificação do produto de número 15, identificar como \"Arroz\".\n"
                "--------------</pre>",
            ),
            (
                "Como uso os snippets (frases prontas)?",
                "Digite o prefixo, por exemplo <b>dp1</b>. Aparece uma lista com as opções que começam com o que "
                "você digitou, mostrando o prefixo e o nome da frase."
                "<ul>"
                "<li><b>↑ / ↓</b> escolhem a opção.</li>"
                "<li><b>Tab</b> ou <b>Enter</b> inserem a frase.</li>"
                "<li><b>Esc</b> fecha a lista.</li>"
                "<li><b>Ctrl + Espaço</b> abre a lista manualmente.</li>"
                "</ul>",
            ),
            (
                "Como preencho as partes da frase (id, nome, direita…)?",
                "Depois de inserir a frase, o cursor vai para o primeiro campo, com o texto sugerido selecionado. "
                "Digite por cima para trocar ou deixe como está."
                "<ul>"
                "<li><b>Tab</b> vai para o próximo campo.</li>"
                "<li><b>Shift + Tab</b> volta para o campo anterior.</li>"
                "<li>Depois do último campo, o <b>Tab</b> leva o cursor para o fim da frase.</li>"
                "<li><b>Esc</b> encerra o preenchimento a qualquer momento.</li>"
                "</ul>"
                "Os campos ficam destacados em amarelo (o atual) e azul (os outros) enquanto você preenche.",
            ),
            (
                "Como marco uma seção como correta?",
                "Depois dos dois pontos, digite <b>cr</b> e aperte <b>Tab</b>. Isso insere <b>Correto.</b>",
            ),
            (
                "Dois snippets aparecem com o mesmo prefixo. Está certo?",
                "Sim. Prefixos repetidos são permitidos (por exemplo, <b>mp1</b> para “Marcar produto 40%” e "
                "“Marcar produto escopo”). Os dois aparecem na lista e você escolhe pelo nome.",
            ),
            (
                "Como copio o texto para o sistema da empresa?",
                "Clique em <b>Copiar tudo</b> e cole onde precisar com <b>Ctrl + V</b>.",
            ),
            (
                "Para que serve o botão “Resetar formato”?",
                "Ele apaga o texto e volta ao modelo padrão. Se houver texto escrito, o programa pede confirmação. "
                "Se resetar sem querer, aperte <b>Ctrl + Z</b> no editor para desfazer.",
            ),
        ],
    ),
    (
        "Calculadora 40%",
        [
            (
                "Como coloco imagens?",
                "Tire um print e aperte <b>Ctrl + V</b> com a Calculadora aberta, ou clique em <b>Selecionar imagens</b> "
                "(dá para escolher várias de uma vez). Também dá para arrastar arquivos de imagem do Explorer "
                "para a área cinza. Cada imagem nova entra ao lado da anterior.",
            ),
            (
                "Como faço a marcação?",
                "Com o <b>botão esquerdo</b>, clique e arraste sobre a imagem para desenhar o retângulo. "
                "Depois, também com o botão esquerdo:"
                "<ul>"
                "<li>arraste o retângulo para movê-lo;</li>"
                "<li>arraste as alças (quadradinhos) para mudar o tamanho.</li>"
                "</ul>"
                "Cada imagem tem a sua própria marcação. Para desenhar de novo, use <b>Resetar Seleção</b>.",
            ),
            (
                "Como leio as faixas de 40%?",
                "A <b>faixa azul</b> marca 40% da altura do retângulo e a <b>faixa amarela</b> marca 40% da largura. "
                "As linhas mostram onde termina cada 40%. Use <b>Horizontal</b> (Esquerda/Direita) e "
                "<b>Vertical</b> (Superior/Inferior) para escolher de que lado as faixas começam.",
            ),
            (
                "Como movo as imagens e a tela?",
                "Segure o <b>botão direito</b> e arraste:"
                "<ul>"
                "<li><b>em cima de uma imagem</b>: move aquela imagem (para deixar lado a lado e comparar);</li>"
                "<li><b>no fundo vazio</b>: move a vista inteira.</li>"
                "</ul>"
                "A <b>roda do mouse</b> faz zoom no ponto onde está o cursor (de 20% a 1000%).",
            ),
            (
                "O que é a imagem selecionada?",
                "É a última imagem em que você clicou. Ela fica com <b>borda tracejada</b>, por cima das outras e "
                "com as alças visíveis. Os botões <b>Remover imagem</b>, <b>Resetar Seleção</b>, "
                "<b>Horizontal</b> e <b>Vertical</b> agem só nela. A tecla <b>Delete</b> também remove a "
                "imagem selecionada.",
            ),
        ],
    ),
    (
        "Anotações",
        [
            (
                "Para que serve a área de Anotações?",
                "É um bloco de notas livre, para anotar o que quiser. Não tem snippets nem modelo: é só digitar. "
                "O texto é salvo automaticamente no seu computador "
                "(<code>AppData\\Roaming\\AuditoriaDQ\\anotacoes.txt</code>) e continua lá quando você "
                "fechar e abrir o programa. O botão <b>Copiar tudo</b> copia as anotações.",
            ),
        ],
    ),
    (
        "Snippets",
        [
            (
                "Como crio ou edito uma frase?",
                "Na área <b>Snippets</b>, escolha um item da lista ou clique em <b>Novo snippet</b>. Preencha:"
                "<ul>"
                "<li><b>Nome</b>: aparece na lista de sugestões e ajuda a escolher.</li>"
                "<li><b>Prefixo</b>: o que você digita para chamar a frase. Para ter mais de um, separe com "
                "vírgula.</li>"
                "<li><b>Frase</b>: o texto que será inserido.</li>"
                "</ul>"
                "As alterações são salvas automaticamente.",
            ),
            (
                "Como crio os campos para preencher?",
                "Use <code>${1:texto}</code>, <code>${2:texto}</code> e assim por diante. O número define a ordem "
                "do Tab e o texto é o valor sugerido. Exemplo:"
                "<pre>Desmarcar o produto de número ${1:id}, ${2:ele não aparece até 40%}.</pre>"
                "Use <code>$0</code> para dizer onde o cursor deve parar no final. A <b>Prévia</b> mostra a frase "
                "com os campos destacados.",
            ),
            (
                "Posso usar meu arquivo de snippets do VS Code?",
                "Sim. O formato é o mesmo. Use <b>Importar arquivo…</b> para trazer um arquivo do VS Code "
                "(escolha entre adicionar aos seus ou substituir todos) e <b>Exportar arquivo…</b> para gerar um "
                "arquivo que o VS Code também entende.",
            ),
            (
                "Onde ficam salvos os meus snippets?",
                "Cada pessoa tem o próprio arquivo, salvo na pasta do usuário no Windows "
                "(<code>AppData\\Roaming\\AuditoriaDQ\\snippets.json</code>). O caminho completo aparece "
                "no rodapé da área Snippets, junto com o botão <b>Abrir pasta do arquivo</b>. "
                "Para passar seus snippets a um colega, exporte o arquivo e peça para ele importar.",
            ),
        ],
    ),
    (
        "Atalhos",
        [
            (
                "Lista de atalhos",
                "<table cellspacing='0' cellpadding='4'>"
                "<tr><td><b>Tab</b> / <b>Enter</b></td><td>Inserir o snippet escolhido na lista</td></tr>"
                "<tr><td><b>Tab</b> / <b>Shift + Tab</b></td><td>Próximo / anterior campo do snippet</td></tr>"
                "<tr><td><b>Esc</b></td><td>Fechar a lista ou sair dos campos</td></tr>"
                "<tr><td><b>Ctrl + Espaço</b></td><td>Abrir a lista de sugestões</td></tr>"
                "<tr><td><b>Ctrl + Z</b></td><td>Desfazer no editor</td></tr>"
                "<tr><td><b>Ctrl + V</b></td><td>Colar print (na Calculadora 40%)</td></tr>"
                "<tr><td><b>Delete</b></td><td>Remover a imagem selecionada (na Calculadora 40%)</td></tr>"
                "<tr><td><b>Botão esquerdo</b></td><td>Marcar, mover e redimensionar</td></tr>"
                "<tr><td><b>Botão direito</b></td><td>Arrastar imagem ou a vista</td></tr>"
                "<tr><td><b>Roda do mouse</b></td><td>Zoom</td></tr>"
                "</table>",
            ),
        ],
    ),
]


class FaqItem(QWidget):
    def __init__(self, question: str, answer: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.question = question
        self.answer_text = answer
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.button = QPushButton()
        self.button.setCheckable(True)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setObjectName("faqQuestion")
        self.button.toggled.connect(self._toggle)
        lay.addWidget(self.button)

        self.answer = QLabel(answer)
        self.answer.setWordWrap(True)
        self.answer.setTextFormat(Qt.TextFormat.RichText)
        self.answer.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.answer.setObjectName("faqAnswer")
        self.answer.hide()
        lay.addWidget(self.answer)
        self._toggle(False)

    def _toggle(self, open_: bool) -> None:
        self.button.setText(("▾  " if open_ else "▸  ") + self.question)
        self.answer.setVisible(open_)

    def matches(self, query: str) -> bool:
        q = query.casefold()
        return q in self.question.casefold() or q in self.answer_text.casefold()


class HelpTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Procurar na ajuda… (ex.: zoom, Tab, importar)")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter)
        root.addWidget(self.search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setObjectName("faqContent")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(4, 4, 12, 4)
        self.content_layout.setSpacing(6)

        self.items: list[FaqItem] = []
        self.headers: list[tuple[QLabel, list[FaqItem]]] = []
        for section, entries in FAQ:
            header = QLabel(section)
            header.setObjectName("faqSection")
            self.content_layout.addWidget(header)
            section_items = []
            for q, a in entries:
                item = FaqItem(q, a)
                self.content_layout.addWidget(item)
                self.items.append(item)
                section_items.append(item)
            self.headers.append((header, section_items))
        self.content_layout.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        if self.items:
            self.items[0].button.setChecked(True)

    def _filter(self, text: str) -> None:
        q = text.strip()
        for header, items in self.headers:
            any_visible = False
            for item in items:
                visible = not q or item.matches(q)
                item.setVisible(visible)
                if q and visible:
                    item.button.setChecked(True)
                any_visible = any_visible or visible
            header.setVisible(any_visible)
