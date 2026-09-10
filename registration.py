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
st.title("📋 National Emergency Registry Intake Portal")
st.caption("Official Compliance Ingestion System for Disaster Response Providers")
st.markdown("---")

# Main Intake Form
with st.form("org_reg_form", clear_on_submit=True):
    
    # SECTION 1: IDENTITY AND ACCOUNTING
    st.subheader("🏢 Corporate Profile & Identification")
    org_name = st.text_input("Organization Legal Name / DBA:*", placeholder="e.g., Volunteer Response Force")
    fein_num = st.text_input("9-Digit Federal Employer Identification Number (FEIN):*", max_chars=10, placeholder="XX-XXXXXXX")
    primary_phone = st.text_input("Primary Dispatch Hotline / Crisis Contact Phone:*", placeholder="1-800-555-0100")
    
    # SECTION 2: JURISDICTION HORIZON
    st.markdown("---")
    st.subheader("🗺️ Operational Footprint Scope")
    op_scope = st.selectbox("Operational Footprint Tier:*", ["National", "Statewide", "Local / Mutual Aid"])
    state_footprint = st.selectbox("Primary State Horizon Base:*", ["FL", "TX", "GA", "NC", "SC", "All States"])
    counties = st.text_input("Counties Covered:*", value="All Counties", help="Specify single counties or write 'All Counties'.")
    
    # SECTION 3: FRAMEWORK REALIGNMENT
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
    resource_inventory = st.text_area("Resource Inventory Capacities & Logistical Assets:*", placeholder="Detail standard NIMS types, vehicle counts, feeding capacities, or specialty personnel numbers.")
    
    # SECTION 4: CREDENTIAL DOCUMENTATION
    st.markdown("---")
    st.subheader("🔗 Verification Media & Assets")
    logo_url = st.text_input("Organization Logo Vector URL (Optional):", placeholder="https://example.com")
    doc_url = st.text_input("Tax Exempt IRS Determination PDF Link (Optional):", placeholder="https://example.com")
    
    # SECTION 5: SIGNATURE & COMPLIANCE AGREEMENT
    st.markdown("---")
    compliance_check = st.checkbox("I certify that all information submitted is true, accurate, and represents verifiable active asset capacities ready for state or federal deployment authorization.*")
    
    # FORM INTAKE RUN BUTTON
    submit_btn = st.form_submit_button("Submit Registry Records to Compliance Queue")
    
    if submit_btn:
        if org_name and list(fein_num) and primary_phone and resource_inventory:
            if compliance_check:
                new_id = generate_org_id()
                
                # Constructing the exact 18-field operational layout matrix matching the spreadsheet
                new_row = pd.DataFrame([{
                    "Org_ID": new_id,
                    "Organization_Name": org_name,
                    "FEIN": fein_num,
                    "Operation_Scope": op_scope,
                    "State_Supported": state_footprint,
                    "Counties_Covered": counties,
                    "Primary_Phone": primary_phone,
                    "Primary_ESF": primary_esf,
                    "Secondary_ESFs": secondary_esfs,
                    "Resource_Inventory": resource_inventory,
                    "Org_Logo_URL": logo_url,
                    "Tax_Exempt_Doc_URL": doc_url,
                    "Account_Status": "Active",
                    "Data_Verified": "Pending",        # Flagged as pending for administrator review
                    "Verification_Time": "N/A",
                    "Verifying_Email": "N/A",
                    "Latitude": 0.0,                   # Form structures latitude
                    "Longitude": 0.0                   # Form structures longitude
                }])
                
                # Connection Sync Engine Execution Loop
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
                st.info("💡 Give this tracking key to your leadership. It will be required to fetch or modify your corporate status logs post-demo.")
            else:
                st.error("❌ You must check the compliance verification box to complete your application entry.")
        else:
            st.error("❌ Mandatory metrics missing. Please complete Name, FEIN, Phone, and Resource Inventory metrics.")
