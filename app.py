from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import requests
import streamlit as st

# 1. Configuration de la page
st.set_page_config(
    page_title="Météo, Trafic, Webcams & Change",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Styles CSS personnalisés
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
        font-size: 1rem;
        margin-bottom: 15px;
    }

    .badge-tz {
        display: inline-block;
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #DBEAFE;
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 1rem;
        margin-bottom: 15px;
        margin-left: 8px;
    }

    .badge-currency {
        display: inline-block;
        background: #F0FDF4;
        color: #16A34A;
        border: 1px solid #DCFCE7;
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 1rem;
        margin-bottom: 15px;
        margin-left: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Liste des villes + webcam (Windy / EarthCam / Live Embed)
CAPITALES_ET_VILLES = {
    "Europe": {
        "Paris (France)": {
            "lat": 48.8566,
            "lon": 2.3522,
            "tz": "Europe/Paris",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": (
                "https://webcams.windy.com/webcams/stream/1518063080?autoplay=1"
            ),
        },
        "Marseille (France)": {
            "lat": 43.2965,
            "lon": 5.3698,
            "tz": "Europe/Paris",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1515228518",
        },
        "Lyon (France)": {
            "lat": 45.7640,
            "lon": 4.8357,
            "tz": "Europe/Paris",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1539201948",
        },
        "Berlin (Allemagne)": {
            "lat": 52.5200,
            "lon": 13.4050,
            "tz": "Europe/Berlin",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1352495536",
        },
        "Madrid (Espagne)": {
            "lat": 40.4168,
            "lon": -3.7038,
            "tz": "Europe/Madrid",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1512403681",
        },
        "Barcelone (Espagne)": {
            "lat": 41.3851,
            "lon": 2.1734,
            "tz": "Europe/Madrid",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1202888126",
        },
        "Rome (Italie)": {
            "lat": 41.9028,
            "lon": 12.4964,
            "tz": "Europe/Rome",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1283281577",
        },
        "Londres (Royaume-Uni)": {
            "lat": 51.5074,
            "lon": -0.1278,
            "tz": "Europe/London",
            "currency": "GBP",
            "currency_name": "Livre Sterling (£)",
            "webcam": "https://webcams.windy.com/webcams/stream/1453229605",
        },
        "Bruxelles (Belgique)": {
            "lat": 50.8503,
            "lon": 4.3517,
            "tz": "Europe/Brussels",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1512140652",
        },
        "Lisbonne (Portugal)": {
            "lat": 38.7223,
            "lon": -9.1393,
            "tz": "Europe/Lisbon",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518175510",
        },
        "Athènes (Grèce)": {
            "lat": 37.9838,
            "lon": 23.7275,
            "tz": "Europe/Athens",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1359815042",
        },
        "Varsovie (Pologne)": {
            "lat": 52.2297,
            "lon": 21.0122,
            "tz": "Europe/Warsaw",
            "currency": "PLN",
            "currency_name": "Zloty polonais (zł)",
            "webcam": "https://webcams.windy.com/webcams/stream/1501258600",
        },
        "Vienne (Autriche)": {
            "lat": 48.2082,
            "lon": 16.3738,
            "tz": "Europe/Vienna",
            "currency": "EUR",
            "currency_name": "Euro (€)",
            "webcam": "https://webcams.windy.com/webcams/stream/1360188049",
        },
        "Istanbul (Turquie)": {
            "lat": 41.0082,
            "lon": 28.9784,
            "tz": "Europe/Istanbul",
            "currency": "TRY",
            "currency_name": "Livre turque (₺)",
            "webcam": "https://webcams.windy.com/webcams/stream/1519548002",
        },
    },
    "Amérique": {
        "New York (États-Unis)": {
            "lat": 40.7128,
            "lon": -74.0060,
            "tz": "America/New_York",
            "currency": "USD",
            "currency_name": "Dollar US ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1514800109",
        },
        "Los Angeles (États-Unis)": {
            "lat": 34.0522,
            "lon": -118.2437,
            "tz": "America/Los_Angeles",
            "currency": "USD",
            "currency_name": "Dollar US ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1392817812",
        },
        "Chicago (États-Unis)": {
            "lat": 41.8781,
            "lon": -87.6298,
            "tz": "America/Chicago",
            "currency": "USD",
            "currency_name": "Dollar US ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1523306801",
        },
        "Toronto (Canada)": {
            "lat": 43.6532,
            "lon": -79.3832,
            "tz": "America/Toronto",
            "currency": "CAD",
            "currency_name": "Dollar canadien ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1516082001",
        },
        "Montréal (Canada)": {
            "lat": 45.5017,
            "lon": -73.5673,
            "tz": "America/Toronto",
            "currency": "CAD",
            "currency_name": "Dollar canadien ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1516081995",
        },
        "Mexico (Mexique)": {
            "lat": 19.4326,
            "lon": -99.1332,
            "tz": "America/Mexico_City",
            "currency": "MXN",
            "currency_name": "Peso mexicain ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1517551000",
        },
        "Rio de Janeiro (Brésil)": {
            "lat": -22.9068,
            "lon": -43.1729,
            "tz": "America/Sao_Paulo",
            "currency": "BRL",
            "currency_name": "Real brésilien (R$)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518055101",
        },
        "Buenos Aires (Argentine)": {
            "lat": -34.6037,
            "lon": -58.3816,
            "tz": "America/Argentina/Buenos_Aires",
            "currency": "ARS",
            "currency_name": "Peso argentin ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518055200",
        },
    },
    "Asie": {
        "Tokyo (Japon)": {
            "lat": 35.6762,
            "lon": 139.6503,
            "tz": "Asia/Tokyo",
            "currency": "JPY",
            "currency_name": "Yen japonais (¥)",
            "webcam": "https://webcams.windy.com/webcams/stream/1454556002",
        },
        "Hong Kong (Chine)": {
            "lat": 22.3193,
            "lon": 114.1694,
            "tz": "Asia/Hong_Kong",
            "currency": "HKD",
            "currency_name": "Dollar de Hong Kong ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518000100",
        },
        "Bangkok (Thaïlande)": {
            "lat": 13.7563,
            "lon": 100.5018,
            "tz": "Asia/Bangkok",
            "currency": "THB",
            "currency_name": "Baht thaïlandais (฿)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518012010",
        },
        "Dubaï (Émirats Arabes Unis)": {
            "lat": 25.2048,
            "lon": 55.2708,
            "tz": "Asia/Dubai",
            "currency": "AED",
            "currency_name": "Dirham des EAU (AED)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518099000",
        },
    },
    "Afrique": {
        "Le Caire (Égypte)": {
            "lat": 30.0444,
            "lon": 31.2357,
            "tz": "Africa/Cairo",
            "currency": "EGP",
            "currency_name": "Livre égyptienne (E£)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518100200",
        },
        "Casablanca (Maroc)": {
            "lat": 33.5731,
            "lon": -7.5898,
            "tz": "Africa/Casablanca",
            "currency": "MAD",
            "currency_name": "Dirham marocain (DH)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518100300",
        },
        "Johannesburg (Afrique du Sud)": {
            "lat": -26.2041,
            "lon": 28.0473,
            "tz": "Africa/Johannesburg",
            "currency": "ZAR",
            "currency_name": "Rand sud-africain (R)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518100400",
        },
    },
    "Océanie": {
        "Sydney (Australie)": {
            "lat": -33.8688,
            "lon": 151.2093,
            "tz": "Australia/Sydney",
            "currency": "AUD",
            "currency_name": "Dollar australien ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1392817800",
        },
        "Auckland (Nouvelle-Zélande)": {
            "lat": -36.8485,
            "lon": 174.7633,
            "tz": "Pacific/Auckland",
            "currency": "NZD",
            "currency_name": "Dollar néo-zélandais ($)",
            "webcam": "https://webcams.windy.com/webcams/stream/1518111000",
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


@st.cache_data(ttl=3600)
def fetch_exchange_rate(target_currency):
  if target_currency == "EUR":
    return 1.0

  url = "https://open.er-api.com/v6/latest/EUR"
  try:
    response = requests.get(url)
    if response.status_code == 200:
      rates = response.json().get("rates", {})
      return rates.get(target_currency, None)
  except Exception:
    pass
  return None


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
taux_change = fetch_exchange_rate(coords["currency"])

st.markdown(
    f'<h1 class="gradient-title">{capitale_nom}</h1>',
    unsafe_allow_html=True,
)

if data:
  current = data["current"]
  w_code = current.get("weather_code", 0)
  w_desc = WEATHER_CODES.get(w_code, "Inconnu")

  if coords["currency"] == "EUR":
    currency_str = "💶 Monnaie : Euro (€)"
  elif taux_change:
    currency_str = f"💱 1 EUR = {taux_change:.2f} {coords['currency']} ({coords['currency_name']})"
  else:
    currency_str = f"💱 Monnaie : {coords['currency_name']}"

  # Badges
  st.markdown(
      f"""
        <span class="badge-weather">{w_desc}</span>
        <span class="badge-tz">🕒 Heure locale : {info_horaire['heure_locale']} ({info_horaire['decalage_str']})</span>
        <span class="badge-currency">{currency_str}</span>
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
    st.markdown("### 🚦 Trafic, Cartes & Webcams Live")

    tab_traffic, tab_sat, tab_webcam = st.tabs(
        ["🚦 Carte & Trafic", "🛰️ Vue Satellite", "🎥 Webcam Direct"]
    )

    lat, lon = coords["lat"], coords["lon"]

    with tab_traffic:
      url_traffic = f"https://maps.google.com/maps?q={lat},{lon}&t=m&z=12&layer=t&ie=UTF8&iwloc=&output=embed"
      st.components.v1.iframe(url_traffic, height=380, scrolling=False)

    with tab_sat:
      url_sat = f"https://maps.google.com/maps?q={lat},{lon}&t=k&z=12&ie=UTF8&iwloc=&output=embed"
      st.components.v1.iframe(url_sat, height=380, scrolling=False)

    with tab_webcam:
      webcam_url = coords.get("webcam")
      if webcam_url:
        st.components.v1.iframe(webcam_url, height=380, scrolling=False)
      else:
        st.info("Webcam en direct non disponible pour cette ville.")

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
