from flask import Flask, render_template, request, url_for
from BestTimeToFertilizeModule import BestTimeToFertilize
from NPKEstimatorModule import NPKEstimator
import joblib


app = Flask(__name__)


@app.route('/processing/', methods=['GET', 'POST'])
def processing():
    if request.method == "GET":
        print("The URL /processing is accessed directly.")
        return url_for('index.html')

    if request.method == "POST":
        form_data = request.form
        call_success = []
        npk_list_dict = []
        popup_data = []
        seven_days = []

        crop = form_data['crop']
        state = form_data['state']
        city = form_data['city']

        with open("InputData.csv", "w") as fh:
            input_data = "%s,%s,%s" % (crop.strip(), state.strip(), city.strip())
            fh.write(input_data)
        
        bttf = BestTimeToFertilize(city_name = city, state_name = state)
        bttf.api_caller()

        if bttf.is_api_call_success():
            popup_data = bttf.best_time_fertilize()

            call_success.append(1)
            # popup_data.append([category, heading, desc])
            seven_days = bttf.weather_data[:]
            print(seven_days)
            
            # today's weather data
            di = bttf.weather_data[0]
            Temp = di['Temperature']
            humidity = di['Relative Humidity']
            rainfall = di["Rainfall"]

            est = NPKEstimator()
            est.renameCol()
            npk = {'Label_N':0, 'Label_P':0, 'Label_K':0}
            for y_label in ['Label_N', 'Label_P', 'Label_K']:
                npk[y_label] = est.estimator(crop, Temp, humidity, rainfall, y_label)
            # print(npk)
            print(est.accuracyCalculator())

            npk_list_dict.append(npk)
            print("pop_data :",popup_data)
            output_data = popup_data['type'] +"\n"+ popup_data['title'] +"\n"+ popup_data['description'] +"\n"+ str(npk['Label_N'])  +"\n"+ str(npk['Label_P'])  +"\n"+ str(npk['Label_K'])
            with open("output.txt", "w") as fh:
                fh.write(output_data)
            knn_loaded = joblib.load('knn_model.pkl')
            sample_input = [[Temp, humidity, npk['Label_N'], npk['Label_K'], npk['Label_P']]]
            predicted_fertilizer = knn_loaded.predict(sample_input)
            print("Predicted Fertilizer Name:", predicted_fertilizer[0])
        else:
            print("Error Occured")
        print(call_success, npk_list_dict, form_data, popup_data)
        return render_template('update.html',TEMP=Temp,HUMIDITY =humidity,RAINFALL=rainfall, CALL_SUCCESS = call_success, NPK = npk_list_dict, FORM_DATA = form_data, POPUP_DATA = popup_data, SEVEN_DAYS = seven_days,predicted_fertilizer_temp =predicted_fertilizer[0])
    

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)