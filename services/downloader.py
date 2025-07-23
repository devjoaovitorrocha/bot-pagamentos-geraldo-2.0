import os
import time
import logging
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from utils.logger import registrar_erro

URLS = {
    "orcamentario": "http://pagamentoderesolucoes.saude.mg.gov.br/pagamentos-orcamentarios",
    "restos": "http://pagamentoderesolucoes.saude.mg.gov.br/restos-a-pagar"
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

def configurar_driver(pasta_download: Path) -> webdriver.Firefox:
    options = Options()

    # Preferências para download automático
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", str(pasta_download.resolve()))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    options.set_preference("pdfjs.disabled", True)
    options.set_preference("browser.download.manager.showWhenStarting", False)

    # Disfarçar WebDriver
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
    )

    return webdriver.Firefox(service=FirefoxService(), options=options)

def baixar_excel(tipo: str, ano: str, municipios: list[str], folders: dict):
    base_output = folders[tipo]
    inicio_total = time.time()
    print(f"🚀 Iniciando worker para tipo '{tipo}' com {len(municipios)} municípios")

    for i, municipio in enumerate(municipios):
        tentativa = 1
        sucesso = False
        inicio_municipio = time.time()

        while tentativa <= 10 and not sucesso:
            driver = None
            temp_dir = base_output / f"temp_{i}_{municipio.replace(' ', '_')}"
            temp_dir.mkdir(parents=True, exist_ok=True)

            try:
                print(f"[{i+1}/{len(municipios)}] ▶️ Tentativa {tentativa} - {municipio}")
                driver = configurar_driver(temp_dir)
                driver.get(URLS[tipo])

                wait = WebDriverWait(driver, 2)
                wait.until(EC.presence_of_element_located((By.ID, "ano_pagamento"))).find_element(
                    By.XPATH, f".//option[text()='{ano}']").click()
                wait.until(EC.presence_of_element_located((By.ID, "dsc_municipio"))).find_element(
                    By.XPATH, f".//option[contains(text(), '{municipio}')]" ).click()

                driver.find_element(By.XPATH, "//input[@value='Consultar']").click()
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dt-button.buttons-excel"))).click()

                timeout = 30
                while timeout > 0:
                    arquivos = list(temp_dir.glob("*.xlsx"))
                    arquivos_part = list(temp_dir.glob("*.part"))

                    if arquivos and not arquivos_part:
                        origem = arquivos[0]
                        destino = base_output / f"{ano}_{municipio.replace(' ', '_').upper()}.xlsx"
                        os.replace(origem, destino)
                        sucesso = True
                        print(f"✅ {municipio} concluído em {time.time() - inicio_municipio:.2f}s")
                        break

                    time.sleep(1)
                    timeout -= 1

                if not sucesso:
                    print(f"⏳ {municipio} ainda não finalizado na tentativa {tentativa}")

            except Exception as e:
                print(f"❌ Erro ao baixar {municipio} na tentativa {tentativa}: {e}")
                registrar_erro(tipo, ano, municipio, tentativa, 1, "Erro Selenium", str(e))
                tentativa += 1
                time.sleep(2)

            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                try:
                    for f in temp_dir.glob("*"):
                        f.unlink()
                    temp_dir.rmdir()
                except Exception:
                    pass

        if not sucesso:
            print(f"⚠️ {municipio} falhou após 10 tentativas")

    print(f"🏁 Worker para tipo '{tipo}' finalizado em {time.time() - inicio_total:.2f}s")
