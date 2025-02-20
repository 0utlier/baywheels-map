import streamlit as st
import folium
import requests
from geopy.distance import geodesic
from streamlit_folium import folium_static

# Define Bay Wheels GBFS endpoints
STATION_INFO_URL = "https://gbfs.baywheels.com/gbfs/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.baywheels.com/gbfs/en/station_status.json"

ZIP_94110_COORDS = (37.7599, -122.4148)

def fetch_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_ebike_only_stations():
    station_info = fetch_data(STATION_INFO_URL)["data"]["stations"]
    station_status = fetch_data(STATION_STATUS_URL)["data"]["stations"]
    status_dict = {s["station_id"]: s for s in station_status}

    eligible_stations = []
    for station in station_info:
        station_id = station["station_id"]
        if station_id in status_dict:
            num_ebikes = status_dict[station_id]["num_ebikes_available"]
            num_classic_bikes = status_dict[station_id]["num_bikes_available"] - num_ebikes

            if num_ebikes > 0 and num_classic_bikes == 0:
                distance = geodesic(ZIP_94110_COORDS, (station["lat"], station["lon"])).miles
                eligible_stations.append({
                    "name": station["name"],
                    "lat": station["lat"],
                    "lon": station["lon"],
                    "num_ebikes": num_ebikes,
                    "distance": distance
                })

    eligible_stations.sort(key=lambda x: x["distance"])
    return eligible_stations[:20]

def create_map():
    stations = get_ebike_only_stations()
    m = folium.Map(location=ZIP_94110_COORDS, zoom_start=13)

    for station in stations:
        folium.Marker(
            location=(station["lat"], station["lon"]),
            popup=f"{station['name']} ({station['num_ebikes']} e-bikes)",
            icon=folium.Icon(color='blue', icon='bicycle', prefix='fa')
        ).add_to(m)

    return m

st.title("Bay Wheels E-Bike Availability Map")
st.write("Showing stations with only e-bikes available near 94110.")

folium_map = create_map()
folium_static(folium_map)
