from flask import Flask, request
from supabase import create_client, Client
from supaconfig import supabase_key, supabase_url
import requests 
import base64



app = Flask(__name__)


client_id = '23RW9Q'
client_secret = '252bcb2f8ea01c138d866ddd0984fdcc'
basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
headers = {
               'Authorization': f'Basic {basic_token}',
                'Content-Type': 'application/x-www-form-urlencoded' }

supabase: Client = create_client(supabase_url, supabase_key)

def store_tokens(access_token, refresh_token):
      data, count = supabase.table('access_tokens').upsert({
       "access_token" : access_token, 
       "refresh_token" : refresh_token
    }).execute()
      if data:
          print(data)
    


@app.route('/')
def home():
    return 'Home Page - Navigate to /fitbit/oauth2callback with an access token in the URL fragment for testing.'
 
@app.route('/fitbit/oauth2callback')
def fitbit_oauth2callback():
    code = request.args.get('code')
    if code:
         url = 'https://api.fitbit.com/oauth2/token'
         data = {
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://fit-bit-eight.vercel.app/fitbit_oauth2callback',
                'code': code
                }
         response = requests.post(url, headers=headers, data=data)
         if response.status_code == 200:
              tokens = response.json()
              access_token, refresh_token = tokens.get('access_token'), tokens.get('refresh_token')
              print("Access Token:", access_token)
              print("Refresh Token:", refresh_token)
              store_tokens(access_token, refresh_token)
              return "SUCCESSFULLY CONNECTED"
         else:
              return "Something failed"
    else:
         return "Authorization failed."
        
