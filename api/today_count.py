
from http.server import BaseHTTPRequestHandler
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

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
            today_str = datetime.now().strftime('%Y-%m-%d')
            count = 0
            date_column_index = 3

            for row in all_values[1:]:
                if len(row) > date_column_index and row[date_column_index].startswith(today_str):
                    count += 1
            
            response_body = json.dumps({"today_count": count})

        except Exception as e:
            response_body = json.dumps({"error": f"Exception in API (today_count): {type(e).__name__} - {e}"})

        self.wfile.write(response_body.encode('utf-8'))
        return
