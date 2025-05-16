import streamlit as st
import pandas as pd
import os

# Caminho da pasta onde estão os CSVs
PASTA = r'C:\Users\marce\Desktop\Projetos Cursor\RaspagemTimeform\Coletas'

st.set_page_config(page_title='Dashboard Corridas Timeform', layout='wide')
st.title('Dashboard Corridas Timeform')

# Listar datas disponíveis
if not os.path.exists(PASTA):
    st.error('Pasta de coletas não encontrada!')
    st.stop()

datas = sorted([d for d in os.listdir(PASTA) if os.path.isdir(os.path.join(PASTA, d))], reverse=True)
if not datas:
    st.warning('Nenhuma coleta encontrada.')
    st.stop()

data_escolhida = st.selectbox('Escolha a data da coleta:', datas)
pasta_data = os.path.join(PASTA, data_escolhida)

# Listar arquivos CSV disponíveis (exceto corridas.csv)
arquivos = [f for f in os.listdir(pasta_data) if f.endswith('.csv') and f != 'corridas.csv']
if not arquivos:
    st.warning('Nenhum arquivo de corrida encontrado nesta data.')
    st.stop()

arquivo_escolhido = st.selectbox('Escolha a corrida:', arquivos)

# Ler o CSV escolhido
caminho_csv = os.path.join(pasta_data, arquivo_escolhido)
try:
    df = pd.read_csv(caminho_csv, header=None)
except Exception as e:
    st.error(f'Erro ao ler o arquivo: {e}')
    st.stop()

# Função para identificar blocos de cavalos
def separar_blocos(df):
    blocos = []
    bloco = []
    for _, row in df.iterrows():
        if row.isnull().all() or (row.count() == 1 and str(row[0]).strip() == ''):
            if bloco:
                blocos.append(bloco)
                bloco = []
        else:
            bloco.append(row.tolist())
    if bloco:
        blocos.append(bloco)
    return blocos

# Cabeçalho da corrida
cabecalho = []
for i, row in df.iterrows():
    if row.isnull().all() or (row.count() == 1 and str(row[0]).strip() == ''):
        break
    cabecalho.append(row.tolist())

df_restante = df.iloc[len(cabecalho):].reset_index(drop=True)
blocos_cavalos = separar_blocos(df_restante)

# Exibir cabeçalho da corrida
st.markdown('---')
if cabecalho and len(cabecalho[0]) >= 2:
    st.subheader(f'{cabecalho[0][0]} {cabecalho[0][1]}')
elif cabecalho and len(cabecalho[0]) == 1:
    st.subheader(f'{cabecalho[0][0]}')
else:
    st.warning('Cabeçalho da corrida não encontrado ou arquivo vazio.')
for linha in cabecalho[1:]:
    st.markdown(' '.join([str(x) for x in linha if pd.notnull(x)]))
st.markdown('---')

# Montar tabela resumida dos cavalos
resumo_cavalos = []
for bloco in blocos_cavalos:
    if not bloco:
        continue
    # Primeira linha: Form, Horse Name, Jockey, Age, Wgt, Odds (se houver)
    if len(bloco) > 0:
        resumo = bloco[0][:6] if len(bloco[0]) >= 6 else bloco[0]
        # Odds pode estar em outra linha, mas vamos tentar pegar da primeira
        resumo_cavalos.append(resumo)

# Exibir tabela resumida
st.markdown('### Cavalos na Corrida')
if resumo_cavalos:
    df_resumo = pd.DataFrame(resumo_cavalos, columns=['Form', 'Horse Name', 'Jockey', 'Age', 'Wgt', 'Odds'][:len(resumo_cavalos[0])])
    st.dataframe(df_resumo, use_container_width=True)
else:
    st.info('Nenhum cavalo encontrado para exibir na tabela resumida.')

# Expanders para detalhes de cada cavalo
for idx, bloco in enumerate(blocos_cavalos):
    if not bloco:
        continue
    with st.expander(f"{bloco[0][1]} (Detalhes)"):
        # Dados principais
        st.markdown('**Dados principais:**')
        st.write(pd.DataFrame([bloco[0]], columns=['Form', 'Horse Name', 'Jockey', 'Age', 'Wgt', 'Odds'][:len(bloco[0])]))
        # Outras linhas do bloco
        for linha in bloco[1:]:
            if any('Analyst Comment' in str(x) for x in linha):
                st.markdown(f"**{linha[0]}**")
            elif any('Statistic' in str(x) for x in linha):
                st.markdown('**Estatísticas:**')
                st.write(pd.DataFrame([linha], columns=linha))
            elif len(linha) > 2 and all(x for x in linha):
                # Provavelmente uma tabela (estatísticas ou histórico)
                st.write(pd.DataFrame([linha]))
            else:
                st.write(' '.join([str(x) for x in linha if pd.notnull(x)]))
        # Bloco para copiar toda a estrutura do cavalo
        texto_cavalo = '\n'.join(['\t'.join([str(x) for x in linha if pd.notnull(x)]) for linha in bloco])
        st.code(texto_cavalo, language='text')

def flatten(linha):
    flat = []
    for x in linha:
        if isinstance(x, list):
            flat.extend(flatten(x))
        else:
            flat.append(x)
    return flat

def limpar_linha(linha, remover_premium=False):
    # Achata listas aninhadas e remove todos os campos vazios
    linha = flatten(linha)
    campos = [str(x) for x in linha if str(x).strip() != '' and str(x).lower() != 'nan']
    if remover_premium and len(campos) > 5:
        # Remove os últimos 5 campos (campos premium)
        campos = campos[:-5]
    return campos

texto_corrida = ''
if cabecalho:
    for linha in cabecalho:
        l = limpar_linha(linha)
        if l:
            texto_corrida += ' '.join(l) + '\n'
    texto_corrida += '\n'
for bloco in blocos_cavalos:
    for linha in bloco:
        # Detecta se é uma linha de histórico (começa com data e tem colunas premium)
        if len(linha) > 10 and any(mes in str(linha[0]) for mes in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
            l = limpar_linha(linha, remover_premium=True)
        else:
            l = limpar_linha(linha)
        if l:
            texto_corrida += ' '.join(l) + '\n'
    texto_corrida += '\n'

# Exibir todo o texto em uma caixa de texto grande para facilitar Ctrl+A/Ctrl+C
st.text_area('Copie toda a estrutura da corrida abaixo:', texto_corrida, height=300)

st.info('Você pode usar filtros e recursos do próprio Streamlit para explorar os dados. Para atualizar, basta recarregar a página.') 