from flask import Flask, render_template, url_for
from googleapiclient.discovery import build
from google.oauth2 import service_account
from markupsafe import Markup

def listify(value):
    lines = value.split('\n')
    list_items = [f'<li>{line[2:]}</li>' if line.startswith('- ') else line for line in lines]
    inside_list = False
    result = []
    for item in list_items:
        if item.startswith('<li>'):
            if not inside_list:
                result.append('<ul>')
                inside_list = True
            result.append(item)
        else:
            if inside_list:
                result.append('</ul>')
                inside_list = False
            result.append(item)
    if inside_list:
        result.append('</ul>')
    print ('\n'.join(result))
    print ('-----')
    return Markup('\n'.join(result))

app = Flask(__name__)

app.jinja_env.filters['listify'] = listify

@app.route('/')
def index():
    return "Hello world!"


@app.route('/<int:id>')
def show(id):
    SPREADSHEET_ID = '19uTZm44ygWBIhcR4aZSkdBu0HvcME0PvYkAHPjQN1EY'
    sheet_name = 'gpt-3.5-turbo'
    INPUT_RANGE = sheet_name + '!A' + str(id + 1) + ':Z' + str(id + 1)

    SERVICE_ACCOUNT_FILE = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    # Retrieving data from the Google Sheets document.
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=INPUT_RANGE).execute()

    values = result.get('values', [])
    
    profession = values[0][3]
    headings = []
    paragraphs = []
    for i in range(1, 10):
        heading = values[0][8 + i * 2 - 2]
        paragraph = values[0][9 + i * 2 - 2]
        headings.append(heading)
        paragraphs.append(paragraph)
    
    return render_template('index.html', profession = profession, headings = headings, paragraphs = paragraphs)

if __name__ == '__main__':
    app.run()
