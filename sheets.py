import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("Ruya Buyurtmalar").sheet1
    return sheet

def write_order(name, phone, comment):
    sheet = get_sheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, phone, comment, timestamp])
