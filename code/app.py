# Importing libraries
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import time
import pickle

# Open the file in binary mode for reading
with open(b"models/crop.model", "rb") as model_file:
    # Load the model from the file
    crop_model = pickle.load(model_file)

with open(b"models/fertilizer.model", "rb") as model_file:
    # Load the model from the file
    fertilizer_model = pickle.load(model_file)

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

    crop_list = ['apple', 'banana', 'blackgram', 'chickpea', 'coconut', 'coffee',
                'cotton', 'grapes', 'jute', 'kidneybeans', 'lentil', 'maize',
                'mango', 'mothbeans', 'mungbean', 'muskmelon', 'orange', 'papaya',
                'pigeonpeas', 'pomegranate', 'rice', 'watermelon']

    crop_result = []
    crop_input = [[nitrogen,phosphorous,temperature,humidity,ph]]
    crop_prob = crop_model.predict_proba(crop_input)[0]
    crop_pred = crop_prob.argsort()[::-1][:3]
    for i in range(len(crop_pred)):
        crop_result.append(crop_list[crop_pred[i]])
    return render_template('result.html', crop_result=crop_result)

@app.route('/crop_details')
def crop_details():
    crop_name = request.args.get('crop_name')

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

    # Check if the token is present in the JSON response
    if 'access' not in json_response:
        error_message = "Failed to obtain access token."
        return jsonify({'error': error_message}), 500

    token = json_response['access']

    # Makes an API call for crop data
    api_url = f"https://krishiprabidhi.net/crop/api/bmp/{crop_name}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Make a GET request to the crop API
    response = requests.get(api_url, headers=headers)

    # Check if the API call is successful
    if response.status_code != 200:
        error_message = f"Failed to fetch crop data for {crop_name}."
        return render_template('crop_details_error.html', crop_name=crop_name)

    # Parse the JSON response
    crop_data = response.json()

    # Rest of your code...

    return render_template('crop_details.html', crop_name=crop_name, crop_data=crop_data)
port_number = 8000

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port_number)