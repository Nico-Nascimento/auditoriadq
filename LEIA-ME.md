# AuditoriaDQ (Windows)

Programa com quatro abas:

- **Auditoria**: editor com o modelo padrão (Roi / Espaços / Preços / Produtos) e snippets no estilo do VS Code.
- **Calculadora 40%**: várias imagens lado a lado, uma marcação por imagem e faixas de 40%.
- **Snippets**: cadastro de prefixos e frases. Importa e exporta no formato do VS Code.
- **Ajuda**: perguntas frequentes sobre como usar o programa.

## Testar rapidamente (precisa de Python 3.10 ou mais novo)

Dê dois cliques em **`executar.bat`**. Na primeira vez, ele instala o PySide6 e depois abre o programa.

## Gerar o `.exe` para distribuir

Dê dois cliques em **`gerar_exe.bat`**. O programa fica em `dist\AuditoriaDQ.exe`, um arquivo único que roda sem Python instalado. É só copiar esse arquivo para os colegas.

## Onde ficam os snippets de cada pessoa

`%APPDATA%\AuditoriaDQ\snippets.json`

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
