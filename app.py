import streamlit as st
import pandas as pd

st.set_page_config(page_title="Emergency Registry - UI Review", layout="wide")
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Database Hub — Phase 1 UI Review Protocol")

# 🔴 RESTORED: YOUR EXACT FULL GOOGLE SPREADSHEET URL
FULL_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY/edit?usp=sharing"

@st.cache_data(ttl=5)
def load_live_data(sheet_name):
    # FIXED: Restored clean string split logic to properly append gviz export format
    base_url = FULL_SPREADSHEET_URL.split("/edit")[0]
    gviz_export_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(gviz_export_url)
    df.columns = df.columns.str.strip() # Defensive cleanup for column headers
    return df

# Load separate tabs directly into memory by their literal text names
try:
    df_orgs = load_live_data("Organizations")
    df_lookup = load_live_data("State_ESF_Lookup")
    df_vols = load_live_data("Volunteers")
except Exception as e:
    st.error(f"❌ Connection Error: Google Sheet connection blocked. Please check that 'Anyone with the link can view' is turned on. Details: {e}")
    st.stop()

# ==============================================================================
# 🛠️ COMPASS FEATURE: SCREEN-BY-SCREEN PHASE 1 REVIEW GATEWAY
# ==============================================================================
st.sidebar.markdown("### 🏛️ Phase 1: UI Sign-Off Controls")
ui_review_gate = st.sidebar.selectbox(
    "Select Screen to Review (Task T1.0a-c):", 
    ["Screen 2: Geospatial Map Dashboard (T1.0b)", "Screen 1: Volunteer Registration Flow (T1.0a)", "Screen 3: Master Admin Reports (T1.0c)"]
)

# 🔄 STATE TRANSLATOR ENGINE
def clean_state_value(val):
    text = str(val).strip().upper()
    if "FLORIDA" in text or text == "FL": return "FL"
    elif "TEXAS" in text or text == "TX": return "TX"
    elif "GEORGIA" in text or text == "GA": return "GA"
    elif "GLOBAL" in text: return "Global"
    elif "ALL" in text: return "All States"
    return text

state_col = next((c for c in df_orgs.columns if 'state' in c.lower()), None)
if state_col:
    df_orgs["State_Supported_Clean"] = df_orgs[state_col].apply(clean_state_value)
else:
    df_orgs["State_Supported_Clean"] = "FL"

# 📊 DATA LINKING ENGINE: Match Volunteers to Organizations
if 'Associated_Org_ID' in df_vols.columns and 'Org_ID' in df_orgs.columns:
    active_statuses = ["AVAILABLE", "DEPLOYED", "STANDBY"]
    active_vols = df_vols[df_vols["Availability_Status"].astype(str).str.upper().str.strip().isin(active_statuses)]
    vol_counts = active_vols["Associated_Org_ID"].value_counts().to_dict()
    df_orgs["Active_Volunteer_Count"] = df_orgs["Org_ID"].map(vol_counts).fillna(0).astype(int)
else:
    df_orgs["Active_Volunteer_Count"] = 0

# ==============================================================================
# SCREEN RENDER MANAGEMENT
# ==============================================================================
if ui_review_gate == "Screen 1: Volunteer Registration Flow (T1.0a)":
    st.info("💡 **Stakeholder Review Focus (T1.0a):** Validate nested hierarchy (County vs State vs Global Red Cross Tiering) and verify skill onboarding loops.")
    st.subheader("📝 Live Volunteer Intake Wireframe Engine")
    
    with st.form("mock_reg_form"):
        st.text_input("Full Legal Name:")
        st.selectbox("Operational Tier Affiliation:", ["Hyper-Local County Unit", "State Emergency Management Branch", "Global NGO / Red Cross Network"])
        st.multiselect("Select FEMA ESF Certified Skillsets:", df_lookup["ESF_Code"].unique() if "ESF_Code" in df_lookup.columns else ["ESF-6", "ESF-8", "ESF-9"])
        st.form_submit_button("Submit Registration Profile")

elif ui_review_gate == "Screen 2: Geospatial Map Dashboard (T1.0b)":
    st.info("💡 **Critical Stakeholder Review Focus (T1.0b):** Confirm cross-filtering matrix logic and county visibility upon deep zoom-in.")
    
    # 🌍 EXPANDED GEOSPATIAL MAP FILTERS PANEL
    st.sidebar.subheader("🌍 Multi-Variable Matrix Filters")
    selected_state = st.sidebar.selectbox("1. Target State Filter:", ["All States", "FL", "TX", "GA"])
    
    # County Filter Configuration
    county_col = next((c for c in df_orgs.columns if 'county' in c.lower() or 'counties' in c.lower()), None)
    unique_counties = ["All Counties"]
    
    if county_col and not df_orgs.empty:
        raw_counties = df_orgs[county_col].dropna().astype(str).tolist()
        for item in raw_counties:
            for sub_item in item.split(","):
                cleaned_item = sub_item.strip()
                if cleaned_item and cleaned_item.upper() != "ALL COUNTIES" and cleaned_item not in unique_counties:
                    unique_counties.append(cleaned_item)
                    
    selected_county = st.sidebar.selectbox("2. County Level Resolution:", sorted(unique_counties))
    
    # FEMA ESF Filter Implementation
    esf_options = ["All FEMA ESF Functions"]
    if "Primary_ESF_Focus" in df_orgs.columns:
        esf_options += list(df_orgs["Primary_ESF_Focus"].dropna().unique())
    selected_esf = st.sidebar.selectbox("3. FEMA ESF Framework Filter:", esf_options)
    
    # 🗺️ COUNTY ZOOM OPTIMIZATION SLIDER MOCK
    st.sidebar.markdown("---")
    map_zoom_resolution = st.sidebar.select_slider("Map Zoom Level Layer:", options=["State Boundary Level View", "Detailed County Line Zoom"])

    # Apply Strict Data Matrix Filtering Logic (AND Operators)
    filtered_df = df_orgs.copy()
    if selected_state != "All States":
        filtered_df = filtered_df[(filtered_df["State_Supported_Clean"] == selected_state) | (filtered_df["State_Supported_Clean"] == "All States") | (filtered_df["State_Supported_Clean"] == "Global")]
    if selected_county != "All Counties" and county_col:
        filtered_df = filtered_df[
            filtered_df[county_col].astype(str).str.contains(selected_county, case=False) | 
            filtered_df[county_col].astype(str).str.contains("All Counties", case=False)
        ]
    if selected_esf != "All FEMA ESF Functions" and "Primary_ESF_Focus" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Primary_ESF_Focus"] == selected_esf]

    # Map Pipeline Core Rendering Execution
    st.markdown(f"### 📍 Active Logistics Map Representation ({map_zoom_resolution})")
    lat_col = next((c for c in df_orgs.columns if c.lower() in ["latitude", "lat"]), None)
    lon_col = next((c for c in df_orgs.columns if c.lower() in ["longitude", "lon", "long"]), None)
    
    if lat_col and lon_col and not filtered_df.empty:
        map_ready = filtered_df.copy()
        map_ready[lat_col] = pd.to_numeric(map_ready[lat_col], errors='coerce')
        map_ready[lon_col] = pd.to_numeric(map_ready[lon_col], errors='coerce')
        map_ready = map_ready.dropna(subset=[lat_col, lon_col])
        
        # Adjust zoom factor based on your review slider choice
        zoom_val = 5 if map_zoom_resolution == "State Boundary Level View" else 9
        
        if not map_ready.empty:
            st.map(map_ready[[lat_col, lon_col]].rename(columns={lat_col: 'latitude', lon_col: 'longitude'}), zoom=zoom_val)
        else:
            st.info("No matching locations found for this specific combination. Displaying center coordinates.")
            st.map(pd.DataFrame({'latitude': [28.5383], 'longitude': [-81.3792]}), zoom=4)
    else:
        fallback_us_coords = pd.DataFrame({'latitude': [28.5383, 27.3364, 33.7490], 'longitude': [-81.3792, -82.5307, -84.3880]})
        st.map(fallback_us_coords, zoom=4)

    # Output Data Verification Table Below Map
    st.markdown("#### 📋 Matched Regional Logistics Grid Layout")
    main_view_cols = ["Organization_Name", "Active_Volunteer_Count", "Primary_ESF_Focus", "State_Supported", "Counties_Covered"]
    clean_display_cols = [c for c in main_view_cols if c in filtered_df.columns]
    
    if not filtered_df.empty:
        st.dataframe(filtered_df[clean_display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No matching organizations found for this filter criteria.")

elif ui_review_gate == "Screen 3: Master Admin Reports (T1.0c)":
    st.info("💡 **Stakeholder Review Focus (T1.0c):** Audit core system health metrics, file processing statuses, and check multi-factor framework spaces.")
    st.subheader("📊 Administrative System Integrity Analytics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Agencies Registered", len(df_orgs))
    
    v_col = next((c for c in df_orgs.columns if 'verify' in c.lower()), None)
    unverified_count = len(df_orgs[df_orgs[v_col].astype(str).str.upper().str.strip() == "FALSE"]) if v_col else 0
    c2.metric("⚠️ Pending Attestation Check", unverified_count, delta=f"{unverified_count} Alerts Pending", delta_color="inverse")
    c3.metric("Live Active Volunteers Registered", len(df_vols))
    
    st.markdown("#### Full System Organizational Health Table")
    st.dataframe(df_orgs, use_container_width=True, hide_index=True)
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Emergency Registry", layout="wide")
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Database Hub")

# 🔴 HARDCODED WITH YOUR EXACT FULL GOOGLE SPREADSHEET URL
FULL_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY/edit?usp=sharing"

@st.cache_data(ttl=5) # 5-second fast cache window for rapid deployment testing
def load_live_data(sheet_name):
    # FIXED: Reconstructed url structure to force Google to respect separate tabs by literal name
    base_url = FULL_SPREADSHEET_URL.split("/edit")[0]
    gviz_export_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(gviz_export_url)
    df.columns = df.columns.str.strip() # Defensive cleanup for column headers
    return df

# Load separate tabs directly into memory by their literal text names
try:
    df_orgs = load_live_data("Organizations")
    df_lookup = load_live_data("State_ESF_Lookup")
    df_vols = load_live_data("Volunteers")
except Exception as e:
    st.error(f"❌ Connection Error: Google Sheet connection blocked. Please check that 'Anyone with the link can view' is turned on. Details: {e}")
    st.stop()

# Sidebar Navigation Panel
st.sidebar.header("Compass Dashboard Navigation")
app_mode = st.sidebar.radio("Go to view:", ["Public Interactive Map", "🔒 Master Admin Reports"])

# 🔄 STATE TRANSLATOR ENGINE
def clean_state_value(val):
    text = str(val).strip().upper()
    if "FLORIDA" in text or text == "FL": return "FL"
    elif "TEXAS" in text or text == "TX": return "TX"
    elif "GEORGIA" in text or text == "GA": return "GA"
    elif "GLOBAL" in text: return "Global"
    elif "ALL" in text: return "All States"
    return text

state_col = next((c for c in df_orgs.columns if 'state' in c.lower()), None)
if state_col:
    df_orgs["State_Supported_Clean"] = df_orgs[state_col].apply(clean_state_value)
else:
    df_orgs["State_Supported_Clean"] = "FL"

# 📊 DATA LINKING ENGINE: Match Volunteers to Organizations
if 'Associated_Org_ID' in df_vols.columns and 'Org_ID' in df_orgs.columns:
    active_statuses = ["AVAILABLE", "DEPLOYED", "STANDBY"]
    active_vols = df_vols[df_vols["Availability_Status"].astype(str).str.upper().str.strip().isin(active_statuses)]
    vol_counts = active_vols["Associated_Org_ID"].value_counts().to_dict()
    df_orgs["Active_Volunteer_Count"] = df_orgs["Org_ID"].map(vol_counts).fillna(0).astype(int)
else:
    df_orgs["Active_Volunteer_Count"] = 0

if app_mode == "Public Interactive Map":
    st.sidebar.subheader("🌍 Regional Map Filters")
    
    filter_mode = st.sidebar.radio("Display Priority:", ["Show All Registered Agencies", "Only Show Orgs with Active Volunteers"])
    selected_state = st.sidebar.selectbox("1. Select Target State:", ["All States", "FL", "TX", "GA"])
    
    if selected_state == "All States":
        state_filtered_df = df_orgs.copy()
    else:
        state_filtered_df = df_orgs[(df_orgs["State_Supported_Clean"] == selected_state) | (df_orgs["State_Supported_Clean"] == "All States") | (df_orgs["State_Supported_Clean"] == "Global")]
    
    if filter_mode == "Only Show Orgs with Active Volunteers":
        state_filtered_df = state_filtered_df[state_filtered_df["Active_Volunteer_Count"] > 0]
    
    county_col = next((c for c in df_orgs.columns if 'county' in c.lower() or 'counties' in c.lower()), None)
    unique_counties = ["All Counties"]
    
    if county_col and not state_filtered_df.empty:
        raw_counties = state_filtered_df[county_col].dropna().astype(str).tolist()
        for item in raw_counties:
            for sub_item in item.split(","):
                cleaned_item = sub_item.strip()
                if cleaned_item and cleaned_item.upper() != "ALL COUNTIES" and cleaned_item not in unique_counties:
                    unique_counties.append(cleaned_item)
                    
    selected_county = st.sidebar.selectbox("2. Narrow Down by County Scope:", sorted(unique_counties))
    
    if selected_county == "All Counties":
        filtered_df = state_filtered_df.copy()
    else:
        filtered_df = state_filtered_df[
            state_filtered_df[county_col].astype(str).str.contains(selected_county, case=False) | 
            state_filtered_df[county_col].astype(str).str.contains("All Counties", case=False)
        ]
    
    # 🌍 GEOSPATIAL VISUAL MAPPING BLOCK
    st.markdown(f"### 📍 Active Logistics Map Representation")
    
    lat_col = next((c for c in df_orgs.columns if c.lower() in ["latitude", "lat"]), None)
    lon_col = next((c for c in df_orgs.columns if c.lower() in ["longitude", "lon", "long"]), None)
    
    if lat_col and lon_col:
        map_df = filtered_df.copy()
        map_df[lat_col] = pd.to_numeric(map_df[lat_col], errors='coerce')
        map_df[lon_col] = pd.to_numeric(map_df[lon_col], errors='coerce')
        map_ready = map_df.dropna(subset=[lat_col, lon_col])
        
        if not map_ready.empty:
            map_render = map_ready.rename(columns={lat_col: 'latitude', lon_col: 'longitude'})
            st.map(map_render[['latitude', 'longitude']], size=25)
        else:
            fallback_us_coords = pd.DataFrame({'latitude': [28.5383, 27.3364, 33.7490], 'longitude': [-81.3792, -82.5307, -84.3880]})
            st.map(fallback_us_coords, zoom=4)
    else:
        fallback_us_coords = pd.DataFrame({'latitude': [28.5383, 27.3364, 33.7490], 'longitude': [-81.3792, -82.5307, -84.3880]})
        st.map(fallback_us_coords, zoom=4)

    st.write("---")

    # 📊 MAIN TABULAR RENDER ENGINE: Focuses explicitly on Organizations
    st.markdown(f"#### 📋 Active Responders Registered Region Layout (`{selected_state}` View)")
    st.write("Review primary operational jurisdictions below. Select an organization from the dropdown to extract their dossier profile.")
    
    # Ensuring specific Company/Jurisdiction metrics are shown upfront instead of volunteer strings
    main_view_cols = ["Organization_Name", "Active_Volunteer_Count", "Primary_ESF_Focus", "State_Supported", "Counties_Covered"]
    clean_display_cols = [c for c in main_view_cols if c in filtered_df.columns]
    
    if not filtered_df.empty and "Organization_Name" in filtered_df.columns:
        st.dataframe(filtered_df[clean_display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No matching organizations found for this filter criteria.")
    
    st.write("---")
    
    # 🔍 DETAILED COMPANY DOSSIER SELECTION MATRIX
    col1, col2 = st.columns(2)
    with col1:
        org_list = filtered_df["Organization_Name"].dropna().tolist() if ("Organization_Name" in filtered_df.columns and not filtered_df.empty) else []
        selected_org = st.selectbox("Select an organization to expand dossier profile:", org_list)
        
    with col2:
        if selected_org and not filtered_df.empty:
            org_rows = filtered_df[filtered_df["Organization_Name"] == selected_org]
            if not org_rows.empty:
                org_row = org_rows.iloc[0]
                
                st.markdown(f"### 📋 COMPREHENSIVE DOSSIER: {org_row.get('Organization_Name', selected_org)}")
                st.success(f"👥 **Live Personnel Available right now:** {org_row.get('Active_Volunteer_Count', 0)} active volunteers managed.")
                st.write("---")
                
                for key, val in org_row.items():
                    if str(val) != 'nan' and key not in ['Organization_Name', 'Latitude', 'Longitude', 'State_Supported_Clean', 'Active_Volunteer_Count']:
                        st.write(f"• **{key.replace('_',' ').title()}**: {val}")
                
                phone_key = next((k for k in org_row.index if 'phone' in k.lower() or 'contact' in k.lower()), None)
                if phone_key and str(org_row[phone_key]) != 'nan':
                    raw_phone = str(org_row[phone_key])
                    phone_url = f"tel:{raw_phone.replace('-', '').replace(' ', '').replace('+', '')}"
                    st.write("---")
                    st.markdown(f'👉 <a href="{phone_url}" style="font-size:20px; font-weight:bold; color:#2e7d32; text-decoration:none;">📲 CLICK TO DISPATCH LINE: {raw_phone}</a>', unsafe_allow_html=True)

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
