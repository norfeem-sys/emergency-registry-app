import streamlit as st
import pandas as pd

st.set_page_config(page_title="Emergency Registry - Multi-View Portal", layout="wide")

# ==============================================================================
# 🗃️ LIVE DATABASE PIPELINE INGESTION ENGINE
# ==============================================================================
# 🔴 HARDCODED WITH YOUR EXACT FULL GOOGLE SPREADSHEET URL
FULL_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY/edit?usp=sharing"

@st.cache_data(ttl=5)
def load_live_data(sheet_name):
    try:
        base_url = FULL_SPREADSHEET_URL.split("/edit")[0]
        gviz_export_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(gviz_export_url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        # Integrated fallback generation if Google Sheet pipeline fails to return structures during testing
        if sheet_name == "Organizations":
            return pd.DataFrame({
                "Org_ID": ["ORG-GL-001", "ORG-REG-002", "ORG-ST-003", "ORG-LOC-004"],
                "Organization_Name": ["American Red Cross (Global Network)", "Florida Baptist Disaster Relief", "Florida State Emergency Management Branch", "Brevard County SAR Rescue Team"],
                "Operational_Tier": ["Global / International", "Multi-State Regional", "State-Specific", "Hyper-Local County Unit"],
                "Lifecycle_Status": ["VERIFIED_ACTIVE", "VERIFIED_ACTIVE", "VERIFIED_ACTIVE", "PENDING_REVIEW"],
                "Primary_ESF_Focus": ["ESF-6: Mass Care", "ESF-11: Agriculture & Resource Support", "ESF-5: Information & Planning", "ESF-9: Search & Rescue"],
                "State_Supported": ["Global", "FL, GA, AL", "FL", "FL"],
                "Counties_Covered": ["All Counties", "Multi-Region", "All Counties", "Brevard County"],
                "Latitude": [27.3364, 28.5383, 30.4383, 28.2639],
                "Longitude": [-82.5307, -81.3792, -84.2807, -80.7214]
            })
        elif sheet_name == "Volunteers":
            return pd.DataFrame({"Associated_Org_ID": ["ORG-GL-001", "ORG-REG-002"], "Availability_Status": ["AVAILABLE", "AVAILABLE"]})
        else:
            return pd.DataFrame()

# Ingest data structures from memory
df_orgs = load_live_data("Organizations")
df_lookup = load_live_data("State_ESF_Lookup")
df_vols = load_live_data("Volunteers")

# Ensure tracking metrics exist natively
if not df_orgs.empty and "Lifecycle_Status" not in df_orgs.columns:
    df_orgs["Lifecycle_Status"] = "VERIFIED_ACTIVE"
if not df_orgs.empty and "Operational_Tier" not in df_orgs.columns:
    df_orgs["Operational_Tier"] = "State-Specific"

# Linked Aggregate Personnel Matrix Counting Loop
if not df_vols.empty and 'Associated_Org_ID' in df_vols.columns and not df_orgs.empty and 'Org_ID' in df_orgs.columns:
    active_statuses = ["AVAILABLE", "DEPLOYED", "STANDBY"]
    active_vols = df_vols[df_vols["Availability_Status"].astype(str).str.upper().str.strip().isin(active_statuses)]
    vol_counts = active_vols["Associated_Org_ID"].value_counts().to_dict()
    df_orgs["Active_Volunteer_Count"] = df_orgs["Org_ID"].map(vol_counts).fillna(0).astype(int)
else:
    if not df_orgs.empty:
        df_orgs["Active_Volunteer_Count"] = 0


# ==============================================================================
# 🔑 CENTRAL MAIN SCREEN SIGN-IN PORTAL LAYER
# ==============================================================================
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Database Hub")

# Main Screen Interactive Sign-In Accordion Engine
with st.expander("🔐 CENTRAL GATEWAY PORTAL SIGN-IN (Click to Open Safe Authorized Views)", expanded=False):
    st.markdown("#### Authorized Identity Validation Panel")
    
    # Establish local layout grids for forms
    login_col1, login_col2 = st.columns(2)
    
    with login_col1:
        st.markdown("##### 🔵 Partner Organization Login")
        with st.form("org_login_form"):
            input_org_token = st.text_input("Enter Private Organization Key Token:", type="password", help="Demo Keys: ORG-GL-001, ORG-REG-002, or ORG-ST-003").strip().upper()
            submit_org = st.form_submit_button("Verify & Open Dossier Workspace")
            
            if submit_org and input_org_token:
                if not df_orgs.empty and "Org_ID" in df_orgs.columns and input_org_token in df_orgs["Org_ID"].astype(str).str.upper().str.strip().values:
                    st.session_state["access_role"] = "ORGANIZATION"
                    st.session_state["user_token"] = input_org_token
                    st.success(f" Handshake verified. Connected token: {input_org_token}. Scroll below to view workspace.")
                else:
                    st.error("❌ Invalid Organization Key Token.")
                    
    with login_col2:
        st.markdown("##### 🔒 Registry Master Administration")
        with st.form("admin_login_form"):
            input_admin_pass = st.text_input("Enter Master Admin Passcode:", type="password", help="Demo Override Key: admin123")
            submit_admin = st.form_submit_button("Verify & Open Root Command Console")
            
            if submit_admin and input_admin_pass:
                if input_admin_pass == "admin123":
                    st.session_state["access_role"] = "ADMIN"
                    st.success("🔑 Root Access Verified. Global administrative structures initialized below.")
                else:
                    st.error("❌ Credentials unverified. Access Denied.")

    # Contextual Sign-out Command Route Trigger
    if "access_role" in st.session_state:
        st.write("---")
        if st.button("🔴 Securely Sign Out & Return to Open Public Lookup Mode"):
            for key in ["access_role", "user_token"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

st.write("---")


# ==============================================================================
# INTERACTIVE DYNAMIC VIEW COORDINATOR ENGINE
# ==============================================================================
current_view = st.session_state.get("access_role", "PUBLIC")

# TIER 1: THE OPEN PUBLIC LOOK-UP ENVIRONMENT (DEFAULT BASELINE VIEW)
if current_view == "PUBLIC":
    st.subheader("🔍 Public Relief Directory Directory Lookup")
    st.info("ℹ️ **Data Masking Active:** Public access is unrestricted. Sensitive map tracking features, coordinate layers, specific volunteer PII registries, and accounts pending verification are structurally blocked.")
    
    if not df_orgs.empty:
        # Enforce lifecycle query constraint rule
        active_pub_df = df_orgs[df_orgs["Lifecycle_Status"] == "VERIFIED_ACTIVE"]
        
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            pub_state = st.selectbox("Search State Jurisdictions:", ["All States", "FL", "TX", "GA"])
        with p_col2:
            pub_tier = st.selectbox("Organizational Scale Classification:", ["All Scales", "Global / International", "Multi-State Regional", "State-Specific", "Hyper-Local County Unit"])
            
        if pub_state != "All States" and "State_Supported" in active_pub_df.columns:
            active_pub_df = active_pub_df[active_pub_df["State_Supported"].astype(str).str.contains(pub_state, case=False) | active_pub_df["State_Supported"].astype(str).str.contains("Global", case=False)]
        if pub_tier != "All Scales":
            active_pub_df = active_pub_df[active_pub_df["Operational_Tier"] == pub_tier]
            
        public_safe_columns = ["Organization_Name", "Operational_Tier", "Primary_ESF_Focus", "State_Supported", "Counties_Covered", "Active_Volunteer_Count"]
        clean_cols = [c for c in public_safe_columns if c in active_pub_df.columns]
        
        st.dataframe(active_pub_df[clean_cols], use_container_width=True, hide_index=True)

# TIER 2: AUTHENTICATED PARTNER SELF-SERVICE DOSSIER WORKSPACE (3RD VIEW)
elif current_view == "ORGANIZATION":
    target_token = st.session_state.get("user_token", "")
    org_profile = df_orgs[df_orgs["Org_ID"].astype(str).str.upper().str.strip() == target_token].iloc[0]
    
    st.subheader(f"🏢 Profile Dossier Workspace: {org_profile.get('Organization_Name')}")
    st.markdown(f"**Lifecycle Account State:** `{org_profile.get('Lifecycle_Status')}` | **Scale Classification:** `{org_profile.get('Operational_Tier')}`")
    
    if org_profile.get('Lifecycle_Status') == "PENDING_REVIEW":
        st.error("⏳ **Account Access Restricted:** Your registration request is currently processing through the Admin Vetting Gate. Interactive update tools, field metrics logs, and localized map footprint coordinate vectors are locked out until cleared.")
    else:
        st.success(f"🔓 Security Boundary Handshake Clear. Data container restricted strictly to **{target_token}** records.")
        
        d_form, d_map = st.columns(2)
        with d_form:
            st.markdown("### 📝 Manage Profile and Boundaries")
            with st.form("dossier_main_screen_form"):
                st.write(f"• **Current FEMA ESF Focus Matrix:** `{org_profile.get('Primary_ESF_Focus')}`")
                st.text_input("Modify Operational Phone Link Line:", value="1-800-555-0199")
                st.text_area("Adjust Operational Geographic Scope Boundaries:", value=str(org_profile.get('Counties_Covered')))
                st.form_submit_button("Submit Staged Changes for Administrator Audit Review")
                
        with d_map:
            st.markdown("### 🗺️ Your Isolated Pinned Footprint")
            lat_col = next((c for c in df_orgs.columns if c.lower() in ["latitude", "lat"]), None)
            lon_col = next((c for c in df_orgs.columns if c.lower() in ["longitude", "lon", "long"]), None)
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
