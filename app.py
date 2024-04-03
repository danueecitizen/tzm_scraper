from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
import requests

app = Flask(__name__)

@app.route('/update-sheet', methods=['GET'])
def update_sheet():
    # Fetch data
    res = []
    for x in range(1,3):
        url = f"https://api.tuzonamarket.com/api/producto/oferta/zona/2/{x}"
        headers = {"User-Agent": "insomnia/8.6.1"}
        response = requests.request("GET", url, headers=headers)
        data = response.json()
        for p in data['data']:
            res.append(p)

    # Normaliza la data y crea el DataFrame
    df = pd.json_normalize(res)

    # Limpia Data
    df['precio'] = df['precio'].apply(lambda x: x[0]['precio'] if x else None)
    df = df.drop(['sku', 'observacion', 'slug', 'inventario', 'ancho', 'altura', 'profundidad', 'vendido', 'recarga', 'estatus', 'descripcion', 'categoria', 'etiqueta', 'createdAt'], axis=1)

    # Autentificacion Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('your secret_key_here.json', scope)
    client = gspread.authorize(creds)

    # Abre la el google sheet con la pagina
    sheet = client.open("your_sheetname").sheet1

    # Convierte el dataframe en una lista de listas
    values = df.astype(str).values.tolist()

    # Actualiza el sheet
    sheet.update(values, 'A2')

    return "Sheet updated."

if __name__ == '__main__':
    app.run(port=5000)