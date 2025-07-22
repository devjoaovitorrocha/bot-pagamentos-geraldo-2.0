from pathlib import Path
import aiofiles


async def registrar_erro(tipo, ano, municipio, worker_id, tentativa, erro, detalhe):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "erros_detalhados.log"
    async with aiofiles.open(log_file, "a", encoding="utf-8") as f:
        await f.write(
            f"[Worker {worker_id}] ❌ ERRO AO PROCESSAR MUNICÍPIO em {municipio} | "
            f"Tentativa {tentativa} | Tipo: {tipo} | Ano: {ano} | Erro: {erro} | Detalhe: {detalhe}\n"
        )
