import requests
import base64
import csv
from datetime import datetime, timedelta

client_id = '23RW9Q'
client_secret = '252bcb2f8ea01c138d866ddd0984fdcc'
basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
headers = {
               'Authorization': f'Basic {basic_token}',
                'Content-Type': 'application/x-www-form-urlencoded' }

end_date = datetime.now()
start_date = end_date - timedelta(days=6)
end_date_str = end_date.strftime('%Y-%m-%d')
start_date_str = start_date.strftime('%Y-%m-%d')



def get_new_access_token(row):
     url = 'https://api.fitbit.com/oauth2/token'
     refresh_token = row[1]
     data = {
               'grant_type': 'refresh_token',
               'refresh_token': refresh_token
               }
               #Get new access token and refresh token to make the call
     response = requests.post(url, headers = headers, data = data)
     if response.status_code == 200:
          tokens = response.json()
          access_token, refresh_token = tokens.get('access_token'), tokens.get('refresh_token')
          print("SUCCESSFULLY GOT THE TOKENS")
          return access_token, refresh_token
     else:
          return None, None

def get_name(access_token):
     profile_header = {
                         'Authorization': f'Bearer {access_token}'
                    }
     profile_url = 'https://api.fitbit.com/1/user/-/profile.json'
     profile_response = requests.get(profile_url, headers = profile_header)
     if profile_response.status_code == 200:
          profile_data = profile_response.json()
          name = profile_data['user']['fullName']
          return name
     else: 
          return "Could not Retrieve"

def get_steps(header):
     steps_url =f'https://api.fitbit.com/1/user/-/activities/steps/date/{start_date_str}/{end_date_str}.json'
     steps_response = requests.get(steps_url, headers = header)
     if steps_response.status_code == 200:
          daily_steps = []
          steps_data = steps_response.json()
          #Get weekend average
          weekend_data_steps_avg = (float(steps_data['activities-steps'][-1]['value']) + float(steps_data['activities-steps'][-2]['value']))/2
          #print(steps_data)
          #Get weekday average
          weekday_data_steps_total = 0
          for i in range(5):
               weekday_data_steps_total += float(steps_data['activities-steps'][i]['value'])
               weekday_data_steps_avg = weekday_data_steps_total/5
               #print(weekday_data_steps_avg)
          for entry in steps_data['activities-steps']:
               daily_steps.append(entry['value'])
          return daily_steps, weekday_data_steps_avg, weekend_data_steps_avg
     else:
          return None
     #Also just need to return steps each day 




def get_activity(header):
     minutes_lightly_active_url =f'https://api.fitbit.com/1/user/-/activities/minutesLightlyActive/date/{start_date_str}/{end_date_str}.json'
     minutes_fairly_active_url =f'https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/{start_date_str}/{end_date_str}.json'
     minutes_very_active_url =f'https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/{start_date_str}/{end_date_str}.json'
     light_activity_response = requests.get(minutes_lightly_active_url, headers = header)
     fairly_activity_response = requests.get(minutes_fairly_active_url, headers = header)
     very_activity_response = requests.get(minutes_very_active_url, headers = header)
     if light_activity_response.status_code == 200 and fairly_activity_response.status_code == 200 and very_activity_response.status_code == 200:
          light_activity_data = light_activity_response.json()
          fairly_activity_data = fairly_activity_response.json()
          very_activity_data = very_activity_response.json()
          weekend_activity_average = (float(light_activity_data['activities-minutesLightlyActive'][-1]['value']) + float(light_activity_data['activities-minutesLightlyActive'][-2]['value']) + float(fairly_activity_data['activities-minutesFairlyActive'][-1]['value']) + float(fairly_activity_data['activities-minutesFairlyActive'][-2]['value']) + float(very_activity_data['activities-minutesVeryActive'][-1]['value']) + float(very_activity_data['activities-minutesVeryActive'][-2]['value'])) / 2
          weekday_activity_total = 0
          for i in range(5):
               weekday_activity_total =  weekday_activity_total + float(very_activity_data['activities-minutesVeryActive'][i]['value']) + float(fairly_activity_data['activities-minutesFairlyActive'][i]['value']) + float(light_activity_data['activities-minutesLightlyActive'][i]['value'])
          weekday_activity_average = weekday_activity_total / 5
          daily_activity = []
          for i in range(7):
               day_activity = float(very_activity_data['activities-minutesVeryActive'][i]['value']) + float(fairly_activity_data['activities-minutesFairlyActive'][i]['value']) + float(light_activity_data['activities-minutesLightlyActive'][i]['value'])
               daily_activity.append(day_activity)
          return daily_activity, weekday_activity_average, weekend_activity_average


def get_distance(header):
     distance_url = f'https://api.fitbit.com/1/user/-/activities/distance/date/{start_date_str}/{end_date_str}.json'
     distance_response = requests.get(distance_url, headers = header)
     if distance_response.status_code == 200:
          daily_distance = []
          distance_data = distance_response.json()
          weekend_distance_avg = (float(distance_data['activities-distance'][-1]['value']) + float(distance_data['activities-distance'][-2]['value'])) / 2
          weekday_distance_total = 0
          for i in range(5):
               weekday_distance_total += float(distance_data['activities-distance'][i]['value'])
          weekday_distance_avg = weekday_distance_total/5
          for entry in distance_data['activities-distance']:
               daily_distance.append(entry['value'])
          return daily_distance, weekday_distance_avg, weekend_distance_avg
     else:
          return None

def update_csv_tokens(updates):
     with open('data/tokens.csv', mode = 'w', newline='') as file:
        csv_writer = csv.writer(file)
        for entry in updates:
            csv_writer.writerow(entry)




def make_requests():
    updated_tokens = []
    data_headers = [
    'Name', 'Average weekday daily steps', 'Average weekday active time', 'Average weekday miles traveled',
    'Average weekend daily steps', 'Average weekend active time', 'Average weekend miles traveled'
     ]
# Add headers for each day in the week for steps, activity, and distance
    for i in range(7):  # 0 to 6, for each day of the week
          date = end_date - timedelta(days=6-i)
          date_str = date.strftime('%Y-%m-%d')
          data_headers.extend([
               f'{date_str} steps',
               f'{date_str} active time',
               f'{date_str} miles traveled'
          ])
         
    with open('data/activity_data.csv', mode = 'w') as activity_file:
         csv_writer = csv.writer(activity_file)
         csv_writer.writerow(data_headers)

    with open('data/tokens.csv', mode = 'r') as file:
          csv_reader = csv.reader(file)
          #Iterate through all the rows
          for row in csv_reader:
               access_token, refresh_token = get_new_access_token(row)
               if not access_token:
                    continue
               updated_tokens.append([access_token, refresh_token])
                    #Profile Call
               activity_header = {
                    'Authorization': f'Bearer {access_token}',
                    'accept': 'application/json'
               }
               #Name
               name = get_name(access_token)
               #Steps
               daily_steps, weekday_data_steps_avg, weekend_data_steps_avg = get_steps(activity_header)
               #Activity
               daily_activity, weekday_activity_avg, weekend_activity_avg = get_activity(activity_header)
               #distance
               daily_distances, weekday_distance_avg, weekend_distance_avg = get_distance(activity_header)

               row_data = [name, weekday_data_steps_avg, weekday_activity_avg, weekday_distance_avg, weekend_data_steps_avg, weekend_activity_avg, weekend_distance_avg]
               for i in range(7):
                    row_data.extend([daily_steps[i], daily_activity[i], daily_distances[i]])
               

               with open('data/activity_data.csv', mode = 'a') as activity_file:
                    csv_writer = csv.writer(activity_file)
                    csv_writer.writerow(row_data)
               
                    # #Sleep 
                    # sleep_url = f'https://api.fitbit.com/1.2/user/-/sleep/date/{start_date_str}/{end_date_str}.json'
                    # sleep_response = requests.get(sleep_url, headers = activity_header)
                    # if sleep_response.status_code == 200:
                    #      sleep_data = sleep_response.json()
                    #      weekend_avg_sleep_hours = (float(sleep_data['sleep'][-1]['minutesAsleep']) + float(sleep_data['sleep'][-2]['minutesAsleep']) / 2) / 60
                    #      sunday_levels, saturday_levels = sleep_data['sleep'][-1]['levels']['data'], sleep_data['sleep'][-2]['levels']['data']
                    #      weekend_deep_sleep_total, weekend_light_sleep_total = 0, 0
                    #      for entry in sunday_levels:
                    #           if entry['level'] == 'deep':
                    #                weekend_deep_sleep_total += entry['seconds']
                    #           if entry['level'] == 'light':
                    #                weekend_light_sleep_total += entry['seconds']
                    #      for entry in saturday_levels:
                    #           if entry['level'] == 'deep':
                    #                weekend_deep_sleep_total += entry['seconds']
                    #           if entry['level'] == 'light':
                    #                weekend_light_sleep_total += entry['seconds']
                    #      weekend_light_avg, weekend_deep_avg = weekend_light_sleep_total / 3600, weekend_deep_sleep_total / 3600
                    #      #Weekday sleep averages
                    #      weekday_total_sleep_hours, weekday_deep_sleep_total, weekday_light_sleep_total = 0, 0, 0
                    #      for i in range(5):
                    #           current_day = sleep_data['sleep'][i]['levels']['data']
                    #           weekday_total_sleep_hours += float(sleep_data['sleep'][i]['minutesAsleep'])
                    #           for entry in current_day:
                    #                if entry['level'] == 'deep':
                    #                     weekday_deep_sleep_total += entry['seconds']
                    #                if entry['level'] == 'light':
                    #                      weekday_light_sleep_total += entry['seconds']
                    #      weekday_light_avg, weekday_deep_avg, weekday_avg_sleep_hours  = weekday_light_sleep_total / 3600, weekday_deep_sleep_total / 3600, weekday_total_sleep_hours / 300
                         
                    # else:
                    #      print("Could not retrieve sleep data")
                    

     #Write new tokens to csv file 
    update_csv_tokens(updated_tokens)

make_requests()
                