import pandas as pd
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Météo des Capitales", page_icon="🌍", layout="wide"
)

# Capitales du monde avec coordonnées géographiques
CAPITALES = {
    "Europe": {
        "Paris (France)": {"lat": 48.8566, "lon": 2.3522},
        "Berlin (Allemagne)": {"lat": 52.5200, "lon": 13.4050},
        "Madrid (Espagne)": {"lat": 40.4168, "lon": -3.7038},
        "Rome (Italie)": {"lat": 41.9028, "lon": 12.4964},
        "Londres (Royaume-Uni)": {"lat": 51.5074, "lon": -0.1278},
        "Bruxelles (Belgique)": {"lat": 50.8503, "lon": 4.3517},
        "Lisbonne (Portugal)": {"lat": 38.7223, "lon": -9.1393},
        "Athènes (Grèce)": {"lat": 37.9838, "lon": 23.7275},
        "Varsovie (Pologne)": {"lat": 52.2297, "lon": 21.0122},
        "Vienne (Autriche)": {"lat": 48.2082, "lon": 16.3738},
    },
    "Amérique": {
        "Ottawa (Canada)": {"lat": 45.4215, "lon": -75.6972},
        "Washington D.C. (États-Unis)": {"lat": 38.9072, "lon": -77.0369},
        "Mexico (Mexique)": {"lat": 19.4326, "lon": -99.1332},
        "Brasília (Brésil)": {"lat": -15.7975, "lon": -47.8919},
        "Buenos Aires (Argentine)": {"lat": -34.6037, "lon": -58.3816},
        "Santiago (Chili)": {"lat": -33.4489, "lon": -70.6693},
        "Bogota (Colombie)": {"lat": 4.7110, "lon": -74.0721},
    },
    "Asie": {
        "Tokyo (Japon)": {"lat": 35.6762, "lon": 139.6503},
        "Pékin (Chine)": {"lat": 39.9042, "lon": 116.4074},
        "New Delhi (Inde)": {"lat": 28.6139, "lon": 77.2090},
        "Séoul (Corée du Sud)": {"lat": 37.5665, "lon": 126.9780},
        "Bangkok (Thaïlande)": {"lat": 13.7563, "lon": 100.5018},
        "Riyad (Arabie Saoudite)": {"lat": 24.7136, "lon": 46.6753},
        "Jakarta (Indonésie)": {"lat": -6.2088, "lon": 106.8456},
    },
    "Afrique": {
        "Le Caire (Égypte)": {"lat": 30.0444, "lon": 31.2357},
        "Rabat (Maroc)": {"lat": 34.0208, "lon": -6.8416},
        "Pretoria (Afrique du Sud)": {"lat": -25.7479, "lon": 28.2293},
        "Nairobi (Kenya)": {"lat": -1.2921, "lon": 36.8219},
        "Dakar (Sénégal)": {"lat": 14.7167, "lon": -17.4677},
        "Alger (Algérie)": {"lat": 36.7538, "lon": 3.0588},
    },
    "Océanie": {
        "Canberra (Australie)": {"lat": -35.2809, "lon": 149.1300},
        "Wellington (Nouvelle-Zélande)": {"lat": -41.2865, "lon": 174.7762},
        "Suva (Fidji)": {"lat": -18.1248, "lon": 178.4501},
    },
}

# Codes météo Open-Meteo vers descriptions en français
WEATHER_CODES = {
    0: "Ciel dégagé ☀️",
    1: "Principalement dégagé 🌤️",
    2: "Partiellement nuageux ⛅",
    3: "Couvert ☁️",
    45: "Brouillard 🌫️",
    48: "Brouillard givrant 🌫️",
    51: "Bruine légère 🌦️",
    53: "Bruine modérée 🌦️",
    55: "Bruine dense 🌧️",
    61: "Pluie faible 🌧️",
    63: "Pluie modérée 🌧️",
    65: "Pluie forte 🌧️",
    71: "Neige faible 🌨️",
    73: "Neige modérée 🌨️",
    75: "Neige forte 🌨️",
    80: "Averses de pluie 🌦️",
    95: "Orage 🌩️",
}


@st.cache_data(ttl=600)
def fetch_weather(lat, lon):
  url = "https://api.open-meteo.com/v1/forecast"
  params = {
      "latitude": lat,
      "longitude": lon,
      "current": [
          "temperature_2m",
          "relative_humidity_2m",
          "apparent_temperature",
          "precipitation",
          "weather_code",
          "wind_speed_10m",
      ],
      "hourly": ["temperature_2m"],
      "forecast_days": 1,
  }
  response = requests.get(url, params=params)
  return response.json() if response.status_code == 200 else None


# Interface
st.title("🌍 Météo des Capitales du Monde")

# Barre latérale - Filtres
st.sidebar.header("Navigation")
continent = st.sidebar.selectbox("Choisir un continent", list(CAPITALES.keys()))
capitale_nom = st.sidebar.selectbox(
    "Choisir une capitale", list(CAPITALES[continent].keys())
)

coords = CAPITALES[continent][capitale_nom]
data = fetch_weather(coords["lat"], coords["lon"])

if data:
  current = data["current"]
  w_code = current.get("weather_code", 0)
  w_desc = WEATHER_CODES.get(w_code, "Inconnu")

  st.subheader(f"Météo actuelle à **{capitale_nom}** : {w_desc}")

  # Indicateurs clés
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Température", f"{current['temperature_2m']} °C")
  col2.metric("Ressenti", f"{current['apparent_temperature']} °C")
  col3.metric("Humidité", f"{current['relative_humidity_2m']} %")
  col4.metric("Vent", f"{current['wind_speed_10m']} km/h")

  st.markdown("---")

  col_left, col_right = st.columns(2)

  with col_left:
    st.write("### 📍 Localisation")
    map_data = pd.DataFrame({"lat": [coords["lat"]], "lon": [coords["lon"]]})
    st.map(map_data, zoom=6)

  with col_right:
    st.write("### 📈 Prévisions sur 24 heures (°C)")

    # Modification apportée ici pour corriger l'erreur :
    hourly_df = pd.DataFrame(data["hourly"])
    hourly_df["Heure"] = pd.to_datetime(hourly_df["time"]).dt.strftime("%H:%M")
    hourly_df = hourly_df.rename(columns={"temperature_2m": "Température (°C)"})

    st.line_chart(hourly_df.set_index("Heure")[["Température (°C)"]])

else:
  st.error("Impossible de récupérer les données météo pour cette ville.")
