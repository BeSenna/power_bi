import msal
import requests
import json
import csv
from azure.identity import ClientSecretCredential, InteractiveBrowserCredential, UsernamePasswordCredential
from datetime import datetime, timedelta


# --------------------------------------------------
# URL das APIs
# --------------------------------------------------

url_groups = 'https://api.powerbi.com/v1.0/myorg/admin/groups?$top=1000'
url_reports = 'https://api.powerbi.com/v1.0/myorg/admin/groups?$expand=dashboards&$top=1000'
url_datasets = 'https://api.powerbi.com/v1.0/myorg/admin/groups?$expand=datasets&$top=1000'
url_users = 'https://api.powerbi.com/v1.0/myorg/admin/groups?$expand=users&$top=1000'


#  Activity Events

ontem = datetime.now() - timedelta(1)
url_activity_events = "https://api.powerbi.com/v1.0/myorg/admin/activityevents?startDateTime='" + ontem.strftime("%Y-%m-%d") + "T15:00:00.000Z'&endDateTime='" + ontem.strftime("%Y-%m-%d") + "T16:00:00.000Z'"



# --------------------------------------------------
# Configuração dos parâmetros da API
# --------------------------------------------------

client_id=''
username = '' #somente é necessário caso não esteja utilizando o acesso via aplicativo
password = '' #somente é necessário caso não esteja utilizando o acesso via aplicativo
authority_url = 'https://login.microsoftonline.com/seu-tenant-id-aqui' #preencher com o tenand id do aplicativo azure
scope1 = ["https://analysis.windows.net/powerbi/api/.default"]
scope2 = "https://analysis.windows.net/powerbi/api/.default"
# ==================================================
url = url_groups #preencher com a url da api que deseja utilizar
# ==================================================
tenant_id = ''
client_secret = ''

# --------------------------------------------------
# Lib MSAL para buscar o token
# --------------------------------------------------

# Método 1: Utilizando usuário e senha (não funciona com MFA)
app = msal.PublicClientApplication(client_id, authority=authority_url)
resultado1 = app.acquire_token_by_username_password(username=username,password=password,scopes=scope1)



#Método 2: Utilizando as credenciais do aplicativo azure
client_secret_credential_class = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
access_token_class = client_secret_credential_class.get_token(scope2)
resultado2 = access_token_class.token

# --------------------------------------------------
# Verifique se o token foi gerado e utilize na API
# --------------------------------------------------

access_token = resultado2 # Editar conforme o método utilizado para autenticação
header = {'Content-Type':'application/json','Authorization': f'Bearer {access_token}'}
#print(header['Authorization'])

# --------------------------------------------------
# Gerando o resultado da API de acordo com o view solicitada
# --------------------------------------------------


if url == url_activity_events:

    api_out = requests.get(url=url, headers=header)
    resposta_api = api_out.json()['activityEventEntities']
    continuation_token = api_out.json()['continuationUri']
    

    while continuation_token is not None:        
            api_out_cont = requests.get(url=continuation_token, headers=header)
            continuation_token = api_out_cont.json()['continuationUri']
            resultado = api_out_cont.json()['activityEventEntities']
            resposta_api.expand(resultado)
            resultado.clear()
    #with open( 'activityEvent-' + ontem.strftime("%Y-%m-%d") + '.json' , "w" ) as write:
    #    json.dump( resposta_api , write )   
    with open('datasets.csv', 'w', newline='') as csvfile:
        writer = resposta_api.DictWriter(csvfile, fieldnames=resposta_api[0].keys())
        writer.writeheader()
        for element in resposta_api:
            for row in element:
                writer.writerow(row)
        

else:
    api_out = requests.get(url=url, headers=header)
    resposta2 = api_out.json()['value']
    with open('datasets.csv', 'w', newline='') as csvfile:
        fieldnames = resposta2[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for element in resposta2:
            for row in element:
                writer.writerow(element)
