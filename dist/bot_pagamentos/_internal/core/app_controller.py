import time
import asyncio
from services.downloader import baixar_excel
from pathlib import Path
from datetime import datetime
from services.downloader import baixar_excel, preparar_pastas


class AppController:
    def executar_fluxo(self, ano: str, municipios: list[str], tipo: str):
        print(f"🟡 Iniciando tipo: {tipo}")
        start = time.perf_counter()

        # ✅ Cria pasta com timestamp único
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_output = Path("downloads") / timestamp
        folders = preparar_pastas(base_output)  # agora retorna os paths

        if tipo == "ambos":
            asyncio.run(self.executar_ambos_tipos(ano, municipios, folders))
        else:
            asyncio.run(baixar_excel(tipo, ano, municipios, folders))

        elapsed = time.perf_counter() - start
        print(f"🟢 Finalizado tipo: {tipo} em {elapsed:.2f} segundos.")

    async def executar_ambos_tipos(self, ano: str, municipios: list[str], folders: dict):
        print("🟡 Iniciando Restos a Pagar...")
        await baixar_excel("restos", ano, municipios, folders, worker_count=5)
        print("🟢 Finalizado Restos a Pagar.")

        print("🟡 Iniciando Orçamentários...")
        await baixar_excel("orcamentario", ano, municipios, folders, worker_count=2)
        print("🟢 Finalizado Orçamentários.")
