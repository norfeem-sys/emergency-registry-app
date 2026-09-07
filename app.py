import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

st.set_page_config(page_title="Emergency Registry", layout="wide")
st.title("🗺️ National Volunteer & Organization Emergency Registry")
st.caption("501(c)(3) Live Multi-State Disaster Response Advanced Spatial Sandbox")

# 🔗 Live Connection Parameters
SPREADSHEET_ID = "1CAXvQUPhOfq2QAxqVaaZ8IhPuUUfN13FlCj75EUbhhY"
url = f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Organizations"

try:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df = df.dropna(subset=["Latitude", "Longitude"])
except Exception as e:
    st.error(f"🌐 Google Connection Refreshing... Click 'Reboot' if stuck. Details: {e}")
    st.stop()

# 🌍 Sidebar Regional Filter
st.sidebar.header("Operational Filters")
states = ["All States"] + sorted(df["State_Supported"].dropna().unique().tolist())
sel_state = st.sidebar.selectbox("Select Target State:", states)

filtered_df = df.copy()
center = [37.0902, -95.7129]
zoom = 4

if sel_state != "All States":
    filtered_df = df[df["State_Supported"].str.upper() == sel_state.upper()]
    if not filtered_df.empty:
        center = [filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()]
        zoom = 6

# 🗺️ Panoramic Panoramic Canvas Window
st.subheader("📍 Interactive Panoramic Drawing Canvas")
m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
Draw(position='topleft', draw_options={'polyline':False, 'circle':False, 'marker':False, 'polygon':True, 'rectangle':True}).add_to(m)

for idx, row in filtered_df.iterrows():
    folium.CircleMarker(location=[row["Latitude"], row["Longitude"]], radius=6, color="#1f77b4", fill=True, popup=f"<b>{row['Organization_Name']}</b>").add_to(m)

map_out = st_folium(m, width=1400, height=450, key="canvas")

# 🖱️ Mouse Bounding Box Processing
drawn = map_out.get("last_active_drawing")
if drawn and "geometry" in drawn:
    coords = drawn["geometry"]["coordinates"][0]
    lats, lons = [c[1] for c in coords], [c[0] for c in coords]
    filtered_df = filtered_df[(filtered_df["Latitude"] >= min(lats)) & (filtered_df["Latitude"] <= max(lats)) & (filtered_df["Longitude"] >= min(lons)) & (filtered_df["Longitude"] <= max(lons))]

st.write("---")

# 📊 Lower Section Layout Split
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏢 Expanded Asset Logs")
    if not filtered_df.empty:
        chosen = st.selectbox("Inspect profile metrics:", filtered_df["Organization_Name"].tolist())
        rec = filtered_df[filtered_df["Organization_Name"] == chosen].iloc[0]
        st.markdown(f"### **{rec['Organization_Name']}**")
        st.info(f"💪 **Capacity:** {rec.get('Resource_Capacity', 'No description logged.')}")
        phone = str(rec.get("Phone", ""))
        if phone and phone != "nan":
            st.markdown(f'👉 <a href="tel:{phone.replace("-","")}" style="font-size:16px; font-weight:bold; color:#1f77b4; text-decoration:none;">📲 Click to Call: {phone}</a>', unsafe_allow_html=True)
    else:
        st.write("No groups inside this layout scope.")

with col2:
    st.subheader("📊 Operational Resource Metrics")
    if not filtered_df.empty:
        st.metric("Total Responders in View", len(filtered_df))
        st.bar_chart(filtered_df["Primary_ESF_Focus"].value_counts())

st.write("---")
st.subheader("📊 Dynamic Data Records Pipeline Table")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# force container network flush

