import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from zoneinfo import ZoneInfo


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="WeatherNow",
    page_icon="🌤️",
    layout="wide"
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>

.main {
    background: linear-gradient(135deg, #eef7ff, #ffffff);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.weather-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
}

.weather-subtitle {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
}

.weather-card {
    padding: 25px;
    border-radius: 20px;
    background: rgba(255,255,255,0.85);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.temperature {
    font-size: 60px;
    font-weight: 800;
}

.condition {
    font-size: 22px;
    font-weight: 600;
}

.metric-card {
    padding: 20px;
    border-radius: 18px;
    background: white;
    box-shadow: 0px 5px 18px rgba(0,0,0,0.07);
    text-align: center;
}

.metric-value {
    font-size: 25px;
    font-weight: 700;
}

.metric-label {
    color: #777;
    font-size: 14px;
}

.forecast-card {
    padding: 18px;
    border-radius: 18px;
    background: white;
    box-shadow: 0px 5px 18px rgba(0,0,0,0.06);
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# WEATHER CODE CONVERTER
# ---------------------------------------------------------

def weather_description(code):

    weather_codes = {
        0: ("Clear Sky", "☀️"),
        1: ("Mainly Clear", "🌤️"),
        2: ("Partly Cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Fog", "🌫️"),
        48: ("Rime Fog", "🌫️"),
        51: ("Light Drizzle", "🌦️"),
        53: ("Drizzle", "🌦️"),
        55: ("Heavy Drizzle", "🌧️"),
        61: ("Light Rain", "🌦️"),
        63: ("Rain", "🌧️"),
        65: ("Heavy Rain", "🌧️"),
        71: ("Light Snow", "🌨️"),
        73: ("Snow", "❄️"),
        75: ("Heavy Snow", "❄️"),
        80: ("Rain Showers", "🌦️"),
        81: ("Rain Showers", "🌧️"),
        82: ("Heavy Rain Showers", "⛈️"),
        95: ("Thunderstorm", "⛈️"),
        96: ("Thunderstorm + Hail", "⛈️"),
        99: ("Heavy Thunderstorm + Hail", "⛈️")
    }

    return weather_codes.get(
        code,
        ("Unknown Weather", "🌈")
    )


# ---------------------------------------------------------
# GEOCODING
# ---------------------------------------------------------

def get_location(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data:
        return None

    return data["results"][0]


# ---------------------------------------------------------
# WEATHER API
# ---------------------------------------------------------

def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "is_day,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m"
        ),

        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation_probability,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "precipitation_probability_max,"
            "sunrise,"
            "sunset"
        ),

        "timezone": "auto",

        "forecast_days": 7
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ---------------------------------------------------------
# APP HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="weather-title">🌤️ WeatherNow</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="weather-subtitle">'
    'Live weather insights at your fingertips'
    '</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

col1, col2 = st.columns([5, 1])

with col1:

    city = st.text_input(
        "🔍 Search City",
        placeholder="Enter a city name..."
    )

with col2:

    st.write("")

    refresh = st.button(
        "🔄 Refresh",
        use_container_width=True
    )


# ---------------------------------------------------------
# DEFAULT CITY
# ---------------------------------------------------------

if not city:

    city = "Chennai"


# ---------------------------------------------------------
# FETCH DATA
# ---------------------------------------------------------

try:

    with st.spinner("Fetching live weather data..."):

        location = get_location(city)

        if location is None:

            st.error(
                "❌ City not found. Please check the city name."
            )

            st.stop()

        latitude = location["latitude"]
        longitude = location["longitude"]

        weather = get_weather(
            latitude,
            longitude
        )


except requests.exceptions.RequestException:

    st.error(
        "⚠️ Unable to connect to the weather service. "
        "Please check your internet connection."
    )

    st.stop()


# ---------------------------------------------------------
# LOCATION INFORMATION
# ---------------------------------------------------------

city_name = location.get(
    "name",
    city
)

country = location.get(
    "country",
    ""
)

timezone = weather.get(
    "timezone",
    "UTC"
)


# ---------------------------------------------------------
# CURRENT WEATHER
# ---------------------------------------------------------

current = weather["current"]

temperature = current["temperature_2m"]

humidity = current["relative_humidity_2m"]

feels_like = current["apparent_temperature"]

wind_speed = current["wind_speed_10m"]

wind_direction = current["wind_direction_10m"]

precipitation = current["precipitation"]

weather_code = current["weather_code"]

condition, icon = weather_description(
    weather_code
)


# ---------------------------------------------------------
# DYNAMIC LOCAL DATE & TIME
# ---------------------------------------------------------

try:

    local_time = datetime.now(
        ZoneInfo(timezone)
    )

except Exception:

    local_time = datetime.now()


date_string = local_time.strftime(
    "%A, %d %B %Y"
)

time_string = local_time.strftime(
    "%I:%M %p"
)


# ---------------------------------------------------------
# CURRENT WEATHER CARD
# ---------------------------------------------------------

st.markdown(
    '<div class="weather-card">',
    unsafe_allow_html=True
)

left, middle, right = st.columns(
    [2, 3, 2]
)

with left:

    st.markdown(
        f"## {city_name}"
    )

    st.write(country)

    st.write(
        f"📅 {date_string}"
    )

    st.write(
        f"🕐 {time_string}"
    )


with middle:

    st.markdown(
        f'<div class="temperature">'
        f'{temperature:.1f}°C'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="condition">'
        f'{icon} {condition}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"Feels like {feels_like:.1f}°C"
    )


with right:

    st.markdown(
        f"<h1>{icon}</h1>",
        unsafe_allow_html=True
    )

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# WEATHER METRICS
# ---------------------------------------------------------

st.subheader("📊 Current Weather Details")

m1, m2, m3, m4, m5 = st.columns(5)


with m1:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-value">
        💧 {humidity}%
        </div>
        <div class="metric-label">
        Humidity
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m2:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-value">
        🌬️ {wind_speed:.1f} km/h
        </div>
        <div class="metric-label">
        Wind Speed
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m3:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-value">
        🧭 {wind_direction}°
        </div>
        <div class="metric-label">
        Wind Direction
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m4:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-value">
        🌧️ {precipitation} mm
        </div>
        <div class="metric-label">
        Precipitation
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m5:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-value">
        🌡️ {feels_like:.1f}°C
        </div>
        <div class="metric-label">
        Feels Like
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# HOURLY DATA
# ---------------------------------------------------------

hourly = weather["hourly"]

hourly_df = pd.DataFrame({
    "Time": pd.to_datetime(
        hourly["time"]
    ),

    "Temperature": hourly[
        "temperature_2m"
    ],

    "Humidity": hourly[
        "relative_humidity_2m"
    ],

    "Rain Probability": hourly[
        "precipitation_probability"
    ],

    "Rain": hourly[
        "precipitation"
    ],

    "Wind Speed": hourly[
        "wind_speed_10m"
    ]
})


# ---------------------------------------------------------
# HOURLY FORECAST
# ---------------------------------------------------------

st.subheader("🕐 Next 24 Hours")

next_24 = hourly_df.head(24)

cols = st.columns(6)

for i in range(6):

    row = next_24.iloc[i]

    with cols[i]:

        st.markdown(
            f"""
            <div class="forecast-card">

            <b>{row["Time"].strftime("%I %p")}</b>

            <h2>
            {row["Temperature"]:.0f}°C
            </h2>

            🌧️ {row["Rain Probability"]}%<br>

            💧 {row["Humidity"]}%<br>

            🌬️ {row["Wind Speed"]:.0f} km/h

            </div>
            """,
            unsafe_allow_html=True
        )


# ---------------------------------------------------------
# TEMPERATURE GRAPH
# ---------------------------------------------------------

st.subheader("🌡️ Temperature Trend")

fig_temp = go.Figure()

fig_temp.add_trace(
    go.Scatter(
        x=next_24["Time"],
        y=next_24["Temperature"],
        mode="lines+markers",
        name="Temperature",
        line=dict(width=3)
    )
)

fig_temp.update_layout(
    xaxis_title="Time",
    yaxis_title="Temperature (°C)",
    hovermode="x unified",
    height=400
)

st.plotly_chart(
    fig_temp,
    use_container_width=True
)


# ---------------------------------------------------------
# RAIN PROBABILITY GRAPH
# ---------------------------------------------------------

st.subheader("🌧️ Rain Probability")

fig_rain = go.Figure()

fig_rain.add_trace(
    go.Scatter(
        x=next_24["Time"],
        y=next_24["Rain Probability"],
        mode="lines+markers",
        name="Rain Probability"
    )
)

fig_rain.update_layout(
    xaxis_title="Time",
    yaxis_title="Probability (%)",
    yaxis=dict(
        range=[0, 100]
    ),
    hovermode="x unified",
    height=400
)

st.plotly_chart(
    fig_rain,
    use_container_width=True
)


# ---------------------------------------------------------
# HUMIDITY GRAPH
# ---------------------------------------------------------

st.subheader("💧 Humidity Trend")

fig_humidity = go.Figure()

fig_humidity.add_trace(
    go.Scatter(
        x=next_24["Time"],
        y=next_24["Humidity"],
        mode="lines+markers",
        name="Humidity"
    )
)

fig_humidity.update_layout(
    xaxis_title="Time",
    yaxis_title="Humidity (%)",
    yaxis=dict(
        range=[0, 100]
    ),
    hovermode="x unified",
    height=400
)

st.plotly_chart(
    fig_humidity,
    use_container_width=True
)


# ---------------------------------------------------------
# DAILY FORECAST
# ---------------------------------------------------------

st.subheader("📅 7-Day Forecast")

daily = weather["daily"]

daily_df = pd.DataFrame({
    "Date": pd.to_datetime(
        daily["time"]
    ),

    "Weather Code": daily[
        "weather_code"
    ],

    "Max": daily[
        "temperature_2m_max"
    ],

    "Min": daily[
        "temperature_2m_min"
    ],

    "Rain": daily[
        "precipitation_sum"
    ],

    "Rain Probability": daily[
        "precipitation_probability_max"
    ]
})


# ---------------------------------------------------------
# DAILY FORECAST CARDS
# ---------------------------------------------------------

forecast_cols = st.columns(7)

for i, row in daily_df.iterrows():

    condition_name, weather_icon = weather_description(
        row["Weather Code"]
    )

    with forecast_cols[i]:

        st.markdown(
            f"""
            <div class="forecast-card">

            <b>
            {row["Date"].strftime("%a")}
            </b>

            <br>

            {row["Date"].strftime("%d %b")}

            <h1>
            {weather_icon}
            </h1>

            <b>
            {row["Max"]:.0f}°C
            </b>

            /

            {row["Min"]:.0f}°C

            <br><br>

            {condition_name}

            <br><br>

            🌧️ {row["Rain Probability"]}%

            </div>
            """,
            unsafe_allow_html=True
        )


# ---------------------------------------------------------
# HIGH VS LOW TEMPERATURE
# ---------------------------------------------------------

st.subheader("🌡️ Daily High vs Low")

fig_daily = go.Figure()

fig_daily.add_trace(
    go.Bar(
        x=daily_df["Date"],
        y=daily_df["Max"],
        name="Maximum"
    )
)

fig_daily.add_trace(
    go.Bar(
        x=daily_df["Date"],
        y=daily_df["Min"],
        name="Minimum"
    )
)

fig_daily.update_layout(
    barmode="group",
    xaxis_title="Date",
    yaxis_title="Temperature (°C)",
    height=450
)

st.plotly_chart(
    fig_daily,
    use_container_width=True
)


# ---------------------------------------------------------
# WEATHER ANALYTICS
# ---------------------------------------------------------

st.subheader("📈 Weather Analytics")

average_temp = next_24["Temperature"].mean()

maximum_temp = next_24["Temperature"].max()

minimum_temp = next_24["Temperature"].min()

average_humidity = next_24["Humidity"].mean()

maximum_rain_probability = (
    next_24["Rain Probability"].max()
)


a1, a2, a3, a4, a5 = st.columns(5)


with a1:

    st.metric(
        "Average Temperature",
        f"{average_temp:.1f}°C"
    )


with a2:

    st.metric(
        "Maximum Temperature",
        f"{maximum_temp:.1f}°C"
    )


with a3:

    st.metric(
        "Minimum Temperature",
        f"{minimum_temp:.1f}°C"
    )


with a4:

    st.metric(
        "Average Humidity",
        f"{average_humidity:.0f}%"
    )


with a5:

    st.metric(
        "Highest Rain Probability",
        f"{maximum_rain_probability:.0f}%"
    )


# ---------------------------------------------------------
# AUTOMATIC SUMMARY
# ---------------------------------------------------------

st.subheader("🤖 Weather Summary")

if maximum_rain_probability >= 70:

    summary = (
        "Rain is quite likely during the next 24 hours. "
        "Consider carrying an umbrella."
    )

elif maximum_rain_probability >= 40:

    summary = (
        "There is a moderate possibility of rain "
        "during the next 24 hours."
    )

else:

    summary = (
        "The probability of rain is relatively low "
        "during the next 24 hours."
    )


st.info(summary)


# LAST UPDATED
# ---------------------------------------------------------

st.divider()

st.caption(
    f"📡 Live weather data • "
    f"Location: {city_name}, {country} • "
    f"Timezone: {timezone} • "
    f"Last updated: {local_time.strftime('%d %B %Y, %I:%M:%S %p')}"
)

st.caption(
    "Weather data provided by Open-Meteo."
)
