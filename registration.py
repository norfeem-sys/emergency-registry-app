import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import string
import uuid
from datetime import datetime

# Initialize session state keys for form workflows
if "form_submit_success" not in st.session_state:
    st.session_state.form_submit_success = False

st.set_page_config(page_title="Organization Registration Portal", layout="centered")

# --- APP BRANDING HEADERS ---
st.title("📋 National Emergency Registry Ingestion Portal")
st.caption("Official Compliance Intake Form for Disaster Response Providers")
st.markdown("---")

# ==============================================================================
# FIX: Robust GSheets Connection Engine Initialization (Local & Cloud Compatible)
# ==============================================================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as conn_error:
    st.error("❌ Database Engine Timeout: GSheets connection engine is not initialized locally.")
    st.info("💡 **Local Fix Checklist:** Ensure you have a file named `.streamlit/secrets.toml` inside your project folder with your `[connections.gsheets]` keys.")
    conn = None

def generate_org_id():
    """Generates a unique tracking key matching the Org_ID database format."""
    return "ORG-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ==============================================================================
# 🏢 SECTION 1: CORPORATE PROFILE & IDENTIFICATION (Hierarchy level 1)
# ==============================================================================
st.subheader("🏢 Corporate Profile & Identification")

org_name = st.text_input("Organization Legal Name / DBA:*", placeholder="e.g., Volunteer Response Force", key="org_name_val")
fein_num = st.text_input("9-Digit Federal Employer Identification Number (FEIN):*", placeholder="XX-XXXXXXX", key="fein_num_val")
primary_phone = st.text_input("Primary Dispatch Hotline / Crisis Contact Phone:*", placeholder="1-800-555-0100", key="primary_phone_val")

# Rule 1: Control framework structures downstream via setup tier choice
op_scope = st.selectbox(
    "Operational Footprint Tier:*", 
    ["National", "Statewide", "Local / Mutual Aid"], 
    key="op_scope_val",
    help="Rule 1: National tier limits selections downstream strictly to the core 15 standard ESFs."
)

st.markdown("---")

# ==============================================================================
# 🗺️ SECTION 2: GEOGRAPHIC FOOTPRINT SCOPE (Hierarchy level 2)
# ==============================================================================
st.subheader("🗺️ Geographic Footprint Scope")

state_footprint = st.multiselect(
    "State Supported (Select 1 or more states):*", 
    options=["AK", "AL", "FL", "GA", "LA", "NC", "SC", "TX"],
    key="state_footprint_val"
)

county_database = {
    "FL": ["Alachua", "Brevard", "Broward", "Duval", "Hillsborough", "Miami-Dade", "Orange", "Osceola", "Palm Beach", "Pinellas", "Polk", "Sarasota", "Volusia"],
    "GA": ["Chatham", "Cherokee", "Cobb", "DeKalb", "Fulton", "Gwinnett", "Muscogee", "Richmond"],
    "TX": ["Bexar", "Collin", "Dallas", "Denton", "El Paso", "Harris", "Tarrant", "Travis"],
    "NC": ["Buncombe", "Durham", "Forsyth", "Guilford", "Mecklenburg", "Wake"],
    "SC": ["Charleston", "Greenville", "Horry", "Richland", "Spartanburg"],
    "AL": ["Jefferson", "Mobile", "Madison", "Montgomery"],
    "LA": ["Orleans", "Jefferson", "East Baton Rouge", "Caddo"],
    "AK": ["Anchorage", "Fairbanks North Star", "Matanuska-Susitna"]
}

counties_string = "Unassigned"

# Enforce Rule 3: If multi-state selection is active, county assignment is bypassed
if len(state_footprint) > 1:
    counties_string = "Not Applicable (Regional Scope)"
    st.info("ℹ️ Rule 3 Active: Multi-state footprint verified. County targeting defaults to 'Regional / Not Applicable'.")

# Enforce Rule 4: If exactly one state is selected, determine if it's statewide or section-specific
elif len(state_footprint) == 1:
    state_focus = state_footprint[0]
    
    coverage_choice = st.radio(
        f"Coverage Scope Selection for {state_focus}:*",
        options=["Statewide Coverage (All Counties)", "Specific Counties Only"],
        horizontal=True,
        key="coverage_choice_val"
    )
    
    if coverage_choice == "Specific Counties Only":
        available_counties = county_database.get(state_focus, ["Zone Alpha", "Zone Beta"])
        selected_counties = st.multiselect(
            "Select Covered Counties:*",
            options=available_counties,
            key="selected_counties_val"
        )
        if selected_counties:
            counties_string = ", ".join(selected_counties)
        else:
            st.warning("⚠️ Action Required: Please specify at least one county or switch coverage type back to 'Statewide'.")
            counties_string = ""
    else:
        counties_string = "All Counties"
        st.info(f"ℹ️ Rule 4 Active: Organization registered for all counties across {state_focus}.")

else:
    st.caption("🔒 *Awaiting geographic state criteria choices to calculate localized county bounds...*")

st.markdown("---")

# ==============================================================================
# ⚡ SECTION 3: CORE CAPABILITIES & ESF ALIGNMENT (Hierarchy level 3)
# ==============================================================================
st.subheader("⚡ Core Capabilities & Framework Alignment")

FEMA_15_BASE = [
    "ESF #1: Transportation", "ESF #2: Communications", "ESF #3: Public Works & Engineering",
    "ESF #4: Firefighting", "ESF #5: Information & Planning", "ESF #6: Mass Care & Human Services",
    "ESF #7: Logistics", "ESF #8: Public Health & Medical Services", "ESF #9: Search & Rescue",
    "ESF #10: Oil & Hazardous Materials Response", "ESF #11: Agriculture & Natural Resources", "ESF #12: Energy",
    "ESF #13: Public Safety & Security", "ESF #14: Cross-Sector Business & Infrastructure", "ESF #15: External Affairs"
]

TEXAS_EXPANSION = [
    "ESF #16: Law Enforcement Mutual Aid & State Administrative Controls",
    "ESF #17: Standalone Animal & Agricultural Concerns",
    "ESF #18: Business, Industry & Private Sector Stabilization",
    "ESF #19: Emergency Fuel Logistics Coordination",
    "ESF #20: State Cybersecurity Defense Operations",
    "ESF #21: Defense Support to Civil Authorities (State Military Annex)",
    "ESF #22: Border Security Operational Coordination Taskforce",
    "ESF #23: Evacuation Transportation & Transit Logistics",
    "ESF #24: Volunteer Agency & Spontaneous Donations Management"
]

STANDARD_STATE_EXPANSION = [
    "ESF #16: State-Level Mutual Aid Coordination",
    "ESF #17: Animal and Agricultural Welfare Issues",
    "ESF #18: Business & Industry Stabilization Network",
    "ESF #19: Regional Emergency Fuel Logistics",
    "ESF #20: Cybersecurity Defense Infrastructure"
]

# Rule 1 Verification Logic: Match valid options matrix to jurisdiction profiles
if op_scope == "National":
    esf_options_pool = FEMA_15_BASE
    st.caption("🇺🇸 *Framework Sync: Restricted to standard FEMA ESF #1 through #15 under National guidelines.*")
elif "TX" in state_footprint:
    esf_options_pool = FEMA_15_BASE + TEXAS_EXPANSION
    st.caption("🤠 *Framework Sync: Expanded Texas Annex Matrix (ESF #1 to #24) initialized.*")
else:
    esf_options_pool = FEMA_15_BASE + STANDARD_STATE_EXPANSION
    st.caption("📋 *Framework Sync: Standard State Blueprint Matrix (ESF #1 to #20) initialized.*")

# Rule 2: Multi-select array allocation tracking
primary_esf_selection = st.selectbox("Primary Emergency Support Function (ESF) Focus:*", options=esf_options_pool, key="primary_esf_val")

secondary_esf_selections = st.multiselect(
    "Secondary ESF Classifications Supported (Rule 2 Multi-Select):", 
    options=[item for item in esf_options_pool if item != primary_esf_selection],
    key="secondary_esfs_val",
    help="Rule 2: Select all additional functions your group supports."
)

resource_inventory = st.text_area("Resource Inventory Capacities & Logistical Assets:*", placeholder="Detail NIMS resource types, equipment inventory, vehicles, or specialized staff profiles.", key="resource_inventory_val")

# ==============================================================================
# 📝 FORM SUBMISSION & DATABASE SERIALIZATION LAYER
# ==============================================================================
with st.form("registry_write_submission_form", clear_on_submit=False):
    st.subheader("🔗 Verification Media & Compliance Execution")
    logo_url = st.text_input("Organization Logo Vector URL (Optional):", placeholder="https://example.com", key="logo_url_form")
    doc_url = st.text_input("Tax Exempt IRS Determination PDF Link (Optional):", placeholder="https://example.com", key="doc_url_form")
    compliance_check = st.checkbox("I certify that all parameters represent verifiable active deployment capacities.*", key="compliance_check_form")
    
    submit_btn = st.form_submit_button("Submit Registry Records to Database System Cluster")

if submit_btn:
    if not org_name.strip():
        st.error("Validation Halt: Organization Legal Name parameter cannot be left blank.")
    elif not fein_num.strip():
        st.error("Validation Halt: Corporate 9-Digit FEIN identification missing.")
    elif not primary_phone.strip():
        st.error("Validation Halt: Emergency Hotline Dispatch number missing.")
    elif not state_footprint:
        st.error("Validation Halt: You must assign at least one active operating base state.")
    elif counties_string == "":
        st.error("Validation Halt: Supported county boundaries are unassigned.")
    elif not resource_inventory.strip():
        st.error("Validation Halt: Resource asset logging statement cannot be empty.")
    elif not compliance_check:
        st.error("Validation Halt: You must certify the operational data parameters.")
    elif conn is None:
        st.error("Database Framework Timeout: Connection Engine is currently uninitialized.")
    else:
        with st.spinner("Processing transactional rows and writing to datastore cluster..."):
            try:
                existing_sheet_df = pd.DataFrame(conn.read(ttl="0d"))
            except Exception:
                existing_sheet_df = pd.DataFrame()
                
            states_field_value = ", ".join(state_footprint)
            secondary_field_value = ", ".join(secondary_esf_selections) if secondary_esf_selections else "None Assigned"
            combined_capacity_payload = f"Hotline: {primary_phone.strip()} | Inventory: {resource_inventory.strip()}"
            
            # SCHEMA ALIGNED EXACTLY TO LIVE SPREADSHEET HEADERS
            new_record_payload = pd.DataFrame([{
                "Org_ID": generate_org_id(),
                "Organization_Name": org_name.strip(),
                "EIN_Number": fein_num.strip(),
                "Operation_Scope": op_scope,
                "State_Supported": states_field_value,
                "Counties_Covered": counties_string,
                "Primary_ESF_Focus": primary_esf_selection,
                "Secondary_ESFs": secondary_field_value,
                "Resource_Capacity": combined_capacity_payload,
                "Org_Logo_URL": logo_url.strip() if logo_url.strip() else "None Provided",
                "Tax_Exempt_Doc_URL": doc_url.strip() if doc_url.strip() else "None Uploaded",
                "Data_Verified": "TRUE",
                "Verification_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Verifying_Email": "system-ingestion@voad.registry.internal",
                "Account_Status": "Active",
                "Latitude": 0.0,
                "Longitude": 0.0
            }])
            
            if not existing_sheet_df.empty:
                df_final_matrix = pd.concat([existing_sheet_df, new_record_payload], ignore_index=True)
            else:
                df_final_matrix = new_record_payload

            try:
                conn.update(data=df_final_matrix)
                st.success(f"🎉 Transaction Confirmed! '{org_name.strip()}' has been successfully appended to the Master Registry Database.")
                st.balloons()
            except Exception as write_err:
                st.error("Write Blocked: Secure API authorization mapping failure.")
                st.info("Ensure that your Service Account email is assigned 'Editor' permissions inside the Google Sheet sharing window.")
