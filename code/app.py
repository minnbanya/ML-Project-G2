# Importing libraries
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import time

import mlflow
import mlflow.sklearn


mlflow.set_tracking_uri("http://157.230.38.70:5000")
modelName = "crop_recommender"
modelVersion = 1
stage = "Production"
# load the latest version of a model in that stage.
crop_model = mlflow.sklearn.load_model(model_uri=f"models:/{modelName}/{stage}")

mlflow.set_tracking_uri("http://157.230.38.70:5000")
modelVersion = 1
stage = "Production"
modelName = "fertilizer_recommender_w_crop"
fert_w_model = mlflow.sklearn.load_model(model_uri=f"models:/{modelName}/{stage}")

mlflow.set_tracking_uri("http://157.230.38.70:5000")
modelVersion = 1
stage = "Production"
modelName = "fertilizer_recommender_wo_crop"
fert_wo_model = mlflow.sklearn.load_model(model_uri=f"models:/{modelName}/{stage}")

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['GET','POST'])
def process_input():
    if request.method == 'GET':
        latitude = request.args.get('lat')
        longitude = request.args.get('lon')
    if request.method == 'POST':
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
    
    start_time = time.time()

    token_url = "https://krishiprabidhi.net/api/token"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "email": "st124145@ait.ac.th",
        "password": "nopassword99",
    }
    # Make a POST request to obtain the token
    response = requests.post(token_url, headers=headers, json=payload)
    json_response = response.json()
    token = json_response['access']

    # Makes an API call for soil data
    api_url = f"https://krishiprabidhi.net/soil/soildata/"
    
    headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",  # Adjust based on the API requirements
            }   
    params = {
        "lon" : longitude,
        "lat" : latitude
    }
    response = requests.get(api_url, headers=headers, params=params)
    # print(response.json())

    # Check if the API call is successful
    if response.status_code == 200:
        # Parse the JSON response
        soil_data = response.json()

        # Store values from JSON response
        nitrogen_percentage = soil_data.get('totalNitrogen', None)
        phosphorous_kg = soil_data.get('p2o5', None)
        print(soil_data.get('p2o5', None))
        ph = soil_data.get('ph', None)

    

    # Makes an API call for weather data
    api_url = f"http://api.weatherstack.com/current?access_key=bca5f2d868c585889eaccfb267a5ce7b&query={latitude},{longitude}"
    
    response = requests.get(api_url)
    # print(response.json())

    # Check if the API call is successful
    if response.status_code == 200:
        # Parse the JSON response
        weather_data = response.json()

        temperature = weather_data.get('current', {}).get('temperature', None)
        humidity = weather_data.get('current', {}).get('humidity', None)

        print(f'API response time: {time.time() - start_time:.0f} seconds')
    
    # Remove the percentage symbol and convert to float
    try:
        nitrogen = float(nitrogen_percentage.replace('%', '')) if nitrogen_percentage else None
    except ValueError:
        print("Error: Could not convert nitrogen to float")
        nitrogen = None

    try:
        phosphorous = float(phosphorous_kg.replace('kg/ha', '')) if phosphorous_kg else None
    except ValueError:
        print("Error: Could not convert phosphorous to float")
        phosphorous = None

    crop_list = ['Apple', 'Banana', 'Blackgram', 'Chickpea', 'Coconut', 'Coffee',
                'Cotton', 'Grapes', 'Jute', 'Kidneybeans', 'Lentil', 'Maize',
                'Mango', 'Mothbeans', 'Mungbean', 'Muskmelon', 'Orange', 'Papaya',
                'Pigeonpeas', 'Pomegranate', 'Rice', 'Watermelon']

    
    crop_input = [[nitrogen,phosphorous,temperature,humidity,ph]]
    crop_prob = crop_model.predict_proba(crop_input)[0]
    crop_pred = crop_prob.argsort()[::-1][:3]
    crop_suit = sorted(crop_prob, reverse=True)[:3]

    

    #Image API for crop image display
    api_url = "https://api.unsplash.com//search/photos"

    access_key = "Rh-yjXnAefB0EVCAU48O9Rgh-Z_LyoeE3_rkbmREpVc"

    # Fertilizer Recommendation
    fertilizer_list = ['Urea', 'DAP', 'MOP', '10:26:26 NPK', 'SSP', 'Magnesium Sulphate',
                        '13:32:26 NPK', '12:32:16 NPK', '50:26:26 NPK', '19:19:19 NPK',
                        'Chilated Micronutrient', '18:46:00 NPK', 'Sulphur',
                        '20:20:20 NPK', 'Ammonium Sulphate', 'Ferrous Sulphate',
                        'White Potash', '10:10:10 NPK', 'Hydrated Lime', '14-35-14',
                        '28-28', '17-17-17', '20-20']
    fert_input = [[nitrogen,phosphorous,temperature,humidity]]
    fert_prob = fert_wo_model.predict_proba(fert_input)[0]
    fert_pred = fert_prob.argsort()[::-1][:3]
    fert_result = []
    for i in range(len(fert_pred)):
        fertilizer = fertilizer_list[fert_pred[i]]
        fert_result.append(fertilizer)

    fert_w_list = ['Sugarcane', 'Jowar', 'Cotton', 'Rice', 'Wheat', 'Groundnut',
                    'Maize', 'Tur', 'Urad', 'Moong', 'Gram', 'Masoor', 'Soybean',
                    'Ginger', 'Turmeric', 'Grapes', 'Tobacco', 'Paddy', 'Barley',
                    'Millets', 'Oil seeds', 'Pulses', 'Ground Nuts']
    
    crop_result = []
    crop_image = []
    fertilizers = []
    for i in range(len(crop_pred)):
        crop_name = crop_list[crop_pred[i]]
        crop_result.append(crop_name)
        
        if crop_name in fert_w_list:
            fert_w_input = [[crop_name, nitrogen,phosphorous,temperature,humidity]]
            fert_w_prob = fert_w_model.predict_proba(fert_w_input)[0]
            fert_w_pred = fert_w_prob.argsort()[::-1][:3]
            fert_w_result = []
            for i in range(len(fert_w_pred)):
                fertilizer = fertilizer_list[fert_w_pred[i]]
                fert_w_result.append(fertilizer)
        else:
            fert_w_result = fert_result
        fertilizers.append(fert_w_result)

        params = {
        "client_id": access_key,
        "query": crop_name
    }
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
        # Parse the JSON response
            image_data = response.json()
            results = image_data.get('results', [])
            if results:
                # Assuming you want the first result
                first_result = results[0]
                image_url = first_result.get('urls', {}).get('regular', None)
            else:
                image_url = "https://via.placeholder.com/150x150.png?text=Image+Not+Available"
            crop_image.append(image_url)

    if 'coord' in soil_data:
        del soil_data['coord']
    
    desired_keys = ['temperature', 'precip', 'humidity']
    weather_data = weather_data['current']
    weather_data = {key: value for key, value in weather_data.items() if key in desired_keys}
    
    print(soil_data)
    print(weather_data)
    return render_template('result.html', crop_result=crop_result, crop_image=crop_image, crop_suit=crop_suit, fertilizers = fertilizers,
                           soil_data=soil_data,weather_data=weather_data)

port_number = 8000

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port_number)