# AI Review Bot v2.1 🤖

Repositório para automação de *code review* usando Cursor + Copilot + GPT‑4.

## ✨ Funcionalidades

- 🔍 Análise automática de diffs usando GPT-4
- 🐛 Detecção de bugs e vulnerabilidades
- 📋 Sugestões de melhorias e refatoração
- 🧪 Recomendações de testes automatizados
- 🔄 Suporte a projetos Node.js (frontend) e Python (backend)
- 📝 Relatórios em Markdown com seções organizadas

## 🚀 Instalação local

1. Clone o repositório:

```bash
git clone <repository-url>
cd ai-review-automation
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure sua chave da OpenAI:

```bash
cp .env.example .env
# Edite o arquivo .env e adicione sua chave OpenAI
export OPENAI_API_KEY=sk-...
```

4. Execute o bot:

```bash
python scripts/ai_orchestrator.py --mode diff
```

## ⚙️ Configuração

Crie um arquivo `.env` baseado no `.env.example`:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
```

## 📖 Uso em outros repositórios

### GitHub Actions (Recomendado)

Adicione no seu workflow `.github/workflows/ai-review.yml`:

```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

jobs:
  ai-review:
    uses: <org>/ai-review-automation/.github/workflows/callable.yml@main
    secrets:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### Action Composite

Você também pode usar como uma action composite:

```yaml
steps:
  - uses: <org>/ai-review-automation@main
    with:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### Trigger por comentário

Para executar apenas quando alguém comentar `/ai-review`:

```yaml
name: AI Review on Comment
on:
  issue_comment:
    types: [created]

jobs:
  ai-review:
    if: |
      github.event.issue.pull_request &&
      github.event.comment.body == '/ai-review'
    uses: <org>/ai-review-automation/.github/workflows/callable.yml@main
    secrets:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

## 🛠️ Modos de Uso

- `--mode diff`: Analisa diferenças git (padrão)
- `--mode file`: Analisa arquivos específicos

### Exemplos

```bash
# Analisar diff staged
python scripts/ai_orchestrator.py --mode diff

# Analisar arquivos específicos
python scripts/ai_orchestrator.py --mode file src/app.py src/utils.py
```

## 💡 Exemplos de Uso Local

```bash
# Executar via VS Code (Ctrl+Shift+P > Tasks: Run Task > AI Review Bot)
# Ou via linha de comando:

# Analisar mudanças staged
python scripts/ai_orchestrator.py --mode diff

# Analisar arquivos específicos
python scripts/ai_orchestrator.py --mode file src/app.py tests/test_app.py

# Com variáveis de ambiente
OPENAI_API_KEY=sk-... python scripts/ai_orchestrator.py --mode diff
```

* Configure seu `OPENAI_API_KEY` no arquivo `.env` para uso local
* Use o modo `diff` para analisar mudanças git staged
* Use o modo `file` para análise de arquivos específicos

---