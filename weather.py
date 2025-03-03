import flask
import requests
import os

app = flask.Flask(__name__)

# OpenWeather API Key
OPENWEATHER_API_KEY = "cae190d63ed577c1bc29e73afc0768d5"

# Function to get weather data directly by city name
def get_weather(city):
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
    response = requests.get(weather_url).json()

    if "main" in response:
        temp = response["main"]["temp"]
        condition = response["weather"][0]["main"]
        return f"The average temerature in {city} is {temp}°C with {condition.lower()}."
    
    return f"Sorry, I couldn't find weather data for {city}."

@app.route("/webhook", methods=["POST"])
def dialogflow_webhook(request):
    req = flask.request.get_json()
    
    # Extract city from Dialogflow request
    parameters = req["sessionInfo"]["parameters"]
    city = parameters.get("geo-city") or parameters.get("city") or "Unknown Location"

    # Fetch weather data
    weather_info = get_weather(city)

    # Return response to Dialogflow
    return flask.jsonify({"fulfillment_response": {"messages": [{"text": {"text": [weather_info]}}]}})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  #