import hashlib


def calcular_hash_rollout(user_id: int, flag_name: str) -> int:
    """Calcula percentil determinístico para rollout baseado em usuário e flag.

    Garante que o mesmo usuário sempre receba o mesmo resultado para a mesma flag.
    Retorna um inteiro entre 0 e 99.
    """
    chave = f"{user_id}{flag_name}".encode()
    digest = hashlib.sha256(chave).hexdigest()
    return int(digest, 16) % 100
