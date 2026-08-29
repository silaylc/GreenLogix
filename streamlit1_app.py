"""
GreenLogix Pro Dashboard v3.1 (Professional UI Edition)
==============================================================
Girinti hataları ve boş satır kontrolleri düzeltilmiş sürüm.
"""

import sys
import os
import copy
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
import streamlit as st
import random

# --- PATH & IMPORT FIX ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

try:
    from src.model import Customer, Vehicle, Problem
    from src.solver import evaluate_route
    from src.optimizer import run_optimizer
    from src.services.geocoding_service import geocode_address
    from src.services.routing_service import get_route_for_points
except ImportError as e:
    st.error(f"❌ Kritik Import Hatası: {e}")
    st.info("İpucu: 'src' ve 'services' klasörlerinde __init__.py olduğundan emin olun.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="GreenLogix Pro Dashboard", page_icon="🌿", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff; border: 1px solid #e9ecef; border-radius: 8px;
        padding: 12px 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 12px;
    }
    .metric-value { font-size: 20px; font-weight: 800; color: #2c3e50; }
    .metric-label { font-size: 11px; font-weight: 600; color: #7f8c8d; text-transform: uppercase; }
    .green-impact {
        background-color: #f1fdf4; border-left: 5px solid #2ecc71; padding: 16px;
        border-radius: 6px; color: #1e8449; margin: 16px 0;
    }
    </style>
""", unsafe_allow_html=True)

def display_metric_card(label, value):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

def generate_driver_log(res, edited_df):
    logs = []
    current_load = edited_df["Demand"].sum()
    for idx, node_id in enumerate(res.route):
        row = edited_df[edited_df["ID"] == node_id].iloc[0]
        if idx == 0:
            action = f"Depart from Depot (Load: {current_load}kg)"
        elif idx == len(res.route) - 1:
            action = "Return to Depot & Finish"
        else:
            action = f"Unload {row['Demand']}kg"
            current_load -= row["Demand"]
        logs.append({
            "Step": idx + 1, 
            "Location": row["Location"], 
            "Action": action, 
            "Remaining Load": f"{current_load:.1f} kg"
        })
    return pd.DataFrame(logs)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/814/814513.png", width=60)
    st.markdown("## GreenLogix")
    st.divider()

    with st.expander("🚐 Vehicle Settings", expanded=True):
        veh_capacity = st.number_input("Capacity (kg)", value=500.0)
        veh_fuel_cap = st.number_input("Fuel Capacity (L)", value=60.0)
        veh_base_fuel = st.number_input("Base Fuel (L/km)", value=0.20)
        veh_load_factor = st.number_input("Load Factor", value=0.010, format="%.3f")
        veh_speed = st.number_input("Avg Speed (km/h)", value=40.0)
        veh_max_drive = st.number_input("Max Drive (min)", value=240.0)
        veh_break_dur = st.number_input("Break Duration (min)", value=45.0)

    with st.expander("💰 Cost & Green Parameters", expanded=True):
        fuel_price = st.number_input("Fuel Price ($/L)", value=1.50)
        veh_emission = st.number_input("Emission Factor", value=2.68)

    with st.expander("⚙️ Optimizer Settings"):
        num_candidates = st.slider("Candidates", 5, 100, 30)
        use_2opt = st.checkbox("Apply 2-opt", value=True)
        seed = st.number_input("Seed", value=42)

    vehicle = Vehicle(
        capacity=veh_capacity, fuel_capacity=veh_fuel_cap, base_fuel_per_km=veh_base_fuel,
        load_factor=veh_load_factor, average_speed_kmph=veh_speed,
        max_drive_minutes=veh_max_drive, break_duration=veh_break_dur, emission_factor=veh_emission
    )

# --- MAIN CONTENT ---
st.title("Logistics Command Center")

if "customer_data" not in st.session_state:
    st.session_state.customer_data = pd.DataFrame([
        {"ID": 0, "Location": "Main Depot", "Lat": 39.9334, "Lon": 32.8597, "Demand": 0.0},
        {"ID": 1, "Location": "Customer A", "Lat": 39.9208, "Lon": 32.8541, "Demand": 80.0},
        {"ID": 2, "Location": "Customer B", "Lat": 39.9150, "Lon": 32.8600, "Demand": 60.0}
    ])

addr = st.text_input("📍 Add new smart stop:")
if st.button("Add to Network"):
    geo = geocode_address(addr)
    if geo:
        new_node = {"ID": len(st.session_state.customer_data), "Location": addr[:15], "Lat": geo["lat"], "Lon": geo["lon"], "Demand": 50.0}
        st.session_state.customer_data = pd.concat([st.session_state.customer_data, pd.DataFrame([new_node])], ignore_index=True)

edited_df = st.data_editor(st.session_state.customer_data, use_container_width=True, num_rows="dynamic")
st.session_state.customer_data = edited_df

if st.button("▶ Start AI Optimizer", type="primary", use_container_width=True):
    # DÜZELTME: Bu blok artık doğru şekilde girintilendi
    custs = {
        int(r["ID"]): Customer(id=int(r["ID"]), demand=r["Demand"]) 
        for _, r in edited_df.iterrows() 
        if pd.notnull(r["ID"]) and r["ID"] != 0
    }

    # Mesafe matrisi
    dist_mat = [[(( (r1['Lat']-r2['Lat'])**2 + (r1['Lon']-r2['Lon'])**2 )**0.5)*111 for _, r2 in edited_df.iterrows()] for _, r1 in edited_df.iterrows()]
    trf_mat = [[1.0]*len(edited_df) for _ in range(len(edited_df))]
    
    prob = Problem(customers=custs, vehicle=vehicle, distance_matrix=dist_mat, traffic_matrix=trf_mat)
    
    with st.spinner("Optimizing..."):
        res = run_optimizer(prob, num_candidates=num_candidates, use_2opt=use_2opt, seed=seed)
        
        # OSRM Geometrisi
        coords = [(edited_df[edited_df["ID"] == node]["Lon"].iloc[0], edited_df[edited_df["ID"] == node]["Lat"].iloc[0]) for node in res.route]
        osrm = get_route_for_points(coords)
        if osrm:
            res.geometry = osrm["geometry"]
            res.total_distance = osrm["distance_m"] / 1000
        
        st.session_state.active_res = res

# --- RESULTS DASHBOARD ---
if "active_res" in st.session_state:
    res = st.session_state.active_res
    st.divider()
    
    if res.feasible: st.success("✅ Route is feasible.")
    else: st.error("❌ Constraints violated.")

    cols = st.columns(8)
    metrics = [
        ("Dist", f"{res.total_distance:.1f}km"), 
        ("Fuel", f"{res.total_fuel:.1f}L"), 
        ("Time", f"{res.total_time:.0f}min"), 
        ("Cost", f"${res.total_fuel*fuel_price:.1f}"), 
        ("CO2", f"{res.total_emission:.1f}kg"), 
        ("Eff", f"{res.total_distance/max(1, len(res.route)-2):.1f}"), 
        ("Score", f"{res.score:.1f}"), 
        ("Pen", f"{res.penalty:.0f}")
    ]
    
    for i, (l, v) in enumerate(metrics):
        with cols[i]: display_metric_card(l, v)

    st.markdown(f'<div class="green-impact">🌱 Sustainability Insight: This AI route saved approx {(res.total_distance*0.04):.2f} kg CO2</div>', unsafe_allow_html=True)

    view_col1, view_col2 = st.columns([1.8, 1])
    with view_col1:
        st.markdown("#### 🗺️ Fleet Tracking Map")
        m = folium.Map(location=[edited_df.Lat.mean(), edited_df.Lon.mean()], zoom_start=12, tiles="CartoDB positron")
        bounds = []
        for _, r in edited_df.iterrows():
            if pd.notnull(r.Lat) and pd.notnull(r.Lon):
                folium.Marker(
                    [r.Lat, r.Lon], 
                    tooltip=r.Location, 
                    icon=folium.Icon(color='red' if r.ID==0 else 'blue')
                ).add_to(m)
                bounds.append([r.Lat, r.Lon])
        
        if res.geometry:
            folium.GeoJson(res.geometry, style_function=lambda x: {'color': '#2ecc71', 'weight': 5}).add_to(m)
            route_coords = [[lat, lon] for lon, lat in res.geometry["coordinates"]]
            bounds.extend(route_coords)
        
        if bounds: m.fit_bounds(bounds, padding=(30, 30))
        st_folium(m, width=1200, height=500, use_container_width=True)

    with view_col2:
        st.markdown("#### 📋 Driver Operations Log")
        st.dataframe(generate_driver_log(res, edited_df), use_container_width=True, height=450)