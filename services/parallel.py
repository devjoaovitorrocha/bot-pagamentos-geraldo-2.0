# services/parallel.py

from services.downloader import baixar_excel

def worker_restos(ano: str, subset: list[str], folders: dict):
    baixar_excel("restos", ano, subset, folders)

def worker_orcamentario(ano: str, subset: list[str], folders: dict):
    baixar_excel("orcamentario", ano, subset, folders)
