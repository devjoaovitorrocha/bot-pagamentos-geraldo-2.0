from pathlib import Path
from datetime import datetime
from multiprocessing import Process
from services.downloader import baixar_excel, preparar_pastas
from services.parallel import worker_restos, worker_orcamentario  # Adicionei worker_orcamentario

class AppController:
    def executar_fluxo(self, ano: str, municipios: list[str], tipo: str):
        print(f"🟡 Iniciando tipo: {tipo}")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_output = Path("downloads") / timestamp
        folders = preparar_pastas(base_output)

        chunk_size = max(1, len(municipios) // 5)
        chunks = [municipios[i:i + chunk_size] for i in range(0, len(municipios), chunk_size)]

        if tipo == "ambos":
            workers_restos = [Process(target=worker_restos, args=(ano, chunk, folders)) for chunk in chunks[:5]]
            workers_orcamentario = [Process(target=worker_orcamentario, args=(ano, chunk, folders)) for chunk in chunks[:5]]

            for w in workers_restos + workers_orcamentario:
                w.start()
            for w in workers_restos + workers_orcamentario:
                w.join()

        elif tipo == "restos":
            workers = [Process(target=worker_restos, args=(ano, chunk, folders)) for chunk in chunks[:5]]
            for w in workers:
                w.start()
            for w in workers:
                w.join()

        elif tipo == "orcamentario":
            workers = [Process(target=worker_orcamentario, args=(ano, chunk, folders)) for chunk in chunks[:5]]
            for w in workers:
                w.start()
            for w in workers:
                w.join()
