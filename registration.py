import streamlit as st
import pandas as pd
import random
import string

# Secure Google Sheets Connection Engine via Streamlit Native Secrets
try:
    conn = st.connection("gsheets", type=st.connections.GSheetsConnection)
except Exception:
    conn = None

def generate_org_id():
    """Generates a unique tracking key matching the Org_ID database format."""
    return "ORG-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# 🔄 Initialize session state keys for clear/reset operations if not already set
if "form_submit_success" not in st.session_state:
    st.session_state.form_submit_success = False

st.set_page_config(page_title="Organization Registration Portal", layout="centered")

# --- APP BRANDING HEADERS ---
st.title("📋 National Emergency Registry Ingestion Portal")
st.caption("Official Compliance Intake Form for Disaster Response Providers")
st.markdown("---")

# ==============================================================================
# 🗺️ STEP 1: INTERACTIVE JURISDICTION MATRIX LAYER
# ==============================================================================
st.subheader("🗺️ Operational Footprint Scope")

# Multi-select state framework bound to session state for explicit reset capabilities
state_footprint = st.multiselect(
    "1. Primary State Horizon Base (Select 1 or more states):*", 
    options=["FL", "TX", "GA", "NC", "SC", "All States"],
    key="state_footprint_val"
)

# Detailed mapping containing real, official county records
county_database = {
    "FL": [
        "Alachua", "Baker", "Bay", "Bradford", "Brevard", "Broward", "Calhoun", "Charlotte", "Citrus", "Clay", 
        "Collier", "Columbia", "DeSoto", "Dixie", "Duval", "Escambia", "Flagler", "Franklin", "Gadsden", "Gilchrist", 
        "Glades", "Gulf", "Hamilton", "Hardee", "Hendry", "Hernando", "Highlands", "Hillsborough", "Indian River", "Jackson", 
        "Jefferson", "Lafayette", "Lake", "Lee", "Leon", "Levy", "Liberty", "Madison", "Manatee", "Marion", 
        "Martin", "Miami-Dade", "Monroe", "Nassau", "Okaloosa", "Okeechobee", "Orange", "Osceola", "Palm Beach", "Pasco", 
        "Pinellas", "Polk", "Putnam", "Santa Rosa", "Sarasota", "Seminole", "St. Johns", "St. Lucie", "Sumter", "Suwannee", 
        "Taylor", "Union", "Volusia", "Wakulla", "Walton", "Washington"
    ],
    "GA": ["Chatham", "Cherokee", "Bibb", "Cobb", "DeKalb", "Forsyth", "Fulton", "Gwinnett", "Muscogee", "Richmond"],
    "TX": ["Bexar", "Collin", "Dallas", "Denton", "El Paso", "Fort Bend", "Harris", "Hidalgo", "Tarrant", "Travis"],
    "NC": ["Buncombe", "Cumberland", "Durham", "Forsyth", "Guilford", "Mecklenburg", "New Hanover", "Union", "Wake"],
    "SC": ["Anderson", "Berkeley", "Charleston", "Greenville", "Horry", "Lexington", "Richland", "Spartanburg", "York"]
}

# Aggregate valid choices dynamically based on the selected states
combined_county_options = []
is_national = "All States" in state_footprint

if state_footprint and not is_national:
    for state in state_footprint:
        if state in county_database:
            state_counties = [f"{county} ({state})" for county in county_database[state]]
            combined_county_options.extend(state_counties)
    combined_county_options = sorted(combined_county_options)

# Render the dynamic county dropdown based on the user's state selection
if is_national:
    st.info("🇺🇸 National Scope Selected. Counties default automatically to 'All Counties'.")
    selected_counties = ["All Counties"]
elif len(state_footprint) == 0:
    st.caption("🔒 *Awaiting state selection above to unlock local county choices...*")
    selected_counties = []
else:
    selected_counties = st.multiselect(
        "2. Select Covered Counties (Leave empty for 'All Counties'):",
        options=["Select All Counties"] + combined_county_options,
        key="selected_counties_val"
    )

st.markdown("---")

# ==============================================================================
# 📝 STEP 2: STABLE COMPLIANCE INTAKE FORM CONTAINER
# ==============================================================================
with st.form("org_reg_form", clear_on_submit=True):
    
    st.subheader("🏢 Corporate Profile & Identification")
    org_name = st.text_input("Organization Legal Name / DBA:*", placeholder="e.g., Volunteer Response Force", key="org_name_val")
    fein_num = st.text_input("9-Digit Federal Employer Identification Number (FEIN):*", placeholder="XX-XXXXXXX", key="fein_num_val")
    primary_phone = st.text_input("Primary Dispatch Hotline / Crisis Contact Phone:*", placeholder="1-800-555-0100", key="primary_phone_val")
    
    op_scope = st.selectbox("Operational Footprint Tier:*", ["National", "Statewide", "Local / Mutual Aid"], key="op_scope_val")
    
    st.markdown("---")
    st.subheader("⚡ Core Capabilities & Framework Alignment")
    primary_esf = st.selectbox("Primary Emergency Support Function (ESF):*", [
        "ESF #2: Communications", 
        "ESF #6: Mass Care", 
        "ESF #9: Search & Rescue", 
        "ESF #13: Public Safety",
        "ESF #15: Volunteers & Donations"
    ], key="primary_esf_val")
    secondary_esfs = st.text_input("Secondary ESFs Supported (Optional):", placeholder="e.g., ESF #3, ESF #11", key="secondary_esfs_val")
    resource_inventory = st.text_area("Resource Inventory Capacities & Logistical Assets:*", placeholder="Detail standard NIMS resource types, vehicle counts, kitchens, or personnel.", key="resource_inventory_val")
    
    st.markdown("---")
    st.subheader("🔗 Verification Media & Assets")
    logo_url = st.text_input("Organization Logo Vector URL (Optional):", placeholder="https://example.com", key="logo_url_val")
    doc_url = st.text_input("Tax Exempt IRS Determination PDF Link (Optional):", placeholder="https://example.com", key="doc_url_val")
    
    st.markdown("---")
    compliance_check = st.checkbox("I certify that all submitted parameters represent verifiable active deployment capacities.*", key="compliance_check_val")
    
    # FORM SUBMISSION EXECUTOR
    submit_btn = st.form_submit_button("Submit Registry Records to Compliance Queue")
    
    if submit_btn:
        # 🟢 SIMPLIFIED STRING VERIFICATION TO GUARANTEE PIPELINE WRITE EXECUTION
        if org_name and fein_num and primary_phone and resource_inventory and state_footprint:
            if compliance_check:
                new_id = generate_org_id()
                
                # Format text strings from multi-choice widgets cleanly for your 17-column sheet
                states_string = ", ".join(state_footprint)
                
                if not selected_counties or "Select All Counties" in selected_counties or is_national:
                    counties_string = "All Counties"
                else:
                    counties_string = ", ".join(selected_counties)
                
                # 🚨 CRITICAL FIX: Schema matched exactly to your live spreadsheet columns
                new_row = pd.DataFrame([{
                    "Org_ID": new_id,
                    "Organization_Name": org_name,
                    "EIN_Number": fein_num,
                    "Operation_Scope": op_scope,
                    "State_Supported": states_string,
                    "Counties_Covered": counties_string,
                    "Primary_ESF_Focus": primary_esf,
                    "Secondary_ESFs": secondary_esfs,
                    "Resource_Capacity": f"Hotline: {primary_phone} | Assets: {resource_inventory}",
                    "Org_Logo_URL": logo_url,
                    "Tax_Exempt_Doc_URL": doc_url,
                    "Data_Verified": False,
                    "Verification_Time": "",
                    "Verifying_Email": "",
                    "Account_Status": "Active",
                    "Latitude": 0.0,
                    "Longitude": 0.0
                }])
                
                # Google Sheets Write Pipeline
                try:
                    if conn:
                        # 🚨 FORCE CACHE REFRESH: Pulls the absolute latest records
                        # Double-check your Google Sheets tab name! Change "Organizations" below if your tab is named "Sheet1"
                        existing_data = conn.read(worksheet="Organizations", ttl=0)
                        
                        # Append the newly structured organization row
                        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
                        
                        # Overwrite the spreadsheet with the updated matrix
                        conn.update(worksheet="Organizations", data=updated_data)
                        
                        # Track execution variables inside temporary storage keys to pass past rerun context
                        st.session_state.last_submitted_id = new_id
                        st.session_state.form_submit_success = True
                        
                        # 🔄 FLUSH FORM: Clear all bound fields out of session state memory instantly
                        for key in list(st.session_state.keys()):
                            if key.endswith("_val"):
                                del st.session_state[key]
                        
                        # Force instant application layout visual refresh
                        st.rerun()
                    else:
                        st.warning("⚠ Sandbox Offline Mode: Data processed locally but cloud secrets are missing.")
                except Exception as e:
                    st.error(f"❌ Spreadsheet Write Failure: {e}")
            else:
                st.error("❌ You must check the compliance verification box to complete your entry.")
        else:
            st.error("❌ Missing required fields. Please fill out Name, FEIN, Phone, States, and Resource Inventory.")

# Display persistent tracking details on the clean rerouted page state layout
if st.session_state.form_submit_success:
    st.success("💾 Staged corporate records securely appended to live Google Sheet database!")
    st.balloons()
    st.markdown(f"### 🔑 Tracking Identification Key: `{st.session_state.last_submitted_id}`")
    st.info("💡 Save this key. It is required to modify or archive your assets post-demo.")
    # Reset completion flag to ensure clean workflows for consecutive entries
    st.session_state.form_submit_success = False
