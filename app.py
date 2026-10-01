from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import requests
import streamlit as st

# 1. Configuration de la page
st.set_page_config(
    page_title="Météo, Trafic & Heures du Monde",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Styles CSS personnalisés (Fond blanc, cartes dynamiques, couleurs peps)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF !important;
        color: #1E293B;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 2px solid #F1F5F9;
    }

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

    div[data-testid="stMetric"] label, 
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

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

# Liste des capitales et métropoles de +1 million d'habitants avec coordonnées et fuseaux IANA
CAPITALES_ET_VILLES = {
    "Europe": {
        "Paris (France)": {
            "lat": 48.8566,
            "lon": 2.3522,
            "tz": "Europe/Paris",
        },
        "Marseille (France)": {
            "lat": 43.2965,
            "lon": 5.3698,
            "tz": "Europe/Paris",
        },
        "Lyon (France)": {"lat": 45.7640, "lon": 4.8357, "tz": "Europe/Paris"},
        "Berlin (Allemagne)": {
            "lat": 52.5200,
            "lon": 13.4050,
            "tz": "Europe/Berlin",
        },
        "Hambourg (Allemagne)": {
            "lat": 53.5511,
            "lon": 9.9937,
            "tz": "Europe/Berlin",
        },
        "Munich (Allemagne)": {
            "lat": 48.1351,
            "lon": 11.5820,
            "tz": "Europe/Berlin",
        },
        "Cologne (Allemagne)": {
            "lat": 50.9375,
            "lon": 6.9603,
            "tz": "Europe/Berlin",
        },
        "Madrid (Espagne)": {
            "lat": 40.4168,
            "lon": -3.7038,
            "tz": "Europe/Madrid",
        },
        "Barcelone (Espagne)": {
            "lat": 41.3851,
            "lon": 2.1734,
            "tz": "Europe/Madrid",
        },
        "Rome (Italie)": {"lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome"},
        "Milan (Italie)": {"lat": 45.4642, "lon": 9.1900, "tz": "Europe/Rome"},
        "Londres (Royaume-Uni)": {
            "lat": 51.5074,
            "lon": -0.1278,
            "tz": "Europe/London",
        },
        "Birmingham (Royaume-Uni)": {
            "lat": 52.4862,
            "lon": -1.8904,
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
        "Istanbul (Turquie)": {
            "lat": 41.0082,
            "lon": 28.9784,
            "tz": "Europe/Istanbul",
        },
        "Moscou (Russie)": {
            "lat": 55.7558,
            "lon": 37.6173,
            "tz": "Europe/Moscow",
        },
        "Saint-Pétersbourg (Russie)": {
            "lat": 59.9343,
            "lon": 30.3351,
            "tz": "Europe/Moscow",
        },
    },
    "Amérique": {
        "New York (États-Unis)": {
            "lat": 40.7128,
            "lon": -74.0060,
            "tz": "America/New_York",
        },
        "Los Angeles (États-Unis)": {
            "lat": 34.0522,
            "lon": -118.2437,
            "tz": "America/Los_Angeles",
        },
        "Chicago (États-Unis)": {
            "lat": 41.8781,
            "lon": -87.6298,
            "tz": "America/Chicago",
        },
        "Houston (États-Unis)": {
            "lat": 29.7604,
            "lon": -95.3698,
            "tz": "America/Chicago",
        },
        "Phoenix (États-Unis)": {
            "lat": 33.4484,
            "lon": -112.0740,
            "tz": "America/Phoenix",
        },
        "Washington D.C. (États-Unis)": {
            "lat": 38.9072,
            "lon": -77.0369,
            "tz": "America/New_York",
        },
        "Toronto (Canada)": {
            "lat": 43.6532,
            "lon": -79.3832,
            "tz": "America/Toronto",
        },
        "Montréal (Canada)": {
            "lat": 45.5017,
            "lon": -73.5673,
            "tz": "America/Toronto",
        },
        "Ottawa (Canada)": {
            "lat": 45.4215,
            "lon": -75.6972,
            "tz": "America/Toronto",
        },
        "Mexico (Mexique)": {
            "lat": 19.4326,
            "lon": -99.1332,
            "tz": "America/Mexico_City",
        },
        "Guadalajara (Mexique)": {
            "lat": 20.6597,
            "lon": -103.3496,
            "tz": "America/Mexico_City",
        },
        "Monterrey (Mexique)": {
            "lat": 25.6866,
            "lon": -100.3161,
            "tz": "America/Monterrey",
        },
        "São Paulo (Brésil)": {
            "lat": -23.5505,
            "lon": -46.6333,
            "tz": "America/Sao_Paulo",
        },
        "Rio de Janeiro (Brésil)": {
            "lat": -22.9068,
            "lon": -43.1729,
            "tz": "America/Sao_Paulo",
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
        "Lima (Pérou)": {"lat": -12.0464, "lon": -77.0428, "tz": "America/Lima"},
        "Caracas (Venezuela)": {
            "lat": 10.4806,
            "lon": -66.9036,
            "tz": "America/Caracas",
        },
    },
    "Asie": {
        "Tokyo (Japon)": {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo"},
        "Osaka (Japon)": {"lat": 34.6937, "lon": 135.5023, "tz": "Asia/Tokyo"},
        "Pékin (Chine)": {"lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai"},
        "Shanghai (Chine)": {
            "lat": 31.2304,
            "lon": 121.4737,
            "tz": "Asia/Shanghai",
        },
        "Shenzhen (Chine)": {
            "lat": 22.5431,
            "lon": 114.0579,
            "tz": "Asia/Shanghai",
        },
        "Guangzhou (Chine)": {
            "lat": 23.1291,
            "lon": 113.2644,
            "tz": "Asia/Shanghai",
        },
        "Hong Kong (Chine)": {
            "lat": 22.3193,
            "lon": 114.1694,
            "tz": "Asia/Hong_Kong",
        },
        "Mumbai (Inde)": {"lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata"},
        "Delhi (Inde)": {"lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata"},
        "Bangalore (Inde)": {
            "lat": 12.9716,
            "lon": 77.5946,
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
        "Jakarta (Indonésie)": {
            "lat": -6.2088,
            "lon": 106.8456,
            "tz": "Asia/Jakarta",
        },
        "Manille (Philippines)": {
            "lat": 14.5995,
            "lon": 120.9842,
            "tz": "Asia/Manila",
        },
        "Hô Chi Minh-Ville (Vietnam)": {
            "lat": 10.8231,
            "lon": 106.6297,
            "tz": "Asia/Ho_Chi_Minh",
        },
        "Riyad (Arabie Saoudite)": {
            "lat": 24.7136,
            "lon": 46.6753,
            "tz": "Asia/Riyadh",
        },
        "Dubaï (Émirats Arabes Unis)": {
            "lat": 25.2048,
            "lon": 55.2708,
            "tz": "Asia/Dubai",
        },
        "Téhéran (Iran)": {"lat": 35.6892, "lon": 51.3890, "tz": "Asia/Tehran"},
        "Bagdad (Irak)": {"lat": 33.3152, "lon": 44.3661, "tz": "Asia/Baghdad"},
    },
    "Afrique": {
        "Le Caire (Égypte)": {
            "lat": 30.0444,
            "lon": 31.2357,
            "tz": "Africa/Cairo",
        },
        "Alexandrie (Égypte)": {
            "lat": 31.2001,
            "lon": 29.9187,
            "tz": "Africa/Cairo",
        },
        "Casablanca (Maroc)": {
            "lat": 33.5731,
            "lon": -7.5898,
            "tz": "Africa/Casablanca",
        },
        "Rabat (Maroc)": {
            "lat": 34.0208,
            "lon": -6.8416,
            "tz": "Africa/Casablanca",
        },
        "Alger (Algérie)": {
            "lat": 36.7538,
            "lon": 3.0588,
            "tz": "Africa/Algiers",
        },
        "Tunis (Tunisie)": {
            "lat": 36.8065,
            "lon": 10.1815,
            "tz": "Africa/Tunis",
        },
        "Lagos (Nigeria)": {
            "lat": 6.5244,
            "lon": 3.3792,
            "tz": "Africa/Lagos",
        },
        "Kinshasa (RD Congo)": {
            "lat": -4.4419,
            "lon": 15.2663,
            "tz": "Africa/Kinshasa",
        },
        "Johannesburg (Afrique du Sud)": {
            "lat": -26.2041,
            "lon": 28.0473,
            "tz": "Africa/Johannesburg",
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
        "Abidjan (Côte d'Ivoire)": {
            "lat": 5.3600,
            "lon": -4.0083,
            "tz": "Africa/Abidjan",
        },
        "Douala (Cameroun)": {
            "lat": 4.0511,
            "lon": 9.7679,
            "tz": "Africa/Douala",
        },
        "Yaoundé (Cameroun)": {
            "lat": 3.8480,
            "lon": 11.5021,
            "tz": "Africa/Douala",
        },
    },
    "Océanie": {
        "Sydney (Australie)": {
            "lat": -33.8688,
            "lon": 151.2093,
            "tz": "Australia/Sydney",
        },
        "Melbourne (Australie)": {
            "lat": -37.8136,
            "lon": 144.9631,
            "tz": "Australia/Melbourne",
        },
        "Brisbane (Australie)": {
            "lat": -27.4705,
            "lon": 153.0260,
            "tz": "Australia/Brisbane",
        },
        "Perth (Australie)": {
            "lat": -31.9505,
            "lon": 115.8605,
            "tz": "Australia/Perth",
        },
        "Canberra (Australie)": {
            "lat": -35.2809,
            "lon": 149.1300,
            "tz": "Australia/Sydney",
        },
        "Auckland (Nouvelle-Zélande)": {
            "lat": -36.8485,
            "lon": 174.7633,
            "tz": "Pacific/Auckland",
        },
        "Wellington (Nouvelle-Zélande)": {
            "lat": -41.2865,
            "lon": 174.7762,
            "tz": "Pacific/Auckland",
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
    80: "Averses de pluie 🌦️",
    95: "Orage 🌩️",
}


def calculer_decalage_paris(tz_target_str):
  now_utc = datetime.now(ZoneInfo("UTC"))
  heure_paris = now_utc.astimezone(ZoneInfo("Europe/Paris"))
  heure_cible = now_utc.astimezone(ZoneInfo(tz_target_str))

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
continent = st.sidebar.selectbox("Continent", list(CAPITALES_ET_VILLES.keys()))
capitale_nom = st.sidebar.selectbox(
    "Ville / Capitale (+1M hab.)",
    list(CAPITALES_ET_VILLES[continent].keys()),
)

coords = CAPITALES_ET_VILLES[continent][capitale_nom]
data = fetch_weather(coords["lat"], coords["lon"])

info_horaire = calculer_decalage_paris(coords["tz"])

st.markdown(
    f'<h1 class="gradient-title">{capitale_nom}</h1>',
    unsafe_allow_html=True,
)

if data:
  current = data["current"]
  w_code = current.get("weather_code", 0)
  w_desc = WEATHER_CODES.get(w_code, "Inconnu")

  # Badges
  st.markdown(
      f"""
        <span class="badge-weather">{w_desc}</span>
        <span class="badge-tz">🕒 Heure locale : {info_horaire['heure_locale']} ({info_horaire['decalage_str']})</span>
    """,
      unsafe_allow_html=True,
  )

  # Métriques
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Température", f"{current['temperature_2m']} °C")
  col2.metric("Ressenti", f"{current['apparent_temperature']} °C")
  col3.metric("Humidité", f"{current['relative_humidity_2m']} %")
  col4.metric("Vent", f"{current['wind_speed_10m']} km/h")

  st.write("")
  st.write("")

  col_left, col_right = st.columns([1, 1], gap="medium")

  with col_left:
    st.markdown("### 🚦 Trafic & Cartes en Temps Réel")

    tab_traffic, tab_sat = st.tabs(
        ["🚦 Carte & Trafic Direct", "🛰️ Vue Satellite"]
    )

    lat, lon = coords["lat"], coords["lon"]

    with tab_traffic:
      # Vue Carte avec couche de trafic
      url_traffic = f"https://maps.google.com/maps?q={lat},{lon}&t=m&z=12&layer=t&ie=UTF8&iwloc=&output=embed"
      st.components.v1.iframe(url_traffic, height=380, scrolling=False)

    with tab_sat:
      # Vue Satellite
      url_sat = f"https://maps.google.com/maps?q={lat},{lon}&t=k&z=12&ie=UTF8&iwloc=&output=embed"
      st.components.v1.iframe(url_sat, height=380, scrolling=False)

  with col_right:
    st.markdown("### 📈 Tendance Météo sur 24h")

    hourly_df = pd.DataFrame(data["hourly"])
    hourly_df["Heure"] = pd.to_datetime(hourly_df["time"]).dt.strftime("%H:%M")
    hourly_df = hourly_df.rename(columns={"temperature_2m": "Température (°C)"})

    st.line_chart(
        hourly_df.set_index("Heure")[["Température (°C)"]], color="#FF4500"
    )

else:
  st.error("Impossible de récupérer les données météo pour cette ville.")
