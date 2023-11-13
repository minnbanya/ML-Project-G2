# Importing libraries
from flask import Flask, render_template, request
import requests

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    if request.method == 'POST':
        latitude = request.form.get('latitude')
        logitude = request.form.get('logitude')

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
            "lon" : logitude,
            "lat" : latitude
        }
        response = requests.get(api_url, headers=headers, params=params)
        print(response.json())

        # Check if the API call is successful
        if response.status_code == 200:
            # Parse the JSON response
            soil_data = response.json()

            # Store values from JSON response
            nitrogen = soil_data.get('totalNitrogen', None)
            phosphorous = soil_data.get('p2o5', None)
            print(soil_data.get('p2o5', None))
            ph = soil_data.get('ph', None)

        # Makes an API call for soil data
        crop = "cauliflower"
        api_url = f"https://krishiprabidhi.net/crop/api/bmp/{crop}"
        
        headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",  # Adjust based on the API requirements
                }   

        response = requests.get(api_url, headers=headers)
        print(response.json())

        # Check if the API call is successful
        if response.status_code == 200:
            # Parse the JSON response
            crop_data = response.json()

            # Store values from JSON response
            # nitrogen = soil_data.get('totalNitrogen', None)
            # phosphorous = soil_data.get('p2o5', None)
            # print(soil_data.get('p2o5', None))
            # ph = soil_data.get('ph', None)

            return render_template('result.html', nitrogen=nitrogen, phosphorous=phosphorous, ph=ph)
        else:
            return render_template('error.html')


port_number = 8000

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port_number)