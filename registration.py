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

st.set_page_config(page_title="Organization Registration Portal", layout="centered")

# --- APP BRANDING HEADERS ---
st.title("📋 National Emergency Registry Ingestion Portal")
st.caption("Official Compliance Intake Form for Disaster Response Providers")
st.markdown("---")

# ==============================================================================
# 🗺️ STEP 1: INTERACTIVE JURISDICTION MATRIX LAYER
# ==============================================================================
st.subheader("🗺️ Operational Footprint Scope")

# Multi-select state framework to capture regions like the Southeast
state_footprint = st.multiselect(
    "1. Primary State Horizon Base (Select 1 or more states):*", 
    options=["FL", "TX", "GA", "NC", "SC", "All States"],
    default=[]
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
            # Append county options along with their state marker for absolute clarity
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
    # County picker drops down instantly the second a state is clicked
    selected_counties = st.multiselect(
        "2. Select Covered Counties (Leave empty for 'All Counties'):",
        options=["Select All Counties"] + combined_county_options
    )

st.markdown("---")

# ==============================================================================
# 📝 STEP 2: STABLE COMPLIANCE INTAKE FORM CONTAINER
# ==============================================================================
with st.form("org_reg_form", clear_on_submit=True):
    
    st.subheader("🏢 Corporate Profile & Identification")
    org_name = st.text_input("Organization Legal Name / DBA:*", placeholder="e.g., Volunteer Response Force")
    fein_num = st.text_input("9-Digit Federal Employer Identification Number (FEIN):*", placeholder="XX-XXXXXXX")
    primary_phone = st.text_input("Primary Dispatch Hotline / Crisis Contact Phone:*", placeholder="1-800-555-0100")
    
    op_scope = st.selectbox("Operational Footprint Tier:*", ["National", "Statewide", "Local / Mutual Aid"])
    
    st.markdown("---")
    st.subheader("⚡ Core Capabilities & Framework Alignment")
    primary_esf = st.selectbox("Primary Emergency Support Function (ESF):*", [
        "ESF #2: Communications", 
        "ESF #6: Mass Care", 
        "ESF #9: Search & Rescue", 
        "ESF #13: Public Safety",
        "ESF #15: Volunteers & Donations"
    ])
    secondary_esfs = st.text_input("Secondary ESFs Supported (Optional):", placeholder="e.g., ESF #3, ESF #11")
    resource_inventory = st.text_area("Resource Inventory Capacities & Logistical Assets:*", placeholder="Detail standard NIMS resource types, vehicle counts, kitchens, or personnel.")
    
    st.markdown("---")
    st.subheader("🔗 Verification Media & Assets")
    logo_url = st.text_input("Organization Logo Vector URL (Optional):", placeholder="https://example.com")
    doc_url = st.text_input("Tax Exempt IRS Determination PDF Link (Optional):", placeholder="https://example.com")
    
    st.markdown("---")
    compliance_check = st.checkbox("I certify that all submitted parameters represent verifiable active deployment capacities.*")
    
    # FORM SUBMISSION EXECUTOR
    submit_btn = st.form_submit_button("Submit Registry Records to Compliance Queue")
    
    if submit_btn:
        # 🟢 SIMPLIFIED STRING VERIFICATION TO GUARANTEE PIPELINE WRITE EXECUTION
        if org_name and fein_num and primary_phone and resource_inventory and state_footprint:
            if compliance_check:
                new_id = generate_org_id()
                
                # Format text strings from multi-choice widgets cleanly for your 18-column sheet
                states_string = ", ".join(state_footprint)
                
                if not selected_counties or "Select All Counties" in selected_counties or is_national:
                    counties_string = "All Counties"
                else:
                    counties_string = ", ".join(selected_counties)
                
                # Constructing the exact data frame matching your 18-field tracking layout
                               # Google Sheets Write Pipeline
                try:
                    if conn:
                        # 🚨 FORCE CACHE REFRESH: Pulls the absolute latest records
                        existing_data = conn.read(worksheet="Organizations", ttl=0)
                        
                        # Append the newly structured organization row
                        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
                        
                        # Overwrite the spreadsheet with the updated matrix
                        conn.update(worksheet="Organizations", data=updated_data)
                        
                        st.success("💾 Staged corporate records securely appended to live Google Sheet database!")
                        st.balloons()
                    else:
                        st.warning("⚠ Sandbox Offline Mode: Data processed locally but cloud secrets are missing.")
                except Exception as e:
                    st.error(f"❌ Spreadsheet Write Failure: {e}")
                
                st.markdown(f"### 🔑 Tracking Identification Key: `{new_id}`")
                st.info("💡 Save this key. It is required to modify or archive your assets post-demo.")

                    "Account_Status": "Active",
                    "Data_Verified": "Pending",
                    "Verification_Time": "N/A",
                    "Verifying_Email": "N/A",
                    "Latitude": 0.0,
                    "Longitude": 0.0
                }])
                
                # Google Sheets Write Pipeline
                try:
                    if conn:
                        existing_data = conn.read(worksheet="Organizations")
                        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
                        conn.update(worksheet="Organizations", data=updated_data)
                        st.success("💾 Staged corporate records securely appended to live Google Sheet database!")
                    else:
                        st.warning("⚠️ Sandbox Offline Mode: Data processed locally but cloud secrets are missing.")
                except Exception as e:
                    st.error(f"❌ Spreadsheet Write Failure: {e}")
                    
                st.markdown(f"### 🔑 Tracking Identification Key: `{new_id}`")
                st.info("💡 Save this key. It is required to modify or archive your assets post-demo.")
            else:
                st.error("❌ You must check the compliance verification box to complete your entry.")
        else:
            st.error("❌ Missing required fields. Please fill out Name, FEIN, Phone, States, and Resource Inventory.")
