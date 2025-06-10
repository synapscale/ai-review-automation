#!/usr/bin/env python3
"""AI Orchestrator v2.1 – revisão Node + Python
- Compatível com OpenAI Python SDK >=1.0
- Fragmenta diffs longos
- Retries exponenciais para falhas de API
- Escreve step summary em CI
"""
import argparse
import os
import sys
import time
from pathlib import Path
from typing import List

import openai
from dotenv import load_dotenv
from git import Repo
from git.exc import GitCommandError

# ─── Config ────────────────────────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    sys.exit("❌ OPENAI_API_KEY não definido no ambiente ou .env")
openai.api_key = OPENAI_API_KEY
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_CHARS = 12_000  # ~8 k tokens

SYSTEM_PROMPT = """Você é um revisor sênior para projetos Node (frontend) \
e Python (backend).
1. Identifique bugs, vulnerabilidades e breaking changes.
2. Sugira refatorações (Clean Code, PEP 8, ESLint).
3. Sugira testes automatizados.
Saída em Markdown com seções: **Bugs · Melhorias · Testes · TL;DR**.
""".strip()


# ─── Helpers ───────────────────────────────────────────────────────────────


def chunk(text: str, length: int) -> List[str]:
    """Divide texto em chunks de tamanho específico."""
    return [text[i:i+length] for i in range(0, len(text), length)]


def call_openai(prompt: str) -> str:
    """Chama a API da OpenAI com retry exponencial."""
    for attempt in range(3):
        try:
            resp = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1200,
            )
            content = resp.choices[0].message.content
            return content.strip() if content else ""
        except openai.OpenAIError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    return ""


# ─── Diff capture ─────────────────────────────────────────────────────────


def get_diff(repo: Repo) -> str:
    """Captura diff do git (staged ou entre commits)."""
    try:
        diff = repo.git.diff("--cached")
        if diff:
            return diff
    except GitCommandError:
        pass
    base, head = os.getenv("GITHUB_BASE_SHA"), os.getenv("GITHUB_HEAD_SHA")
    if base and head:
        return repo.git.diff(f"{base}...{head}")
    return ""


def review_diff(diff: str) -> str:
    """Revisa diff usando OpenAI, fragmentando se necessário."""
    if len(diff) <= MAX_CHARS:
        prompt = f"Revise o diff a seguir:\n```diff\n{diff}\n```"
        return call_openai(prompt)
    sections = []
    for part in chunk(diff, MAX_CHARS):
        prompt = f"Revise esta parte do diff:\n```diff\n{part}\n```"
        sections.append(call_openai(prompt))
    combined = "\n\n".join(sections)
    consolidate_prompt = ("Consolide o relatório a seguir em um único "
                          f"resumo:\n{combined}")
    return call_openai(consolidate_prompt)


# ─── CLI ──────────────────────────────────────────────────────────────────


def main():
    """Função principal do CLI."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["diff", "file"], default="diff")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()

    repo = Repo(Path.cwd(), search_parent_directories=True)

    if args.mode == "diff":
        diff = get_diff(repo)
        if not diff:
            print("⚠️  Nenhum diff detectado.")
            return
        report = review_diff(diff)
    else:
        blobs = []
        for p in args.paths:
            code = Path(p).read_text(encoding="utf-8")
            if p.endswith('.py'):
                lang = "python"
            elif p.endswith('.ts'):
                lang = "typescript"
            else:
                lang = "javascript"
            blobs.append(f"### {p}\n```{lang}\n{code}\n```")
        files_content = "\n".join(blobs)
        report = call_openai(f"Revise os arquivos abaixo:\n{files_content}")

    print(report)
    if path := os.getenv("GITHUB_STEP_SUMMARY"):
        Path(path).write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
