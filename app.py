import streamlit as st
import pandas as pd

st.title("🌍 Météo mondiale")

df = pd.DataFrame(weather_data)

st.dataframe(df)

csv = df.to_csv(index=False)

st.download_button(
    "Télécharger CSV",
    csv,
    "meteo_mondiale.csv",
    "text/csv"
)
