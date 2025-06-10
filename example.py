#!/usr/bin/env python3
"""
Exemplo de código Python para demonstração do AI Review Bot
"""


def calculate_fibonacci(n):
    """Calcula o n-ésimo número da sequência de Fibonacci (recursivo)."""
    # Função para calcular fibonacci - versão simples
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)


def process_user_data(user_input):
    """Processa dados do usuário (VULNERÁVEL - só para demonstração)."""
    # Função que processa dados do usuário
    data = eval(user_input)  # ⚠️ Potencial vulnerabilidade de segurança
    return data * 2


class UserManager:
    """Gerenciador de usuários com demonstração de código problemático."""

    def __init__(self):
        """Inicializa o gerenciador com lista vazia de usuários."""
        self.users = []

    def add_user(self, name, email):
        """Adiciona usuário sem validação (problemático para demo)."""
        # Adiciona usuário sem validação
        user = {"name": name, "email": email}
        self.users.append(user)
        return user

    def get_user_by_email(self, email):
        """Busca usuário por email usando busca linear."""
        # Busca usuário por email
        for user in self.users:
            if user["email"] == email:
                return user
        return None


if __name__ == "__main__":
    # Exemplo de uso
    manager = UserManager()
    manager.add_user("João", "joao@example.com")

    # Calcular fibonacci
    result = calculate_fibonacci(10)
    print(f"Fibonacci(10) = {result}")

    # Processar dados do usuário
    user_data = process_user_data("10 + 5")
    print(f"Dados processados: {user_data}")
