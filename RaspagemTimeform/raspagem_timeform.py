import os
import time
import re
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv('TIMEFORM_EMAIL')
PASSWORD = os.getenv('TIMEFORM_PASSWORD')

# Configurações iniciais
LOGIN_URL = 'https://www.timeform.com/horse-racing/account/sign-in?returnUrl=%2Fhorse-racing'
HOME_URL = 'https://www.timeform.com/horse-racing'
BASE_PATH = r'C:\Users\marce\Desktop\Projetos Cursor\RaspagemTimeform\Coletas'

# Configurar Selenium
chrome_options = Options()
chrome_options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)

def aceitar_cookies():
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow All Cookies')]"))).click()
        time.sleep(1)
    except Exception as e:
        print('Botão de cookies não encontrado ou já aceito.')

def fazer_login():
    driver.get(LOGIN_URL)
    aceitar_cookies()
    wait.until(EC.visibility_of_element_located((By.ID, 'EmailAddress'))).send_keys(EMAIL)
    wait.until(EC.visibility_of_element_located((By.ID, 'Password'))).send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Sign In']"))).click()
    time.sleep(3)

def criar_pasta_data():
    data_str = datetime.now().strftime('%d-%m-%Y')
    pasta = os.path.join(BASE_PATH, data_str)
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        return pasta
    else:
        i = 1
        while True:
            nova_pasta = f"{pasta}_{i}"
            if not os.path.exists(nova_pasta):
                os.makedirs(nova_pasta)
                return nova_pasta
            i += 1

def raspar_corridas():
    driver.get(HOME_URL)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find('div', class_='w-cards-results')
    dados = []
    for sec in cards.find_all('section'):
        nome_hipodromo = sec.find('h3').get_text(strip=True)
        for li in sec.find_all('li'):
            a = li.find('a')
            horario = a.get_text(strip=True)
            link = 'https://www.timeform.com' + a['href']
            dados.append({'Hipodromo': nome_hipodromo, 'Horario': horario, 'Link': link})
    return dados

def salvar_csv_corridas(dados, pasta):
    # Ordenar por horário e depois nome da pista
    def horario_para_minutos(horario):
        try:
            partes = horario.split(':')
            return int(partes[0]) * 60 + int(partes[1])
        except:
            return 0
    dados_ordenados = sorted(dados, key=lambda x: (horario_para_minutos(x['Horario']), x['Hipodromo']))
    caminho = os.path.join(pasta, 'corridas.csv')
    df = pd.DataFrame(dados_ordenados)
    df.to_csv(caminho, index=False, encoding='utf-8-sig')
    return caminho

def raspar_corredores(tabela):
    corredores = []
    for tbody in tabela.find_all('tbody', class_='rp-horse-row'):
        if tbody.get('data-open') != 'True':
            continue
        # Campos principais
        form = ''
        form_td = tbody.find('td', class_='rp-td-horse-form')
        if form_td:
            form = form_td.get_text(strip=True)
        horse_name = ''
        horse_td = tbody.find('td', class_='rp-td-horse-name')
        if horse_td:
            name = horse_td.find('a', class_='rp-horse')
            name_txt = name.get_text(strip=True) if name else ''
            sup = horse_td.find('sup')
            sup_txt = sup.get_text(strip=True) if sup else ''
            cd = horse_td.find('div', class_='rp-cdwf')
            cd_txt = cd.get_text(strip=True) if cd else ''
            horse_name = f"{name_txt} {sup_txt} {cd_txt}".strip()
        jockey = ''
        jockey_td = tbody.find('td', class_='rp-td-horse-jockey')
        if jockey_td:
            jockey_a = jockey_td.find('a')
            jockey = jockey_a.get_text(strip=True) if jockey_a else jockey_td.get_text(strip=True)
        age = ''
        age_td = tbody.find('td', class_='rp-td-horse-age')
        if age_td:
            age = age_td.get_text(strip=True)
        wgt = ''
        wgt_td = tbody.find('td', class_='rp-td-horse-weight')
        if wgt_td:
            wgt = wgt_td.get_text(strip=True)
        entry = ''
        entry_td = tbody.find('td', class_='rp-td-horse-entry')
        if entry_td:
            entry_span = entry_td.find('span', class_='rp-entry-number')
            entry = entry_span.get_text(strip=True) if entry_span else entry_td.get_text(strip=True)
        pedigree = ''
        pedigree_td = tbody.find('td', class_='rp-td-horse-pedigree')
        if pedigree_td:
            sire = pedigree_td.find('span', title='Sire')
            dam = pedigree_td.find('span', title='Dam')
            dam_sire = pedigree_td.find('span', title='Dam Sire')
            sire_txt = sire.get_text(strip=True) if sire else ''
            dam_txt = dam.get_text(strip=True) if dam else ''
            dam_sire_txt = dam_sire.get_text(strip=True) if dam_sire else ''
            pedigree = f'Sire: {sire_txt} Dam: {dam_txt} Dam Sire: {dam_sire_txt}'.strip()
        trainer = ''
        trainer_td = tbody.find('td', class_='rp-td-horse-trainer')
        if trainer_td:
            trainer_a = trainer_td.find('a')
            trainer = trainer_a.get_text(strip=True) if trainer_a else trainer_td.get_text(strip=True)
        equip = ''
        equip_td = tbody.find('td', class_='rp-td-horse-equipment')
        if equip_td:
            equip = equip_td.get_text(strip=True)
        orating = ''
        or_td = tbody.find('td', class_='rp-td-horse-or')
        if or_td:
            or_span = or_td.find('span')
            orating = or_span.get_text(strip=True) if or_span else or_td.get_text(strip=True)
        analyst_comment = ''
        comment_tr = tbody.find_next('tr', class_='rp-entry-comment')
        if comment_tr:
            comment_span = comment_tr.find('span', class_='rp-verdict')
            analyst_comment = comment_span.get_text(strip=True) if comment_span else ''
        linhas = [
            [f'Form: {form}', f'Horse Name (Days Off): {horse_name}', f'Jockey: {jockey}', f'Age: {age}', f'Wgt: {wgt}'],
            [f'Entry: {entry}', f'Pedigree: {pedigree}', f'Trainer: {trainer}', f'Equip: {equip}', f'OR: {orating}'],
            [f'Analyst Comment: {analyst_comment}']
        ]
        corredores.append(linhas)
    return corredores

def raspar_tabela_estatisticas(tr_stats_tr):
    """Raspa a tabela de estatísticas do treinador/jockey."""
    bloco = []
    if not tr_stats_tr:
        return bloco
    section = tr_stats_tr.find('section', class_='jt-ledger ledger-statistics')
    if not section:
        return bloco
    table = section.find('table', class_='ledger-table')
    if not table:
        return bloco
    
    # Cabeçalho
    thead = table.find('thead')
    if thead:
        for tr in thead.find_all('tr'):
            if 'rp-my-timeform' in tr.get('class', []):
                continue
            linha = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
            if any(linha):  # Só adiciona se houver algum conteúdo
                bloco.append(linha)
    
    # Corpo
    tbody = table.find('tbody')
    if tbody:
        for tr in tbody.find_all('tr'):
            if 'rp-my-timeform' in tr.get('class', []):
                continue
            linha = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
            if any(linha):  # Só adiciona se houver algum conteúdo
                bloco.append(linha)
    
    return bloco

def raspar_historico_corridas(tr_historico):
    """Raspa a tabela de histórico de corridas do cavalo, ignorando campos premium e linhas de controle/alerta, sem repetir cabeçalho ou linhas."""
    bloco = []
    if not tr_historico:
        return bloco
    table = tr_historico.find('table')
    if not table:
        return bloco
    # Cabeçalho
    thead = table.find('thead')
    cabecalho = None
    if thead:
        for tr in thead.find_all('tr'):
            if 'rp-my-timeform' in tr.get('class', []):
                continue  # Ignora linhas de controle/alerta
            linha = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
            if len(linha) > 5:
                linha = linha[:-5]
            if any(linha):
                cabecalho = linha
                bloco.append(linha)
                break  # Só pega o primeiro cabeçalho
    # Corpo
    tbody = table.find('tbody')
    if tbody:
        for tr in tbody.find_all('tr'):
            if 'rp-my-timeform' in tr.get('class', []):
                continue  # Ignora linhas de controle/alerta
            linha = [td.get_text(strip=True) for td in tr.find_all('td')]
            if len(linha) > 5:
                linha = linha[:-5]
            if any(linha):
                # Não adiciona se for igual ao cabeçalho (mesmo se vier do tbody)
                if cabecalho and linha == cabecalho:
                    continue
                # Não adiciona se for igual à última linha já adicionada
                if bloco and linha == bloco[-1]:
                    continue
                # Não adiciona se for igual a qualquer linha já adicionada (para evitar repetições)
                if linha in bloco:
                    continue
                bloco.append(linha)
    return bloco

def raspar_detalhes_corrida_formatado(link):
    driver.get(link)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    linhas_saida = []
    
    # Cabeçalho da corrida
    h1 = soup.find('h1', class_='rp-title')
    nome_hipodromo = h1.find('span', class_='rp-title-course-name').get_text(strip=True) if h1 else ''
    horario = h1.find('span', class_='hide').get_text(strip=True) if h1 and h1.find('span', class_='hide') else ''
    linhas_saida.append([nome_hipodromo, horario])
    
    # Tabela de informações principais da corrida
    header_table = soup.find('table', class_='rp-header-table')
    if header_table:
        for tr in header_table.find_all('tr'):
            if 'rp-my-timeform' in tr.get('class', []):
                continue
            tds = tr.find_all('td')
            if tds:
                linha = [td.get_text(strip=True) for td in tds]
                if any(linha):  # Só adiciona se houver algum conteúdo
                    linhas_saida.append(linha)
    
    # Tabela dos cavalos
    tabela = soup.find('table', id='race-pass-body')
    if tabela:
        for idx, tbody in enumerate(tabela.find_all('tbody', class_='rp-horse-row'), start=1):
            if tbody.get('data-open') != 'True':
                continue

            # Nome do cavalo
            horse_td = tbody.find('td', class_='rp-td-horse-name')
            horse_name = ''
            if horse_td:
                name = horse_td.find('a', class_='rp-horse')
                horse_name = name.get_text(strip=True) if name else horse_td.get_text(strip=True)

            # Jockey
            jockey_td = tbody.find('td', class_='rp-td-horse-jockey')
            jockey = ''
            if jockey_td:
                jockey_a = jockey_td.find('a')
                jockey = jockey_a.get_text(strip=True) if jockey_a else jockey_td.get_text(strip=True)

            # Treinador
            trainer_td = tbody.find('td', class_='rp-td-horse-trainer')
            trainer = ''
            if trainer_td:
                trainer_a = trainer_td.find('a')
                trainer = trainer_a.get_text(strip=True) if trainer_a else trainer_td.get_text(strip=True)

            # Idade
            age_td = tbody.find('td', class_='rp-td-horse-age')
            age = age_td.get_text(strip=True) if age_td else ''

            # Peso
            wgt_td = tbody.find('td', class_='rp-td-horse-weight')
            wgt = wgt_td.get_text(strip=True) if wgt_td else ''

            # Odds (se houver)
            odds_td = tbody.find('td', class_='rp-td-horse-odds')
            odds = odds_td.get_text(strip=True) if odds_td else ''

            linha = [
                horse_name,
                f'Jockey: {jockey}',
                f'Trainer: {trainer}',
                age,
                wgt,
                odds
            ]
            linhas_saida.append(linha)

            # Analyst Comment
            comment_tr = tbody.find_next('tr', class_='rp-entry-comment')
            if comment_tr and 'rp-my-timeform' not in comment_tr.get('class', []):
                comment_span = comment_tr.find('span', class_='rp-verdict')
                if comment_span:
                    comment = comment_span.get_text(strip=True)
                    if comment:
                        linhas_saida.append([f'Analyst Comment: {comment}'])

            # Tabela estatísticas do treinador
            tr_stats_tr = tbody.find_next('tr', class_=f'rp-jt-ledger-stats rp-trainer-stats-{idx} hide')
            if tr_stats_tr and 'rp-my-timeform' not in tr_stats_tr.get('class', []):
                bloco_trainer = raspar_tabela_estatisticas(tr_stats_tr)
                if bloco_trainer:
                    linhas_saida.append(['Trainer Statistic'])
                    linhas_saida.extend(bloco_trainer)

            # Tabela estatísticas do jockey
            tr_stats_jockey = tbody.find_next('tr', class_=f'rp-jt-ledger-stats rp-jockey-stats-{idx} hide')
            if tr_stats_jockey and 'rp-my-timeform' not in tr_stats_jockey.get('class', []):
                bloco_jockey = raspar_tabela_estatisticas(tr_stats_jockey)
                if bloco_jockey:
                    linhas_saida.append(['Jockey Statistic'])
                    linhas_saida.extend(bloco_jockey)

            # Histórico de corridas
            tr_historico = tbody.find_next('tr', id=re.compile(r'horseFormBox\d+'))
            if tr_historico and 'rp-my-timeform' not in tr_historico.get('class', []):
                bloco_hist = raspar_historico_corridas(tr_historico)
                if bloco_hist:
                    linhas_saida.extend(bloco_hist)

            # Linha em branco separando cada cavalo
            linhas_saida.append([])
    
    # Remove linhas vazias consecutivas
    linhas_filtradas = []
    for i, linha in enumerate(linhas_saida):
        if not linha or not any(linha):  # Se a linha atual está vazia
            if i > 0 and linhas_saida[i-1] and any(linhas_saida[i-1]):  # Se a linha anterior não está vazia
                linhas_filtradas.append(linha)
        else:
            linhas_filtradas.append(linha)
    
    return linhas_filtradas

def salvar_csv_formatado(linhas, pasta, nome_arquivo):
    caminho = os.path.join(pasta, nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        for linha in linhas:
            writer.writerow([linha])
    return caminho

def main():
    fazer_login()
    pasta = criar_pasta_data()
    dados_corridas = raspar_corridas()
    csv_corridas = salvar_csv_corridas(dados_corridas, pasta)
    print(f'Corridas salvas em: {csv_corridas}')
    # Para cada corrida, criar um arquivo específico e raspar os detalhes formatados
    for corrida in dados_corridas:
        nome_hipodromo = corrida["Hipodromo"].replace("/", "-").replace(" ", "_")
        horario = corrida["Horario"].replace(":", "-")
        nome_arquivo = f"{horario}_{nome_hipodromo}.csv"
        linhas = raspar_detalhes_corrida_formatado(corrida['Link'])
        csv_detalhes = salvar_csv_formatado(linhas, pasta, nome_arquivo)
        print(f'Detalhes da corrida salvos em: {csv_detalhes}')
    driver.quit()

if __name__ == '__main__':
    main() 