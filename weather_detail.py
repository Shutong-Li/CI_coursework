import flask
import requests
import os

app = flask.Flask(__name__)

OPENWEATHER_API_KEY = "cae190d63ed577c1bc29e73afc0768d5"

# Function to fetch weather details for a city
def get_weather_details(city, detail_type):
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
    response = requests.get(weather_url).json()

    if "main" not in response:
        return "Sorry, I couldn't retrieve the weather data."
    
    humidity = response["main"]["humidity"]
    wind = response["wind"]['speed']
    visibility = response['visibility']
    pressure = response["main"]["pressure"]
        
    # Map user-requested details to actual weather data
    detail_map = {
        "humidity": f"The humidity is {humidity}%.",
        "humid": f"The humidity is {humidity}%.",
        "pressure": f"The pressure is {pressure} hPa.",
        "wind": f"The wind speed is {wind} m/s.",
        "windy": f"The wind speed is {wind} m/s.",
        "visibility": f"The visibility is {visibility} meters."
    }
    
    return detail_map.get(detail_type, "Sorry, I couldn't find the requested weather information.")
    
    
@app.route("/webhook", methods=["POST"])
def dialogflow_webhook(request):
    req = flask.request.get_json()

    parameters = req["sessionInfo"]["parameters"]
    city = parameters.get("geo-city") or parameters.get("city") or "Unknown Location"
    detail_type = parameters.get("weather_detail") or "Unkown Detail"
    weather_info = get_weather_details(city, detail_type)

    # Return response to Dialogflow
    return flask.jsonify({"fulfillment_response": {"messages": [{"text": {"text": [weather_info]}}]}})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  #