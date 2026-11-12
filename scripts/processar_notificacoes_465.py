"""Mantido por compatibilidade: o script principal já trata a porta 465 (SSL) e a 587 (STARTTLS).

Use: python -m scripts.processar_notificacoes
"""
from scripts.processar_notificacoes import main

if __name__ == '__main__': main()
