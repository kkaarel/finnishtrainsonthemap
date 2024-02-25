import streamlit as st
import requests
import pandas as pd
from streamlit_folium import folium_static
import folium

st.title("Train locations on the map")

st.write("The API returns the latest location information for trains on the map in Finland")
#geo location
url = "https://rata.digitraffic.fi/api/v1/train-locations.geojson/latest/"
response = requests.get(url)
data = response.json()

#trains
url_trains = "https://rata.digitraffic.fi/api/v1/live-trains"
response = requests.get(url_trains)
data_trains = response.json()

df_trains = pd.json_normalize(data_trains)


df = pd.json_normalize(data["features"])

df_merged = pd.merge(df, df_trains, left_on="properties.trainNumber", right_on="trainNumber")

# Create a map centered on the first geo point
m = folium.Map(location=[df_merged.iloc[0]["geometry.coordinates"][1], df_merged.iloc[0]["geometry.coordinates"][0]], zoom_start=5)

# Add markers for each geo point
for index, row in df_merged.iterrows():
    folium.Marker(location=[row["geometry.coordinates"][1], row["geometry.coordinates"][0]], 
                  popup=f"Train number: {row['properties.trainNumber']}\nSpeed: {row['properties.speed']} km/h\nOperator: {row['operatorShortCode']}\nTrain type: {row['trainType']}\nTrain category: {row['trainCategory']}").add_to(m)

# Display the map
folium_static(m)

# Display the DataFrame
st.write("Raw data")
st.write(df_merged)

st.write("[Fintraffic’s Creative Commons 4.0 By license](https://www.digitraffic.fi/en/terms-of-service/)")
st.write("Data used: https://rata.digitraffic.fi/api/v1/train-locations.geojson/latest/ , Train metadata: https://rata.digitraffic.fi/api/v1/trains/latest/")

st.write("[Developed by Kaarel Kõrvemaa](https://www.kkaarel.com)")