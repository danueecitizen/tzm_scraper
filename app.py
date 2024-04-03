from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
import requests

app = Flask(__name__)

@app.route('/update-sheet', methods=['GET'])
def update_sheet():
    # Fetch the data
    res = []
    for x in range(1,3):
        url = f"https://api.tuzonamarket.com/api/producto/oferta/zona/2/{x}"
        headers = {"User-Agent": "insomnia/8.6.1"}
        response = requests.request("GET", url, headers=headers)
        data = response.json()
        for p in data['data']:
            res.append(p)

    # Normalize the data and create a DataFrame
    df = pd.json_normalize(res)

    # Clean the DataFrame
    df['precio'] = df['precio'].apply(lambda x: x[0]['precio'] if x else None)
    df = df.drop(['sku', 'observacion', 'slug', 'inventario', 'ancho', 'altura', 'profundidad', 'vendido', 'recarga', 'estatus', 'descripcion', 'categoria', 'etiqueta', 'createdAt'], axis=1)

    # Authenticate with the Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/workspace_vs/tzm_scraper/tuzona.json', scope)
    client = gspread.authorize(creds)

    # Open the test sheet and get the first worksheet
    sheet = client.open("import_tuzona").sheet1

    # Convert the DataFrame to a list of lists
    values = df.astype(str).values.tolist()

    # Update the worksheet with new data
    sheet.update(values, 'A2')

    return "Sheet updated."

if __name__ == '__main__':
    app.run(port=5000)