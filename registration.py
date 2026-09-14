import streamlit as st
import gspread
from google.oauth2.service_account import Credentials as SACredentials

st.title("Emergency Volunteer Registration Baseline")
st.subheader("Step 1: Verify Connection and Write Organization Name")

try:
    # 1. Core Scopes for Google Drive and Google Sheets APIs
    scope = [
        "https://google.com",
        "https://googleapis.com"
    ]
    
    # 2. Extract Secrets Dictionary
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # 3. Authenticate directly
    credentials = SACredentials.from_service_account_info(creds_dict, scopes=scope)
    gc = gspread.authorize(credentials)

    # 4. Bind Sheet Target
    sheet_id = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"
    spreadsheet = gc.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet("Organizations")
    
    st.write("Secure connection to Google Sheet established successfully.")

    # 5. Interface Definition
    with st.form("simple_org_form"):
        org_name = st.text_input("Enter Organization Name:")
        submit_button = st.form_submit_button(label="Submit to Spreadsheet")
        
        if submit_button:
            if not org_name.strip():
                st.write("Please enter a valid name before submitting.")
            else:
                new_row = [
                    "PENDING",      # Org_ID
                    org_name,       # Organization_Name
                    "", "", "", "", "", "", "", "", "", "", "", "", "Pending", "", ""
                ]
                worksheet.append_row(new_row)
                st.write(f"Success. {org_name} has been written to the spreadsheet.")

except Exception as e:
    st.write("Connection Error Flagged")
    st.write(f"Details: {e}")
