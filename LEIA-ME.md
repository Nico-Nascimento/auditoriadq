# AuditoriaDQ (Windows)

Programa com quatro abas:

- **Auditoria**: editor com o modelo padrão (Roi / Espaços / Preços / Produtos) e snippets no estilo do VS Code.
- **Calculadora 40%**: várias imagens lado a lado, uma marcação por imagem e faixas de 40%.
- **Snippets**: cadastro de prefixos e frases. Importa e exporta no formato do VS Code.
- **Ajuda**: perguntas frequentes sobre como usar o programa.

## Baixar o programa

A versão mais recente fica em **Releases**, na página do repositório, no arquivo **AuditoriaDQ.zip**. Extraia a pasta para um local permanente e execute o `AuditoriaDQ.exe` que está dentro dela. Não é preciso ter Python instalado. As instruções completas estão no arquivo `COMO INSTALAR.txt`, dentro da pasta.

## Como sai uma versão nova

A cada envio para a branch `main`, o GitHub Actions (num Windows) faz quatro coisas:
1. roda o teste automático;
2. gera o programa (pasta) e o `AuditoriaDQ.zip`;
3. confere se o `.exe` abre e se uma segunda cópia só traz a primeira para a frente;
4. se o número em `VERSION` (arquivo `app/main_window.py`) for novo, publica em Releases.

Para lançar uma versão, aumente esse número (ex.: `1.0.1`).

## Testar rapidamente (precisa de Python 3.10 ou mais novo)

Dê dois cliques em **`executar.bat`**. Na primeira vez, ele instala o PySide6 e depois abre o programa.

## Gerar o programa para distribuir

Dê dois cliques em **`gerar_exe.bat`**. O programa fica na pasta `dist\AuditoriaDQ` (com o `AuditoriaDQ.exe` e a pasta `_internal`). Para distribuir, compacte essa pasta inteira.

## Onde ficam os snippets de cada pessoa

`%APPDATA%\AuditoriaDQ\` (snippets.json, anotacoes.txt, auditoria.txt e config.ini)

Na primeira execução, esse arquivo é criado com os snippets padrão (`app\snippets_padrao.json`). Depois disso, cada pessoa edita o próprio arquivo pela aba Snippets.

## Estrutura do código

| Arquivo | O que faz |
|---|---|
| `main.py` | Ponto de entrada |
| `app/main_window.py` | Janela principal e abas |
| `app/editor.py` | Aba Auditoria: modelo, lista de sugestões, campos com Tab |
| `app/snippets.py` | Leitura e gravação de snippets e interpretação de `${1:texto}` (sem Qt) |
| `app/store.py` | Arquivo de snippets do usuário |
| `app/snippets_tab.py` | Aba Snippets |
| `app/calculator.py` | Aba Calculadora 40% |
| `app/geometry.py` | Cálculo das faixas de 40% e redimensionamento (sem Qt) |
| `app/help_tab.py` | Aba Ajuda (FAQ) |
| `app/theme.py` | Cores e estilo |
