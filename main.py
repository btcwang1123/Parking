import streamlit as st
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic

# 網頁 URL
url = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"

def fetch_data():
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("無法獲取數據")
        return []

def is_open_now(business_hours):
    return True

def parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def parse_float(value):
    try:
        return float(value.replace("元", ""))
    except (ValueError, TypeError):
        return 0

def main():
    global current_time
    current_time = datetime.now().strftime("%H:%M")

    # 獲取用戶的經緯度
    user_lat = st.number_input("輸入您的緯度", value=24.8138)
    user_lon = st.number_input("輸入您的經度", value=120.9675)
    search_radius = st.slider("搜索半徑 (公里)", 0.1, 5.0, 1.0)

    field_choice = ["停車場名稱", "地址", "小車剩餘車位數", "平日收費", "假日收費"]

    data = fetch_data()
    update_time = data[0]['UPDATETIME'] if data else "無法獲取更新時間"
    st.write(f"數據更新時間: {update_time}")

    user_location = (user_lat, user_lon)
    filtered_data = []
    for park in data:
        park_location = (float(park['LATITUDE']), float(park['LONGITUDE']))
        distance = geodesic(user_location, park_location).km
        if distance <= search_radius:
            filtered_data.append(park)

    if filtered_data:
        folium_map = folium.Map(location=user_location, zoom_start=14, width=350)

        folium.Marker(
            location=user_location,
            popup="您的位置",
            icon=folium.Icon(icon="user")
        ).add_to(folium_map)

        for park in filtered_data:
            folium.Marker(
                location=[float(park['LATITUDE']), float(park['LONGITUDE'])],
                popup=folium.Popup(f"""
                    停車場名稱: {park['PARKINGNAME']}<br>
                    地址: {park['ADDRESS']}<br>
                    小車剩餘車位數: {park['FREEQUANTITY']}/{park['TOTALQUANTITY']}<br>
                    平日收費: {park['WEEKDAYS']}<br>
                    假日收費: {park['HOLIDAY']}<br>
                    更新時間: {park['UPDATETIME']}
                """, max_width=200),
                icon=folium.Icon(icon="info-sign")
            ).add_to(folium_map)

        folium_static(folium_map, width=350)

if __name__ == "__main__":
    main()
