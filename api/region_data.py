
from http.server import BaseHTTPRequestHandler
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from collections import Counter

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # --- Configuración de Google Sheets ---
            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file"
            ]
            SHEET_ID = "1c0CuXVEXdFVCbN6nZFYLb4c1MTU-To8jLnGwzZg_RhY"

            creds_json_str = os.getenv("GSPREAD_CREDENTIALS")
            if not creds_json_str:
                raise ValueError("La variable de entorno GSPREAD_CREDENTIALS no está configurada.")
            
            creds_info = json.loads(creds_json_str)
            creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
            client = gspread.authorize(creds)

            # --- Lógica de la función ---
            spreadsheet = client.open_by_key(SHEET_ID)
            worksheet = spreadsheet.get_worksheet(0)
            all_values = worksheet.get_all_values()
            start_row_index = 11075
            region_column_index = 19

            if len(all_values) <= start_row_index:
                response_data = {"info": "No se encontraron datos de regiones en el rango especificado (Fila 11076+, Columna T)."}
            else:
                region_counts = Counter()
                for row in all_values[start_row_index:]:
                    if len(row) > region_column_index:
                        cell_value = row[region_column_index].strip().lower()
                        if cell_value:
                            individual_regions = [name.strip() for name in cell_value.split(',')]
                            region_counts.update(individual_regions)
                region_counts.pop("", None)
                if not region_counts:
                    response_data = {"info": "No se encontraron datos de regiones en el rango especificado (Fila 11076+, Columna T)."}
                else:
                    response_data = dict(region_counts)
            
            response_body = json.dumps(response_data)

        except Exception as e:
            response_body = json.dumps({"error": f"Exception in API (region_data): {type(e).__name__} - {e}"})

        self.wfile.write(response_body.encode('utf-8'))
        return
