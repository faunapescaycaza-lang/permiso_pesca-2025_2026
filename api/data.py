
from http.server import BaseHTTPRequestHandler
import json
import os
import gspread
from google.oauth2.service_account import Credentials

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
            worksheet = spreadsheet.get_worksheet(0) # Hoja 1
            all_values = worksheet.get_all_values()
            start_row_index = 11075
            count = 0
            if len(all_values) > start_row_index:
                count = len(all_values[start_row_index:])
            
            # --- Enviar respuesta ---
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response_body = json.dumps({"count": count})
            self.wfile.write(response_body.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {"error": f"Ocurrió un error en el servidor: {e}"}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
        return
