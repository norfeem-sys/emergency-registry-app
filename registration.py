import streamlit as st
import gspread
from google.oauth2.service_account import Credentials as SACredentials
import random

st.title("Emergency Volunteer Registration Baseline")
st.subheader("Step 1: Verify Connection and Registration")

try:
    # 1. Correct Google API endpoint scopes (Requires Spreadsheets AND Drive)
    scope = [
        "https://googleapis.com",
        "https://googleapis.com"
    ]
    
    # 2. Extract configuration payload dynamically from secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # 3. Handle literal string line breaks correctly
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    # FIX: Step 4 manual URL overrides removed to fix the 404 connection crash.
    # Google auto-resolves these perfectly from your original service account data.

    # 5. Authorize directly
    credentials = SACredentials.from_service_account_info(creds_dict, scopes=scope)
    gc = gspread.authorize(credentials)

    # 6. Target Sheet Identification
    sheet_id = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"
    spreadsheet = gc.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet("Organizations")
    
    st.success("Secure connection to Google Sheet established successfully.")

    # 7. Comprehensive Form Processing matching your exact 17 columns
    with st.form("simple_org_form"):
        st.write("### Organization Registration Dossier")
        
        org_name = st.text_input("Organization Name:")
        ein_number = st.text_input("EIN Number (Format: XX-XXXXXXX):")
        op_scope = st.selectbox("Operation Scope:", ["Local", "Regional", "Statewide", "National", "Global"])
        state_supported = st.text_input("State Supported (e.g., FL):")
        counties_covered = st.text_input("Counties Covered:")
        
        primary_esf = st.text_input("Primary ESF Focus:")
        secondary_esfs = st.text_input("Secondary ESFs (Comma separated):")
        resource_capacity = st.text_area("Resource Capacity:")
        
        logo_url = st.text_input("Organization Logo URL:", value="https://unsplash.com")
        doc_url = st.text_input("Tax Exempt Documentation URL:", value="https://example.org")
        
        lat = st.text_input("Latitude:")
        lon = st.text_input("Longitude:")
        
        submit_button = st.form_submit_button(label="Submit to Spreadsheet")
        
        if submit_button:
            if not org_name.strip():
                st.write("Please enter a valid name before submitting.")
            else:
                # Aligned strictly to your 17 structural spreadsheet columns
                generated_id = f"ORG-{random.randint(1000, 9999)}"
                
                new_row = [
                    generated_id,            # 1. Org_ID
                    org_name.strip(),        # 2. Organization_Name
                    ein_number.strip(),      # 3. EIN_Number
                    op_scope,                # 4. Operation_Scope
                    state_supported.strip(), # 5. State_Supported
                    counties_covered.strip(),# 6. Counties_Covered
                    primary_esf.strip(),     # 7. Primary_ESF_Focus
                    secondary_esfs.strip(),  # 8. Secondary_ESFs
                    resource_capacity.strip(),# 9. Resource_Capacity
                    logo_url.strip(),        # 10. Org_Logo_URL
                    doc_url.strip(),         # 11. Tax_Exempt_Doc_URL
                    "False",                 # 12. Data_Verified
                    "",                      # 13. Verification_Time
                    "",                      # 14. Verifying_Email
                    "Pending Vetting",       # 15. Account_Status
                    lat.strip(),             # 16. Latitude
                    lon.strip()              # 17. Longitude
                ]
                
                worksheet.append_row(new_row)
                st.write(f"Success. {org_name} has been written to the spreadsheet row.")

except Exception as e:
    st.write("Connection Error Flagged")
    st.write(f"Details: {e}")
