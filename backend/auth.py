import sys
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.file']
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
# Imprimir la URL antes de bloquear
auth_url, _ = flow.authorization_url(prompt='consent')
print(auth_url)
sys.stdout.flush()

creds = flow.run_local_server(port=8001, open_browser=False)

with open('token.pickle', 'wb') as token:
    pickle.dump(creds, token)

print("¡Autenticación exitosa! Se guardó token.pickle")
