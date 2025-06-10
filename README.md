# AI Review Bot v2.1

Repositório para automação de *code review* usando Cursor + Copilot + GPT‑4.

## Instalação local
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python scripts/ai_orchestrator.py --mode diff
```

## Uso em outros repositórios
Adicione no seu workflow:
```yaml
uses: <org>/ai-review-bot/.github/workflows/callable.yml@v2.1
with:
  openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```
