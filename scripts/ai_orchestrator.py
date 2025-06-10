#!/usr/bin/env python3
"""AI Orchestrator v2.1 – revisão Node + Python
- Compatível com OpenAI Python SDK >=1.0
- Fragmenta diffs longos
- Retries exponenciais para falhas de API
- Escreve step summary em CI
"""
import os, sys, time, argparse
from pathlib import Path
from typing import List

from git import Repo
from git.exc import GitCommandError
from dotenv import load_dotenv
import openai

# ─── Config ────────────────────────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    sys.exit("❌ OPENAI_API_KEY não definido no ambiente ou .env")
openai.api_key = OPENAI_API_KEY
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_CHARS = 12_000  # ~8 k tokens

SYSTEM_PROMPT = """Você é um revisor sênior para projetos Node (frontend) e Python (backend).
1. Identifique bugs, vulnerabilidades e breaking changes.
2. Sugira refatorações (Clean Code, PEP 8, ESLint).
3. Sugira testes automatizados.
Saída em Markdown com seções: **Bugs · Melhorias · Testes · TL;DR**.
""".strip()

# ─── Helpers ───────────────────────────────────────────────────────────────
def chunk(text: str, length: int) -> List[str]:
    return [text[i:i+length] for i in range(0, len(text), length)]

def call_openai(prompt: str) -> str:
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
            return resp.choices[0].message.content.strip()
        except openai.OpenAIError as err:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

# ─── Diff capture ─────────────────────────────────────────────────────────
def get_diff(repo: Repo) -> str:
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
    if len(diff) <= MAX_CHARS:
        return call_openai(f"Revise o diff a seguir:\n```diff\n{diff}\n```")
    sections = []
    for part in chunk(diff, MAX_CHARS):
        sections.append(call_openai(f"Revise esta parte do diff:\n```diff\n{part}\n```"))
    combined = "\n\n".join(sections)
    return call_openai("Consolide o relatório a seguir em um único resumo:\n" + combined)

# ─── CLI ──────────────────────────────────────────────────────────────────
def main():
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
            code = Path(p).read_text("utf-8")
            lang = "python" if p.endswith('.py') else 'typescript' if p.endswith('.ts') else 'javascript'
            blobs.append(f"### {p}\n```{lang}\n{code}\n```")
        report = call_openai("Revise os arquivos abaixo:\n" + "\n".join(blobs))

    print(report)
    if path := os.getenv("GITHUB_STEP_SUMMARY"):
        Path(path).write_text(report)

if __name__ == "__main__":
    main()
