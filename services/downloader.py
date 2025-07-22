import asyncio
from pathlib import Path
from datetime import datetime
import time
import logging
from playwright.async_api import async_playwright
from utils.logger import registrar_erro

URLS = {
    "orcamentario": "http://pagamentoderesolucoes.saude.mg.gov.br/pagamentos-orcamentarios",
    "restos": "http://pagamentoderesolucoes.saude.mg.gov.br/restos-a-pagar"
}

EXECUTION_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
BASE_OUTPUT = Path("downloads") / EXECUTION_TIMESTAMP
FOLDERS = {
    "orcamentario": BASE_OUTPUT / "Orcamentarios",
    "restos": BASE_OUTPUT / "Restos_a_pagar"
}

def preparar_pastas(base_path: Path):
    folders = {
        "orcamentario": base_path / "Orcamentarios",
        "restos": base_path / "Restos_a_pagar"
    }

    base_path.mkdir(parents=True, exist_ok=True)
    for pasta in folders.values():
        pasta.mkdir(parents=True, exist_ok=True)

    return folders


async def processar_municipio(playwright, tipo, ano, municipio, worker_id, semaphore, folders):
    tentativas = 0
    sucesso = False

    async with semaphore:
        browser = await playwright.chromium.launch(headless=False, slow_mo=30)

        while tentativas < 10 and not sucesso:
            tentativas += 1
            try:
                context = await browser.new_context(accept_downloads=True)
                page = await context.new_page()

                # Timeout global de inatividade após carregar a página
                async def fluxo_download():
                    await executar_fluxo_download(page, tipo, ano, municipio, folders[tipo])

                inatividade_task = asyncio.create_task(asyncio.sleep(7))
                fluxo_task = asyncio.create_task(fluxo_download())
                done, _ = await asyncio.wait(
                    [inatividade_task, fluxo_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                if inatividade_task in done:
                    await page.close()
                    await context.close()
                    raise Exception("Timeout de inatividade: Nenhuma ação realizada após 3s do carregamento da página.")
                await fluxo_task
                sucesso = True

            except Exception as e:
                logging.error(f"[Worker {worker_id}] ERRO {municipio} - tentativa {tentativas} - {str(e)}")
                await registrar_erro(tipo, ano, municipio, worker_id, tentativas, "Erro ao baixar", str(e))

                delay = 2 + (tentativas * 2)
                if tentativas >= 3:
                    delay += 10  # Alívio adicional após 3 falhas
                await asyncio.sleep(delay)

        await browser.close()


async def executar_fluxo_download(page, tipo, ano, municipio, output_folder: Path):
    await page.goto(URLS[tipo])
    await page.wait_for_selector("#ano_pagamento", timeout=500)
    await page.select_option("#ano_pagamento", ano)

    await page.wait_for_selector("#dsc_municipio", timeout=500)
    await page.select_option("#dsc_municipio", municipio)

    await page.click("input[type='submit'][value='Consultar']")
    await page.wait_for_selector("button.dt-button.buttons-excel", timeout=500)

    async with page.expect_download() as download_info:
        await page.click("button.dt-button.buttons-excel")
    download = await download_info.value

    file_name = f"{ano}_{municipio.replace(' ', '_')}.xlsx"
    await download.save_as(output_folder / file_name)



async def baixar_excel(tipo: str, ano: str, municipios: list[str], folders: dict, worker_count: int = 6, evento_restos: asyncio.Event = None):
    semaphore = asyncio.Semaphore(1 if tipo == "orcamentario" else worker_count)

    async with async_playwright() as playwright:
        tasks = []

        for i, municipio in enumerate(municipios):
            worker_id = (i % worker_count) + 1

            async def wrapper(m=municipio, wid=worker_id):
                try:
                    await processar_municipio(playwright, tipo, ano, m, wid, semaphore, folders)
                except Exception as e:
                    if tipo == "orcamentario" and evento_restos and not evento_restos.is_set():
                        evento_restos.set()
                    raise e

            task = asyncio.create_task(wrapper())
            tasks.append(task)

        if tipo == "orcamentario" and evento_restos:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            evento_restos.set()
            await asyncio.gather(*tasks)
        else:
            await asyncio.gather(*tasks)
