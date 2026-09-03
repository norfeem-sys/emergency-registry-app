import streamlit as st
import pandas as pd

st.set_page_config(page_title="Emergency Registry", layout="wide")
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Multi-State Disaster Response Pilot Framework")

# Prepopulated test data for our first online test deployment
# YOUR GOOGLE SHEET LINK IS DIRECTLY CODED BELOW:
LIVE_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY/edit?usp=sharing"

@st.cache_data
def load_bootstrap_data():
    data = {
        "Organization_Name": ["Florida Baptist Disaster Relief", "ITDRC", "Texas Response Network", "Georgia Feeding VOAD", "Sarasota Local CERT", "Global Rescue Corps"],
        "State_Supported": ["FL", "All States", "TX", "GA", "FL", "Global"],
        "Primary_ESF": ["ESF #6: Mass Care", "ESF #2: Communications", "ESF #13: Public Safety", "ESF #6: Mass Care", "ESF #9: Search & Rescue", "ESF #6: Mass Care"],
        "Phone": ["+18005550122", "+18773873646", "+15555550199", "+15555550144", "+15555550133", "+15555550111"],
        "Display_Phone": ["1-800-555-0122", "1-877-387-3646", "1-555-555-0199", "1-555-555-0144", "1-555-555-0133", "1-555-555-0111"],
        "Data_Verified": [True, True, False, True, False, False],
        "Capacity": ["3 Mobile Kitchens, 4 Chainsaw teams", "Satellite loops, Emergency Mesh WiFi towers", "Regional logistics assets", "Bulk feeding units", "Light rescue squads, 20 active members", "International deployment ready"]
    }
    return pd.DataFrame(data)

df = load_bootstrap_data()

# Sidebar Navigation Panel
st.sidebar.header("🧭 Dashboard Navigation")
app_mode = st.sidebar.radio("Go to view:", ["Public Interactive Map", "🔒 Master Admin Reports"])

if app_mode == "Public Interactive Map":
    st.sidebar.subheader("Map Filters")
    selected_state = st.sidebar.selectbox("Select State Horizon:", ["FL", "TX", "GA", "All States"])
    
    # Filter dataset matches
    filtered_df = df[(df["State_Supported"] == selected_state) | (df["State_Supported"] == "All States") | (df["State_Supported"] == "Global")]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### Active Responders Supporting: `{selected_state}`")
        st.dataframe(filtered_df[["Organization_Name", "Primary_ESF", "State_Supported"]], use_container_width=True, hide_index=True)
        selected_org = st.selectbox("Select an organization to expand live details:", filtered_df["Organization_Name"].tolist())
        
    with col2:
        if selected_org:
            org_row = filtered_df[filtered_df["Organization_Name"] == selected_org].iloc
            st.markdown(f"#### 🏢 {org_row['Organization_Name']}")
            st.markdown(f"**Primary Task Matrix:** `{org_row['Primary_ESF']}`")
            st.info(f"**Logistical Capacity:**\n{org_row['Capacity']}")
            
            # Click to Call Hyperlink Injection
            phone_url = f"tel:{org_row['Phone']}"
            st.markdown(f'👉 <a href="{phone_url}" style="font-size:18px; font-weight:bold; color:#1f77b4; text-decoration:none;">📲 Click to Call: {org_row["Display_Phone"]}</a>', unsafe_allow_html=True)

elif app_mode == "🔒 Master Admin Reports":
    st.subheader("📊 Administrative System Integrity Analytics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Agencies Registered", len(df))
    unverified_count = len(df[df["Data_Verified"] == False])
    c2.metric("⚠️ Pending Attestation Check", unverified_count, delta=f"{unverified_count} Alerts Pending", delta_color="inverse")
    c3.metric("Global Scaling Footprint", "Active")
    
    st.markdown("#### Organizations Missing Data Sign-off")
    unverified_table = df[df["Data_Verified"] == False]
    st.dataframe(unverified_table[["Organization_Name", "State_Supported", "Display_Phone"]], use_container_width=True, hide_index=True)
