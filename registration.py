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
    return "ORG-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

st.set_page_config(page_title="Organization Registration Portal", layout="centered")

st.title("📋 National Emergency Registry Intake Portal")
st.caption("Official Compliance Ingestion System for Disaster Response Providers")
st.markdown("---")

# Comprehensive built-in county database for standard operational states
COUNTY_DATABASE = {
    "FL": ["Alachua", "Baker", "Bay", "Bradford", "Brevard", "Broward", "Calhoun", "Charlotte", "Citrus", "Clay", "Collier", "Columbia", "DeSoto", "Dixie", "Duval", "Escambia", "Flagler", "Franklin", "Gadsden", "Gilchrist", "Glades", "Gulf", "Hamilton", "Hardee", "Hendry", "Hernando", "Highlands", "Hillsborough", "Holmes", "Indian River", "Jackson", "Jefferson", "Lafayette", "Lake", "Lee", "Leon", "Levy", "Liberty", "Madison", "Manatee", "Marion", "Martin", "Miami-Dade", "Monroe", "Nassau", "Okaloosa", "Okeechobee", "Orange", "Osceola", "Palm Beach", "Pasco", "Pinellas", "Polk", "Putnam", "Santa Rosa", "Sarasota", "Seminole", "St. Johns", "St. Lucie", "Sumter", "Suwannee", "Taylor", "Union", "Volusia", "Wakulla", "Walton", "Washington"],
    "TX": ["Harris", "Dallas", "Tarrant", "Bexar", "Travis", "El Paso", "Collin", "Hidalgo", "Denton", "Fort Bend", "Montgomery", "Williamson", "Cameron", "Nueces", "Galveston"],
    "GA": ["Fulton", "Gwinnett", "Cobb", "DeKalb", "Chatham", "Cherokee", "Forsyth", "Richmond", "Muscogee", "Hall", "Paulding", "Bibb"],
    "NC": ["Wake", "Mecklenburg", "Guilford", "Forsyth", "Cumberland", "Durham", "Buncombe", "New Hanover", "Union", "Gaston"],
    "SC": ["Greenville", "Richland", "Charleston", "Horry", "Spartanburg", "Lexington", "York", "Berkeley", "Anderson", "Beaufort"]
}

with st.form("org_reg_form", clear_on_submit=True):
    st.subheader("🏢 Corporate Profile & Identification")
    org_name = st.text_input("Organization Legal Name / DBA:*")
    fein_num = st.text_input("9-Digit Federal Employer Identification Number (FEIN):*")
    primary_phone = st.text_input("Primary Dispatch Hotline / Crisis Contact Phone:*")
    
    st.markdown("---")
    st.subheader("🗺️ Operational Footprint Scope")
    
    op_scope = st.selectbox("Operational Footprint Tier:*", ["Local / Mutual Aid", "Statewide", "National"])
    
    # Use multiselect directly to support Southeast regional clusters
    state_options = ["FL", "TX", "GA", "NC", "SC", "All States"]
    selected_states = st.multiselect("Select States Supported:*", options=state_options)
    
    merged_counties = []
    is_national = "All States" in selected_states or op_scope == "National"
    
    if not is_national and selected_states:
        for state in selected_states:
            if state in COUNTY_DATABASE:
                merged_counties.extend([f"{county} ({state})" for county in COUNTY_DATABASE[state]])
        merged_counties = sorted(list(set(merged_counties)))
        
    if is_national:
        st.markdown("🔒 **Counties Covered Scope:** `All Counties` (Bypassed for National footprint)")
        final_counties_str = "All Counties"
    elif not selected_states:
        st.info("💡 Please select at least one state code above to populate available counties list.")
        final_counties_str = "All Counties"
    else:
        chosen_counties = st.multiselect(
            "Select Counties Covered (Leave completely blank or select 'Select All' to cover entire state profile):",
            options=["Select All"] + merged_counties
        )
        if "Select All" in chosen_counties or not chosen_counties:
            final_counties_str = "All Counties"
        else:
            final_counties_str = ", ".join(chosen_counties)
            
    st.markdown("---")
    st.subheader("⚡ Core Capabilities & Framework Alignment")
    primary_esf = st.selectbox("Primary Emergency Support Function (ESF):*", [
        "ESF #2: Communications", "ESF #6: Mass Care", "ESF #9: Search & Rescue", "ESF #13: Public Safety", "ESF #15: Volunteers & Donations"
    ])
    secondary_esfs = st.text_input("Secondary ESFs Supported (Optional):")
    resource_inventory = st.text_area("Resource Inventory Capacities & Logistical Assets:*")
    
    st.markdown("---")
    st.subheader("🔗 Verification Media & Assets")
    logo_url = st.text_input("Organization Logo Vector URL (Optional):")
    doc_url = st.text_input("Tax Exempt IRS Determination PDF Link (Optional):")
    
    st.markdown("---")
    compliance_check = st.checkbox("I certify that all information submitted is true and accurate.*")
    
    submit_btn = st.form_submit_button("Submit Registry Records to Compliance Queue")
    
    if submit_btn:
        if org_name and fein_num and primary_phone and resource_inventory:
            if compliance_check:
                new_id = generate_org_id()
                states_str = "All States" if is_national else ", ".join(selected_states)
                
                new_row = pd.DataFrame([{
                    "Org_ID": new_id,
                    "Organization_Name": org_name,
                    "FEIN": fein_num,
                    "Operation_Scope": op_scope,
                    "State_Supported": states_str,
                    "Counties_Covered": final_counties_str,
                    "Primary_Phone": primary_phone,
                    "Primary_ESF": primary_esf,
                    "Secondary_ESFs": secondary_esfs,
                    "Resource_Inventory": resource_inventory,
                    "Org_Logo_URL": logo_url,
                    "Tax_Exempt_Doc_URL": doc_url,
                    "Account_Status": "Active",
                    "Data_Verified": "Pending",
                    "Verification_Time": "N/A",
                    "Verifying_Email": "N/A",
                    "Latitude": 0.0,
                    "Longitude": 0.0
                }])
                
                try:
                    if conn:
                        existing_data = conn.read(worksheet="Organizations")
                        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
                        conn.update(worksheet="Organizations", data=updated_data)
                        st.success("💾 Staged corporate records securely appended to live Google Sheet database!")
                    else:
                        st.warning("⚠️ Sandbox Offline Mode: Record processed locally but connection secrets are missing.")
                except Exception as e:
                    st.error(f"❌ Spreadsheet Write Failure: {e}")
                    
                st.markdown(f"### 🔑 Tracking Identification Key: `{new_id}`")
            else:
                st.error("❌ You must check the compliance verification box.")
        else:
            st.error("❌ Mandatory metrics missing.")
