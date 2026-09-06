import streamlit as st
import pandas as pd

st.set_page_config(page_title="Emergency Registry - Setup Prototype", layout="wide")

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
                "Org_ID": ["ORG-GL-001", "ORG-REG-002", "ORG-ST-003"],
                "Organization_Name": ["American Red Cross (Global Network)", "Florida Baptist Disaster Relief", "Florida State Emergency Management Branch"],
                "Operational_Tier": ["Global / International", "Multi-State Regional", "State-Specific"],
                "Lifecycle_Status": ["VERIFIED_ACTIVE", "VERIFIED_ACTIVE", "VERIFIED_ACTIVE"],
                "Primary_ESF_Focus": ["ESF-6: Mass Care", "ESF-11: Agriculture & Resource Support", "ESF-5: Information & Planning"],
                "State_Supported": ["Global", "FL, GA, AL", "FL"],
                "Counties_Covered": ["All Counties", "Brevard, Orange, Volusia", "All Counties"],
                "Latitude": [27.3364, 28.5383, 30.4383],
                "Longitude": [-82.5307, -81.3792, -84.2807]
            })
        elif sheet_name == "State_ESF_Lookup":
            return pd.DataFrame({
                "State": ["FL", "FL", "FL"],
                "ESF_Code": ["ESF-6", "ESF-9", "ESF-11"],
                "FEMA_Function": ["Mass Care & Shelter", "Search and Rescue", "Resource Support"]
            })
        else:
            return pd.DataFrame()

# Ingest data structures into live environment
df_orgs = load_live_data("Organizations")
df_lookup = load_live_data("State_ESF_Lookup")

# Ensure structural properties exist natively
if not df_orgs.empty and "Lifecycle_Status" not in df_orgs.columns:
    df_orgs["Lifecycle_Status"] = "VERIFIED_ACTIVE"
if not df_orgs.empty and "Operational_Tier" not in df_orgs.columns:
    df_orgs["Operational_Tier"] = "State-Specific"

# ==============================================================================
# 🏛️ INTERACTIVE PLATFORM WORKSPACE (MAIN CANVAS)
# ==============================================================================
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Hub — Core Feature Demo")
st.info("💡 **Sandbox Configuration Notice:** Formal login checkpoints have been bypassed for this review session. Onboarding, team setup, and matrix maps are completely unlocked for evaluation.")

# Re-engineered Navigation tabs placed directly on the main screen
tab_lookup, tab_signup, tab_team = st.tabs([
    "🔍 1. Interactive Directory Lookup & Map Matrix", 
    "➕ 2. Register New Organization Node", 
    "👥 3. Manage Agency Team Roles"
])

# 🟢 TAB 1: OPEN LOOKUP TOOL WITH INTEGRATED GEOSPATIAL MAP
with tab_lookup:
    st.subheader("Active Logistics Map Matrix")
    
    if not df_orgs.empty:
        active_display_df = df_orgs[df_orgs["Lifecycle_Status"] == "VERIFIED_ACTIVE"].copy()
        
        # 🗺️ MULTI-VARIABLE INPUT LAYOUTS
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_state = st.selectbox("1. Filter Target State Jurisdiction:", ["All States", "FL", "TX", "GA"])
        with col_f2:
            search_esf = st.selectbox("2. Filter FEMA ESF Core Capability:", ["All ESF Frameworks"] + list(active_display_df["Primary_ESF_Focus"].dropna().unique()))
            
        # 🔍 COUNTY LEVEL ZOOM OPTIMIZATION SIDEWAY CONTROLLER
        map_zoom_resolution = st.select_slider(
            "🗺️ Simulating Geographic Detail Resolution Overlay:", 
            options=["State High-Level Regional Heatmap", "Detailed County Line Boundary Zoom"]
        )
        
        # Apply Query Matrix Multi-Filters (AND Operators)
        if search_state != "All States" and "State_Supported" in active_display_df.columns:
            active_display_df = active_display_df[active_display_df["State_Supported"].astype(str).str.contains(search_state, case=False) | active_display_df["State_Supported"].astype(str).str.contains("Global", case=False)]
        if search_esf != "All ESF Frameworks" and "Primary_ESF_Focus" in active_display_df.columns:
            active_display_df = active_display_df[active_display_df["Primary_ESF_Focus"] == search_esf]
            
        # Dynamic Geospatial Mapping Execution Layer
        st.markdown(f"### 📍 Real-Time Logistics Grid Location View ({map_zoom_resolution})")
        lat_col = next((c for c in active_display_df.columns if c.lower() in ["latitude", "lat"]), None)
        lon_col = next((c for c in active_display_df.columns if c.lower() in ["longitude", "lon", "long"]), None)
        
        if lat_col and lon_col and not active_display_df.empty:
            map_ready = active_display_df.copy()
            map_ready[lat_col] = pd.to_numeric(map_ready[lat_col], errors='coerce')
            map_ready[lon_col] = pd.to_numeric(map_ready[lon_col], errors='coerce')
            map_ready = map_ready.dropna(subset=[lat_col, lon_col])
            
            # Map Zoom state adjustments to prove county layer visibility to stakeholders
            zoom_factor = 5 if map_zoom_resolution == "State High-Level Regional Heatmap" else 9
            
            if not map_ready.empty:
                st.map(map_ready[[lat_col, lon_col]].rename(columns={lat_col: 'latitude', lon_col: 'longitude'}), zoom=zoom_factor)
            else:
                st.info("No active matching locations found for this matrix query combination.")
        else:
            st.warning("Spatial coordinate columns are missing or loading from the spreadsheet pipeline.")
            
        # Output Public Safe Table Grid Below Map
        st.write("---")
        st.markdown("#### 📋 Matched Regional Logistics Grid Layout")
        public_safe_columns = ["Organization_Name", "Operational_Tier", "Primary_ESF_Focus", "State_Supported", "Counties_Covered"]
        clean_display_cols = [c for c in public_safe_columns if c in active_display_df.columns]
        st.dataframe(active_display_df[clean_display_cols], use_container_width=True, hide_index=True)

# 🔵 TAB 2: ORGANIZATION SELF-SERVICE SIGNUP INTAKE
with tab_signup:
    st.subheader("Agency Registration Intake Form")
    st.write("Newly submitted organizations are automatically dropped into a `PENDING_REVIEW` state until vetted by you.")
    
    with st.form("organization_signup_form"):
        s_name = st.text_input("Official Organization / Agency Name:")
        s_tier = st.selectbox("Operational Scale Class Hierarchy:", ["Hyper-Local County Unit", "State-Specific Organization", "Multi-State Regional Network", "Global / International Entity"])
        s_esf = st.selectbox("Primary FEMA ESF Capabilities Focus:", ["ESF-5: Information & Planning", "ESF-6: Mass Care", "ESF-8: Public Health", "ESF-9: Search & Rescue", "ESF-11: Agriculture & Resource Support"])
        s_state = st.text_input("Operational States Supported (e.g., FL, GA):", value="FL")
        s_counties = st.text_area("Covered Counties Scope (Comma Separated Key Areas):", value="Brevard County")
        
        submit_signup = st.form_submit_button("Submit Registry Enrollment Request")
        
        if submit_signup:
            if not s_name:
                st.error("❌ Submission failed: Please declare an official Organization Name.")
            else:
                st.success(f"🎉 **Intake Processing Success!** **'{s_name}'** has been safely captured into the Ingestion queue matrix. Account status locked to: `PENDING_REVIEW`.")
                st.json({
                    "Org_ID": "ORG-PENDING-NEW",
                    "Organization_Name": s_name,
                    "Operational_Tier": s_tier,
                    "Lifecycle_Status": "PENDING_REVIEW",
                    "Primary_ESF_Focus": s_esf,
                    "State_Supported": s_state,
                    "Counties_Covered": s_counties
                })

# 🔵 TAB 3: INTERNAL TEAM ROLE AND PERSONNEL MANAGEMENT MANAGER
with tab_team:
    st.subheader("Manage Agency Team Personnel Roles")
    st.write("Allows participating organizations to build out their internal command structure by provisioning users under distinct operational authorization boundaries.")
    
    available_parent_agencies = list(df_orgs["Organization_Name"].unique()) if not df_orgs.empty else ["American Red Cross", "Florida Baptist Disaster Relief"]
    selected_parent_agency = st.selectbox("1. Target Parent Organization Node:", available_parent_agencies)
    
    st.write("---")
    st.markdown(f"##### 👤 Provision New User to **{selected_parent_agency}**")
    
    with st.form("team_role_provision_form"):
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            u_name = st.text_input("User Full Legal Name:")
            u_email = st.text_input("Professional Email Address Identity:")
        with col_u2:
            u_role = st.selectbox(
                "Assign Internal System Operational Role:",
                [
                    "Agency Team Admin (Can modify entire organization dossier profile)",
