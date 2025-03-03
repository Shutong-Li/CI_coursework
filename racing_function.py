from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENWEATHER_API_KEY = "cae190d63ed577c1bc29e73afc0768d5"

f1_calendar_country = {
    "Australia": "Melbourne",
    "China": "Shanghai",
    "Japan": "Suzuka",
    "Baharain": "Sakhir",
    "Saudi Arabia": "Jeddah",
    "Monaco": "Monaco",
    "Spain": "Barcelona",
    "Canada": "Montreal",
    "Austria": "Spielberg",
    "United Kingdom": "Silverstone",
    "Belgium": "Spa",
    "Hungary": "Mogyorod",
    "Netherlands": "Zandvoort",
    "United States": "Austin",
    "Italy": "Monza",
    "Azerbaijan": "Baku",
    "Singapore": "Singapore",
    "Mexico": "Mexico City",
    "Brazil": "Sao Paulo",
    "Qatar": "Lusail",
    "Abu Dhabi": "Abu Dhabi"
}


f1_calendar_cities = [
    "melbourne", "shanghai", "suzuka", "bahrain", "jeddah", "miami", "imola",
    "monaco", "barcelona", "montreal", "spielberg", "silverstone", "spa",
    "mogyorod", "zandvoort", "monza", "baku", "singapore", "austin",
    "mexico city", "sao paulo", "las vegas", "lusail", "abu dhabi"
]


team_preferences = {
    "Red Bull": ["rain"],
    "McLaren": ["dry", "hot"],
    "Ferrari": ["dry", "hot"],
    "Mercedes": ["cold"]
}

def check_country(country):
    return country.title() in f1_calendar_country

def check_city(city):
    return city.lower() in f1_calendar_cities

def get_weather(city):
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
    response = requests.get(weather_url).json()
    if "main" not in response:
        return None, None, "Sorry, I couldn't retrieve the weather data."
    temp = response["main"]["temp"]
    weather = response["weather"][0]["main"]
    
    if weather.lower() == "clear":
        weather = "dry"
    return temp, weather, None

@app.route("/webhook", methods=["POST"])
def dialogflow_webhook(request):
    req = request.get_json()
    parameters = req["sessionInfo"]["parameters"]

    team = parameters.get("team_name", "Unknown Team").title()
    country = parameters.get("geo-country")
    city = parameters.get("geo-city") or parameters.get("city")

    if city:
        city = city.lower()

    # checking weather the country or city is in the calendar
    if country:
        if not check_country(country):
            return jsonify({
                "fulfillment_response": {
                    "messages": [{"text": {"text": ["Sorry, the country you're checking is not on the F1 2025 calendar."]}}]
                }
            })
        city = f1_calendar_country[country.title()]
    elif city:
        if not check_city(city):
            return jsonify({
                "fulfillment_response": {
                    "messages": [{"text": {"text": ["Sorry, the city you're checking is not on the F1 2025 calendar."]}}]
                }
            })
    else:
        return jsonify({
            "fulfillment_response": {
                "messages": [{"text": {"text": ["Sorry, please provide a city or country."]}}]
            }
        })

    temp, weather, error = get_weather(city)
    if error:
        return jsonify({
            "fulfillment_response": {
                "messages": [{"text": {"text": [error]}}]
            }
        })

    conditions = []
    # checking weather condition
    if weather.lower() in ["rain", "drizzle", "thunderstorm"]:
        conditions.append("rain")
    if temp >= 25:
        conditions.append("hot")
    if temp <= 10:
        conditions.append("cold")
    if not conditions:
        conditions.append("dry")

    # matching condition with team
    if any(cond in team_preferences.get(team, []) for cond in conditions):
        reply = f"Good for you! The current weather in {city.title()} is {temp}°C and {weather.lower()}, which is  perfect for {team}!"
    else:
        preferred_teams = []
        for cond in conditions:
            preferred_teams.extend(
                [t for t, prefs in team_preferences.items() if cond in prefs]
            )
        preferred_teams = list(set(preferred_teams))

        if preferred_teams:
            teams_list = " and ".join(preferred_teams)
            reply = f"Oops! It's {temp}°C and {weather.lower()} in {city.title()}. {teams_list} might perform better in these conditions. Want to switch your support?"
        else:
            reply = f"The current conditions in {city.title()} are {', '.join(conditions)},although this is not the best condition for {team}, but also no other team is good at this!"

    return jsonify({
        "fulfillment_response": {
            "messages": [{"text": {"text": [reply]}}]
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  #
