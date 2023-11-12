# Importing libraries
from flask import Flask, render_template, request

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    if request.method == 'POST':
        latitude = request.form.get('latitude')
        logitude = request.form.get('logitude')

        # Makes an API call for soil data
        api_url = f"https://krishiprabidhi.net/soil/soildata/?lon={logitude}&lat={latitude}"
        response = request.get(api_url)

        # Check if the API call is successful
        if response.status_code == 200:



port_number = 8000

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port_number)