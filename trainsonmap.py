import streamlit as st
import requests
import pandas as pd
from streamlit_folium import folium_static
import folium

st.title("Train locations on map")

st.write("The API returns the latest location information for trains on the map in Finland")

url = "https://rata.digitraffic.fi/api/v1/train-locations.geojson/latest/"
response = requests.get(url)
data = response.json()


df = pd.json_normalize(data["features"])


# Loop through the train numbers in the DataFrame and get the metadata for each train from the API
metadata = []
for train_number in df["properties.trainNumber"].unique():
    metadata_url = f"https://rata.digitraffic.fi/api/v1/trains/latest/{train_number}"
    metadata_response = requests.get(metadata_url)
    metadata_data = metadata_response.json()
    metadata_dict = metadata_data[0] if isinstance(metadata_data, list) and len(metadata_data) > 0 else {}
    metadata.append({
        "trainNumber": metadata_dict.get("trainNumber", ""),
        "operatorShortCode": metadata_dict.get("operatorShortCode", ""),
        "trainType": metadata_dict.get("trainType", ""),
        "trainCategory": metadata_dict.get("trainCategory", "")
    })

# Create a DataFrame from the metadata
metadata_df = pd.json_normalize(metadata)


# Merge the metadata DataFrame with the train locations DataFrame
merged_df = pd.merge(df, metadata_df, left_on="properties.trainNumber", right_on="trainNumber")

# Create a map centered on the first geo point
m = folium.Map(location=[merged_df.iloc[0]["geometry.coordinates"][1], merged_df.iloc[0]["geometry.coordinates"][0]], zoom_start=5)

# Add markers for each geo point
for index, row in merged_df.iterrows():
    folium.Marker(location=[row["geometry.coordinates"][1], row["geometry.coordinates"][0]], 
                  popup=f"Train number: {row['properties.trainNumber']}\nSpeed: {row['properties.speed']} km/h\nOperator: {row['operatorShortCode']}\nTrain type: {row['trainType']}\nTrain category: {row['trainCategory']}").add_to(m)

# Display the map
folium_static(m)

# Display the DataFrame
st.write("Raw data")
st.write(merged_df)


st.write("Data used: https://rata.digitraffic.fi/api/v1/train-locations.geojson/latest/ , Train metadata: https://rata.digitraffic.fi/api/v1/trains/latest/")