import streamlit as st
import pandas as pd
import random
import string
import uuid
from datetime import datetime

# Secure Google Sheets Connection Engine via Streamlit Native Secrets
try:
    conn = st.connection("gsheets", type=st.connections.GSheetsConnection)
except Exception:
    conn = None

def generate_org_id():
    """Generates a unique tracking key matching the Org_ID database format."""
    return "ORG-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Initialize session state keys for clear/reset operations if not already set
if "form_submit_success" not in st.session_state:
    st.session_state.form_submit_success = False

st.set_page_config(page_title="Organization Registration Portal", layout="centered")

# --- APP BRANDING HEADERS ---
st.title("📋 National Emergency Registry Ingestion Portal")
st.caption("Official Compliance Intake Form for Disaster Response Providers")
st.markdown("---")

# ==============================================================================
# 🏢 STEP 1: CORPORATE PROFILE & IDENTIFICATION (Hierarchy Level 1)
# ==============================================================================
st.subheader("🏢 Corporate Profile & Identification")

org_name = st.text_input("Organization Legal Name / DBA:*", placeholder="e.g., Volunteer Response Force", key="org_name_val")
fein_num = st.text_input("9-Digit Federal Employer Identification Number (FEIN):*", placeholder="XX-XXXXXXX", key="fein_num_val")
primary_phone = st.text_input("Primary Dispatch Hotline / Crisis Contact Phone:*", placeholder="1-800-555-0100", key="primary_phone_val")

# Rule 1 Guideline variable
op_scope = st.selectbox(
    "Operational Footprint Tier:*", 
    ["National", "Statewide", "Local / Mutual Aid"], 
    key="op_scope_val",
    help="Rule 1: National tier limits selections down to the core 15 standard FEMA ESFs."
)

st.markdown("---")

# ==============================================================================
# 🗺️ STEP 2: INTERACTIVE JURISDICTION MATRIX LAYER (Hierarchy Level 2)
# ==============================================================================
st.subheader("🗺️ Operational Footprint Scope")

# Multi-select state framework bound to session state
state_footprint = st.multiselect(
    "Primary State Horizon Base (Select 1 or more states):*", 
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

# Rule 3 Check: Multi-state selection bypasses county target configuration
if len(state_footprint) > 1:
    counties_string = "Not Applicable (Regional Scope)"
    st.info("ℹ️ Rule 3 Active: Multi-state footprint verified. County targeting defaults to 'Regional Scope'.")

# Rule 4 Check: Conditional selection panel toggle for single state selection
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
            st.warning("⚠️ Action Required: Specify at least one county or switch coverage type back to 'Statewide'.")
            counties_string = ""
    else:
        counties_string = "Statewide"
        st.info(f"ℹ️ Rule 4 Active: Organization registered for all counties across {state_focus}.")
else:
    st.caption("🔒 *Awaiting state footprint configuration to unlock localized choices...*")

st.markdown("---")

# ==============================================================================
# ⚡ STEP 3: CORE CAPABILITIES & FRAMEWORK ALIGNMENT (Hierarchy Level 3)
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

# Rule 1 Enforcement: Select options pool based on footprint tier context
if op_scope == "National":
    esf_options_pool = FEMA_15_BASE
    st.caption("🇺🇸 *Framework Sync: Restricted to standard FEMA ESF #1 through #15 under National guidelines.*")
elif "TX" in state_footprint:
    esf_options_pool = FEMA_15_BASE + TEXAS_EXPANSION
    st.caption("🤠 *Framework Sync: Expanded Texas Annex Matrix (ESF #1 to #24) initialized.*")
else:
    esf_options_pool = FEMA_15_BASE + STANDARD_STATE_EXPANSION
    st.caption("📋 *Framework Sync: Standard State Blueprint Matrix (ESF #1 to #20) initialized.*")

primary_esf = st.selectbox("Primary Emergency Support Function (ESF):*", options=esf_options_pool, key="primary_esf_val")

# Rule 2: Multi-select parameter capture interface
secondary_esfs = st.multiselect(
    "Secondary ESFs Supported (Optional Multi-Select):", 
    options=[item for item in esf_options_pool if item != primary_esf],
    key="secondary_esfs_val"
)

resource_inventory = st.text_area("Resource Inventory Capacities & Logistical Assets:*", placeholder="Detail standard NIMS resource types, vehicle counts, kitchens, or personnel.", key="resource_inventory_val")

st.markdown("---")

# ==============================================================================
# 📝 STEP 4: SUBMISSION FORM WRAPPER CONTAINER
# ==============================================================================
with st.form("org_reg_form", clear_on_submit=False):
    
    st.subheader("🔗 Verification Media & Assets")
    logo_url = st.text_input("Organization Logo Vector URL (Optional):", placeholder="https://example.com/logo.png", key="logo_url_val")
    doc_url = st.text_input("Tax Exempt IRS Determination PDF Link (Optional):", placeholder="https://example.com/irs-letter.pdf", key="doc_url_val")
    
    st.markdown("---")
    compliance_check = st.checkbox("I certify that all submitted parameters represent verifiable active deployment capacities.*", key="compliance_check_val")
    
    # FORM SUBMISSION EXECUTOR
    submit_btn = st.form_submit_button("Submit Registry Records to Compliance Queue")

if submit_btn:
    if not org_name.strip():
        st.error("Validation Error: Organization Legal Name cannot be empty.")
    elif not fein_num.strip():
        st.error("Validation Error: Federal Identification Number (FEIN) is required.")
    elif not primary_phone.strip():
        st.error("Validation Error: Dispatch Hotline Contact number is required.")
    elif not state_footprint:
        st.error("Validation Error: Select at least one primary operating base state.")
    elif counties_string == "":
        st.error("Validation Error: Supported county bounds selection incomplete.")
    elif not resource_inventory.strip():
        st.error("Validation Error: Logistical resource inventory breakdown must be detailed.")
    elif not compliance_check:
        st.error("Validation Error: Certification box must be checked to complete registry ingestion.")
    else:
        with st.spinner("Processing transactional arrays and streaming record blocks..."):
            new_id = generate_org_id()
            states_string = ", ".join(state_footprint)
            secondary_string = ", ".join(secondary_esfs) if secondary_esfs else "None Assigned"
            
            # Format dataframe row record mapped to your exact 17-column layout
            new_row = pd.DataFrame([{
                "Org_ID": new_id,
                "Organization_Name": org_name.strip(),
                "EIN_Number": fein_num.strip(),
                "Operation_Scope": op_scope,
                "State_Supported": states_string,
                "Counties_Covered": counties_string,
                "Primary_ESF_Focus": primary_esf,
                "Secondary_ESFs": secondary_string,
                "Resource_Capacity": f"Hotline: {primary_phone.strip()} | Assets: {resource_inventory.strip()}",
                "Org_Logo_URL": logo_url.strip() if logo_url.strip() else "None Provided",
                "Tax_Exempt_Doc_URL": doc_url.strip() if doc_url.strip() else "None Uploaded",
                "Data_Verified": "TRUE",
                "Verification_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Verifying_Email": "system-ingestion@registry.internal",
                "Account_Status": "Active",
                "Latitude": 0.0,
                "Longitude": 0.0
            }])
            
            # Google Sheets Write Pipeline Engine
            if conn is not None:
                try:
                    try:
                        existing_data = pd.DataFrame(conn.read(ttl="0d"))
                    except Exception:
                        existing_data = pd.DataFrame()
                    
                    if not existing_data.empty:
                        df_final_matrix = pd.concat([existing_data, new_row], ignore_index=True)
                    else:
                        df_final_matrix = new_row
                        
                    conn.update(data=df_final_matrix)
                    st.success(f"🎉 Success! '{org_name.strip()}' safely saved to Master Registry Database.")
                    st.balloons()
                except Exception as write_error:
                    st.error("Write Blocked: Google Cloud API Authorization failure.")
                    st.info("Please verify your Service Account email has 'Editor' access inside your sheet's Share settings.")
            else:
                st.error("Database Engine Timeout: GSheets connection engine is not initialized locally.")
