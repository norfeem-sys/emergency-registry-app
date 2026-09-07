import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

# 1. Page Configuration & Layout Rules
st.set_page_config(page_title="Emergency Registry Sandbox", layout="wide")
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Database — Advanced Spatial Sandbox")

# 2. Live Spreadsheet Data Extraction with Network Armor
SPREADSHEET_ID = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"

@st.cache_data(ttl=5) # 5-second ultra-fast cache window for fluent map interactions
def fetch_live_data(sheet_name):
    csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        # Pull the data streams safely
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip() # Strip manual column header spacing variants
        return df
    except Exception as e:
        # Network interceptor alert handles DNS timeouts cleanly without crashing the script
        st.error(f"🌐 **Temporary Cloud Network Lag Detected:** Streamlit is temporarily unable to resolve Google's servers. "
                 f"Your code and spreadsheet settings are correct. Internal Log Error: {e}")
        
        # Injects a recovery retry switch directly onto your sidebar screen
        if st.sidebar.button("♻️ Force Network Reconnect Retry"):
            st.cache_data.clear() # Wipe cache memory registers
            st.rerun() # Re-execute connection handshake pipeline
            
        st.stop()

# Load tabs into server memory safely
df_orgs = fetch_live_data("Organizations")
df_lookup = fetch_live_data("State_ESF_Lookup")

if df_orgs.empty or df_lookup.empty:
    st.warning("🔄 Connecting to cloud spreadsheets... Please ensure your Google Sheet sharing is public.")
    st.stop()

# Auto-sanitize space and capitalization variations inside spreadsheet rows
df_orgs.columns = df_orgs.columns.str.replace(" ", "_").str.replace("Name", "Name").str.replace("name", "Name")
df_lookup.columns = df_lookup.columns.str.replace(" ", "_")

if "Primary_ESF" in df_orgs.columns and "Primary_ESF_Focus" not in df_orgs.columns:
    df_orgs["Primary_ESF_Focus"] = df_orgs["Primary_ESF"]

# Force coordinate data to numeric types to shield from text-entry pipeline crashes
df_orgs["Latitude"] = pd.to_numeric(df_orgs["Latitude"], errors="coerce")
df_orgs["Longitude"] = pd.to_numeric(df_orgs["Longitude"], errors="coerce")
df_vetted_gps = df_orgs.dropna(subset=["Latitude", "Longitude"]).copy()

# 3. Vectorized Haversine Proximity Logic (Miles Calculator)
def calculate_miles_radius(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return 3956 * c # 3956 represents Earth radius in Miles

# 4. Interactive Configuration Sidebar Panels
st.sidebar.header("🌍 Dynamic Spatial Parameters")

state_options = ["Select State"] + sorted(df_vetted_gps["State_Supported"].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("1. Target State Base:", state_options)

# Isolate cascading filter data pools
state_filtered_df = df_vetted_gps.copy()
available_esfs = ["All ESF Formats"]
available_counties = ["All Counties"]
center_coords = [37.0902, -95.7129]
zoom_factor = 4

if selected_state != "Select State":
    state_filtered_df = df_vetted_gps[df_vetted_gps["State_Supported"].str.upper() == selected_state.upper()]
    
    # Intelligently adapt base coordinates depending on the chosen state zoom window
    if not state_filtered_df.empty:
        center_coords = [state_filtered_df["Latitude"].mean(), state_filtered_df["Longitude"].mean()]
        zoom_factor = 6
        
    # Extract structural counties covered natively in this region
    if "Counties_Covered" in state_filtered_df.columns:
        for val in state_filtered_df["Counties_Covered"].dropna().astype(str):
            for county in val.split(","):
                c_clean = county.strip()
                if c_clean and c_clean.upper() != "ALL COUNTIES" and c_clean not in available_counties:
                    available_counties.append(c_clean)

    # 🔄 DYNAMIC FORMAT SHIFTER: Adapts ESF drop-downs directly to chosen state laws
    state_specific_lookup = df_lookup[df_lookup["Jurisdiction"].str.upper() == selected_state.upper()]
    if not state_specific_lookup.empty:
        available_esfs = ["All ESF Formats"] + (state_specific_lookup["Local_ESF_Number"] + ": " + state_specific_lookup["Local_Official_Title"]).tolist()
    else:
        available_esfs = ["All ESF Formats"] + sorted(state_filtered_df["Primary_ESF_Focus"].dropna().unique().tolist())

# Render context drop-downs
selected_county = st.sidebar.selectbox("2. Narrow Down by County Scope:", available_counties)
selected_esf = st.sidebar.selectbox("3. State-Specific ESF Framework Filter:", available_esfs)

# Filter 4: Miles Radius Selection
st.sidebar.markdown("---")
st.sidebar.subheader("📐 Logistical Range Slider")
radius_limit = st.sidebar.select_slider(
    "Asset Deployment Proximity:",
    options=["Unrestricted Focus", "50 Miles", "100 Miles", "150 Miles", "200 Miles"]
)

# Apply context-based filters
filtered_df = state_filtered_df.copy()
if selected_county != "All Counties":
    filtered_df = filtered_df[filtered_df["Counties_Covered"].astype(str).str.contains(selected_county, case=False)]

if selected_esf != "All ESF Formats" and selected_state != "Select State":
    esf_code = selected_esf.split(":").strip()
    filtered_df = filtered_df[filtered_df["Primary_ESF_Focus"].astype(str).str.contains(esf_code, case=False)]

# 5. Core Interface Split Windows
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Interactive Draw & Filter Canvas")
    st.caption("🖱️ Use the shapes toolbar on the left of the map to draw custom box or shape regions. The system will filter automatically below.")
    
    # Initialize Folium container map
    m = folium.Map(location=center_coords, zoom_start=zoom_factor, tiles="CartoDB positron")
    
    # Inject the Leaflet Draw plugin module to accept mouse interaction bounding boxes
    Draw(
        export=False,
        filename='drawn_regions.geojson',
        position='topleft',
        draw_options={
            'polyline': False, 'circle': False, 'marker': False, 
            'circlemarker': False, 'polygon': True, 'rectangle': True
        }
    ).add_to(m)
    
    # Map dots plotting loop 
    for idx, row in filtered_df.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=6,
            color="#1f77b4",
            fill=True,
            fill_color="#1f77b4",
            fill_opacity=0.7,
            popup=f"<b>{row['Organization_Name']}</b><br>{row['Primary_ESF_Focus']}"
        ).add_to(m)
        
    # Bind map to Streamlit framework layout context
    map_output = st_folium(m, width="100%", height=550, key="folium_canvas")

    # 🖱️ MOUSE HANDLER: Extract coordinates if user draws a region on the canvas
    drawn_geojson = map_output.get("last_active_drawing")
    if drawn_geojson and "geometry" in drawn_geojson:
        geometry_type = drawn_geojson["geometry"]["type"]
        coords = drawn_geojson["geometry"]["coordinates"]
        
        if geometry_type in ["Polygon", "Rectangle"]:
            lats = [c for c in coords]
            lons = [c for c in coords]
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)
            
            # Apply geometric bounding box data slicing dynamically 
            filtered_df = filtered_df[
                (filtered_df["Latitude"] >= min_lat) & (filtered_df["Latitude"] <= max_lat) &
                (filtered_df["Longitude"] >= min_lon) & (filtered_df["Longitude"] <= max_lon)
            ]

    # Apply the mathematical Haversine Proximity checks if a mile slider parameter is set
    if radius_limit != "Unrestricted Focus" and not filtered_df.empty:
        max_miles = int(radius_limit.split(" "))
        center_lat, center_lon = center_coords, center_coords
        
        filtered_df["Miles_Distance"] = calculate_miles_radius(
            center_lat, center_lon, filtered_df["Latitude"], filtered_df["Longitude"]
        )
        filtered_df = filtered_df[filtered_df["Miles_Distance"] <= max_miles]

with col2:
    st.subheader("🏢 Expanded Asset Log")
    if not filtered_df.empty:
        selected_name = st.selectbox("Inspect profile metrics:", filtered_df["Organization_Name"].dropna().tolist())
        if selected_name:
            profile = filtered_df[filtered_df["Organization_Name"] == selected_name].iloc[0]
            st.markdown(f"### **{profile['Organization_Name']}**")
            st.markdown(f"**Jurisdiction Reach:** `{profile.get('Operation_Scope','Statewide')}`")
            st.info(f"💪 **Logistical Capacity:**\n{profile.get('Resource_Capacity','No resource notes found.')}")
            
            # Click to Call Protocol Configuration
            phone = str(profile.get("Phone", ""))
            if phone and phone != "nan":
                st.markdown(f'👉 <a href="tel:{phone.replace("-","")}" style="font-size:18px; font-weight:bold; color:#1f77b4; text-decoration:none;">📲 Click to Call: {phone}</a>', unsafe_allow_html=True)
    else:
        st.write("No registered entities found within this localized scope matrix.")

st.write("---")
st.subheader("📊 Dynamic Data Records Pipeline Table")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
