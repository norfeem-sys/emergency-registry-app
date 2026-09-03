import streamlit as st
import pandas as pd

st.set_page_config(page_title="Emergency Registry", layout="wide")
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Database with Geospatial Mapping")

LIVE_SPREADSHEET_URL = "https://google.com"

@st.cache_data(ttl=30) # Checks your Google Sheet for live updates every 30 seconds
def load_live_data(sheets_url, sheet_name):
    csv_url = sheets_url.replace("/edit?usp=sharing", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
    csv_url = csv_url.replace("/edit#gid=", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
    return pd.read_csv(csv_url)

try:
    df_orgs = load_live_data(LIVE_SPREADSHEET_URL, "Organizations")
    df_lookup = load_live_data(LIVE_SPREADSHEET_URL, "State_ESF_Lookup")
    df_vols = load_live_data(LIVE_SPREADSHEET_URL, "Volunteers")
except Exception as e:
    st.error(f"❌ Connection Error: Could not read tabs. Check sharing settings on your Google Sheet. Details: {e}")
    st.stop()

st.sidebar.header("Compass Dashboard Navigation")
app_mode = st.sidebar.radio("Go to view:", ["Public Interactive Map", "🔒 Master Admin Reports"])

if app_mode == "Public Interactive Map":
    st.sidebar.subheader("Map Filters")
    selected_state = st.sidebar.selectbox("Select State Horizon:", ["FL", "TX", "GA", "All States"])
    
    filtered_df = df_orgs[(df_orgs["State_Supported"] == selected_state) | (df_orgs["State_Supported"] == "All States") | (df_orgs["State_Supported"] == "Global")]
    
    # 🌍 LIVE GEOSPATIAL MAP GENERATION
    st.markdown("### 📍 Active Logistics Map Representation")
    # Filter out rows that are missing coordinate details to prevent map rendering errors
    map_data = filtered_df_orgs=filtered_df.dropna(subset=['Latitude', 'Longitude'])
    
    if not map_data.empty:
        # Renders a physical interactive mapping module using PyDeck/Mapbox for free
        st.map(map_data[['Latitude', 'Longitude']], size=20)
    else:
        st.info("ℹ️ Map pins hidden. Add Latitude and Longitude values to your Google Sheet rows to drop physical markers.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### 📋 Active Responders Supporting: `{selected_state}`")
        st.dataframe(filtered_df[["Organization_Name", "Primary_ESF_Focus", "State_Supported"]], use_container_width=True, hide_index=True)
        selected_org = st.selectbox("Select an organization to expand live details:", filtered_df["Organization_Name"].tolist())
        
    with col2:
        if selected_org:
            org_row = filtered_df[filtered_df["Organization_Name"] == selected_org].iloc[0]
            st.markdown(f"#### 🏢 {org_row['Organization_Name']}")
            st.markdown(f"**Primary Task Matrix:** `{org_row['Primary_ESF_Focus']}`")
            st.markdown(f"**Secondary Assets:** *{org_row['Secondary_ESFs']}*")
            st.info(f"**Logistical Capacity:**\n{org_row['Resource_Capacity']}")
            
            phone_url = f"tel:{str(org_row['Phone']).replace('-', '')}"
            st.markdown(f'👉 <a href="{phone_url}" style="font-size:18px; font-weight:bold; color:#1f77b4; text-decoration:none;">📲 Click to Call: {org_row["Phone"]}</a>', unsafe_allow_html=True)

elif app_mode == "🔒 Master Admin Reports":
    st.subheader("📊 Administrative System Integrity Analytics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Agencies Registered", len(df_orgs))
    
    unverified_count = len(df_orgs[df_orgs["Data_Verified"].astype(str).str.upper() == "FALSE"])
    c2.metric("⚠️ Pending Attestation Check", unverified_count, delta=f"{unverified_count} Alerts Pending", delta_color="inverse")
    c3.metric("Live Active Volunteers", len(df_vols))
    
    st.markdown("#### Organizations Missing Data Sign-off")
    unverified_table = df_orgs[df_orgs["Data_Verified"].astype(str).str.upper() == "FALSE"]
    st.dataframe(unverified_table[["Organization_Name", "State_Supported", "Phone"]], use_container_width=True, hide_index=True)

