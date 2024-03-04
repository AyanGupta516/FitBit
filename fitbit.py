import requests
import base64
import csv
from datetime import datetime, timedelta
from supabase import create_client, Client
from supaconfig import supabase_key, supabase_url


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

supabase: Client = create_client(supabase_url, supabase_key)

def get_new_access_token(row):
     url = 'https://api.fitbit.com/oauth2/token'
     refresh_token = row['refresh_token']
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
          weekend_data_steps_total = 0
          weekday_data_steps_total = 0
          for entry in steps_data['activities-steps']:
               date_object = datetime.strptime(entry['dateTime'], '%Y-%m-%d')
               day_of_week = date_object.strftime("%A")
               if day_of_week == 'Saturday' or day_of_week == 'Sunday':
                    weekend_data_steps_total += float(entry['value'])
               else:
                    weekday_data_steps_total  += float(entry['value'])
               daily_steps.append(round(float(entry['value']),2))
          weekday_data_steps_avg = round(weekday_data_steps_total / 5, 2)
          weekend_data_steps_avg = round(weekend_data_steps_total /2 , 2)
          return daily_steps, weekday_data_steps_avg, weekend_data_steps_avg
     else:
          return None
     #Also just need to return steps each day 




def get_activity(header):
     minutes_fairly_active_url =f'https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/{start_date_str}/{end_date_str}.json'
     minutes_very_active_url =f'https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/{start_date_str}/{end_date_str}.json'
     fairly_activity_response = requests.get(minutes_fairly_active_url, headers = header)
     very_activity_response = requests.get(minutes_very_active_url, headers = header)
     if fairly_activity_response.status_code == 200 and very_activity_response.status_code == 200:
          fairly_activity_data = fairly_activity_response.json()
          very_activity_data = very_activity_response.json()
          weekday_activity_total = 0
          weekend_activity_total = 0
          daily_activity = []
          for i in range(7):
               date_object = datetime.strptime(very_activity_data['activities-minutesVeryActive'][i]['dateTime'], '%Y-%m-%d')
               day_of_week = date_object.strftime("%A")
               if day_of_week == 'Saturday' or day_of_week == 'Sunday':
                    weekend_activity_total = weekend_activity_total + float(very_activity_data['activities-minutesVeryActive'][i]['value']) + float(fairly_activity_data['activities-minutesFairlyActive'][i]['value'])
               else:
                    weekday_activity_total = weekday_activity_total + float(very_activity_data['activities-minutesVeryActive'][i]['value']) + float(fairly_activity_data['activities-minutesFairlyActive'][i]['value'])
               day_activity = float(very_activity_data['activities-minutesVeryActive'][i]['value']) + float(fairly_activity_data['activities-minutesFairlyActive'][i]['value'])
               daily_activity.append(round(float(day_activity),2))
               weekend_activity_average = round(weekend_activity_total / 2 , 2)
               weekday_activity_average = round(weekday_activity_total / 5 , 2)
          return daily_activity, weekday_activity_average, weekend_activity_average


def get_distance(header):
     distance_url = f'https://api.fitbit.com/1/user/-/activities/distance/date/{start_date_str}/{end_date_str}.json'
     distance_response = requests.get(distance_url, headers = header)
     if distance_response.status_code == 200:
          daily_distance = []
          distance_data = distance_response.json()
          weekend_distance_total, weekday_distance_total = 0,0 
          for entry in distance_data['activities-distance']:
               date_object = datetime.strptime(entry['dateTime'], '%Y-%m-%d')
               day_of_week = date_object.strftime("%A")
               if day_of_week == 'Saturday' or day_of_week == 'Sunday':
                    weekend_distance_total += float(entry['value'])
               else:
                    weekday_distance_total  += float(entry['value'])
               daily_distance.append(round(float(entry['value']),2))

          weekend_distance_avg = round(weekend_distance_total / 2, 2)
          weekday_distance_avg = round(weekday_distance_total / 5, 2)
               
          return daily_distance, weekday_distance_avg, weekend_distance_avg
     else:
          return None

def get_sleep_data(header):
     sleep_url = f'https://api.fitbit.com/1.2/user/-/sleep/date/{start_date_str}/{end_date_str}.json'
     sleep_response = requests.get(sleep_url, headers = header)
     res = []
     #Total sleep data
     sleep_hours_by_date = {}
     light_sleep_by_date = {}
     deep_sleep_by_date = {}
     current_date = start_date
     for i in range(7):
          sleep_hours_by_date[current_date.strftime("%Y-%m-%d")] = 'NA'
          light_sleep_by_date[current_date.strftime("%Y-%m-%d")] = 'NA'
          deep_sleep_by_date[current_date.strftime("%Y-%m-%d")] = 'NA'
          current_date += timedelta(1)
     if sleep_response.status_code == 200:
          sleep_data = sleep_response.json()
          sleep_entries = sleep_data['sleep']
          for entry in sleep_entries:
               date = entry['dateOfSleep']
               #Total Sleep 
               sleep_time = float(entry['minutesAsleep']) / 60.0
               sleep_hours_by_date[date] = round(sleep_time, 2)

               sleep_level_data = entry['levels']['data']
               for level_entry in sleep_level_data:
                    if level_entry['level'] == 'deep' or level_entry['level'] == 'asleep':
                         deep_sleep_by_date[date] = round(float(level_entry['seconds']) / 3600, 2)
                    elif level_entry['level'] == 'light' or level_entry['level'] == 'restless':
                         light_sleep_by_date[date] = round(float(level_entry['seconds']) / 3600, 2)
               
          weekday_total_sleep, weekend_total_sleep = 0, 0
          weekday_days_sleep, weekend_days_sleep = 0, 0

          weekday_total_light_sleep, weekend_total_light_sleep = 0, 0
          weekday_days_light_sleep, weekend_days_light_sleep = 0, 0
               
          weekday_total_deep_sleep, weekend_total_deep_sleep = 0, 0
          weekday_days_deep_sleep, weekend_days_deep_sleep = 0, 0

          for entry in sleep_hours_by_date:
               if sleep_hours_by_date[entry] != 'NA':
                    date_object = datetime.strptime(entry, '%Y-%m-%d')
                    day_of_week = date_object.strftime("%A")
                    if day_of_week == "Sunday" or day_of_week == 'Saturday':
                         weekend_days_sleep += 1
                         weekend_total_sleep += sleep_hours_by_date[entry]
                    else:
                         weekday_days_sleep += 1
                         weekday_total_sleep += sleep_hours_by_date[entry]

               if light_sleep_by_date[entry] != 'NA':
                    date_object = datetime.strptime(entry, '%Y-%m-%d')
                    day_of_week = date_object.strftime("%A")
                    if day_of_week == "Sunday" or day_of_week == 'Saturday':
                         weekend_days_light_sleep += 1
                         weekend_total_light_sleep +=  light_sleep_by_date[entry]
                    else:
                         weekday_days_light_sleep += 1
                         weekday_total_light_sleep +=  light_sleep_by_date[entry]

               if deep_sleep_by_date[entry] != 'NA':
                         date_object = datetime.strptime(entry, '%Y-%m-%d')
                         day_of_week = date_object.strftime("%A")
                         if day_of_week == "Sunday" or day_of_week == 'Saturday':
                              weekend_days_deep_sleep += 1
                              weekend_total_deep_sleep +=  deep_sleep_by_date[entry]
                         else:
                              weekday_days_deep_sleep += 1
                              weekday_total_deep_sleep +=  deep_sleep_by_date[entry]
          
          if weekday_days_sleep == 0:
               average_weekday_total_sleep = 'NA'
          else:
               average_weekday_total_sleep = weekday_total_sleep / weekday_days_sleep
          
          if weekend_days_sleep == 0:
               average_weekend_total_sleep = 'NA'
          else:
               average_weekend_total_sleep = weekend_total_sleep / weekend_days_sleep

          if weekday_days_light_sleep == 0:
               average_weekday_light_sleep = 'NA'
          else:
               average_weekday_light_sleep = weekday_total_light_sleep / weekday_days_light_sleep

          if weekend_days_light_sleep == 0:
               average_weekend_light_sleep = 'NA'
          else:
               average_weekend_light_sleep = weekend_total_light_sleep / weekend_days_light_sleep

          if weekday_days_deep_sleep == 0:
               average_weekday_deep_sleep = 'NA'
          else:
               average_weekday_deep_sleep = weekday_total_deep_sleep / weekday_days_deep_sleep

          if weekend_days_deep_sleep == 0:
               average_weekend_deep_sleep = 'NA'
          else:
               average_weekend_deep_sleep = weekend_total_deep_sleep / weekend_days_deep_sleep

          res = []

               
          res.extend([average_weekday_total_sleep, average_weekend_total_sleep, average_weekday_light_sleep, average_weekend_light_sleep, average_weekday_deep_sleep, average_weekend_deep_sleep])

          for entry in sleep_hours_by_date:
               res.append(sleep_hours_by_date[entry])
               res.append(light_sleep_by_date[entry])
               res.append(deep_sleep_by_date[entry])
          print(res)
          return res
     



def make_requests():

    activity_data_headers = [
      'Name', 'Average weekday daily steps', 'Average weekend daily steps',
      'Average weekday active time', 'Average weekend active time',
      'Average weekday miles traveled', 'Average weekend miles traveled'
     ]
    
    sleep_data_headers = ['Name', 'Average weekday sleep', 'Average weekend sleep', 
                          'Average weekday light sleep', 'Average weekend light sleep',
                           'Average weekday deep sleep, Average weekend deep sleep' ]
    for i in range(7):
          date = end_date - timedelta(days=6-i)
          date_str = date.strftime('%Y-%m-%d')
          sleep_data_headers.extend([
               f'{date_str} daily sleep',
               f'{date_str} light sleep',
               f'{date_str} deep sleep'
          ])
# Add headers for each day in the week for steps, activity, and distance
    for i in range(7):  # 0 to 6, for each day of the week
          date = end_date - timedelta(days=6-i)
          date_str = date.strftime('%Y-%m-%d')
          activity_data_headers.extend([
               f'{date_str} steps',
               f'{date_str} active time',
               f'{date_str} miles traveled'
          ])
         
    with open('data/activity_data.csv', mode = 'w') as activity_file:
         csv_writer = csv.writer(activity_file)
         csv_writer.writerow(activity_data_headers)
     
    with open('data/sleep_data.csv', mode = 'w') as sleep_file:
         csv_writer = csv.writer(sleep_file)
         csv_writer.writerow(sleep_data_headers)
     
    rows = supabase.table("access_tokens").select("*").execute().data
          #Iterate through all the rows
    for row in rows:
               current_id = row['id']
               access_token, refresh_token = get_new_access_token(row)
               if not access_token:
                    continue
               data, count = supabase.table('access_tokens').update({'access_token': access_token, 'refresh_token' : refresh_token}).eq('id', current_id).execute()
               activity_header = {
                    'Authorization': f'Bearer {access_token}',
                    'accept': 'application/json',
                    'accept-language': 'en_US'
               }
               #Name
               name = get_name(access_token)
               #Steps
               daily_steps, weekday_data_steps_avg, weekend_data_steps_avg = get_steps(activity_header)
               #Activity
               daily_activity, weekday_activity_avg, weekend_activity_avg = get_activity(activity_header)
               #distance
               daily_distances, weekday_distance_avg, weekend_distance_avg = get_distance(activity_header)

               row_data = [name, weekday_data_steps_avg, weekend_data_steps_avg, weekday_activity_avg, weekend_activity_avg, weekday_distance_avg, weekend_distance_avg]
               for i in range(7):
                    row_data.extend([daily_steps[i], daily_activity[i], daily_distances[i]])
               

               with open('data/activity_data.csv', mode = 'a') as activity_file:
                    csv_writer = csv.writer(activity_file)
                    csv_writer.writerow(row_data)
               
               #Sleep
               sleep_data = get_sleep_data(activity_header)
               if sleep_data != None:
                    sleep_data.insert(0, name)
                    with open ('data/sleep_data.csv', mode = 'a') as sleep_file:
                         csv_writer = csv.writer(sleep_file)
                         csv_writer.writerow(sleep_data)
               else:
                    print("NOTHING")

                    

     #Write new tokens to csv file 
    #update_csv_tokens(updated_tokens)

make_requests()
                