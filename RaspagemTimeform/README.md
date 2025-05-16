# Raspagem Timeform

## Configuração de credenciais

1. Crie um arquivo chamado `.env` na pasta `RaspagemTimeform` com o seguinte conteúdo:

```
TIMEFORM_EMAIL=seu_email_aqui
TIMEFORM_PASSWORD=sua_senha_aqui
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. O arquivo `.env` está no `.gitignore` e **NÃO será enviado ao GitHub**.

## Segurança
- Nunca compartilhe seu `.env`.
- Suas credenciais estarão protegidas e fora do código-fonte.

## Execução
Execute normalmente o script, as credenciais serão carregadas automaticamente do `.env`.

## Pré-requisitos
- Python 3.8+
- Google Chrome instalado
- ChromeDriver compatível com sua versão do Chrome (adicione o executável do chromedriver ao PATH ou na mesma pasta do script)

## Instalação

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Ajuste o caminho do ChromeDriver se necessário no script.

## Como usar

1. Execute o script principal:
   ```bash
   python raspagem_timeform.py
   ```

2. O script irá:
   - Fazer login no site Timeform
   - Aceitar cookies
   - Voltar para a página inicial
   - Criar uma pasta com a data do dia em `Coletas`
   - Raspar nomes, horários e links das corridas e salvar em `corridas.csv`
   - Acessar o primeiro link de corrida, raspar detalhes e salvar em `detalhes_corrida.csv`

## Observações
- O script foi feito para rodar no Windows, ajuste os caminhos se for usar em outro sistema.
- Certifique-se de que o ChromeDriver está atualizado e compatível com seu navegador.
- Assegure-se de que o site não mudou a estrutura dos elementos, pois isso pode afetar a raspagem. 