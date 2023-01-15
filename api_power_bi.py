import msal
import requests
import json
from azure.identity import ClientSecretCredential, InteractiveBrowserCredential, UsernamePasswordCredential
from datetime import datetime, timedelta


# --------------------------------------------------
# URL das APIs
# --------------------------------------------------

url_groups = 'https://api.powerbi.com/v1.0/myorg/admin/groups?%24top=1000'
url_reports = 'https://api.powerbi.com/v1.0/myorg/admin/groups?$expand=dashboards'
url_datasets = 'https://api.powerbi.com/v1.0/myorg/admin/groups?$expand=datasets'
url_users = 'https://api.powerbi.com/v1.0/myorg/admin/groups?$expand=users'


#  Activity Events

ontem = datetime.now() - timedelta(1)
url_activity_events = "https://api.powerbi.com/v1.0/myorg/admin/activityevents?startDateTime='" + ontem.strftime("%Y-%m-%d") + "T15:00:00.000Z'&endDateTime='" + ontem.strftime("%Y-%m-%d") + "T16:00:00.000Z'"



# --------------------------------------------------
# Configuração dos parâmetros da API
# --------------------------------------------------

client_id='c92ef17d-f232-4575-9c90-dd0647269092'
username = 'bernardo.senna@sennaconsultantservice.onmicrosoft.com' #somente é necessário caso não esteja utilizando o acesso via aplicativo
password = 'Showtime@33949418' #somente é necessário caso não esteja utilizando o acesso via aplicativo
authority_url = 'https://login.microsoftonline.com/617383e6-fe4c-4a06-a524-a43164d10756' #preencher com o tenand id do aplicativo azure
scope1 = ["https://analysis.windows.net/powerbi/api/.default"]
scope2 = "https://analysis.windows.net/powerbi/api/.default"
# ==================================================
url = url_activity_events #preencher com a url da api que deseja utilizar
# ==================================================
tenant_id = '617383e6-fe4c-4a06-a524-a43164d10756'
client_secret = 'C688Q~-MSxqHD4oG9BGRbJWX4HNsoLDDQEuAxc55'

# --------------------------------------------------
# Lib MSAL para buscar o token
# --------------------------------------------------

# Método 1: Utilizando usuário e senha
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
            resposta_api.append(resultado)
            resultado.clear()
    with open( 'activityEvent-' + ontem.strftime("%Y-%m-%d") + '.json' , "w" ) as write:
        json.dump( resposta_api , write )
        

else:
    api_out = requests.get(url=url, headers=header)
    resposta2 = api_out.json()['value']
    with open( 'groups-' + ontem.strftime("%Y-%m-%d") + '.json' , "w") as write:
        json.dump( resposta2 , write )