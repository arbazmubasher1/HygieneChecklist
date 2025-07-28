import streamlit as st
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Hygiene Checklist", layout="wide")
st.title("🧼 Daily Inspection: Crew & Rider Hygiene Readiness Checklist")

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
rider_photo = st.camera_input("📸 Capture Employee Photo")
bike_photo = None
if employee_type == "Rider":
    bike_photo = st.camera_input("🏍️ Capture Bike Photo")

# --- Unified Hygiene & Grooming Standards ---
st.subheader("🧼 Grooming Standards")

def checklist_field(label):
    return st.radio(label, ["✅", "❌", "✍️ Remark"], horizontal=True, key=label)

# Always-shown hygiene fields
hygiene_fields = {
    "Clean Shirt": checklist_field("Clean Shirt"),
    "Clean Black Pant": checklist_field("Clean Black Pant"),
    "Wear Black Shoes": checklist_field("Wear Black Shoes"),
    "Wear Black Socks": checklist_field("Wear Black Socks"),
    "Facial Hair Grooming": checklist_field("Facial Hair Grooming"),
    "Nail Care": checklist_field("Nail Care"),
    "Oral Hygiene": checklist_field("Oral Hygiene")
}

# Conditional grooming fields
if employee_type == "Rider":
    hygiene_fields.update({
        "JJ Cap": checklist_field("JJ Cap"),
        "Hair Grooming": checklist_field("Hair Grooming")
    })
    if gender == "Male":
        hygiene_fields["Beard Grooming"] = checklist_field("Beard Grooming")
    if gender == "Female":
        hygiene_fields["Scarf / Cap Management"] = checklist_field("Scarf / Cap Management")

elif employee_type == "Crew":
    if role_type == "FOH":
        hygiene_fields["JJ Cap"] = checklist_field("JJ Cap")
        hygiene_fields["Hair Grooming"] = checklist_field("Hair Grooming")
        if gender == "Male":
            hygiene_fields["Beard Grooming"] = checklist_field("Beard Grooming")
        elif gender == "Female":
            hygiene_fields["Scarf / Cap Management"] = checklist_field("Scarf / Cap Management")
    elif role_type == "BOH":
        if gender == "Female":
            hygiene_fields["Scarf / Cap Management"] = checklist_field("Scarf / Cap Management")


# --- Section 5: Safety Checks for Riders ---
safety_checks = {}
if employee_type == "Rider":
    st.subheader("🛡️ Rider Safety Checks")
    safety_checks = {
        "Helmet": checklist_field("Helmet"),
        "Mobile Phone": checklist_field("Mobile Phone"),
        "Handfree": checklist_field("Handfree"),
        "Gloves": checklist_field("Gloves")
    }

# --- Section 6: Required Documents for Riders ---
documents_check = {}
if employee_type == "Rider":
    st.subheader("📄 Required Documents")
    documents_check = {
        "Motorcycle License": checklist_field("Motorcycle License"),
        "Registration Papers": checklist_field("Registration Papers"),
        "CNIC": checklist_field("CNIC")
    }
    if branch in ["DHA-P6", "Wehshi Lab"]:
        documents_check["Society Gate Pass"] = checklist_field("Society Gate Pass")

# --- Section 7: Bike Inspection for Riders ---
bike_inspection = {}
if employee_type == "Rider":
    st.subheader("🔧 Bike Inspection")
    bike_inspection = {
        "Fuel Level": checklist_field("Fuel Level"),
        "Tire Condition": checklist_field("Tire Condition"),
        "Brakes Working": checklist_field("Brakes Working"),
        "Clean Condition": checklist_field("Clean Condition"),
        "Chain Cover": checklist_field("Chain Cover"),
        "Rear-View Mirrors": checklist_field("Rear-View Mirrors"),
        "Seat Carrier": checklist_field("Seat Carrier"),
        "Leg Guard": checklist_field("Leg Guard")
    }

# --- Section 8: Manager Verification ---
st.subheader("🧾 Manager Verification")
manager_name = st.text_input("Manager Name")
manager_signed = st.checkbox("I verify this information is correct")

# --- Submit Button ---
if st.button("✅ Submit Checklist"):
    st.success("Checklist captured. Ready for image upload and Firebase integration.")
    st.info("📸 Rider and bike images, along with form data, will be sent in the next phase.")
