import requests
import pandas as pd
import time

API_KEY = "VOTRE_CLE_API"

# Liste des principales capitales mondiales
capitals = {
    "France": "Paris",
    "Germany": "Berlin",
    "United Kingdom": "London",
    "Spain": "Madrid",
    "Italy": "Rome",
    "USA": "Washington",
    "Canada": "Ottawa",
    "Brazil": "Brasilia",
    "Argentina": "Buenos Aires",
    "Mexico": "Mexico City",
    "China": "Beijing",
    "Japan": "Tokyo",
    "India": "New Delhi",
    "Russia": "Moscow",
    "Australia": "Canberra",
    "South Africa": "Pretoria",
    "Egypt": "Cairo",
    "Turkey": "Ankara",
    "Saudi Arabia": "Riyadh",
    "Indonesia": "Jakarta"
}

def get_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric&lang=fr"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code == 200:
            return {
                "Ville": city,
                "Température (°C)": data["main"]["temp"],
                "Ressenti (°C)": data["main"]["feels_like"],
                "Humidité (%)": data["main"]["humidity"],
                "Description": data["weather"][0]["description"],
                "Vent (km/h)": round(data["wind"]["speed"] * 3.6, 1)
            }
        else:
            return {"Ville": city, "Erreur": data.get("message", "Erreur API")}

    except Exception as e:
        return {"Ville": city, "Erreur": str(e)}

def display_weather():
    weather_data = []

    for country, capital in capitals.items():
        print(f"Lecture météo : {capital}")
        weather_data.append(get_weather(capital))

    df = pd.DataFrame(weather_data)

    print("\n=== METEO MONDIALE ===")
    print(df)

    df.to_excel("meteo_mondiale.xlsx", index=False)
    print("\nFichier exporté : meteo_mondiale.xlsx")

if __name__ == "__main__":
    display_weather()
