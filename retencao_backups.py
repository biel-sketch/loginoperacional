#!/usr/bin/env python3
"""
Retenção de backups do Firebase LoginServ.

Regra:
- Mantém TODOS os backups dos últimos 30 dias
- Para backups mais antigos que 30 dias, mantém apenas 1 por mês (o mais antigo do mês)
- Backups com mais de 1 ano são removidos

Isso evita que a pasta /backups cresça indefinidamente, sem perder
a capacidade de restaurar um estado de qualquer mês do último ano.
"""
import os
import re
from datetime import datetime, timedelta

BACKUP_DIR = "backups"
PADRAO_NOME = re.compile(r"backup_(\d{4}-\d{2}-\d{2})_\d{2}-\d{2}\.json")

def listar_backups():
    if not os.path.isdir(BACKUP_DIR):
        return []
    itens = []
    for nome in os.listdir(BACKUP_DIR):
        m = PADRAO_NOME.match(nome)
        if m:
            data = datetime.strptime(m.group(1), "%Y-%m-%d")
            itens.append((data, nome))
    return sorted(itens, key=lambda x: x[0])

def main():
    backups = listar_backups()
    if not backups:
        print("Nenhum backup encontrado para aplicar retenção.")
        return

    agora = datetime.now()
    limite_30d = agora - timedelta(days=30)
    limite_1ano = agora - timedelta(days=365)

    manter = set()
    meses_ja_mantidos = set()

    # Mantém tudo dentro dos últimos 30 dias
    for data, nome in backups:
        if data >= limite_30d:
            manter.add(nome)

    # Para o que passou de 30 dias: mantém 1 por mês (o primeiro encontrado, mais antigo do mês)
    for data, nome in backups:
        if data < limite_30d and data >= limite_1ano:
            chave_mes = (data.year, data.month)
            if chave_mes not in meses_ja_mantidos:
                meses_ja_mantidos.add(chave_mes)
                manter.add(nome)

    removidos = 0
    for data, nome in backups:
        if nome not in manter:
            caminho = os.path.join(BACKUP_DIR, nome)
            os.remove(caminho)
            removidos += 1
            print(f"Removido (retenção): {nome}")

    print(f"\nTotal de backups: {len(backups)} | Mantidos: {len(manter)} | Removidos: {removidos}")

if __name__ == "__main__":
    main()
