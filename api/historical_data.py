
from http.server import BaseHTTPRequestHandler
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # --- Configuración de Google Sheets ---
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file"
        ]
        SHEET_ID = "1c0CuXVEXdFVCbN6nZFYLb4c1MTU-To8jLnGwzZg_RhY"

        try:
            # Cargar credenciales desde variable de entorno
            creds_json_str = os.getenv("GSPREAD_CREDENTIALS")
            if not creds_json_str:
                raise ValueError("La variable de entorno GSPREAD_CREDENTIALS no está configurada.")
            
            creds_info = json.loads(creds_json_str)
            creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
            client = gspread.authorize(creds)

            # --- Lógica de la función ---
            spreadsheet = client.open_by_key(SHEET_ID)
        
            try:
                hoja2 = spreadsheet.worksheet('Hoja 2')
            except gspread.exceptions.WorksheetNotFound:
                hoja2 = spreadsheet.add_worksheet(title="Hoja 2", rows="1", cols="2")
                hoja2.append_row(["Fecha", "Cantidad"])

            all_hoja2_values = hoja2.get_all_values()
            if not all_hoja2_values or all_hoja2_values[0] != ["Fecha", "Cantidad"]:
                if len(all_hoja2_values) > 0:
                    hoja2.clear()
                hoja2.append_row(["Fecha", "Cantidad"])
                historical_data = []
            else:
                historical_data = hoja2.get_all_records()

            saved_dates = {row['Fecha'] for row in historical_data}
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y-%m-%d')

            if yesterday_str not in saved_dates:
                hoja1 = spreadsheet.get_worksheet(0)
                all_values_hoja1 = hoja1.get_all_values()
                yesterday_count = 0
                date_column_index = 3 # Columna D
                for row in all_values_hoja1[1:]:
                    if len(row) > date_column_index and row[date_column_index].startswith(yesterday_str):
                        yesterday_count += 1
                hoja2.append_row([yesterday_str, yesterday_count])

            final_data = hoja2.get_all_records()
            
            # --- Enviar respuesta ---
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(final_data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {"error": f"Ocurrió un error en el servidor: {e}"}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
        return
