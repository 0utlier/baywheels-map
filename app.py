import folium
import pandas as pd
import pydeck as pdk
import requests
import streamlit as st

from geopy.distance import geodesic
from streamlit_folium import folium_static

# Define Bay Wheels GBFS endpoints
STATION_INFO_URL = "https://gbfs.baywheels.com/gbfs/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.baywheels.com/gbfs/en/station_status.json"
CLASSIC_BIKE_COUNT = 0

def fetch_data(url):
    """Fetch JSON data from the given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_ebike_only_stations(user_coords, classic_count):
    """Fetch and filter stations that only have e-bikes available."""
    station_info = fetch_data(STATION_INFO_URL)["data"]["stations"]
    station_status = fetch_data(STATION_STATUS_URL)["data"]["stations"]
    status_dict = {s["station_id"]: s for s in station_status}

    classic_count = CLASSIC_BIKE_COUNT % 2
    
    eligible_stations = []
    for station in station_info:
        station_id = station["station_id"]
        if station_id in status_dict:
            num_ebikes = status_dict[station_id]["num_ebikes_available"]
            num_classic_bikes = status_dict[station_id]["num_bikes_available"] - num_ebikes
            
    if num_ebikes > 0 and num_classic == classic_count:
        # Count black style bikes (name length == 7) near this station
        count_black = 0
        station_coords = (station["lat"], station["lon"])
        for bike in free_bikes:
            if "name" in bike and len(bike["name"]) == 7:
                bike_coords = (bike["lat"], bike["lon"])
                # Consider it docked here if within ~10 meters
                if geodesic(station_coords, bike_coords).meters < 10:
                    count_black += 1

            distance = geodesic(user_coords, (station["lat"], station["lon"])).miles
            eligible_stations.append({
                "name": station["name"],
                "lat": station["lat"],
                "lon": station["lon"],
                "num_ebikes": num_ebikes,
                "distance": distance,
                "count_black": count_black
            })
    
    eligible_stations.sort(key=lambda x: x["distance"])
    return eligible_stations

def create_map(user_coords, classic_count):
    """Generate a Folium map with e-bike-only station markers."""
    stations = get_ebike_only_stations(user_coords, classic_count)
    m = folium.Map(location=user_coords, zoom_start=14, control_scale=True)
    
    for station in stations:
        classic_bikes_string = ""
        if classic_count % 2 != 0:
            classic_bikes_string = " + 1 classic"
        folium.Marker(
            location=(station["lat"], station["lon"]),
            popup=folium.Popup(f"{station['name']}<br>({station['num_ebikes']} e-bikes{classic_bikes_string})<br>{station['count_black']} black bikes", max_width=300),
            icon=folium.Icon(color='blue', icon='bicycle', prefix='fa')
        ).add_to(m)
    
    locate_control = folium.plugins.LocateControl(auto_start=True, flyTo=True, keepCurrentZoomLevel=True)
    m.add_child(locate_control)
    
    return m


# Streamlit app setup
st.title("E-Bike Only Map")
#st.write("Showing stations with only e-bikes available.")



    # Add a button to trigger the update
button_pressed = st.button(f"Show Stations with 1 Classic Bike and e-Bikes")

# Default coordinates (San Francisco)
user_coords = (37.7749, -122.4194)
if button_pressed:
    # Filter the stations based on the updated condition
    CLASSIC_BIKE_COUNT += 1
    button_pressed = st.button("Show Stations with ONLY FreE-Bikes")
    # Display map
    folium_map = create_map(user_coords, CLASSIC_BIKE_COUNT)



# JavaScript for dynamic map resizing
st.markdown(
    """
    <script>
            function adjustMapHeight() {
                let mapDiv = document.querySelector('iframe');
                if (mapDiv) {
                    if (window.innerWidth <= 768) {
                        mapDiv.style.height = '400px';
                    } else {
                        mapDiv.style.height = '600px';
                    }
                }
            }
            
            window.addEventListener('resize', adjustMapHeight);
            adjustMapHeight();
        });
    </script>
    """,
    unsafe_allow_html=True
)

# Default coordinates (San Francisco)
user_coords = (37.7749, -122.4194)

# Display map
folium_map = create_map(user_coords, CLASSIC_BIKE_COUNT)
folium_static(folium_map)

# st.write("Use the button on the map to find your current location.")


# ================BUTTONS for BW Mobile App==============================

# Add icon libraries using markdown
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)


# iPhone button with fallback to respective App Store if the app isn't installed
st.markdown("""
    <a href="baywheels://open" target="_blank">
        <button style="padding:10px 20px; background-color:#007BFF; color:white; border:none; border-radius:5px; cursor:pointer; display:inline-block;">
            <i class="fab fa-app-store-ios"></i> <i class="material-icons">android</i>
        </button>
    </a>
""", unsafe_allow_html=True)

#==============================================

