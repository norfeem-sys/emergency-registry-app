import streamlit as st
import pandas as pd
import random
import string
from datetime import datetime

# Secure Google Sheets Connection Engine via Streamlit Native Secrets
try:
    conn = st.connection("gsheets", type=st.connections.GSheetsConnection)
except Exception:
    conn = None

def generate_org_id():
    """Generates a unique tracking key matching the Org_ID database format."""
    return "ORG-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

st.set_page_config(page_title="Organization Registration Portal", layout="centered")
st.title("🏢 Emergency Organization Registry Portal")
st.caption("Live Schema Sync Ingestion Form")

with st.form("org_reg_form", clear_on_submit=True):
    st.subheader("📋 Official Asset Registration & Vetting Intake")
    
    # Core Corporate Fields
    org_name = st.text_input("Organization Name (Legal/DBA):*")
    ein_num = st.text_input("9-Digit EIN Number (Tax ID):*")
    
    # Tiered Scope Selectors
    op_scope = st.selectbox("Operation Scope Tier:*", ["National", "Statewide", "Local / Mutual Aid"])
    state_footprint = st.selectbox("Primary State Supported:*", ["FL", "TX", "GA", "NC", "SC", "All States"])
    counties = st.text_input("Counties Covered (Comma separated list, or 'All Counties'):", value="All Counties")
    
    # Flexible Emergency Alignments
    esf_focus = st.selectbox("Primary ESF Focus Role:*", [
        "ESF #2: Communications", 
        "ESF #6: Mass Care", 
        "ESF #9: Search & Rescue", 
        "ESF #13: Public Safety",
        "ESF #15: Volunteers & Donations"
    ])
    secondary_esfs = st.text_input("Secondary ESFs Supported (Optional, comma separated, e.g., 'ESF #3, ESF #11'):")
    
    # Resource Logs
    inventory = st.text_area("Detailed Resource Capacity & Logistics Assets:*")
    
    # Verification/Media Ingestion Placeholders
    logo_url = st.text_input("Organization Logo URL (Optional):")
    doc_url = st.text_input("Tax Exempt Verification Document PDF Link (Optional):")
    
    # Mapping Coordinates
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("HQ Coordinate Latitude:*", format="%.4f", value=27.3364)
    with col2:
        lon = st.number_input("HQ Coordinate Longitude:*", format="%.4f", value=-82.5307)
        
    submit_btn = st.form_submit_button("Submit Registry Application")
    
    if submit_btn:
        if org_name and ein_num and inventory:
            new_id = generate_org_id()
            
            # Formulating the exact payload layout mapping 1-to-1 to your spreadsheet header keys
            new_row = pd.DataFrame([{
                "Org_ID": new_id,
                "Organization_Name": org_name,
                "EIN_Number": ein_num,
                "Operation_Scope": op_scope,
                "State_Supported": state_footprint,
                "Counties_Covered": counties,
                "Primary_ESF_Focus": esf_focus,
                "Secondary_ESFs": secondary_esfs,
                "Resource_Capacity": inventory,
                "Org_Logo_URL": logo_url,
                "Tax_Exempt_Doc_URL": doc_url,
                "Data_Verified": "Pending",        # Default vetting state
                "Verification_Time": "N/A",        # Empty until an administrator approves
                "Verifying_Email": "N/A",          # Empty until approved
                "Account_Status": "Active",        # Operational baseline status
                "Latitude": float(lat),
                "Longitude": float(lon)
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
            st.info("💡 Keep this tracking key safe. It will be required to fetch or modify your corporate status logs post-demo.")
        else:
            st.error("❌ Mandatory metrics missing. Please complete Name, EIN Number, and Resource Capacity metrics.")
