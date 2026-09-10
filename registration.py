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

# Comprehensive Regional County Mapping Matrix
COUNTY_REGISTRY = {
    "FL": ["Alachua", "Baker", "Bay", "Bradford", "Brevard", "Broward", "Charlotte", "Citrus", "Clay", "Collier", "Columbia", "Dade", "DeSoto", "Dixie", "Duval", "Escambia", "Flagler", "Franklin", "Gadsden", "Gilchrist", "Glades", "Gulf", "Hamilton", "Hardee", "Hendry", "Hernando", "Highlands", "Hillsborough", "Holmes", "Indian River", "Jackson", "Jefferson", "Lafayette", "Lake", "Lee", "Leon", "Levy", "Liberty", "Madison", "Manatee", "Marion", "Martin", "Monroe", "Nassau", "Okaloosa", "Okeechobee", "Orange", "Osceola", "Palm Beach", "Pasco", "Pinellas", "Polk", "Putnam", "Santa Rosa", "Sarasota", "Seminole", "St. Johns", "St. Lucie", "Sumter", "Suwannee", "Taylor", "Union", "Volusia", "Wakulla", "Walton", "Washington"],
    "GA": ["Appling", "Atkinson", "Bacon", "Baker", "Baldwin", "Banks", "Barrow", "Bartow", "Ben Hill", "Berrien", "Bibb", "Bleckley", "Brantley", "Brooks", "Bryan", "Bulloch", "Burke", "Butts", "Calhoun", "Camden", "Candler", "Carroll", "Catoosa", "Charlton", "Chatham", "Chattahoochee", "Chattooga", "Cherokee", "Clarke", "Clay", "Clayton", "Clinch", "Cobb", "Coffee", "Colquitt", "Columbia", "Cook", "Coweta", "Crawford", "Crisp", "Dade", "Dawson", "Decatur", "DeKalb", "Dodge", "Dooly", "Dougherty", "Douglas", "Early", "Echols", "Effingham", "Elbert", "Emanuel", "Evans", "Fannin", "Fayette", "Floyd", "Forsyth", "Franklin", "Fulton", "Gilmer", "Glascock", "Glynn", "Gordon", "Grady", "Greene", "Gwinnett", "Habersham", "Hall", "Hancock", "Haralson", "Harris", "Hart", "Heard", "Henry", "Houston", "Irwin", "Jackson", "Jasper", "Jeff Davis", "Jefferson", "Jenkins", "Johnson", "Jones", "Lamar", "Lanier", "Laurens", "Lee", "Liberty", "Lincoln", "Long", "Lowndes", "Lumpkin", "Macon", "Madison", "Marion", "McDuffie", "McIntosh", "Meriwether", "Miller", "Mitchell", "Monroe", "Montgomery", "Morgan", "Murray", "Muscogee", "Newton", "Oconee", "Oglethorpe", "Paulding", "Peach", "Pickens", "Pierce", "Pike", "Polk", "Pulaski", "Putnam", "Quitman", "Rabun", "Randolph", "Richmond", "Rockdale", "Schley", "Screven", "Seminole", "Spalding", "Stephens", "Stewart", "Sumter", "Talbot", "Taliaferro", "Tattnall", "Taylor", "Telfair", "Terrell", "Thomas", "Tift", "Toombs", "Towns", "Treutlen", "Troup", "Turner", "Twiggs", "Union", "Upson", "Walker", "Walton", "Ware", "Warren", "Washington", "Wayne", "Webster", "Wheeler", "White", "Whitfield", "Wilcox", "Wilkes", "Wilkinson", "Worth"],
    "TX": ["Anderson", "Andrews", "Angelina", "Aransas", "Archer", "Armstrong", "Atascosa", "Austin", "Bailey", "Bandera", "Bastrop", "Baylor", "Bee", "Bell", "Bexar", "Blanco", "Borden", "Bosque", "Bowie", "Brazoria", "Brazos", "Brewster", "Briscoe", "Brooks", "Brown", "Burleson", "Burnet", "Caldwell", "Calhoun", "Callahan", "Cameron", "Camp", "Carson", "Cass", "Castro", "Chambers", "Cherokee", "Childress", "Clay", "Cochran", "Coke", "Coleman", "Collin", "Collingsworth", "Colorado", "Comal", "Comanche", "Concho", "Cooke", "Coryell", "Cottle", "Crane", "Crockett", "Crosby", "Culberson", "Dallam", "Dallas", "Dawson", "Deaf Smith", "Delta", "Denton", "DeWitt", "Dickens", "Dimmit", "Donley", "Duval", "Eastland", "Ector", "Edwards", "Ellis", "El Paso", "Erath", "Falls", "Fannin", "Fayette", "Fisher", "Floyd", "Foard", "Fort Bend", "Franklin", "Freestone", "Frio", "Gaines", "Galveston", "Garza", "Gillespie", "Glasscock", "Goliad", "Gonzales", "Gray", "Grayson", "Gregg", "Grimes", "Guadalupe", "Hale", "Hall", "Hamilton", "Hansford", "Hardeman", "Hardin", "Harris", "Harrison", "Hartley", "Haskell", "Hays", "Hemphill", "Henderson", "Hidalgo", "Hill", "Hockley", "Hood", "Hopkins", "Houston", "Howard", "Hudspeth", "Hunt", "Hutchinson", "Irion", "Jack", "Jackson", "Jasper", "Jeff Davis", "Jefferson", "Jim Hogg", "Jim Wells", "Johnson", "Jones", "Karnes", "Kaufman", "Kendall", "Kenedy", "Kent", "Kerr", "Kimble", "King", "Kinney", "Kleberg", "Knox", "Lamar", "Lamb", "Lampasas", "La Salle", "Lavaca", "Lee", "Leon", "Liberty", "Limestone", "Lipscomb", "Live Oak", "Llano", "Loving", "Lubbock", "Lynn", "McCulloch", "McLennan", "McMullen", "Madison", "Marion", "Martin", "Mason", "Matagorda", "Maverick", "Medina", "Menard", "Midland", "Milam", "Mills", "Mitchell", "Montague", "Montgomery", "Moore", "Morris", "Motley", "Nacogdoches", "Navarro", "Newton", "Nolan", "Nueces", "Ochiltree", "Oldham", "Orange", "Palo Pinto", "Panola", "Parker", "Parmer", "Pecos", "Polk", "Potter", "Presidio", "Rains", "Randall", "Reagan", "Real", "Red River", "Reeves", "Refugio", "Roberts", "Robertson", "Rockwall", "Runnels", "Rusk", "Sabine", "San Augustine", "San Jacinto", "San Patricio", "San Saba", "Schleicher", "Scurry", "Shackelford", "Shelby", "Sherman", "Smith", "Somervell", "Starr", "Stephens", "Sterling", "Stonewall", "Sutton", "Swisher", "Tarrant", "Taylor", "Terrell", "Terry", "Throckmorton", "Titus", "Tom Green", "Travis", "Trinity", "Tyler", "Upshur", "Upton", "Uvalde", "Val Verde", "Van Zandt", "Victoria", "Walker", "Waller", "Ward", "Washington", "Webb", "Wharton", "Wheeler", "Wichita", "Wilbarger", "Willacy", "Williamson", "Wilson", "Winkler", "Wise", "Wood", "Yoakum", "Young", "Zapata", "Zavala"],
    "NC": ["Alamance", "Alexander", "Alleghany", "Anson", "Ashe", "Avery", "Beaufort", "Bertie", "Bladen", "Brunswick", "Buncombe", "Burke", "Cabarrus", "Caldwell", "Camden", "Carteret", "Caswell", "Catawba", "Chatham", "Cherokee", "Chowan", "Clay", "Cleveland", "Columbus", "Craven", "Cumberland", "Currituck", "Dare", "Davidson", "Davie", "Duplin", "Durham", "Edgecombe", "Forsyth", "Franklin", "Gaston", "Gates", "Graham", "Granville", "Greene", "Guilford", "Halifax", "Harnett", "Haywood", "Henderson", "Hertford", "Hoke", "Hyde", "Iredell", "Jackson", "Johnston", "Jones", "Lee", "Lenoir", "Lincoln", "McDowell", "Macon", "Madison", "Martin", "Mecklenburg", "Mitchell", "Montgomery", "Moore", "Nash", "New Hanover", "Northampton", "Onslow", "Orange", "Pamlico", "Pasquotank", "Pender", "Perquimans", "Person", "Pitt", "Polk", "Randolph", "Richmond", "Robeson", "Rockingham", "Rowan", "Rutherford", "Sampson", "Scotland", "Stanly", "Stokes", "Surry", "Swain", "Transylvania", "Tyrrell", "Union", "Vance", "Wake", "Warren", "Washington", "Watauga", "Wayne", "Wilkes", "Wilson", "Yadkin", "Yancey"],
    "SC": ["Abbeville", "Aiken", "Allendale", "Anderson", "Bamberg", "Barnwell", "Beaufort", "Berkeley", "Calhoun", "Charleston", "Cherokee", "Chester", "Chesterfield", "Clarendon", "Colleton", "Darlington", "Dillon", "Dorchester", "Edgefield", "Fairfield", "Florence", "Georgetown", "Greenville", "Greenwood", "Hampton", "Horry", "Jasper", "Kershaw", "Lancaster", "Laurens", "Lee", "Lexington", "McCormick", "Marion", "Marlboro", "Newberry", "Oconee", "Orangeburg", "Pickens", "Richland", "Saluda", "Spartanburg", "Sumter", "Union", "Williamsburg", "York"]
}

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
    
    # Enabled multi-select logic to cover Southeast regions natively
    selected_states = st.multiselect("States Supported:*", options=["FL", "TX", "GA", "NC", "SC"], help="Select all states where your organization actively provides emergency support.")
    
    # Aggregate dynamic cascading county pool based on picked states
    dynamic_county_options = []
    if selected_states:
        for state in selected_states:
            if state in COUNTY_REGISTRY:
                # Format options cleanly with state abbreviation indicators
                dynamic_county_options.extend([f"{county} ({state})" for county in COUNTY_REGISTRY[state]])
    
    # Set default or dynamic choice pool
    if op_scope == "Local / Mutual Aid" and selected_states:
        selected_counties = st.multiselect("Counties Covered:*", options=sorted(dynamic_county_options), help="Select specific local county jurisdictions.")
    else:
        selected_counties = ["All Counties"]
        st.caption("🔒 *Counties set to 'All Counties' automatically for National/Statewide configurations.*")
    
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
    logo_url = st.text_input("Organization Logo Vector URL (Optional):", placeholder="https://example.com/logo.png")
    doc_url = st.text_input("Tax Exempt IRS Determination PDF Link (Optional):", placeholder="https://example.com/determination_doc.pdf")
    
    # SECTION 5: SIGNATURE & COMPLIANCE AGREEMENT
    st.markdown("---")
    compliance_check = st.checkbox("I certify that all information submitted is true, accurate, and represents verifiable active asset capacities ready for state or federal deployment authorization.*")
    
    # FORM INTAKE RUN BUTTON
    submit_btn = st.form_submit_button("Submit Registry Records to Compliance Queue")
    
    if submit_btn:
        if org_name and fein_num and primary_phone and resource_inventory and selected_states:
            if compliance_check:
                new_id = generate_org_id()
                
                # Transform multiselect arrays into flat comma-separated text strings for Google Sheet row cells
                flat_states = ", ".join(selected_states)
                flat_counties = ", ".join(selected_counties) if isinstance(selected_counties, list) else selected_counties
                
                # Constructing the exact 18-field operational layout matrix matching the spreadsheet
                new_row = pd.DataFrame([{
                    "Org_ID": new_id,
                    "Organization_Name": org_name,
                    "FEIN": fein_num,
                    "Operation_Scope": op_scope,
                    "State_Supported": flat_states,
                    "Counties_Covered": flat_counties,
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
            st.error("❌ Mandatory metrics missing. Please complete Name, FEIN, Phone, States, and Resource Inventory metrics.")
