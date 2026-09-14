import streamlit as st
import gspread
from google.oauth2.service_account import Credentials as SACredentials

st.title("Emergency Volunteer Registration Baseline")
st.subheader("Step 1: Verify Connection and Write Organization Name")

try:
    # 1. Broadest baseline scopes required for Google API endpoints
    scope = [
        "https://google.com",
        "https://googleapis.com"
    ]
    
    # 2. Extract configuration dictionary safely
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # 3. Clean up formatting variables dynamically
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    # 4. CRITICAL: Force the correct Google Auth gateway paths right here 
    # This completely overrides any hidden broken URLs inside the secrets panel.
    creds_dict["auth_uri"] = "https://google.com"
    creds_dict["token_uri"] = "https://google.com"
    creds_dict["auth_provider_x509_cert_url"] = "https://googleapis.com"
    creds_dict["client_x509_cert_url"] = f"https://googleapis.com{creds_dict['client_email'].replace('@', '%40')}"

    # 5. Authenticate explicitly with Google
    credentials = SACredentials.from_service_account_info(creds_dict, scopes=scope)
    gc = gspread.authorize(credentials)

    # 6. Establish Connection to the Spreadsheet Tab
    sheet_id = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"
    spreadsheet = gc.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet("Organizations")
    
    st.write("Secure connection to Google Sheet established successfully.")

    # 7. Form Logic Block
    with st.form("simple_org_form"):
        org_name = st.text_input("Enter Organization Name:")
        submit_button = st.form_submit_button(label="Submit to Spreadsheet")
        
        if submit_button:
            if not org_name.strip():
                st.write("Please enter a valid name before submitting.")
            else:
                new_row = [
                    "PENDING", org_name, "", "", "", "", "", "", "", "", "", "", "", "", "Pending", "", ""
                ]
                worksheet.append_row(new_row)
                st.write(f"Success. {org_name} has been written to the spreadsheet.")

except Exception as e:
    st.write("Connection Error Flagged")
    st.write(f"Details: {e}")
