# Exemplo de uso do AI Review Bot em outros repositórios

## Opção 1: Workflow simples (recomendado)

Crie `.github/workflows/ai-review.yml`:

```yaml
name: AI Review

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

jobs:
  ai-review:
    uses: <org>/ai-review-automation/.github/workflows/callable.yml@main
    secrets:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

## Opção 2: Com trigger por comentário

Crie `.github/workflows/ai-review-comment.yml`:

```yaml
name: AI Review

# ➜ 2 gatilhos: PR normal + comentário "/ai-review"
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
  issue_comment:
    types: [created]

permissions:
  contents: read
  pull-requests: write

jobs:
  call-review:
    # Só roda se for (a) evento de PR  OU
    # (b) comentário "/ai-review" dentro de uma PR
    if: |
      github.event_name == 'pull_request' ||
      (
        github.event_name == 'issue_comment' &&
        github.event.comment.body == '/ai-review' &&
        github.event.issue.pull_request
      )

    uses: <org>/ai-review-automation/.github/workflows/callable.yml@main
    secrets:
      openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

## Opção 3: Action composite

```yaml
name: AI Review

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

permissions:
  contents: read
  pull-requests: write

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: <org>/ai-review-automation@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

## Configuração obrigatória

1. **Secret necessário**: Configure `OPENAI_API_KEY` nos secrets do repositório
2. **Permissions**: Os workflows já incluem as permissions necessárias
3. **Branch protection**: Opcional - pode configurar como required check

## Personalização

### Trigger apenas com label
```yaml
on:
  pull_request:
    types: [opened, synchronize, labeled]

jobs:
  ai-review:
    if: contains(github.event.pull_request.labels.*.name, 'ai-review')
    # ... resto do workflow
```

### Excluir paths específicos
```yaml
on:
  pull_request:
    types: [opened, synchronize]
    paths-ignore:
      - 'docs/**'
      - '*.md'
      - '.gitignore'
```

### Apenas para drafts
```yaml
on:
  pull_request:
    types: [ready_for_review]  # Só quando sair de draft
```
