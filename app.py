import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

# Must remain the very first Streamlit command
st.set_page_config(page_title="Emergency Registry", layout="wide")


def render_navigation_menu():
    """Renders a clean inline horizontal navigation bar directly below the main header."""
    st.markdown("""
        <style>
        .nav-container {
            display: flex;
            justify-content: space-around;
            background-color: #f1f3f5;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
        }
        .nav-link {
            text-decoration: none !important;
            color: #495057 !important;
            font-weight: 500;
            font-size: 14px;
        }
        .nav-link:hover {
            color: #0d6efd !important;
        }
        </style>
    """, unsafe_allow_html=True) # <-- FIXED PARAMETER

    st.markdown("""
        <div class="nav-container">
            <a class="nav-link" href="#about">ℹ️ About</a>
            <a class="nav-link" href="#instructions">📖 Instructions</a>
            <a class="nav-link" href="#contributors">🤝 Contributors</a>
            <a class="nav-link" href="https://google.com" target="_blank">🏢 Organization Sign-Up</a>
        </div>
    """, unsafe_allow_html=True) # <-- FIXED PARAMETER

# --- MAIN HEADERS ---
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Advanced Spatial Sandbox")

# Injecting the Menu Bar
render_navigation_menu()


# 🗄️ INTERNAL BACKUP DATA ENGINE
def load_backup_sandbox_data():
    backup_payload = {
        "Organization_Name": ["Florida Baptist Disaster Relief", "ITDRC", "Texas Response Network", "Georgia Feeding VOAD", "Sarasota Local CERT"],
        "State_Supported": ["FL", "All States", "TX", "GA", "FL"],
        "Primary_ESF_Focus": ["ESF #6: Mass Care", "ESF #2: Communications", "ESF #13: Public Safety", "ESF #6: Mass Care", "ESF #9: Search & Rescue"],
        "Counties_Covered": ["All Counties", "All Counties", "All Counties", "All Counties", "Sarasota, Manatee"],
        "Resource_Capacity": ["3 Mobile Kitchens (30k meals/day), 4 Chainsaw Teams", "20 Satellite Internet Terminals, Mesh WiFi Towers", "15 High-Water Rescue Vehicles, 40 Ham Operators", "2 Bulk Food Warehouses, 10 Refrigerated Trailers", "2 Light Rescue Squads, 25 Vetted Members"],
        "Phone": ["1-800-555-0122", "1-877-387-3646", "1-555-555-0199", "1-555-555-0144", "1-555-555-0133"],
        "Latitude": [28.5383, 37.0902, 31.9686, 32.1656, 27.3364],
        "Longitude": [-81.3792, -95.7129, -99.9018, -82.9001, -82.5307]
    }
    return pd.DataFrame(backup_payload)

SPREADSHEET_ID = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"
# Fixed malformed URL string to pull cleanly from Google Sheets engine
url = f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Organizations"

try:
    df = pd.read_csv(url, timeout=3)
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df = df.dropna(subset=["Latitude", "Longitude"])
except Exception:
    df = load_backup_sandbox_data()

# 🌍 SIDEBAR SYSTEM WIDGETS
st.sidebar.header("🌍 Operational Filters")

# Filter 1: State Target Selection Focus
state_options = ["All States"] + sorted(df["State_Supported"].dropna().unique().tolist())
sel_state = st.sidebar.selectbox("1. Target State Horizon:", state_options)

filtered_df = df.copy()
center = [37.0902, -95.7129]
zoom = 4

# Initialize tracking buckets for cascading loops
available_counties = ["All Counties"]
available_esfs = ["All ESF Formats"]

if sel_state != "All States":
    filtered_df = df[df["State_Supported"].str.upper() == sel_state.upper()]
    if not filtered_df.empty:
        center = [filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()]
        zoom = 6
        
        # Populate dynamic cascading context strings
        for val in filtered_df["Counties_Covered"].dropna().astype(str):
            for c in val.split(","):
                c_clean = c.strip()
                if c_clean and c_clean.upper() != "ALL COUNTIES" and c_clean not in available_counties:
                    available_counties.append(c_clean)

# Filter 2 & 3: Cascading Dropdowns
sel_county = st.sidebar.selectbox("2. Narrow Down by County Scope:", available_counties)

# Dynamic Format Shifter logic matches state types
if sel_state == "FL":
    available_esfs += ["ESF #6: Mass Care", "ESF #9: Search & Rescue", "ESF #16: Law Enforcement", "ESF #20: Business Infrastructure"]
elif sel_state == "TX":
    available_esfs += ["ESF #6: Mass Care", "ESF #13: Public Safety", "ESF #17: Military Support", "ESF #20: Cybersecurity"]
else:
    available_esfs += sorted(df["Primary_ESF_Focus"].dropna().unique().tolist())

sel_esf = st.sidebar.selectbox("3. State-Specific ESF Framework Filter:", available_esfs)

# Filter 4: Logistical Range Selector
st.sidebar.markdown("---")
st.sidebar.subheader("📐 Logistical Range Slider")
radius_limit = st.sidebar.select_slider("Asset Search Radius Limit:", options=["Unrestricted Focus", "50 Miles", "100 Miles", "150 Miles", "200 Miles"])

# --- NEW VISIBILITY PREFERENCES TOGGLE SWITCH ---
st.sidebar.markdown("---")
st.sidebar.subheader("👁️ Display Preferences")
show_metrics = st.sidebar.toggle("Show Operational Resource Metrics", value=True)

# Apply cascading filter executions
if sel_county != "All Counties":
    filtered_df = filtered_df[filtered_df["Counties_Covered"].astype(str).str.contains(sel_county, case=False)]

if sel_esf != "All ESF Formats":
    esf_code = sel_esf.split(":")[0].strip()
    filtered_df = filtered_df[filtered_df["Primary_ESF_Focus"].astype(str).str.contains(esf_code, case=False)]

# 🗺️ PANORAMIC DRAW CANVAS WINDOW
st.subheader("📍 Interactive Panoramic Drawing Canvas")
st.caption("🖱️ Click a tool on the left map menu to draw custom boxes. The system will filter data blocks automatically below.")

# Applied cleaner legal notice attribution formatting directly to clean watermark footprint
m = folium.Map(
    location=center, 
    zoom_start=zoom, 
    tiles="CartoDB positron",
    attr="© OpenStreetMap contributors | © CartoDB"
)
Draw(position='topleft', draw_options={'polyline':False, 'circle':False, 'marker':False, 'polygon':True, 'rectangle':True}).add_to(m)

for idx, row in filtered_df.iterrows():
    folium.CircleMarker(location=[row["Latitude"], row["Longitude"]], radius=6, color="#1f77b4", fill=True, fill_opacity=0.7, popup=f"<b>{row['Organization_Name']}</b>").add_to(m)

map_out = st_folium(m, width=1400, height=400, key="canvas")

# 🖱️ Mouse Bounding Box Processing (Bulletproof Structural Matrix Unpack)
drawn = map_out.get("last_active_drawing")
if drawn and "geometry" in drawn and "coordinates" in drawn["geometry"]:
    try:
        poly_coords = drawn["geometry"]["coordinates"][0]
        lons = [float(point[0]) for point in poly_coords]
        lats = [float(point[1]) for point in poly_coords]
        filtered_df = filtered_df[(filtered_df["Latitude"] >= min(lats)) & (filtered_df["Latitude"] <= max(lats)) & (filtered_df["Longitude"] >= min(lons)) & (filtered_df["Longitude"] <= max(lons))]
        st.sidebar.success("🎯 Map filtered by drawn boundaries!")
    except Exception:
        pass

st.write("---")

# 📊 LOWER GRID LAYOUT
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏢 Expanded Asset Logs")
    if not filtered_df.empty:
        chosen = st.selectbox("Inspect profile metrics:", filtered_df["Organization_Name"].tolist())
        rec = filtered_df[filtered_df["Organization_Name"] == chosen].iloc[0]
        st.markdown(f"### **{rec['Organization_Name']}**")
        st.info(f"💪 **Capacity:** {rec.get('Resource_Capacity', 'No description logged.')}")
        phone = str(rec.get("Phone", ""))
        if phone and phone != "nan":
            st.markdown(f'👉 <a href="tel:{phone.replace("-","")}" style="font-size:16px; font-weight:bold; color:#1f77b4; text-decoration:none;">📲 Click to Call: {phone}</a>', unsafe_allow_html=True)
    else:
        st.write("No groups inside this active layout footprint.")

with col2:
    # Wrapped inside conditional layout switch
    if show_metrics:
        st.subheader("📊 Operational Resource Metrics")
        if not filtered_df.empty:
            st.metric("Total Responders in View", len(filtered_df))
            st.bar_chart(filtered_df["Primary_ESF_Focus"].value_counts())
    else:
        st.subheader("📊 Operational Resource Metrics")
        st.caption("🔒 *Metrics layout pane is hidden. Enable via sidebar preferences.*")

st.write("---")
st.subheader("📊 Dynamic Data Records Pipeline Table")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# ==============================================================================
# DOCUMENTATION SECTION ANCHORS
# ==============================================================================
st.write("---")
st.markdown("<div id='about'></div>", unsafe_allow_html=True)
with st.expander("ℹ️ About the Registry Platform", expanded=True):
    st.write("This sandbox registry empowers multi-state disaster routing by bridging organization rosters and regional ESF frameworks together seamlessly during major dynamic emergency events.")

st.markdown("<div id='instructions'></div>", unsafe_allow_html=True)
with st.expander("📖 System Operational Instructions"):
    st.write("1. Choose your active disaster framework using the cascading sidebar dropdown filters.")
    st.write("2. Select or draw geographic bounding layers directly on the map block.")
    st.write("3. Inspect the Dossier panel for exact regional contact routing information.")

st.markdown("<div id='contributors'></div>", unsafe_allow_html=True)
with st.expander("🤝 Open-Source Contributors & Attribution"):
    st.write("Built on Folium, Leaflet, Streamlit, and community OpenStreetMap spatial architecture data. Continuous maintenance by the Emergency Infrastructure Developer Core Team.")
