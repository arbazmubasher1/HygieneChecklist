import streamlit as st
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Hygiene Checklist", layout="wide")
st.title("🧼 Daily Inspection: Crew & Rider Hygiene Readiness Checklist")

def checklist_buttons(label):
    col1, col2, col3 = st.columns([1, 1, 2])
    key_prefix = label.replace(" ", "_")

    # Initial state
    if f"{key_prefix}_value" not in st.session_state:
        st.session_state[f"{key_prefix}_value"] = None
    if f"{key_prefix}_remark" not in st.session_state:
        st.session_state[f"{key_prefix}_remark"] = ""

    # Buttons
    with col1:
        if st.button("✅", key=f"{key_prefix}_yes"):
            st.session_state[f"{key_prefix}_value"] = "✅"
            st.session_state[f"{key_prefix}_remark"] = ""
    with col2:
        if st.button("❌", key=f"{key_prefix}_no"):
            st.session_state[f"{key_prefix}_value"] = "❌"
    with col3:
        if st.button("✍️ Remark", key=f"{key_prefix}_remark_btn"):
            st.session_state[f"{key_prefix}_value"] = "✍️ Remark"

    # Display text input based on selection
    selected = st.session_state[f"{key_prefix}_value"]
    st.markdown(f"**Selected:** {selected or 'None'}")

    if selected == "❌":
        st.session_state[f"{key_prefix}_remark"] = st.text_input(f"📝 Required Remark for: {label}", key=f"{key_prefix}_text", placeholder="Enter remark...")
    elif selected == "✍️ Remark":
        st.session_state[f"{key_prefix}_remark"] = st.text_input(f"✍️ Optional Remark for: {label}", key=f"{key_prefix}_text", placeholder="Add notes...")

    return {
        "selection": selected,
        "remark": st.session_state[f"{key_prefix}_remark"]
    }

# --- Section 1: Filters ---
branch = st.selectbox("📍 Select Branch", [
    "DHA-P6", "DHA-CC", "Cloud Kitchen", "Johar Town", "Bahria", "Wehshi Lab", "Emporium"
])

employee_type = st.selectbox("👷 Select Employee Type", ["Crew", "Rider"])
shift_type = st.selectbox("🕒 Select Shift", ["Morning", "Lunch", "Dinner", "Closing"])
date = st.date_input("📅 Date", value=datetime.today())
gender = st.selectbox("🚻 Select Gender", ["Male", "Female"])

# --- Optional Role Type for Crew ---
role_type = None
if employee_type == "Crew":
    role_type = st.selectbox("🎭 Select Role Type", ["FOH", "BOH"])

# --- Section 2: Employee Info ---
st.subheader("👤 Employee Details")
emp_id = st.text_input("Employee ID")
emp_name = st.text_input("Employee Name")

# --- Camera Input for Images ---
USE_CAMERA = False  # Change to True when deploying on camera-enabled devices

if USE_CAMERA:
    rider_photo = st.camera_input("📸 Capture Employee Photo")
    bike_photo = st.camera_input("🏍️ Capture Bike Photo") if employee_type == "Rider" else None
else:
    #rider_photo = st.file_uploader("📸 Upload Employee Photo", type=["jpg", "jpeg", "png"])
    #bike_photo = st.file_uploader("🏍️ Upload Bike Photo", type=["jpg", "jpeg", "png"]) if employee_type == "Rider" else None
    print("Camera Not Found")

# --- Unified Grooming Standards ---
st.subheader("🧼 Grooming Standards")

hygiene_fields = {}
hygiene_fields["Clean Shirt"] = checklist_buttons("Clean Shirt")
hygiene_fields["Clean Black Pant"] = checklist_buttons("Clean Black Pant")
hygiene_fields["Wear Black Shoes"] = checklist_buttons("Wear Black Shoes")
hygiene_fields["Wear Black Socks"] = checklist_buttons("Wear Black Socks")
hygiene_fields["Facial Hair Grooming"] = checklist_buttons("Facial Hair Grooming")
hygiene_fields["Nail Care"] = checklist_buttons("Nail Care")
hygiene_fields["Oral Hygiene"] = checklist_buttons("Oral Hygiene")

# Conditional grooming
if employee_type == "Rider" or (employee_type == "Crew" and role_type == "FOH"):
    hygiene_fields["JJ Cap"] = checklist_buttons("JJ Cap")
    hygiene_fields["Hair Grooming"] = checklist_buttons("Hair Grooming")
    if gender == "Male":
        hygiene_fields["Beard Grooming"] = checklist_buttons("Beard Grooming")
    elif gender == "Female":
        hygiene_fields["Scarf / Cap Management"] = checklist_buttons("Scarf / Cap Management")
elif employee_type == "Crew" and role_type == "BOH" and gender == "Female":
    hygiene_fields["Scarf / Cap Management"] = checklist_buttons("Scarf / Cap Management")

# --- Section 5: Safety Checks for Riders ---
safety_checks = {}
if employee_type == "Rider":
    st.subheader("🛡️ Rider Safety Checks")
    safety_checks = {
        "Helmet": checklist_buttons("Helmet"),
        "Mobile Phone": checklist_buttons("Mobile Phone"),
        "Handfree": checklist_buttons("Handfree"),
        "Gloves": checklist_buttons("Gloves")
    }

# --- Section 6: Required Documents for Riders ---
documents_check = {}
if employee_type == "Rider":
    st.subheader("📄 Required Documents")
    documents_check = {
        "Motorcycle License": checklist_buttons("Motorcycle License"),
        "Registration Papers": checklist_buttons("Registration Papers"),
        "CNIC": checklist_buttons("CNIC")
    }
    if branch in ["DHA-P6", "Wehshi Lab"]:
        documents_check["Society Gate Pass"] = checklist_buttons("Society Gate Pass")

# --- Section 7: Bike Inspection for Riders ---
bike_inspection = {}
if employee_type == "Rider":
    st.subheader("🔧 Bike Inspection")
    bike_inspection = {
        "Fuel Level": checklist_buttons("Fuel Level"),
        "Tire Condition": checklist_buttons("Tire Condition"),
        "Brakes Working": checklist_buttons("Brakes Working"),
        "Clean Condition": checklist_buttons("Clean Condition"),
        "Chain Cover": checklist_buttons("Chain Cover"),
        "Rear-View Mirrors": checklist_buttons("Rear-View Mirrors"),
        "Seat Carrier": checklist_buttons("Seat Carrier"),
        "Leg Guard": checklist_buttons("Leg Guard")
    }

# --- Section 8: Manager Verification ---
st.subheader("🧾 Manager Verification")
manager_name = st.text_input("Manager Name")
manager_signed = st.checkbox("I verify this information is correct")

# --- Submit Button ---
if st.button("✅ Submit Checklist"):
    st.success("Checklist captured. Ready for image upload and Firebase integration.")
    st.info("📸 Rider and bike images, along with form data, will be sent in the next phase.")
