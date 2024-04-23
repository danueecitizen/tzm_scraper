import json
import os
import pandas as pd
import requests
import gspread
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

def lambda_handler(event, context):
    df = pd.DataFrame()
    
    for x in range(1, 3):
        url = f"https://api.tuzonamarket.com/api/producto/oferta/zona/2/{x}" # Esta es la pagina de ofertas de TZM
        headers = {"User-Agent": "insomnia/8.6.1"}
        response = requests.get(url, headers=headers)

        
        if response.status_code == 200:
            data = response.json()  

            # Listas para almacenar datos
            updated_at_list = []
            nombre_list = []
            peso_list = []
            precio_oferta_list = []

            # Recorrer cada producto en la lista "data"
            for product in data['data']:
                # Extraer los datos necesarios para cada producto
                updated_at_list.append(product.get('updatedAt', None))
                nombre_list.append(product.get('nombre', None))
                peso_list.append(product.get('peso', None))
                precio_oferta_list.append(product.get('precio', [])[0].get('oferta', None))

            # Crear un DataFrame a partir de las listas
            df_page = pd.DataFrame({
                'updatedAt': updated_at_list,
                'nombre': nombre_list,
                'peso': peso_list,
                'precio_oferta': precio_oferta_list
            })
            
            # Concatenar el DataFrame
            df = pd.concat([df, df_page], ignore_index=True)
        
        else:
            print("Error: La solicitud no fue exitosa.")    
    
    # Recuerda cargar tus credenciales a las variables de entorno en tu Lambda
    creds = {
        "type": os.getenv("type"),
        "project_id": os.getenv("project_id"),
        "private_key_id": os.getenv("private_key_id"),
        "private_key": os.getenv("private_key").replace('\\n', '\n'),
        "client_email": os.getenv("client_email"),
        "client_id": os.getenv("client_id"),
        "auth_uri": os.getenv("auth_uri"),
        "token_uri": os.getenv("token_uri"),
        "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
        "client_x509_cert_url": os.getenv("client_x509_cert_url"),
        "universe_domain": os.getenv("universe_domain")
    }
    
     # Credenciales para debuggear
    print("Credenciales:", creds)
    
    # Google Sheets API
    try:
        credentials = service_account.Credentials.from_service_account_info(creds)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive'])
        client = gspread.Client(auth=scoped_credentials)
        client.session = AuthorizedSession(scoped_credentials)
    except Exception as e:
        print("Error de autenticación:", e)
        raise
    # Abre google sheet con la pagina
    sheet = client.open("EL_NOMBRE_DE_TU_GOOGLE_SHEET").sheet1

    # Convert the dataframe into a list of lists
    values = df.astype(str).values.tolist()

    # Update the sheet
    sheet.update(values, 'A2')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Sheet actualizada.')
    }
