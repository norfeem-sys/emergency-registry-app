import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

# Must remain the very first Streamlit command
st.set_page_config(page_title="Emergency Registry Command Canvas", layout="wide")

# ==============================================================================
# 🎨 HORIZONTAL TACTICAL NAVIGATION BAR
# ==============================================================================
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
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="nav-container">
            <a class="nav-link" href="#about">ℹ️ Operational About</a>
            <a class="nav-link" href="#instructions">📖 Dispatch Instructions</a>
            <a class="nav-link" href="#contributors">🤝 Agency Governance</a>
            <a class="nav-link" href="http://localhost:8502" target="_blank">🏢 Open Asset Registration Portal ↗️</a>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN HEADERS ---
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("Live Multi-State Disaster Response Command Board & Spatial Sandbox")

# Injecting the Navigation Bar
render_navigation_menu()

# 🗄️ INTERNAL BACKUP DATA ENGINE (Synchronized to 18-Field Corporate Schema)
def load_backup_sandbox_data():
    backup_payload = {
        "Org_ID": ["ORG-FL01", "ORG-US02", "ORG-TX03", "ORG-GA04", "ORG-FL05"],
        "Organization_Name": ["Florida Baptist Disaster Relief", "ITDRC", "Texas Response Network", "Georgia Feeding VOAD", "Sarasota Local CERT"],
        "FEIN": ["12-3456789", "98-7654321", "55-4443322", "11-2223334", "99-8887776"],
        "Operation_Scope": ["Statewide", "National", "Statewide", "Statewide", "Local / Mutual Aid"],
        "State_Supported": ["FL", "All States", "TX", "GA", "FL"],
        "Counties_Covered": ["All Counties", "All Counties", "All Counties", "All Counties", "Sarasota, Manatee"],
        "Primary_Phone": ["1-800-555-0122", "1-877-387-3646", "1-555-555-0199", "1-555-555-0144", "1-555-555-0133"],
        "Primary_ESF": ["ESF #6: Mass Care", "ESF #2: Communications", "ESF #13: Public Safety", "ESF #6: Mass Care", "ESF #9: Search & Rescue"],
        "Secondary_ESFs": ["ESF #11", "ESF #15", "ESF #1, ESF #12", "ESF #11", "N/A"],
        "Resource_Inventory": ["3 Mobile Kitchens (30k meals/day), 4 Chainsaw Teams", "20 Satellite Internet Terminals, Mesh WiFi Towers", "15 High-Water Rescue Vehicles, 40 Ham Operators", "2 Bulk Food Warehouses, 10 Refrigerated Trailers", "2 Light Rescue Squads, 25 Vetted Members"],
        "Org_Logo_URL": [None, None, None, None, None],
        "Tax_Exempt_Doc_URL": [None, None, None, None, None],
        "Account_Status": ["Active", "Active", "Active", "Active", "Active"],
        "Data_Verified": ["Verified", "Verified", "Pending", "Verified", "Pending"],
        "Verification_Time": ["2026-09-01 10:00", "2026-09-02 14:30", "N/A", "2026-08-15 09:15", "N/A"],
        "Verifying_Email": ["admin@fema.gov", "verify@nims.org", "N/A", "admin@fema.gov", "N/A"],
        "Latitude": [28.5383, 37.0902, 31.9686, 32.1656, 27.3364],
        "Longitude": [-81.3792, -95.7129, -99.9018, -82.9001, -82.5307]
    }
    return pd.DataFrame(backup_payload)

SPREADSHEET_ID = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"
url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Organizations"

try:
    df = pd.read_csv(url, timeout=3)
    df.columns = df.columns.str.strip()
    
    # Strict Account Status Filter Matrix Intercept
    if "Account_Status" in df.columns:
        df = df[df["Account_Status"].str.lower() == "active"]
except Exception:
    df = load_backup_sandbox_data()

# Ensure mandatory layout lat/long columns are parsed numerically safely
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df = df.dropna(subset=["Latitude", "Longitude"])

# ==============================================================================
# 🌍 DYNAMIC TIERED JURISDICTION SIDEBAR INTERFACE
# ==============================================================================
st.sidebar.header("🌍 Operational Filters")

org_scope = st.sidebar.radio(
    "1. Select Operational Horizon Tier:",
    options=["🇺🇸 National Support", "🏛️ Statewide Support", "📍 Local / Mutual Aid"]
)

filtered_df = df.copy()
center = [37.0902, -95.7129]
zoom = 4

# Initialize dynamic cascading context strings
available_counties = ["All Counties"]

if org_scope == "🇺🇸 National Support":
    filtered_df = filtered_df[filtered_df["Operation_Scope"].str.lower() == "national"]
    sel_state = "All States"
    sel_county = "All Counties"
    st.sidebar.info("ℹ️ National Tier active. County boundaries bypassed.")

elif org_scope == "🏛️ Statewide Support":
    state_options = sorted([s for s in df["State_Supported"].unique() if str(s).lower() != "all states"])
    sel_state = st.sidebar.selectbox("2. Select Target State Horizon:", state_options)
    
    filtered_df = df[(df["State_Supported"].str.upper() == sel_state.upper()) & (df["Operation_Scope"].str.lower() == "statewide")]
    if not filtered_df.empty:
        center = [filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()]
        zoom = 6
    sel_county = "All Counties"
    st.sidebar.caption("🔒 *County mapping locked to Statewide footprint.*")

elif org_scope == "📍 Local / Mutual Aid":
    state_options = sorted([s for s in df["State_Supported"].unique() if str(s).lower() != "all states"])
    sel_state = st.sidebar.selectbox("2. Select Local Base State:", state_options)
    state_df = df[df["State_Supported"].str.upper() == sel_state.upper()]
    
    for val in state_df["Counties_Covered"].dropna().astype(str):
        for c in val.split(","):
            c_clean = c.strip()
            if c_clean and c_clean.lower() != "all counties" and c_clean not in available_counties:
                available_counties.append(c_clean)
                
    sel_county = st.sidebar.selectbox("3. Narrow Down Local County Scope:", available_counties)
    
    if sel_county != "All Counties":
        filtered_df = state_df[state_df["Counties_Covered"].astype(str).str.contains(sel_county, case=False)]
    else:
        filtered_df = state_df
        
    if not filtered_df.empty:
        center = [filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()]
        zoom = 7

# Filter 4: Framework ESF Alignment Selector
st.sidebar.markdown("---")
esf_options = ["All Active ESF Formats"] + sorted(df["Primary_ESF"].dropna().unique().tolist())
sel_esf = st.sidebar.selectbox("4. Framework Specific ESF Filter:", esf_options)

if sel_esf != "All Active ESF Formats":
    filtered_df = filtered_df[filtered_df["Primary_ESF"] == sel_esf]

# Filter 5: Logistical Range Selector
st.sidebar.markdown("---")
st.sidebar.subheader("📐 Logistical Range Slider")
radius_limit = st.sidebar.select_slider("Asset Search Radius Limit:", options=["Unrestricted Focus", "50 Miles", "100 Miles", "150 Miles", "200 Miles"])

# Filter 6: Display Switch Controls
st.sidebar.subheader("👁️ Display Preferences")
show_metrics = st.sidebar.toggle("Show Operational Resource Metrics", value=True)

# ==============================================================================
# 🗺️ PANORAMIC DRAW CANVAS WINDOW (Hiding Coordinates if Neutralized at 0.0)
# ==============================================================================
st.subheader("📍 Interactive Panoramic Drawing Canvas")
st.caption("🖱️ Click geometric tools on the left to draw boundary exclusions. Data blocks filter automatically below.")

m = folium.Map(
    location=center, 
    zoom_start=zoom, 
    tiles="CartoDB positron",
    attr="© OpenStreetMap contributors | © CartoDB"
)
Draw(position='topleft', draw_options={'polyline':False, 'circle':False, 'marker':False, 'polygon':True, 'rectangle':True}).add_to(m)

# Drop marker points ONLY if the coordinates have been populated beyond form fallbacks (0.0)
plotable_df = filtered_df[(filtered_df["Latitude"] != 0.0) & (filtered_df["Longitude"] != 0.0)]

for idx, row in plotable_df.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]], 
        radius=6, 
        color="#1f77b4", 
        fill=True, 
        fill_opacity=0.7, 
        popup=f"<b>{row['Organization_Name']}</b><br>{row['Primary_ESF']}"
    ).add_to(m)

map_out = st_folium(m, width=1400, height=400, key="canvas")

# Mouse Bounding Box Processing Engine
drawn = map_out.get("last_active_drawing")
if drawn and "geometry" in drawn and "coordinates" in drawn["geometry"]:
    try:
        poly_coords = drawn["geometry"]["coordinates"]
        lons = [float(point) for point in poly_coords]
        lats = [float(point) for point in poly_coords]
        filtered_df = filtered_df[(filtered_df["Latitude"] >= min(lats)) & (filtered_df["Latitude"] <= max(lats)) & (filtered_df["Longitude"] >= min(lons)) & (filtered_df["Longitude"] <= max(lons))]
        st.sidebar.success("🎯 Map filtered by drawn boundaries!")
    except Exception:
        pass

st.write("---")

# ==============================================================================
# 📊 LOWER MATRIX GRID & COMPREHENSIVE RECONNAISSANCE DOSSIER
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 Expanded Reconnaissance Dossier")
    if not filtered_df.empty:
        chosen = st.selectbox("Inspect profile metrics:", filtered_df["Organization_Name"].tolist())
        
        # PULL ROW USING THE RE-ENGINEERED COMPREHENSIVE SCHEMA MATRICES (.iloc fix)
        rec = filtered_df[filtered_df["Organization_Name"] == chosen].iloc[0]
        
        # Identity Header Layer with optional Branding Logo URL support
        if "Org_Logo_URL" in rec and pd.notna(rec["Org_Logo_URL"]) and str(rec["Org_Logo_URL"]).strip() != "":
            st.image(rec["Org_Logo_URL"], width=90)
            
        st.markdown(f"### 📋 {rec['Organization_Name']}")
        
        # Regulatory Administrative Verification Shield
        v_status = str(rec.get("Data_Verified", "Pending")).lower()
        if v_status == "verified":
            st.success(f"🛡️ Verified Profile (Audited by {rec.get('Verifying_Email', 'Admin')} at {rec.get('Verification_Time', 'N/A')})")
        else:
            st.warning("⚠️ Unverified Sandbox Entry - Document Compliance Check Pending")
            
        # 1-to-1 Schema Fields Mapped to Dossier Readouts
        st.markdown(f"**🔑 Registry ID Token:** `{rec.get('Org_ID', 'N/A')}` | **FEIN Tax ID:** `{rec.get('FEIN', 'N/A')}`")
        st.markdown(f"**📞 Primary Dispatch Hotline:** `{rec.get('Primary_Phone', 'N/A')}`")
        st.markdown(f"**🗺️ Operational Footprint Tier:** `{rec.get('Operation_Scope', 'N/A')}`")
        st.markdown(f"**📍 Jurisdiction Alignment:** `{rec.get('State_Supported', 'N/A')}`")
        st.markdown(f"**🗺️ Counties Covered:** `{rec.get('Counties_Covered', 'N/A')}`")
        st.markdown(f"**⚡ Primary Response Role:** `{rec.get('Primary_ESF', 'N/A')}`")
        
        if "Secondary_ESFs" in rec and pd.notna(rec["Secondary_ESFs"]) and str(rec["Secondary_ESFs"]).strip() != "":
            st.markdown(f"**🔗 Secondary Cross-Alignments:** `{rec['Secondary_ESFs']}`")
            
        if "Tax_Exempt_Doc_URL" in rec and pd.notna(rec["Tax_Exempt_Doc_URL"]) and str(rec["Tax_Exempt_Doc_URL"]).strip() != "":
            st.markdown(f"**📄 Document Compliance Trace:** [View Tax-Exempt Form]({rec['Tax_Exempt_Doc_URL']})")
            
        st.markdown("""**📦 Mobilization Resource Inventory & Equipment Caches:**""")
        st.info(rec.get("Resource_Inventory", "No capability assets cataloged."))
    else:
        st.warning("⚠️ No organizations available to build profile details.")

with col2:
    if show_metrics:
        st.subheader("📊 Operational Resource Metrics")
        
        total_orgs = len(filtered_df)
        states_touched = filtered_df["State_Supported"].nunique() if total_orgs > 0 else 0
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("Active Response Groups", f"{total_orgs} Orgs")
        m_col2.metric("Covered Jurisdictions", f"{states_touched} States")
        
        st.markdown("""**📋 Tactical Sandbox View**""")
        st.dataframe(
            filtered_df[["Organization_Name", "Operation_Scope", "Primary_Phone", "Primary_ESF"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.subheader("📊 Operational Resource Metrics")
        st.caption("🔒 *Metrics hidden by user preferences sidebar switch.*")

# ==============================================================================
# 📑 ANCHORED APPARATUS FOOTER BLOCK
# ==============================================================================
st.write("---")
f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    st.markdown('<div id="about"></div>', unsafe_allow_html=True)
    st.subheader("ℹ️ About the Sandbox")
    st.write("This sandbox tracks multi-state assets, emergency framework points, and disaster mitigation pipelines using Streamlit mapping configurations.")

with f_col2:
    st.markdown('<div id="instructions"></div>', unsafe_allow_html=True)
    st.subheader("📖 Instructions")
    st.write("1. Narrow deployments using the left sidebar parameters.")
    st.write("2. Select box or polygon tools to isolate geometric areas on the fly.")

with f_col3:
    st.markdown('<div id="contributors"></div>', unsafe_allow_html=True)
    st.subheader("🤝 Contributors")
    st.write("Maintained by federal agency technical components, partner NGOs, and disaster management engineering associations.")
