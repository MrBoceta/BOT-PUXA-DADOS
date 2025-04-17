import telebot
import requests
import base64
import time
import json

# Token do bot obtido do BotFather
TOKEN = 'SEU_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Função para processar o CPF e buscar os dados na API
def processar_cpf(cpf):
    credentials = 'EMAIL_ADM:SENHA_ADM'
    credentials_base64 = base64.b64encode(credentials.encode()).decode()
    url_login = 'https://servicos-cloud.saude.gov.br/pni-bff/v1/autenticacao/tokenAcesso'
    url_pesquisa_base = 'https://servicos-cloud.saude.gov.br/pni-bff/v1/cidadao/cpf/'

    headers_login = {
        "Host": "servicos-cloud.saude.gov.br",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
        "accept": "application/json",
        "X-Authorization": f"Basic {credentials_base64}",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "Windows",
        "Origin": "https://si-pni.saude.gov.br",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://si-pni.saude.gov.br/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    max_retries = 3
    retry_delay = 5

    for i in range(max_retries):
        response_login = requests.post(url_login, headers=headers_login, verify=False)
        if response_login.status_code == 200:
            login_data = response_login.json()
            if 'accessToken' in login_data:
                token_acesso = login_data['accessToken']
                url_pesquisa = f"{url_pesquisa_base}{cpf}"
                headers_pesquisa = {
                    "Host": "servicos-cloud.saude.gov.br",
                    "Authorization": f"Bearer {token_acesso}",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    "Origin": "https://si-pni.saude.gov.br",
                    "Sec-Fetch-Site": "same-site",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://si-pni.saude.gov.br/",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
                }

                for j in range(max_retries):
                    response_pesquisa = requests.get(url_pesquisa, headers=headers_pesquisa, verify=False)
                    if response_pesquisa.status_code == 200:
                        dados_pessoais = response_pesquisa.json()
                        if 'records' in dados_pessoais:
                            return formatar_informacoes(dados_pessoais['records'][0])
                        else:
                            return {"error": "Erro na pesquisa", "details": response_pesquisa.text}
                    time.sleep(retry_delay)
                return {"error": "Falha na requisição de pesquisa após várias tentativas"}
        time.sleep(retry_delay)
    return {"error": "Falha na requisição de login após várias tentativas"}

# Função para formatar os dados pessoais
def formatar_informacoes(dados_pessoais):
    return {
        'nome': dados_pessoais.get('nome'),
        'dataNascimento': dados_pessoais.get('dataNascimento'),
        'sexo': dados_pessoais.get('sexo'),
        'nomeMae': dados_pessoais.get('nomeMae'),
        'nomePai': dados_pessoais.get('nomePai'),
        'grauQualidade': dados_pessoais.get('grauQualidade'),
        'ativo': dados_pessoais.get('ativo'),
        'obito': dados_pessoais.get('obito'),
        'partoGemelar': dados_pessoais.get('partoGemelar'),
        'vip': dados_pessoais.get('vip'),
        'racaCor': dados_pessoais.get('racaCor'),
        'telefone': dados_pessoais.get('telefone'),
        'nacionalidade': dados_pessoais.get('nacionalidade'),
        'endereco': dados_pessoais.get('endereco')
    }

# Handler para o comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Envie um CPF para buscar as informações correspondentes.")

# Handler para mensagens de texto (busca por CPF)
@bot.message_handler(func=lambda message: True)
def buscar_cpf(message):
    cpf = message.text.strip()
    if cpf.isdigit() and len(cpf) == 11:
        resultado = processar_cpf(cpf)
        if 'error' in resultado:
            bot.reply_to(message, f"Erro: {resultado['error']}")
        else:
            mensagem = json.dumps(resultado, indent=4, ensure_ascii=False)
            bot.reply_to(message, f"Dados encontrados:\n{mensagem}")
    else:
        bot.reply_to(message, "Por favor, envie um CPF válido (apenas números, 11 dígitos).")

# Inicia o bot
if __name__ == '__main__':
    bot.polling(none_stop=True)
