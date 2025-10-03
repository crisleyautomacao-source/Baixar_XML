import os
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

# --- CONFIGURAÇÃO ---
chaves_nfe = [
    "52250907019882000186550100001297561692778986",
    # Adicione mais chaves aqui, se quiser testar com mais de uma
]
pasta_downloads = os.path.join(os.getcwd(), "XML_Notas_Super_Robustas")
MAX_RETRIES_POR_CHAVE = 3
TEMPO_MAXIMO_ESPERA = 65 # em segundos

# --- FUNÇÕES AUXILIARES "HUMANIZADAS" ---
def digitar_como_humano(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def clicar_como_humano(driver, element):
    action = ActionChains(driver)
    action.move_to_element(element).click().perform()

# --- SCRIPT PRINCIPAL ---
if not os.path.exists(pasta_downloads):
    os.makedirs(pasta_downloads)
print(f"Os arquivos XML serão salvos em: {pasta_downloads}")

driver = None
try:
    print("Iniciando navegador em modo 'undetected'...")
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options, use_subprocess=True)
    
    params = {'behavior': 'allow', 'downloadPath': pasta_downloads}
    driver.execute_cdp_cmd('Page.setDownloadBehavior', params)
    
    url = "https://meudanfe.com.br/"
    driver.get(url)

    # 👉 MUDANÇA AQUI: Usamos enumerate para saber o índice de cada chave
    for index, chave in enumerate(chaves_nfe):
        sucesso = False
        for tentativa in range(1, MAX_RETRIES_POR_CHAVE + 1):
            print("-" * 30)
            print(f"Processando chave: {chave} (Tentativa {tentativa}/{MAX_RETRIES_POR_CHAVE})")
            
            try:
                # ETAPAS 1, 2 e 3 continuam as mesmas...
                print("Aguardando campo de busca...")
                wait = WebDriverWait(driver, TEMPO_MAXIMO_ESPERA)
                campo_chave = wait.until(EC.element_to_be_clickable((By.ID, "searchTxt")))
                campo_chave.clear()
                digitar_como_humano(campo_chave, chave)

                print("Clicando em BUSCAR...")
                botao_buscar = driver.find_element(By.ID, "searchBtn")
                clicar_como_humano(driver, botao_buscar)

                print("Aguardando resultado da consulta e botão de download...")
                botao_baixar_xml = wait.until(EC.element_to_be_clickable((By.ID, "downloadXmlBtn")))
                clicar_como_humano(driver, botao_baixar_xml)
                
                print(f"✅ Download para a chave {chave} iniciado com sucesso!")
                time.sleep(random.uniform(3.0, 5.0))

                # 👉 MUDANÇA AQUI: Só clica em "NOVA CONSULTA" se não for o último item da lista
                if index < len(chaves_nfe) - 1:
                    print("Clicando em NOVA CONSULTA para preparar para o próximo item...")
                    botao_nova_consulta = wait.until(EC.element_to_be_clickable((By.ID, "newSearchBtn")))
                    clicar_como_humano(driver, botao_nova_consulta)
                    print("Pronto para a próxima consulta.")
                else:
                    print("✅ Este foi o último item da lista. Finalizando...")

                sucesso = True
                break

            except TimeoutException:
                print(f"❌ ERRO: Tempo de espera ({TEMPO_MAXIMO_ESPERA}s) excedido na tentativa {tentativa}.")
            except Exception as e:
                print(f"❌ ERRO inesperado na tentativa {tentativa}: {e}")

            if tentativa < MAX_RETRIES_POR_CHAVE:
                print("Recarregando a página para tentar novamente...")
                driver.get(url)
                time.sleep(random.uniform(2.0, 4.0))
            else:
                print(f"🚫 Falha ao processar a chave {chave} após {MAX_RETRIES_POR_CHAVE} tentativas.")

finally:
    if driver:
        print("-" * 30)
        print("Automação concluída!")
        driver.quit()