# Guia Definitivo – AI Review Bot v2.1 🤖🛠️

**Objetivo:** Permitir code‑reviews automáticos com Cursor + Copilot + GPT‑4 em qualquer projeto (Node, Python ou multi‑linguagem) – seja local, em PRs, monorrepos ou micro‑serviços.

## 📋 Requisitos mínimos

| Item | Versão‑alvo |
|------|-------------|
| Python | 3.11+ |
| GitHub Actions Runner | ubuntu‑latest ou self‑hosted |
| OpenAI Python SDK | >= 1.15.0 (já no requirements.txt) |
| Cursor IDE | Qualquer versão atual |
| GitHub Copilot (extensão) | Qualquer |

## 🚀 1. Inicialização do repositório ai‑review‑bot

```bash
unzip ai-review-bot-v2.zip -d ai-review-bot
cd ai-review-bot

# Publicar
gh repo create <org>/ai-review-bot --private -y
git init && git add . && git commit -m "v2.1" && git push -u origin main

# Tag oficial
git tag v2.1 && git push origin v2.1

# Adicionar secret para testes (opcional)
gh secret set OPENAI_API_KEY -b"sk-..."
```

## 🔄 2. Integração em outros repositórios (4 formas)

### 2.1 Workflow reutilizável (recomendado – 2 linhas)

```yaml
# .github/workflows/ai-review.yml
name: AI Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    uses: <org>/ai-review-bot/.github/workflows/callable.yml@v2.1
    with:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

**💡 Ideal quando você quer atualizar todos os projetos trocando só a tag.**

### 2.2 Action do Marketplace (se publicar action.yml)

```yaml
steps:
  - uses: <org>/ai-review-bot@v2.1
    with:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### 2.3 Copiando o workflow pronto

```bash
cp -r ai-review-bot/.github/workflows/review-bot.yml \
      <meu-projeto>/.github/workflows/
```

Permite customizar livremente o job sem afetar outros repos.

### 2.4 Submódulo + Task local (sem CI)

```bash
cd meu-projeto
git submodule add https://github.com/<org>/ai-review-bot external/ai-review-bot

# Opcional: task personalizada
jq '.tasks[0].args[0]="external/ai-review-bot/scripts/ai_orchestrator.py"' \
   external/ai-review-bot/.vscode/tasks.json > .vscode/tasks.json
```

## 💻 3. Fluxo local no Cursor

| Passo | Atalho / comando |
|-------|------------------|
| Adicionar alterações relevantes | `git add -p` |
| Rodar revisão | Palette → Run Task → AI Review |
| Ler relatório | Terminal integrado |
| Aplicar patch sugerido | Selecionar trecho → Cmd+K → "Apply suggestion" |

### Exemplos de prompts para o Composer

- Refatore esta função seguindo SOLID
- Gere testes PyTest para este diff
- Existe vulnerabilidade OWASP?
- Documente o módulo em JSDoc

## 🚀 4. Ideias de possibilidades avançadas

| Cenário | Passo extra |
|---------|-------------|
| Security sweep | Troque SYSTEM_PROMPT para foco em CWE/OWASP |
| Release Notes automáticos | Execute orquestrador com prompt "Gere changelog" |
| Auditoria de dependências | Combine com pip‑audit ou npm audit no mesmo job |
| Monorepo gigantesco | Filtre paths no workflow:paths: ['services/backend/**'] |
| PRs só com label | if: contains(github.event.pull_request.labels.*.name, 'ai-review') |
| Limitar custos | OPENAI_MODEL=gpt-4o-mini + max_tokens=800 |
| Fallback OSS (offline) | Substituir OpenAI SDK por Ollama + Mistral local |
| Auto‑approve arquivos de docs | Adicionar passo gh pr review --approve via CLI |
| Slack/Discord notificação | Pós‑step: webhook com resultado resumido |

## ⚙️ 5. Customizações rápidas

| O que mudar | Onde alterar |
|-------------|--------------|
| Tam. máximo do diff | `MAX_CHARS = 12_000` em ai_orchestrator.py |
| Temperatura do modelo | `temperature=0.2` em função call_openai |
| Modelo OpenAI | `MODEL = "gpt-4o-mini"` ou via env OPENAI_MODEL |
| Prompt padrão | constante `SYSTEM_PROMPT` |
| Dependências extras | requirements.txt + pip install no workflow |
| Timeout de retry | Loop range(3) na função call_openai |

## 🔧 6. Manutenção & Upgrade

1. Atualize o repo‑bot → `git pull`, ajuste código.
2. `git tag v2.2 && git push origin v2.2`.
3. Nos consumidores: troque `@v2.1`→`@v2.2`.
4. Observe custos e logs, refine.

## 🛠️ 7. Troubleshooting

| Erro | Diagnóstico rápido | Solução |
|------|-------------------|---------|
| OPENAI_API_KEY não definido | Secret faltando | Definir em Secrets ou .env |
| Comentário vazio | 429/Quota | Reduzir diff, aumentar retries, checar fatura |
| git diff vazio na task | Esqueceu git add | Stage antes da revisão |
| Latência alta | Modelo 32k, diff grande | Use modelo menor ou limite paths |
| Diff binário (imagens) | Orquestrador ignora | Excluir .png, .jpg no PR |

## ❓ 8. FAQ Essencial

**→ Posso usar em GitHub Enterprise Server?**  
Sim, desde que o runner tenha acesso externo à API OpenAI.

**→ Cobra token de Copilot?**  
Não: Copilot funciona inline; quem faz a chamada à OpenAI é o orquestrador.

**→ Suporta Java/Kotlin?**  
Sim — adicione mapeamento de extensão e ajuste prompt.

**→ Como rodar só em branches release?**  
Altere `on: pull_request.branches`.

## 🌐 9. Plano de Ação

| Fase | When | Responsável | Entregáveis |
|------|------|-------------|-------------|
| 0. Kick‑off | Hoje | DevOps | Repo ai‑review-bot publicado, tag v2.1, secret OPENAI_API_KEY configurado |
| 1. Piloto | Dia +1 | Squad alpha | 1 projeto real usando workflow reutilizável; valida relatório, latência, custo |
| 2. Observabilidade & Custos | Dia +3 | Platform Eng | Adicionar loguru ao script + gravação de usage.total_tokens no GITHUB_STEP_SUMMARY; planilha de custos via Action cron semanal |
| 3. Segurança & Qualidade | Dia +4 | Sec Eng | Pipeline extra: trufflehog, semgrep, cobertura pytest ≥ 80 % |
| 4. Roll‑out | Semana 2 | Todos os squads | Trocar/Adicionar workflow callable.yml em 100 % dos repositórios; tag proteções ai-reviewed |
| 5. Automação contínua | Mês 1 | Dev Tools | Bot de bump de versão (renovate) + auto‑PR de release notes gerados pela IA |

### Checkpoints

- **SLA:** duração do job AI ≤ 3 min em PR médio.
- **Budget:** custo OpenAI por PR ≤ US$ 0,05 (ajustar max_tokens).
- **Segurança:** zero segredos vazados; gitleaks block.

### Snippet ✔️ cost tracking

```python
resp = openai.chat.completions.create(...)
usage = resp.usage.total_tokens
print(f"Tokens usados: {usage}")
Path(os.getenv('GITHUB_STEP_SUMMARY')).write_text(f"## Tokens usados\n{usage}")
```

### Snippet ✔️ semgrep step

```yaml
- uses: returntocorp/semgrep-action@v1
  with:
    config: >
      p/ci p/security-audit
```

A cada fase concluída ➜ abrir issue milestone no repo‑bot com o checklist acima.

---

🎉 **Parabéns!** Agora você tem um roteiro completo – da publicação à personalização – para executar revisões de IA de ponta a ponta em qualquer stack e qualquer fluxo (CLI, CI, Cursor).

Caso surja um cenário não coberto aqui, peça e evoluímos juntos 😉