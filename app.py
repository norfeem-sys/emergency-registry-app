import streamlit as st
import pandas as pd

st.set_page_config(page_title="Emergency Registry", layout="wide")
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Database Hub")

# 🔴 Direct connection to your live Google Sheet layout link
LIVE_SPREADSHEET_URL = "https://google.com"

@st.cache_data(ttl=10) # Updates lightning fast every 10 seconds for real-time testing
def load_live_data(sheets_url, sheet_name):
    csv_url = sheets_url.replace("/edit?usp=sharing", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
    csv_url = csv_url.replace("/edit#gid=", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip() # defensive whitespace trim on headers
    return df

# Load tabs safely
try:
    df_orgs = load_live_data(LIVE_SPREADSHEET_URL, "Organizations")
    df_lookup = load_live_data(LIVE_SPREADSHEET_URL, "State_ESF_Lookup")
    df_vols = load_live_data(LIVE_SPREADSHEET_URL, "Volunteers")
except Exception as e:
    st.error(f"❌ Connection Error: Could not read your Google Sheet tabs. Check permissions. Details: {e}")
    st.stop()

# Sidebar Navigation Panel
st.sidebar.header("Compass Dashboard Navigation")
app_mode = st.sidebar.radio("Go to view:", ["Public Interactive Map", "🔒 Master Admin Reports"])

# Defensive column mapping support to account for manual sheet header variations
for col in ["State_Supported", "State Supported"]:
    if col in df_orgs.columns:
        df_orgs["State_Supported_Clean"] = df_orgs[col]
if "State_Supported_Clean" not in df_orgs.columns:
    df_orgs["State_Supported_Clean"] = "FL"

if app_mode == "Public Interactive Map":
    st.sidebar.subheader("Map Filters")
    selected_state = st.sidebar.selectbox("Select State Horizon:", ["FL", "TX", "GA", "All States"])
    
    # Filter primary tracking matrix data matches
    filtered_df = df_orgs[(df_orgs["State_Supported_Clean"] == selected_state) | (df_orgs["State_Supported_Clean"] == "All States") | (df_orgs["State_Supported_Clean"] == "Global")]
    
    # 🌍 VISUAL MAP ENGINE PLOTTING
    st.markdown("### 📍 Active Logistics Map Representation")
    
    # Standardize coordinate header tracking variants
    lat_col = next((c for c in df_orgs.columns if c.lower() in ["latitude", "lat"]), None)
    lon_col = next((c for c in df_orgs.columns if c.lower() in ["longitude", "lon", "long"]), None)
    
    if lat_col and lon_col:
        # Convert text columns safely to numbers for map rendering parameters
        map_df = filtered_df.copy()
        map_df[lat_col] = pd.to_numeric(map_df[lat_col], errors='coerce')
        map_df[lon_col] = pd.to_numeric(map_df[lon_col], errors='coerce')
        map_ready = map_df.dropna(subset=[lat_col, lon_col])
        
        if not map_ready.empty:
            # Rename headers quickly to match native streamlit mapping expectations
            map_render = map_ready.rename(columns={lat_col: 'latitude', lon_col: 'longitude'})
            st.map(map_render[['latitude', 'longitude']], size=25)
        else:
            st.info("ℹ️ Showing National view. Add explicit coordinates under 'Latitude' and 'Longitude' columns in your sheet to pin active locations.")
            # Default fallback visual center matrix frame
            fallback_us_coords = pd.DataFrame({'latitude': [28.3852, 31.9686, 32.1656], 'longitude': [-81.5639, -99.9018, -82.9001]})
            st.map(fallback_us_coords, zoom=4)
    else:
        st.info("ℹ️ To activate live coordinate map pins, simply add 'Latitude' and 'Longitude' columns to your Google Sheet.")
        fallback_us_coords = pd.DataFrame({'latitude': [28.3852], 'longitude': [-81.5639]})
        st.map(fallback_us_coords, zoom=4)

    st.write("---")

    # 📊 TOTAL GRID VISIBILITY UNLOCKED
    st.markdown(f"#### 📋 Unrestricted Spreadsheet Data Records (`{selected_state}` View)")
    st.write("Scroll right on the table below to view all data fields, links, and documents straight out of your spreadsheet:")
    
    # Displays EVERY column cleanly without hiding anything
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.write("---")
    
    # 🔍 INDIVIDUAL PROFILE EXPANSION PANEL
    col1, col2 = st.columns([1, 2])
    with col1:
        org_list = filtered_df["Organization_Name"].dropna().tolist() if "Organization_Name" in filtered_df.columns else []
        selected_org = st.selectbox("Select an organization to expand live details:", org_list)
        
    with col2:
        if selected_org and not filtered_df.empty:
            org_rows = filtered_df[filtered_df["Organization_Name"] == selected_org]
            if not org_rows.empty:
                org_row = org_rows.iloc[0]
                
                st.markdown(f"#### 🏢 {org_row.get('Organization_Name', selected_org)}")
                
                # Dynamic metadata printing for whatever columns exist
                for key, val in org_row.items():
                    if str(val) != 'nan' and key not in ['Organization_Name', 'Latitude', 'Longitude', 'State_Supported_Clean']:
                        st.write(f"• **{key.replace('_',' ')}**: {val}")
                
                # Check for phone fields to generate active dispatch lines
                phone_key = next((k for k in org_row.index if 'phone' in k.lower() or 'contact' in k.lower()), None)
                if phone_key and str(org_row[phone_key]) != 'nan':
                    raw_phone = str(org_row[phone_key]).split('.')[0]
                    phone_url = f"tel:{raw_phone.replace('-', '').replace(' ', '').replace('+', '')}"
                    st.markdown(f'👉 <a href="{phone_url}" style="font-size:18px; font-weight:bold; color:#1f77b4; text-decoration:none;">📲 Click to Call: {raw_phone}</a>', unsafe_allow_html=True)

elif app_mode == "🔒 Master Admin Reports":
    st.subheader("📊 Administrative System Integrity Analytics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Agencies Registered", len(df_orgs))
    
    v_col = next((c for c in df_orgs.columns if 'verify' in c.lower()), None)
    unverified_count = len(df_orgs[df_orgs[v_col].astype(str).str.upper().str.strip() == "FALSE"]) if v_col else 0
    c2.metric("⚠️ Pending Attestation Check", unverified_count, delta=f"{unverified_count} Alerts Pending", delta_color="inverse")
    c3.metric("Live Active Volunteers Registered", len(df_vols))
    
    st.markdown("#### Full System Organizational Health Table")
    st.dataframe(df_orgs, use_container_width=True, hide_index=True)
