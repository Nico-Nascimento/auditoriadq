"""Aba Ajuda: perguntas frequentes sobre como usar o programa."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget


FAQ: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Visão geral",
        [
            (
                "Qual é a finalidade do programa?",
                "O AuditoriaDQ reúne, em uma única janela, as ferramentas utilizadas no trabalho de auditoria:"
                "<ul>"
                "<li><b>Auditoria</b>: redação do texto da auditoria, com o modelo padrão já preenchido e frases "
                "prontas (snippets) acionadas por prefixos.</li>"
                "<li><b>Calculadora 40%</b>: inserção de capturas de tela, marcação da área do produto e "
                "visualização das faixas de 40%.</li>"
                "<li><b>Anotações</b>: bloco de notas livre, salvo automaticamente.</li>"
                "<li><b>Snippets</b>: cadastro e manutenção dos prefixos e das frases.</li>"
                "</ul>"
                "A navegação entre as áreas é feita pelo menu lateral, à esquerda.",
            ),
            (
                "Como alternar entre o modo claro e o modo escuro?",
                "Utilize o botão <b>Modo escuro</b> (ou <b>Modo claro</b>), localizado no final do menu lateral. "
                "A preferência é registrada e mantida nas próximas utilizações do programa.",
            ),
            (
                "Por que o programa não abre uma segunda janela?",
                "Para evitar que duas janelas gravem ao mesmo tempo nos mesmos arquivos, o programa permite "
                "apenas uma janela aberta. Ao executá-lo novamente, a janela já aberta é trazida para a frente.",
            ),
            (
                "É necessário estar conectado à internet?",
                "Não. O programa funciona integralmente no computador, inclusive o armazenamento dos snippets e "
                "das anotações.",
            ),
        ],
    ),
    (
        "Auditoria",
        [
            (
                "Como funciona o modelo padrão?",
                "O editor é aberto com as seções <b>Roi</b>, <b>Espaços</b>, <b>Preços</b> e <b>Produtos</b>, "
                "separadas por <code>--------------</code>. Os títulos são texto comum e podem ser editados, "
                "removidos ou complementados diretamente no editor.",
            ),
            (
                "Onde cada ajuste deve ser registrado?",
                "O primeiro ajuste deve ser registrado na mesma linha do título, após os dois pontos. "
                "Os ajustes seguintes devem ser registrados um por linha, logo abaixo, antes do separador:"
                "<pre>Produtos: Desmarcar o produto de número 12, ele não aparece até 40%.\n"
                "Ajustar a identificação do produto de número 15, identificar como \"Arroz\".\n"
                "--------------</pre>",
            ),
            (
                "Como utilizar os snippets (frases prontas)?",
                "Digite o prefixo desejado, por exemplo <b>dp</b>. Será exibida uma lista com as opções "
                "correspondentes, contendo o prefixo e o nome de cada frase."
                "<ul>"
                "<li><b>↑ / ↓</b>: selecionam a opção.</li>"
                "<li><b>Tab</b> ou <b>Enter</b>: inserem a frase selecionada.</li>"
                "<li><b>Esc</b>: fecha a lista.</li>"
                "<li><b>Ctrl + Espaço</b>: exibe a lista manualmente.</li>"
                "</ul>",
            ),
            (
                "Como preencher os campos da frase (id, identificação, direita etc.)?",
                "Após a inserção da frase, o cursor é posicionado no primeiro campo, com o texto sugerido "
                "selecionado. Basta digitar o novo conteúdo ou manter o texto sugerido."
                "<ul>"
                "<li><b>Tab</b>: avança para o próximo campo.</li>"
                "<li><b>Shift + Tab</b>: retorna ao campo anterior.</li>"
                "<li>Após o último campo, <b>Tab</b> posiciona o cursor ao final da frase.</li>"
                "<li><b>Esc</b>: encerra o preenchimento a qualquer momento.</li>"
                "</ul>"
                "Durante o preenchimento, o campo atual é destacado em amarelo e os demais, em azul. "
                "Quando o campo possui uma lista de opções (por exemplo, direita/esquerda), a lista é exibida "
                "automaticamente: utilize <b>↑ / ↓</b> para escolher e <b>Tab</b> ou <b>Enter</b> para "
                "confirmar e seguir para o próximo campo. Para informar outro valor, basta digitar. "
                "<b>Ctrl + Espaço</b> reabre a lista.",
            ),
            (
                "Como registrar que uma seção está correta?",
                "Após os dois pontos, digite <b>cr</b> e pressione <b>Tab</b>. O texto <b>Correto.</b> será "
                "inserido.",
            ),
            (
                "Por que mais de um snippet aparece na lista?",
                "A lista exibe todos os snippets cujo prefixo começa com o texto digitado. Por exemplo, "
                "<b>dp</b> exibe <b>dp</b> (Desmarcar produto) e <b>dps</b> (Desmarcar produtos); o prefixo "
                "idêntico ao digitado aparece primeiro. Prefixos repetidos também são permitidos; nesse caso, a "
                "escolha é feita pelo nome.",
            ),
            (
                "Como transferir o texto para o sistema da empresa?",
                "Utilize o botão <b>Copiar tudo</b> e, em seguida, cole o conteúdo no destino com "
                "<b>Ctrl + V</b>.",
            ),
            (
                "Como aumentar ou diminuir o tamanho do texto?",
                "Nas áreas <b>Auditoria</b> e <b>Anotações</b>, utilize os botões <b>A−</b> e <b>A+</b>, no "
                "canto superior direito, ou mantenha <b>Ctrl</b> pressionado e gire a roda do mouse. Também é "
                "possível utilizar <b>Ctrl + +</b>, <b>Ctrl + −</b> e <b>Ctrl + 0</b> (volta a 100%). O tamanho "
                "escolhido é mantido nas próximas utilizações.",
            ),
            (
                "O texto da auditoria é salvo?",
                "Sim. O texto é salvo automaticamente enquanto é digitado. Caso o programa seja fechado, o texto "
                "é recuperado na próxima abertura. Para iniciar uma nova auditoria, utilize "
                "<b>Resetar formato</b>.",
            ),
            (
                "Qual é a função do botão “Resetar formato”?",
                "O botão apaga o texto atual e restaura o modelo padrão. Caso haja texto escrito, será solicitada "
                "confirmação. Para desfazer a operação, pressione <b>Ctrl + Z</b> no editor.",
            ),
        ],
    ),
    (
        "Calculadora 40%",
        [
            (
                "Como inserir imagens?",
                "Com a Calculadora 40% aberta, cole uma captura de tela com <b>Ctrl + V</b> ou utilize o botão "
                "<b>Selecionar imagens</b>, que permite escolher vários arquivos de uma vez. Também é possível "
                "arrastar arquivos de imagem do Explorador de Arquivos para a área cinza. Cada nova imagem é "
                "posicionada ao lado da anterior.",
            ),
            (
                "Como fazer a marcação?",
                "Com o <b>botão esquerdo</b> do mouse, clique e arraste sobre a imagem para desenhar o retângulo. "
                "Em seguida, também com o botão esquerdo:"
                "<ul>"
                "<li>arraste o retângulo para reposicioná-lo;</li>"
                "<li>arraste as alças (pequenos quadrados) para alterar o tamanho.</li>"
                "</ul>"
                "Cada imagem possui a sua própria marcação. Para desenhar uma nova marcação, utilize "
                "<b>Resetar Seleção</b>.",
            ),
            (
                "Como interpretar as faixas de 40%?",
                "A <b>faixa azul</b> representa 40% da altura do retângulo e a <b>faixa amarela</b>, 40% da "
                "largura. As linhas indicam o limite de cada faixa. As opções <b>Horizontal</b> "
                "(Esquerda/Direita) e <b>Vertical</b> (Superior/Inferior) definem o lado a partir do qual as "
                "faixas são calculadas.",
            ),
            (
                "Como mover as imagens e a área de visualização?",
                "Mantenha o <b>botão direito</b> do mouse pressionado e arraste:"
                "<ul>"
                "<li><b>sobre uma imagem</b>: a imagem é movida, o que permite posicioná-las lado a lado para "
                "comparação;</li>"
                "<li><b>sobre o fundo</b>: toda a área de visualização é movida.</li>"
                "</ul>"
                "A <b>roda do mouse</b> aplica zoom no ponto em que o cursor está posicionado (de 5% a 1000%). "
                "O botão <b>Ajustar à tela</b> ajusta o zoom para exibir todas as imagens de uma só vez.",
            ),
            (
                "O que é a imagem selecionada?",
                "É a última imagem em que houve clique. Ela é indicada pela <b>borda tracejada</b>, permanece "
                "à frente das demais e exibe as alças da marcação. Os botões <b>Remover imagem</b>, "
                "<b>Resetar Seleção</b>, <b>Horizontal</b> e <b>Vertical</b> atuam somente sobre ela. A tecla "
                "<b>Delete</b> também remove a imagem selecionada.",
            ),
        ],
    ),
    (
        "Anotações",
        [
            (
                "Qual é a finalidade da área de Anotações?",
                "É um bloco de notas livre, sem snippets e sem modelo. O conteúdo é salvo automaticamente neste "
                "computador (<code>AppData\\Roaming\\AuditoriaDQ\\anotacoes.html</code>) e permanece "
                "disponível ao reabrir o programa. O botão <b>Copiar tudo</b> copia as anotações; ao colar no "
                "Word ou no Outlook, a formatação é mantida.",
            ),
            (
                "Como destacar trechos das anotações?",
                "Selecione a palavra ou o trecho desejado e utilize os botões da barra superior:"
                "<ul>"
                "<li><b>N</b>: negrito (<b>Ctrl + N</b> ou <b>Ctrl + B</b>);</li>"
                "<li><b>I</b>: itálico (<b>Ctrl + I</b>);</li>"
                "<li><b>Cor do texto</b>: altera a cor das letras; a opção <b>Automática</b> restaura a cor "
                "padrão;</li>"
                "<li><b>Marca-texto</b>: aplica uma cor de fundo ao trecho, como um marcador;</li>"
                "<li><b>Limpar formatação</b>: remove cor, marca-texto, negrito e itálico do trecho.</li>"
                "</ul>"
                "Sem seleção, a formatação é aplicada à palavra em que o cursor está. Textos colados de outros "
                "programas entram sem formatação.",
            ),
        ],
    ),
    (
        "Snippets",
        [
            (
                "Como criar ou editar uma frase?",
                "Na área <b>Snippets</b>, selecione um item da lista ou utilize o botão <b>Novo snippet</b>. "
                "Em seguida, preencha:"
                "<ul>"
                "<li><b>Nome</b>: exibido na lista de sugestões, auxilia na escolha da frase.</li>"
                "<li><b>Prefixo</b>: texto digitado para acionar a frase. Para utilizar mais de um prefixo, "
                "separe-os por vírgula.</li>"
                "<li><b>Frase</b>: texto que será inserido.</li>"
                "</ul>"
                "As alterações são salvas automaticamente.",
            ),
            (
                "Como criar campos de preenchimento?",
                "Utilize <code>${1:texto}</code>, <code>${2:texto}</code> e assim por diante. O número define a "
                "ordem de navegação com Tab, e o texto corresponde ao valor sugerido. Exemplo:"
                "<pre>Desmarcar o produto de número ${1:id}, ${2:ele não aparece até 40%}.</pre>"
                "Para oferecer uma lista de opções no campo, separe as opções por vírgula entre barras "
                "verticais: <code>${3|direita,esquerda|}</code>. A primeira opção é a sugerida, e as demais "
                "aparecem em uma lista durante o preenchimento. Exemplo:"
                "<pre>Ampliar a marcação ${1|superior,inferior,lateral direita,lateral esquerda|} do Roi.</pre>"
                "Para usar uma vírgula dentro de uma opção, escreva <code>\\,</code> (no arquivo JSON, <code>\\\\,</code>). "
                "Utilize <code>$0</code> para indicar a posição final do cursor. A <b>Prévia</b> exibe a frase "
                "com os campos destacados; nos campos com lista, todas as opções são exibidas."
            ),
            (
                "É possível utilizar o arquivo de snippets do VS Code?",
                "Sim, o formato é o mesmo. O botão <b>Importar arquivo…</b> permite trazer um arquivo do VS Code, "
                "adicionando-o aos snippets existentes ou substituindo-os. O botão <b>Exportar arquivo…</b> gera "
                "um arquivo compatível com o VS Code.",
            ),
            (
                "Como receber os novos snippets do padrão?",
                "Quando uma nova versão do programa traz snippets padrão novos, utilize o botão "
                "<b>Adicionar padrões ausentes</b>, na área Snippets. Somente os snippets que ainda não constam "
                "na lista são adicionados; os snippets existentes, inclusive os editados, não são alterados.",
            ),
            (
                "Onde os snippets ficam armazenados?",
                "Cada usuário possui o próprio arquivo, armazenado na pasta do usuário no Windows "
                "(<code>AppData\\Roaming\\AuditoriaDQ\\snippets.json</code>). O caminho completo é exibido "
                "no rodapé da área Snippets, junto ao botão <b>Abrir pasta do arquivo</b>. Para compartilhar os "
                "snippets com outra pessoa, exporte o arquivo e solicite que ela o importe.",
            ),
        ],
    ),
    (
        "Atalhos",
        [
            (
                "Lista de atalhos",
                "<table cellspacing='0' cellpadding='4'>"
                "<tr><td><b>Tab</b> / <b>Enter</b></td><td>Inserir o snippet selecionado na lista</td></tr>"
                "<tr><td><b>Tab</b> / <b>Shift + Tab</b></td><td>Avançar / retornar entre os campos do snippet</td></tr>"
                "<tr><td><b>Esc</b></td><td>Fechar a lista ou encerrar o preenchimento</td></tr>"
                "<tr><td><b>Ctrl + Espaço</b></td><td>Exibir a lista de sugestões</td></tr>"
                "<tr><td><b>Ctrl + Z</b></td><td>Desfazer no editor</td></tr>"
                "<tr><td><b>Ctrl + roda do mouse</b></td><td>Aumentar ou diminuir o texto (Auditoria e Anotações)</td></tr>"
                "<tr><td><b>Ctrl + +</b> / <b>Ctrl + −</b> / <b>Ctrl + 0</b></td><td>Aumentar, diminuir ou "
                "restaurar o tamanho do texto</td></tr>"
                "<tr><td><b>Ctrl + N</b> / <b>Ctrl + I</b></td><td>Negrito / itálico (Anotações)</td></tr>"
                "<tr><td><b>Ctrl + V</b></td><td>Colar captura de tela (Calculadora 40%)</td></tr>"
                "<tr><td><b>Delete</b></td><td>Remover a imagem selecionada (Calculadora 40%)</td></tr>"
                "<tr><td><b>Botão esquerdo</b></td><td>Marcar, mover e redimensionar</td></tr>"
                "<tr><td><b>Botão direito</b></td><td>Mover a imagem ou a área de visualização</td></tr>"
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
        self.search.setPlaceholderText("Pesquisar na ajuda… (por exemplo: zoom, Tab, importar)")
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
