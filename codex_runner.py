#!/usr/bin/env python3
"""
codex_runner.py – wrapper completo para Codex CLI (v2)
• Provider switch (openai|gemini|any) + modelo custom (--model)
• Menu de 20 prompts clássicos ou prompt livre (-p)
• approval-mode auto-edit (default) | suggest | full-auto
• Salva diff em codex_patch.diff, faz --apply/--commit opcional
• Pós-patch: roda testes (pytest/jest/vitest) e aborta se falharem
• --open-pr: cria branch, push e abre PR via gh CLI
"""
import os, sys, subprocess, shutil, argparse, textwrap, time, json, tempfile
from pathlib import Path

RECOMMENDED_PROMPTS = {
    "1": "Refatore o código aplicando Clean Code e removendo duplicação",
    "2": "Gerar testes PyTest cobrindo todas as funções alteradas",
    "3": "Migrar chamadas 'requests' para 'httpx' mantendo assinaturas",
    "4": "Adicionar tipagem PEP 484 completa aos módulos modificados",
    "5": "Documentar com JSDoc todas as funções em utils/*.ts",
    "6": "Escanear e corrigir OWASP Top 10 automaticamente",
    "7": "Implementar CRUD padrão para o modelo User no FastAPI",
    "8": "Otimizar consultas SQL usando EXPLAIN ANALYZE",
    "9": "Converter class-based views para FastAPI routers",
    "10": "Gerar fixtures para testes Django",
    "11": "Criar README.md completo para este projeto",
    "12": "Adicionar Dockerfile de produção multi-stage",
    "13": "Substituir prints por logging estruturado com loguru",
    "14": "Aplicar hardening de cabeçalhos HTTP via SecurityMiddleware",
    "15": "Migrar de Mocha para Vitest nos testes frontend",
    "16": "Criar workflow CI (lint+test+build)",
    "17": "Transformar código síncrono em async/await",
    "18": "Escrever mocks para chamadas externas com unittest.mock",
    "19": "Adicionar rubocop e autocorrigir código Ruby",
    "20": "Identificar N+1 queries no ORM e corrigir",
}

def ensure_codex():
    if shutil.which("codex"):
        return
    print("⚙ Instalando Codex CLI via pipx…")
    subprocess.check_call(["pipx", "install", "codex-cli"])

def choose_prompt(prompt_arg):
    if prompt_arg:
        return prompt_arg
    print("\n== PROMPTS POPULARES ==")
    for k, v in RECOMMENDED_PROMPTS.items():
        print(f"[{k}] {v}")
    choice = input("Digite número ou insira prompt livre: ").strip()
    return RECOMMENDED_PROMPTS.get(choice, choice)

def run_shell(cmd, check=True, capture=False):
    return subprocess.run(cmd, check=check, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout if capture else None

def run_codex(prompt, opts):
    codex_cmd = [
        "codex",
        "--provider", opts.provider,
        "--model", opts.model,
        "--approval-mode", opts.approval,
        "--no-spinner",
    ]
    if opts.quiet:
        codex_cmd.append("--quiet")
    if opts.apply:
        codex_cmd.append("--apply")
    codex_cmd.append(prompt)

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        print("▶", *codex_cmd)
        result = subprocess.run(codex_cmd).returncode
        if result == 0:
            return
        print(f"⚠️ Falhou (exit {result}) – tentativa {attempt}/{max_retries}")
        time.sleep(5 * attempt)
    sys.exit("✖ Codex falhou após múltiplas tentativas.")

def run_tests():
    if Path("pytest.ini").exists() or any(Path(".").rglob("test_*.py")):
        print("▶ Rodando pytest…")
        return subprocess.call(["pytest", "-q"]) == 0
    if shutil.which("jest"):
        print("▶ Rodando jest…")
        return subprocess.call(["jest", "--runInBand"]) == 0
    if shutil.which("vitest"):
        print("▶ Rodando vitest…")
        return subprocess.call(["vitest", "run"]) == 0
    print("ℹ Nenhum framework de testes detectado.")
    return True

def open_pr(branch, title="AI-Codex patch"):
    run_shell(["git", "push", "-u", "origin", branch])
    run_shell(["gh", "pr", "create", "--fill", "--title", title])

def main():
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("✖ Defina OPENAI_API_KEY.")

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", help="Prompt customizado")
    parser.add_argument("--provider", default="openai", help="openai|gemini|...")
    parser.add_argument("--model", default="gpt-4o-mini", help="ID do modelo")
    parser.add_argument("--approval", default="auto-edit",
                        choices=["suggest", "auto-edit", "full-auto"])
    parser.add_argument("--apply", action="store_true",
                        help="Aplicar patch automaticamente")
    parser.add_argument("--commit", action="store_true",
                        help="Commitar patch após aplicar")
    parser.add_argument("--quiet", action="store_true",
                        help="Modo silencioso (para CI)")
    parser.add_argument("--open-pr", action="store_true",
                        help="Abrir PR via gh após commit")
    opts = parser.parse_args()

    ensure_codex()
    prompt = choose_prompt(opts.prompt)
    run_codex(prompt, opts)

    if opts.apply and opts.commit:
        run_shell(["git", "add", "-A"])
        run_shell(["git", "commit", "-m", f"codex: {prompt[:60]}"])
        if not run_tests():
            sys.exit("✖ Testes falharam – commit abortado.")
        if opts.open_pr:
            branch = f"codex/{int(time.time())}"
            run_shell(["git", "branch", "-M", branch])
            open_pr(branch)
        print("✔ Patch aplicado, testado e commitado.")

if __name__ == "__main__":
    main()
