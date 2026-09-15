import streamlit as st
import gspread
from google.oauth2.service_account import Credentials as SACredentials
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="Emergency Volunteer Registry", layout="wide", page_icon="🚨")

st.title("🚨 Emergency Volunteer Registration Platform")
st.subheader("Production Data Synchronization Ledger")

# Establish UI layout structure tabs
tab_register, tab_map = st.tabs(["📥 Add New Organization", "🗺️ Registered Emergency Map"])

# Global Config Arrays for Input Validation
ALLOWED_STATES = ["FL", "TX", "GA", "All States"]
STANDARD_ESFS = [
    "ESF #1: Transportation", "ESF #2: Communications", "ESF #3: Public Works",
    "ESF #4: Firefighting", "ESF #5: Info & Planning", "ESF #6: Mass Care",
    "ESF #8: Public Health", "ESF #9: Search & Rescue", "ESF #10: Oil & HazMat",
    "ESF #11: Agriculture", "ESF #12: Energy", "ESF #13: Public Safety",
    "ESF #14: Cross-Sector", "ESF #15: External Affairs", "ESF #17: Military Support"
]

# Initialize Database Bridge
db_connected = False
try:
    scope = [
        "https://googleapis.com",
        "https://googleapis.com"
    ]
    
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds_dict["auth_uri"] = "https://google.com"
    creds_dict["token_uri"] = "https://googleapis.com"
    creds_dict["auth_provider_x509_cert_url"] = "https://googleapis.com"
    creds_dict["client_x509_cert_url"] = f"https://googleapis.com{creds_dict['client_email'].replace('@', '%40')}"

    credentials = SACredentials.from_service_account_info(creds_dict, scopes=scope)
    gc = gspread.authorize(credentials)

    sheet_id = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"
    spreadsheet = gc.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet("Organizations")
    db_connected = True
    st.sidebar.success("⚡ Live Connection to Google Sheet Verified")

except Exception as e:
    st.sidebar.error("❌ Database Connection Interrupted")
    st.sidebar.write(f"Error: {e}")

# ---------------------------------------------------------------------
# 1) FULL SCHEMA WRITE COMPONENT
# ---------------------------------------------------------------------
with tab_register:
    st.header("Comprehensive Organization Dossier Entry")
    
    if db_connected:
        with st.form("comprehensive_org_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                org_name = st.text_input("Organization Name*")
                ein_number = st.text_input("EIN Number (Format: XX-XXXXXXX)*", max_chars=10)
                op_scope = st.selectbox("Operation Scope*", ["Local", "Regional", "Statewide", "National", "Global"])
                state_supported = st.selectbox("State Supported*", ALLOWED_STATES)
                counties_covered = st.text_input("Counties Covered (e.g., 'All Counties' or comma-separated list)*")
            
            with col2:
                primary_esf = st.selectbox("Primary ESF Focus*", STANDARD_ESFS)
                secondary_esfs = st.multiselect("Secondary ESFs", STANDARD_ESFS)
                resource_capacity = st.text_area("Resource Capacity / Inventory Details")
                logo_url = st.text_input("Organization Logo URL", value="https://unsplash.com")
                doc_url = st.text_input("Tax Exempt Documentation URL", value="https://example.org")
            
            st.markdown("---")
            st.subheader("Geospatial Base Coordinates")
            geo_col1, geo_col2 = st.columns(2)
            with geo_col1:
                latitude = st.number_input("Latitude (Decimal)", format="%.4f", min_value=-90.0, max_value=90.0, value=28.0)
            with geo_col2:
                longitude = st.number_input("Longitude (Decimal)", format="%.4f", min_value=-180.0, max_value=180.0, value=-81.0)
                
            submit_button = st.form_submit_button(label="Submit Record to Master Spreadsheet")
            
            if submit_button:
                if not org_name.strip() or not ein_number.strip() or not counties_covered.strip():
                    st.error("❌ Form Submission Halted: Please populate all fields marked with an asterisk (*).")
                elif "-" not in ein_number or len(ein_number) < 10:
                    st.error("❌ Validation Error: EIN must match standard tracking mask format (XX-XXXXXXX).")
                else:
                    # Generate values for metadata auto-fields
                    generated_id = f"ORG-{state_supported[:3].upper() if state_supported != 'All States' else 'NAT'}-{random.randint(100, 999)}"
                    sec_esf_str = ", ".join(secondary_esfs) if secondary_esfs else ""
                    
                    # Array elements aligned strictly with your 17 database columns
                    new_row = [
                        generated_id,                # 1. Org_ID
                        org_name.strip(),            # 2. Organization_Name
                        ein_number.strip(),          # 3. EIN_Number
                        op_scope,                    # 4. Operation_Scope
                        state_supported,             # 5. State_Supported
                        counties_covered.strip(),    # 6. Counties_Covered
                        primary_esf,                 # 7. Primary_ESF_Focus
                        sec_esf_str,                 # 8. Secondary_ESFs
                        resource_capacity.strip(),   # 9. Resource_Capacity
                        logo_url.strip(),            # 10. Org_Logo_URL
                        doc_url.strip(),             # 11. Tax_Exempt_Doc_URL
                        "False",                     # 12. Data_Verified
                        "",                          # 13. Verification_Time
                        "",                          # 14. Verifying_Email
                        "Pending Vetting",           # 15. Account_Status
                        str(latitude),               # 16. Latitude
                        str(longitude)               # 17. Longitude
                    ]
                    
                    try:
                        worksheet.append_row(new_row)
                        st.success(f"🎉 Success! '{org_name}' has been written as {generated_id}.")
                        st.json({col: val for col, val in zip(worksheet.row_values(1), new_row) if val})
                    except Exception as append_err:
                        st.error(f"Write Transaction Failed: {append_err}")
    else:
        st.info("Form disabled until database connection is verified.")

# ---------------------------------------------------------------------
# 2) DYNAMIC LIVE MAP PROCESSING
# ---------------------------------------------------------------------
with tab_map:
    st.header("Live Spatial Operations Map Canvas")
    st.markdown("Geographic footprints of registered emergency response entities pulled straight from the ledger matrix.")
    
    if db_connected:
        try:
            # Query spreadsheet rows directly
            raw_records = worksheet.get_all_records()
            
            if raw_records:
                df = pd.DataFrame(raw_records)
                
                # Verify that coordinates fields exist and convert cleanly to numbers
                if 'Latitude' in df.columns and 'Longitude' in df.columns:
                    df['lat'] = pd.to_numeric(df['Latitude'], errors='coerce')
                    df['lon'] = pd.to_numeric(df['Longitude'], errors='coerce')
                    
                    # Drop rows that lack numeric coordinates data
                    mapped_df = df.dropna(subset=['lat', 'lon'])
                    
                    if not mapped_df.empty:
                        # Render interactive map canvas directly onto screen frame
                        st.map(mapped_df, latitude='lat', longitude='lon', use_container_width=True)
                        
                        # Data Summary Checklist underneath map canvas
                        st.subheader("Active Entities Index")
                        st.dataframe(
                            mapped_df[['Org_ID', 'Organization_Name', 'State_Supported', 'Primary_ESF_Focus', 'Account_Status']],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.warning("Coordinates found in database, but values are blank or incorrectly formatted.")
                else:
                    st.error("Sheet Schema Discrepancy: 'Latitude' or 'Longitude' column headings were not detected.")
            else:
                st.info("The spreadsheet is currently empty. Registers will appear here once submitted.")
        except Exception as read_err:
            st.error(f"Failed to compile operational spatial layer data: {read_err}")
