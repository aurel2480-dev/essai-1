from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import requests
import streamlit as st

# 1. Configuration de la page
st.set_page_config(
    page_title="Météo & Info Capitales",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. CSS Personnalisé (Fond blanc, cartes dynamiques, couleurs peps)
st.markdown(
    """
    <style>
    /* Fond principal blanc */
    .stApp {
        background-color: #FFFFFF !important;
        color: #1E293B;
    }
    
    /* Barre latérale dynamique */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 2px solid #F1F5F9;
    }

    /* Style des métriques */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        border-radius: 16px;
        padding: 16px;
        color: white !important;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
        transition: transform 0.2s ease-in-out;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
    }

    /* Textes des métriques en blanc */
    div[data-testid="stMetric"] label, 
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    /* Titres avec dégradé vif */
    .gradient-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF4500 0%, #FF8C00 50%, #4169E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .badge-weather {
        display: inline-block;
        background: #FFF7ED;
        color: #EA580C;
        border: 1px solid #FFEDD5;
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }

    .badge-tz {
        display: inline-block;
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #DBEAFE;
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 1.1rem;
        margin-bottom: 20px;
        margin-left: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Capitales avec coordonnées et identifiants de fuseaux horaires IANA
CAPITALES = {
    "Europe": {
        "Paris (France)": {
            "lat": 48.8566,
            "lon": 2.3522,
            "tz": "Europe/Paris",
        },
        "Berlin (Allemagne)": {
            "lat": 52.5200,
            "lon": 13.4050,
            "tz": "Europe/Berlin",
        },
        "Madrid (Espagne)": {
            "lat": 40.4168,
            "lon": -3.7038,
            "tz": "Europe/Madrid",
        },
        "Rome (Italie)": {"lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome"},
        "Londres (Royaume-Uni)": {
            "lat": 51.5074,
            "lon": -0.1278,
            "tz": "Europe/London",
        },
        "Bruxelles (Belgique)": {
            "lat": 50.8503,
            "lon": 4.3517,
            "tz": "Europe/Brussels",
        },
        "Lisbonne (Portugal)": {
            "lat": 38.7223,
            "lon": -9.1393,
            "tz": "Europe/Lisbon",
        },
        "Athènes (Grèce)": {
            "lat": 37.9838,
            "lon": 23.7275,
            "tz": "Europe/Athens",
        },
        "Varsovie (Pologne)": {
            "lat": 52.2297,
            "lon": 21.0122,
            "tz": "Europe/Warsaw",
        },
        "Vienne (Autriche)": {
            "lat": 48.2082,
            "lon": 16.3738,
            "tz": "Europe/Vienna",
        },
    },
    "Amérique": {
        "Ottawa (Canada)": {
            "lat": 45.4215,
            "lon": -75.6972,
            "tz": "America/Toronto",
        },
        "Washington D.C. (États-Unis)": {
            "lat": 38.9072,
            "lon": -77.0369,
            "tz": "America/New_York",
        },
        "Mexico (Mexique)": {
            "lat": 19.4326,
            "lon": -99.1332,
            "tz": "America/Mexico_City",
        },
        "Brasília (Brésil)": {
            "lat": -15.7975,
            "lon": -47.8919,
            "tz": "America/Sao_Paulo",
        },
        "Buenos Aires (Argentine)": {
            "lat": -34.6037,
            "lon": -58.3816,
            "tz": "America/Argentina/Buenos_Aires",
        },
        "Santiago (Chili)": {
            "lat": -33.4489,
            "lon": -70.6693,
            "tz": "America/Santiago",
        },
        "Bogota (Colombie)": {
            "lat": 4.7110,
            "lon": -74.0721,
            "tz": "America/Bogota",
        },
    },
    "Asie": {
        "Tokyo (Japon)": {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo"},
        "Pékin (Chine)": {"lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai"},
        "New Delhi (Inde)": {
            "lat": 28.6139,
            "lon": 77.2090,
            "tz": "Asia/Kolkata",
        },
        "Séoul (Corée du Sud)": {
            "lat": 37.5665,
            "lon": 126.9780,
            "tz": "Asia/Seoul",
        },
        "Bangkok (Thaïlande)": {
            "lat": 13.7563,
            "lon": 100.5018,
            "tz": "Asia/Bangkok",
        },
        "Riyad (Arabie Saoudite)": {
            "lat": 24.7136,
            "lon": 46.6753,
            "tz": "Asia/Riyadh",
        },
        "Jakarta (Indonésie)": {
            "lat": -6.2088,
            "lon": 106.8456,
            "tz": "Asia/Jakarta",
        },
    },
    "Afrique": {
        "Le Caire (Égypte)": {
            "lat": 30.0444,
            "lon": 31.2357,
            "tz": "Africa/Cairo",
        },
        "Rabat (Maroc)": {
            "lat": 34.0208,
            "lon": -6.8416,
            "tz": "Africa/Casablanca",
        },
        "Pretoria (Afrique du Sud)": {
            "lat": -25.7479,
            "lon": 28.2293,
            "tz": "Africa/Johannesburg",
        },
        "Nairobi (Kenya)": {
            "lat": -1.2921,
            "lon": 36.8219,
            "tz": "Africa/Nairobi",
        },
        "Dakar (Sénégal)": {
            "lat": 14.7167,
            "lon": -17.4677,
            "tz": "Africa/Dakar",
        },
        "Alger (Algérie)": {
            "lat": 36.7538,
            "lon": 3.0588,
            "tz": "Africa/Algiers",
        },
    },
    "Océanie": {
        "Canberra (Australie)": {
            "lat": -35.2809,
            "lon": 149.1300,
            "tz": "Australia/Sydney",
        },
        "Wellington (Nouvelle-Zélande)": {
            "lat": -41.2865,
            "lon": 174.7762,
            "tz": "Pacific/Auckland",
        },
        "Suva (Fidji)": {
            "lat": -18.1248,
            "lon": 178.4501,
            "tz": "Pacific/Fiji",
        },
    },
}

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
    80: "Averses de pluie 🌦️️",
    95: "Orage 🌩️",
}


def calculer_decalage_paris(tz_target_str):
  """Calcule l'heure locale et le décalage horaire par rapport à Paris"""
  now_utc = datetime.now(ZoneInfo("UTC"))
  heure_paris = now_utc.astimezone(ZoneInfo("Europe/Paris"))
  heure_cible = now_utc.astimezone(ZoneInfo(tz_target_str))

  # Différence en heures
  diff_seconds = (
      heure_cible.utcoffset() - heure_paris.utcoffset()
  ).total_seconds()
  diff_hours = int(diff_seconds / 3600)

  if diff_hours == 0:
    decalage_str = "Même heure qu'à Paris"
  elif diff_hours > 0:
    decalage_str = f"+{diff_hours}h par rapport à Paris"
  else:
    decalage_str = f"{diff_hours}h par rapport à Paris"

  return {
      "heure_locale": heure_cible.strftime("%H:%M"),
      "decalage_str": decalage_str,
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


# Navigation latérale
st.sidebar.title("🌍 Navigation")
continent = st.sidebar.selectbox("Continent", list(CAPITALES.keys()))
capitale_nom = st.sidebar.selectbox(
    "Capitale", list(CAPITALES[continent].keys())
)

coords = CAPITALES[continent][capitale_nom]
data = fetch_weather(coords["lat"], coords["lon"])

# Calcul du décalage horaire
info_horaire = calculer_decalage_paris(coords["tz"])

# Header principal
st.markdown(
    f'<h1 class="gradient-title">{capitale_nom}</h1>',
    unsafe_allow_html=True,
)

if data:
  current = data["current"]
  w_code = current.get("weather_code", 0)
  w_desc = WEATHER_CODES.get(w_code, "Inconnu")

  # Badges d'information (Météo + Heure / Décalage horaire)
  st.markdown(
      f"""
        <span class="badge-weather">{w_desc}</span>
        <span class="badge-tz">🕒 Heure locale : {info_horaire['heure_locale']} ({info_horaire['decalage_str']})</span>
    """,
      unsafe_allow_html=True,
  )

  # Métriques stylisées
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Température", f"{current['temperature_2m']} °C")
  col2.metric("Ressenti", f"{current['apparent_temperature']} °C")
  col3.metric("Humidité", f"{current['relative_humidity_2m']} %")
  col4.metric("Vent", f"{current['wind_speed_10m']} km/h")

  st.write("")
  st.write("")

  # Dispositions en colonnes
  col_left, col_right = st.columns([1, 1], gap="medium")

  with col_left:
    st.markdown("### 🗺️ Carte, Vue Satellite & Trafic")

    tab_sat, tab_traffic = st.tabs(["🛰️ Vue Satellite", "🚦 Trafic & Carte"])

    lat, lon = coords["lat"], coords["lon"]

    with tab_sat:
      # Satellite Google Maps
      url_sat = f"https://maps.google.com/maps?q={lat},{lon}&t=k&z=11&ie=UTF8&iwloc=&output=embed"
      st.components.v1.iframe(url_sat, height=350, scrolling=False)

    with tab_traffic:
      # Carte routière avec couche de trafic
      url_traffic = f"https://maps.google.com/maps?q={lat},{lon}&t=m&z=12&ie=UTF8&iwloc=&output=embed"
      st.components.v1.iframe(url_traffic, height=350, scrolling=False)

  with col_right:
    st.markdown("### 📈 Tendance Météo sur 24h")

    # Traitement des données horaires
    hourly_df = pd.DataFrame(data["hourly"])
    hourly_df["Heure"] = pd.to_datetime(hourly_df["time"]).dt.strftime("%H:%M")
    hourly_df = hourly_df.rename(columns={"temperature_2m": "Température (°C)"})

    # Graphique coloré
    st.line_chart(
        hourly_df.set_index("Heure")[["Température (°C)"]], color="#FF4500"
    )

else:
  st.error("Impossible de récupérer les données météo pour cette ville.")
