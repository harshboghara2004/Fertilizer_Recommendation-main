import requests as rq
import json as js
from time import sleep


class BestTimeToFertilize:
    __BASE_URL = "https://api.weatherbit.io/v2.0/forecast/daily?"
    __API_KEY = "0c63bf48cd1c40bfb2505d7fab4350ad"
    
    
    def __init__(self, city_name = 'Bangalore', state_name = 'Karnataka', days = 2):
        self.city_name = '+'.join(city_name.lower().strip().split())
        self.state_name = '+'.join(state_name.lower().strip().split())
        self.country_name = 'IN'
        self.days = days
        self.response = None
        self.response_code = None
        self.weather_data = list()
        
    def api_caller(self):
        try:
            complete_url = "{0}city={1}&state={2}&country={3}&key={4}&days={5}".format(self.__BASE_URL, self.city_name, self.state_name, self.country_name, self.__API_KEY, self.days)
            # print(complete_url)
            # while self.response == None:
            self.response = rq.get(complete_url)
            sleep(5)
            self.response_code = self.response.status_code
            return self.response_code
        except Exception as msg:
            print("api_caller():", msg)
            return -1
        
    
    def is_api_call_success(self):
        if self.response_code == 200:
            return True
        elif self.response_code == 204:
            print('Content Not available, error code: 204')
        return False
    

    def json_file_bulider(self):
        try:
            json_obj = self.response.json()
            with open('weather_data.json', 'w') as file:
                js.dump(json_obj, file, indent = 1, sort_keys = True)
            print("weather_data.json file build successfully")
        except Exception as msg:
            print("json_bulider():", msg)
            
    
    def best_time_fertilize(self):
        json_obj = self.response.json()
        
        print("City:", json_obj['city_name'], "\n")

        prolonged_precip = 0
        prolonged_prob = 0
        heavy_rain_2d = False
        heavy_rain_chance_2d = 0
        precip_2d = 0
        precip_chance_2d = 0
        
        for i in range(self.days):
            date = json_obj['data'][i]['datetime']
            temp = json_obj['data'][i]['temp']
            rh = json_obj['data'][i]['rh']
            precip = json_obj['data'][i]['precip']
            prob = json_obj['data'][i]['pop']
            w_code = json_obj['data'][i]['weather']['code']
            w_desc = json_obj['data'][i]['weather']['description']
            prolonged_precip += precip
            prolonged_prob += prob

            count_2d = 0
            if i < 2:
                precip_2d += precip
                precip_chance_2d += prob
                if w_code in [202, 233, 502, 521, 522]:
                    heavy_rain_2d = True
                    heavy_rain_chance_2d += prob
                    count_2d += 1
                    heavy_rain_chance_2d //= count_2d
            
            di = {
                  "Date":date, 
                  "Temperature":temp, 
                  "Relative Humidity":rh, 
                  "Rainfall":precip, 
                  "Probability of Precipitation":prob,
                  "Weather Description": w_desc
                 }
            self.weather_data.append(di)

        prolonged_prob //= self.days
        precip_chance_2d //= 2

        result = {}

        if heavy_rain_2d:
            result['type'] = 'Warning'
            result['title'] = 'Heavy Rain Alert'
            result['description'] = 'Heavy Rain Chances within two days from now is %d%%' % (heavy_rain_chance_2d)
            result['details'] = {'risk': 'Heavy Rainfall puts your fertilizer at risk.'}
            
        elif prolonged_precip > 12.7 and prolonged_prob >= 50:
            result['type'] = 'Warning'
            result['title'] = 'Prolonged Rainfall Alert'
            result['description'] = 'Prolonged Rainfall of greater than 12.7 mm puts your fertilizer at risk. From now %.2f mm rainfall will receive for upcoming seven days, chances %d%%' % (prolonged_precip, prolonged_prob)
            result['details'] = {'risk': 'Prolonged Rainfall of greater than 12.7 mm puts your fertilizer at risk.'}
            
        else:
            result['type'] = 'Message'
            result['title'] = 'Precipitation Amount'
            result['description'] = 'The amount of rain for 2 days, counting today is %.2f mm and chances is %d%%' % (precip_2d, precip_chance_2d)
            result['details'] = {'amount': precip_2d, 'chances': precip_chance_2d}
        return result


        