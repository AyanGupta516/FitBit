import fitbit 
import base64
import csv

client_id = '23RW9Q'
client_secret = '252bcb2f8ea01c138d866ddd0984fdcc'
basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
headers = {
               'Authorization': f'Basic {basic_token}',
                'Content-Type': 'application/x-www-form-urlencoded' }

def make_requests():
    url = 'https://api.fitbit.com/oauth2/token'
    updated_rows = []
    with open('data/tokens.csv', mode = 'r') as file:
          csv_reader = csv.reader(file)
          #Iterate through all the rows
          for row in csv_reader:
               refresh_token = row[1]
               data = {
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                    }
               #Get new access token and refresh token to make the call
               response = fitbit.post(url, headers = headers, data = data)
               if response.status_code == 200:
                    tokens = response.json()
                    access_token, refresh_token = tokens.get('access_token'), tokens.get('refresh_token')
                    updated_rows.append([access_token, refresh_token])
                    print("SUCCESSFULLY GOT THE TOKENS")
                    # Get fitbit api data with whatever calls to make

                    #Profile Call
                    profile_header = {
                         'Authorization': f'Bearer {access_token}'
                    }
                    profile_url = 'https://api.fitbit.com/1/user/-/profile.json'
                    profile_response = fitbit.get(profile_url, headers = profile_header)
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        print("Got information")
                        print(profile_data['user']['fullName'])
                    else: 
                        print("ERROR RETRIEVING DATA")
                    
                    #Sleep Data Call
                        
                    
                    #Activity Data Call 

               else:
                    print("ERROR RETRIEVING ACCESS TOKEN FROM REFRESH")

     #Write new tokens to csv file 
    with open('data/tokens.csv', mode = 'w', newline='') as file:
        csv_writer = csv.writer(file)
        for entry in updated_rows:
            csv_writer.writerow(entry)

make_requests()
                