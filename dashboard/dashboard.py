import os
import time
import requests
import streamlit as np  # standard import
import streamlit as st
import numpy as npy

# Initialize page settings
st.set_page_config(
    page_title="GeoKisan / GeoFarmer Control Center",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Design System CSS Injections (Applying geokisan HSL style guidelines)
st.markdown("""
<style>
    /* Styling tokens configuration mapping */
    :root {
        --primary-green: #4A7C2F;
        --ai-gold: #C8860A;
        --water-blue: #1A6B8A;
        --alert-clay: #8B4513;
        --bg-dark: #1C2410;
        --surface-cream: #FAF8F3;
    }
    
    .stApp {
        background-color: var(--surface-cream);
        color: #2F3E1E;
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Header card layout tuning */
    .header-card {
        background-color: var(--primary-green);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-bottom: 5px solid var(--ai-gold);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-card h1 {
        margin: 0;
        font-size: 2.5rem;
        font-family: 'Playfair Display', serif;
    }
    
    /* Interactive metric panels */
    .metric-panel {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid var(--water-blue);
        margin-bottom: 10px;
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        font-weight: bold;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--bg-dark);
        margin-top: 5px;
    }
    
    /* Clay Earth alert layout */
    .alert-panel {
        background-color: #FDF3EB;
        border: 1px solid var(--alert-clay);
        border-left: 8px solid var(--alert-clay);
        color: #5C2B0B;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    
    /* Button layout standardizations */
    .stButton>button {
        background-color: var(--primary-green) !important;
        color: white !important;
        border-radius: 6px !important;
        height: 48px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        background-color: #3B6325 !important;
    }
</style>
""", unsafe_allow_html=True)

# Application state configuration
FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")

# Header container
st.markdown("""
<div class="header-card">
    <h1>GeoFarmer / جیو کسان operations control panel</h1>
    <p>Precision Agriculture IoT Telemetry System & Field Sensor Diagnostics Gateway</p>
</div>
""", unsafe_allow_html=True)

# Layout division: Sidebar Control vs Main Workspace
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&q=80&w=400", use_container_width=True)
    st.markdown("### ⚙️ Telemetry Management Node")
    
    # Active live-polling settings
    enable_polling = st.checkbox("Enable Real-time Device Polling Loop", value=True)
    polling_rate = st.slider("Polling Frequency (Seconds)", min_value=1, max_value=10, value=3)
    
    st.markdown("---")
    st.markdown("### 🚜 Remote IoT Simulator")
    st.write("Trigger virtual sensor voltage outputs straight to the FastAPI telemetry service.")
    
    sim_temp = st.slider("Ambient Temperature (°C)", min_value=-5.0, max_value=50.0, value=28.5, step=0.1)
    sim_humidity = st.slider("Relative Air Humidity (%)", min_value=10.0, max_value=100.0, value=62.0, step=0.5)
    sim_soil = st.slider("Soil Volumetric Moisture (Scale 0-1023)", min_value=0, max_value=1023, value=480, step=1)
    
    if st.button("Transmit Mock Telemetry payload"):
        try:
            payload = {
                "temp": sim_temp,
                "humidity": sim_humidity,
                "soil1": sim_soil
            }
            res = requests.post(f"{FASTAPI_URL}/api/telemetry", data=payload, timeout=3)
            if res.status_code == 200:
                st.success("Telemetry telemetry package broadcast successful!")
            else:
                st.error(f"Transmission returned error code: {res.status_code}")
        except Exception as e:
            st.error(f"Failed to communicate with API backend: {e}")

# Fetch real-time data from backend API
def get_current_metrics():
    try:
        response = requests.get(f"{FASTAPI_URL}/api/latest", timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        # Fallback simulated telemetry values if connection is dropping
        pass
    return {
        "temp": 28.5,
        "humidity": 62.0,
        "soil1": 480,
        "timestamp": time.time(),
        "offline_simulated": True
    }

# Read current states
metrics = get_current_metrics()

# Display active notifications and alerts
if metrics.get("offline_simulated", False):
    st.markdown("""
    <div class="alert-panel">
        <strong>⚠️ BACKEND CONNECTIONS DROPPING:</strong> Dashboard is presently operating in local simulation mode.
        Verify your FastAPI backend service is running locally on port 8000.
    </div>
    """, unsafe_allow_html=True)

# Volumetric Soil Moisture Calibration mapping
soil_raw = metrics["soil1"]
# High reading (dry) vs Low reading (saturated). Standard Pakistani soil probe calibration:
# <= 300: Saturated
# 300 to 700: Optimal dampness
# > 700: Arid drought state
soil_moisture_pct = min(100.0, max(0.0, ((1023 - soil_raw) / 1023.0) * 100.0))

# Alert banner evaluations
if soil_raw > 700:
    st.markdown(f"""
    <div class="alert-panel" style="border-left-color: #8B4513;">
        <strong>🚨 IRID IRRIGATION ALERT (Clay Earth Alert):</strong> Soil moisture levels are excessively low ({soil_raw} raw / {soil_moisture_pct:.1f}%). 
        Aab-e-Rasi automated pump loops should be executed to avoid crop wilting.
    </div>
    """, unsafe_allow_html=True)

if metrics["temp"] <= 4.0:
    st.markdown("""
    <div class="alert-panel" style="background-color: #F0F6F9; border-color: #1A6B8A; color: #0E3C4E;">
        <strong>❄️ FROST RISK FORECAST WARNING:</strong> Ambient air temperature has reached critical freeze threshold. 
        Verify crop thermal insulation and schedule automated warm watering loops immediately.
    </div>
    """, unsafe_allow_html=True)

# Main metric visual layout grid
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-panel" style="border-left-color: #C8860A;">
        <div class="metric-title">🌡️ Ambient Temperature</div>
        <div class="metric-value">{metrics['temp']:.1f} °C</div>
        <small style="color: #666;">Target: 22°C - 35°C (Wheat Optimal)</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-panel" style="border-left-color: #1A6B8A;">
        <div class="metric-title">💧 Relative Humidity</div>
        <div class="metric-value">{metrics['humidity']:.1f} %</div>
        <small style="color: #666;">Atmospheric Vapor Balance</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-panel" style="border-left-color: #4A7C2F;">
        <div class="metric-title">🌱 Volumetric Soil Moisture</div>
        <div class="metric-value">{soil_moisture_pct:.1f} %</div>
        <small style="color: #666;">ADC value: {soil_raw} / 1023 units</small>
    </div>
    """, unsafe_allow_html=True)

# Renders dynamic telemetry visual progress maps
st.markdown("### 📊 Live Telemetry Sparklines & Metrics Trends")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("💧 Volumetric Soil Moisture & Water Consumption Trends")
    # Generating mock series for continuous telemetry charts
    npy.random.seed(int(time.time()) % 1000)
    data_points = 50
    moisture_series = soil_moisture_pct + npy.cumsum(npy.random.normal(0, 0.8, data_points))
    moisture_series = npy.clip(moisture_series, 0.0, 100.0)
    st.line_chart(moisture_series)

with chart_col2:
    st.subheader("📈 Temperature and Vapor Pressure Deficit Tracking")
    temp_series = metrics["temp"] + npy.cumsum(npy.random.normal(0, 0.15, data_points))
    st.area_chart(temp_series)

# Visual status log layout section
st.markdown("### 📋 Connected Devices & Gateway Hub")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.info("📡 Gateway Node status: **ACTIVE**")
with status_col2:
    st.info("🔋 Battery reserves: **94% (Solar Inverter Active)**")
with status_col3:
    st.info(f"⏱️ Telemetry age: **{round(time.time() - metrics['timestamp'], 1)}s ago**")

# Auto-reloader execution logic
if enable_polling:
    time.sleep(polling_rate)
    st.rerun()
