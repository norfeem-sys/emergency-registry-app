import streamlit as st
import pandas as pd

st.set_page_config(page_title="Emergency Registry", layout="wide")
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Database")

# 🔴 YOUR GOOGLE SHEET LINK IS DIRECTLY CODED BELOW:
LIVE_SPREADSHEET_URL = "https://google.com"

@st.cache_data(ttl=30) # Checks your Google Sheet for updates every 30 seconds
def load_live_data(sheets_url, sheet_name):
    csv_url = sheets_url.replace("/edit?usp=sharing", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
    csv_url = csv_url.replace("/edit#gid=", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
    df = pd.read_csv(csv_url)
    # DEFENSIVE CLEANING: Strip accidental hidden trailing spaces from your spreadsheet headers
    df.columns = df.columns.str.strip()
    return df

# Load separate tabs safely using your direct link
try:
    df_orgs = load_live_data(LIVE_SPREADSHEET_URL, "Organizations")
    df_lookup = load_live_data(LIVE_SPREADSHEET_URL, "State_ESF_Lookup")
    df_vols = load_live_data(LIVE_SPREADSHEET_URL, "Volunteers")
except Exception as e:
    st.error(f"❌ Connection Error: Could not read tabs. Check sharing settings on your Google Sheet. Details: {e}")
    st.stop()

# Sidebar Navigation Panel
st.sidebar.header("Compass Dashboard Navigation")
app_mode = st.sidebar.radio("Go to view:", ["Public Interactive Map", "🔒 Master Admin Reports"])

# Ensure critical tracking columns exist natively or create fallback spaces to prevent crashes
if "State_Supported" not in df_orgs.columns:
    # If there is a space typo in the sheet (e.g. 'State Supported'), map it over automatically
    if "State Supported" in df_orgs.columns:
        df_orgs["State_Supported"] = df_orgs["State Supported"]
    else:
        df_orgs["State_Supported"] = "FL" # Safety fallback standard default value

if "Primary_ESF_Focus" not in df_orgs.columns and "Primary ESF Focus" in df_orgs.columns:
    df_orgs["Primary_ESF_Focus"] = df_orgs["Primary ESF Focus"]

if "Resource_Capacity" not in df_orgs.columns and "Resource Capacity" in df_orgs.columns:
    df_orgs["Resource_Capacity"] = df_orgs["Resource Capacity"]

if "Secondary_ESFs" not in df_orgs.columns and "Secondary ESFs" in df_orgs.columns:
    df_orgs["Secondary_ESFs"] = df_orgs["Secondary ESFs"]

if "Data_Verified" not in df_orgs.columns and "Data Verified" in df_orgs.columns:
    df_orgs["Data_Verified"] = df_orgs["Data Verified"]

if app_mode == "Public Interactive Map":
    st.sidebar.subheader("Map Filters")
    selected_state = st.sidebar.selectbox("Select State Horizon:", ["FL", "TX", "GA", "All States"])
    
    # Filter dataset matches safely using the sanitized variables
    filtered_df = df_orgs[(df_orgs["State_Supported"] == selected_state) | (df_orgs["State_Supported"] == "All States") | (df_orgs["State_Supported"] == "Global")]
    
    col1, col2 = st.columns(2) # Fixes the blank columns error explicitly passing 2 layout zones
    with col1:
        st.markdown(f"### Active Responders Supporting: `{selected_state}`")
        display_cols = [c for c in ["Organization_Name", "Primary_ESF_Focus", "State_Supported"] if c in filtered_df.columns]
        st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
        
        org_list = filtered_df["Organization_Name"].dropna().tolist() if "Organization_Name" in filtered_df.columns else []
        selected_org = st.selectbox("Select an organization to expand live details:", org_list)
        
    with col2:
        if selected_org and not filtered_df.empty:
            # Fixes row indexing using dynamic text matching with safety fallbacks
            org_rows = filtered_df[filtered_df["Organization_Name"] == selected_org]
            if not org_rows.empty:
                org_row = org_rows.iloc[0] # Explicitly fetch index row index position 0 safely
                
                st.markdown(f"#### 🏢 {org_row.get('Organization_Name', selected_org)}")
                st.markdown(f"**Primary Task Matrix:** `{org_row.get('Primary_ESF_Focus', 'N/A')}`")
                st.markdown(f"**Secondary Assets:** *{org_row.get('Secondary_ESFs', 'N/A')}*")
                st.info(f"**Logistical Capacity:**\n{org_row.get('Resource_Capacity', 'No description logged.')}")
                
                raw_phone = str(org_row.get('Phone', ''))
                if raw_phone and raw_phone != 'nan':
                    phone_url = f"tel:{raw_phone.replace('-', '').replace(' ', '')}"
                    st.markdown(f'👉 <a href="{phone_url}" style="font-size:18px; font-weight:bold; color:#1f77b4; text-decoration:none;">📲 Click to Call: {raw_phone}</a>', unsafe_allow_html=True)

elif app_mode == "🔒 Master Admin Reports":
    st.subheader("📊 Administrative System Integrity Analytics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Agencies Registered", len(df_orgs))
    
    # Calculate unverified count dynamically safely tracking column names strings
    v_col = "Data_Verified" if "Data_Verified" in df_orgs.columns else ("Data Verified" if "Data Verified" in df_orgs.columns else None)
    if v_col:
        unverified_count = len(df_orgs[df_orgs[v_col].astype(str).str.upper().str.strip() == "FALSE"])
    else:
        unverified_count = 0
        
    c2.metric("⚠️ Pending Attestation Check", unverified_count, delta=f"{unverified_count} Alerts Pending", delta_color="inverse")
    c3.metric("Live Active Volunteers", len(df_vols) if 'df_vols' in locals() else 0)
    
    st.markdown("#### Organizations Missing Data Sign-off")
    if v_col and "Organization_Name" in df_orgs.columns:
        unverified_table = df_orgs[df_orgs[v_col].astype(str).str.upper().str.strip() == "FALSE"]
        phone_col = "Phone" if "Phone" in unverified_table.columns else df_orgs.columns[0]
        st.dataframe(unverified_table[["Organization_Name", "State_Supported", phone_col]], use_container_width=True, hide_index=True)
