import requests
import folium
import streamlit as st
from geopy.distance import geodesic
from streamlit_folium import folium_static
# ==============================================


import streamlit as st
import pandas as pd
import pydeck as pdk

# Set page configuration
st.set_page_config(page_title="Bay Wheels Map", layout="wide")

# Add a single button that detects the device OS and opens the appropriate Bay Wheels app
st.markdown("""
    <script>
        function openBayWheelsApp() {
            var userAgent = navigator.userAgent || navigator.vendor || window.opera;
            if (/android/i.test(userAgent)) {
                window.location.href = "intent://#Intent;package=com.motivateco.gobike;scheme=baywheels;S.browser_fallback_url=https://play.google.com/store/apps/details?id=com.motivateco.gobike;end";
            } else if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
                window.location.href = "https://apps.apple.com/us/app/bay-wheels/id1233398899";
            } else {
                alert('Unsupported device. Please visit the app store manually.');
            }
        }
    </script>
    <button onclick="openBayWheelsApp()" style="padding:10px 20px; background-color:#6f42c1; color:white; border:none; border-radius:5px; cursor:pointer;">
        Open Bay Wheels App
    </button>
""", unsafe_allow_html=True)

# Load your data (example placeholder)
data = pd.DataFrame({
    'lat': [37.7749],
    'lon': [-122.4194],
    'station': ['Example Station'],
    'bikes_available': [5]
})

# Display the map
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=37.7749,
        longitude=-122.4194,
        zoom=12,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=100,
        ),
    ],
))

# ==============================================

# Define Bay Wheels GBFS endpoints
STATION_INFO_URL = "https://gbfs.baywheels.com/gbfs/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.baywheels.com/gbfs/en/station_status.json"

def fetch_data(url):
    """Fetch JSON data from the given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_ebike_only_stations(user_coords):
    """Fetch and filter stations that only have e-bikes available."""
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
                distance = geodesic(user_coords, (station["lat"], station["lon"])).miles
                eligible_stations.append({
                    "name": station["name"],
                    "lat": station["lat"],
                    "lon": station["lon"],
                    "num_ebikes": num_ebikes,
                    "distance": distance
                })
    
    eligible_stations.sort(key=lambda x: x["distance"])
    return eligible_stations[:20]

def create_map(user_coords):
    """Generate a Folium map with e-bike-only station markers."""
    stations = get_ebike_only_stations(user_coords)
    m = folium.Map(location=user_coords, zoom_start=15, control_scale=True)
    
    for station in stations:
        folium.Marker(
            location=(station["lat"], station["lon"]),
            popup=f"{station['name']} ({station['num_ebikes']} e-bikes)",
            icon=folium.Icon(color='blue', icon='bicycle', prefix='fa')
        ).add_to(m)
    
    locate_control = folium.plugins.LocateControl(auto_start=True, flyTo=True, keepCurrentZoomLevel=True)
    m.add_child(locate_control)
    
    return m

# Streamlit app setup
st.title("Bay Wheels E-Bike Availability Map")
st.write("Showing stations with only e-bikes available near your location.")

# JavaScript for pull-to-refresh (Mobile) and dynamic map resizing
st.markdown(
    """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            let startY;
            window.addEventListener('touchstart', function(event) {
                startY = event.touches[0].clientY;
            });
            window.addEventListener('touchend', function(event) {
                let endY = event.changedTouches[0].clientY;
                if (startY - endY > 100) {
                    location.reload();
                }
            });
            
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
folium_map = create_map(user_coords)
folium_static(folium_map)

st.write("Use the button on the map to find your current location.")
