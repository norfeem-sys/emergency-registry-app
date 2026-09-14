import streamlit as st
import gspread
from google.oauth2.service_account import Credentials as SACredentials

st.title("Emergency Volunteer Registration Baseline")
st.subheader("Step 1: Verify Connection and Write Organization Name")

try:
    # 1. Secure Authentication Setup - Corrected endpoints mapping scopes
    scope = [
        "https://google.com",
        "https://googleapis.com"
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    # Clean the private key string to handle formatting variations gracefully
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    credentials = SACredentials.from_service_account_info(creds_dict, scopes=scope)
    gc = gspread.authorize(credentials)

    # 2. Establish Connection to the Spreadsheet Tab
    sheet_id = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"
    spreadsheet = gc.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet("Organizations")
    
    st.write("Secure connection to Google Sheet established successfully.")

    # 3. Simple Form Interface
    with st.form("simple_org_form"):
        org_name = st.text_input("Enter Organization Name:")
        submit_button = st.form_submit_button(label="Submit to Spreadsheet")
        
        if submit_button:
            if not org_name.strip():
                st.write("Please enter a valid name before submitting.")
            else:
                # Array perfectly aligned to your 17 structural sheet columns
                new_row = [
                    "PENDING",      # Org_ID
                    org_name,       # Organization_Name (Your Input)
                    "", "", "", "", "", "", "", "", "", "", "", "", "Pending", "", ""
                ]
                
                # Push row immediately
                worksheet.append_row(new_row)
                st.write(f"Success. {org_name} has been written to the spreadsheet.")

except Exception as e:
    st.write("Connection Error Flagged")
    st.write(f"Details: {e}")
