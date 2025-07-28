import streamlit as st
from datetime import datetime
from firebase_imgbb_upload import submit_to_firebase  # Make sure this file exists
import base64

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
role_type = st.selectbox("🎭 Select Role Type", ["FOH", "BOH"]) if employee_type == "Crew" else None

# --- Section 2: Employee Info ---
st.subheader("👤 Employee Details")
emp_id = st.text_input("Employee ID")
emp_name = st.text_input("Employee Name")

rider_photo = st.camera_input("📸 Capture Employee Photo")
bike_photo = st.camera_input("🏍️ Capture Bike Photo") if employee_type == "Rider" else None

# --- Display Reference Image ---
if employee_type == "Rider" and gender == "Male":
    st.image("Crew_male.PNG", caption="Reference", use_container_width=True)
elif employee_type == "Crew" and gender == "Female":
    st.image("Crew_female.PNG", caption="Reference", use_container_width=True)

# --- Grooming Standards ---
st.markdown("<h2 style='text-align: center;'>🧼 Grooming Standards</h2>", unsafe_allow_html=True)

grooming_items = [
    "Clean Shirt", "Clean Black Pant", "Wear Black Shoes", "Wear Black Socks",
    "Nail Care", "Oral Hygiene"
]

# Add based on role/gender
if employee_type == "Rider" or (employee_type == "Crew" and role_type == "FOH"):
    grooming_items += ["JJ Cap", "Hair Grooming"]
if gender == "Male":
    grooming_items += ["Beard Grooming"]
if gender == "Female":
    grooming_items += ["Scarf / Cap Management"]

# --- Checklist with progress and remarks ---
filled = 0
remarks_dict = {}
selections = {}

for item in grooming_items:
    st.markdown(f"**{item}**")
    col1, col2, col3 = st.columns([1, 1, 2])
    key_prefix = item.replace(" ", "_")

    if f"{key_prefix}_value" not in st.session_state:
        st.session_state[f"{key_prefix}_value"] = None
    if f"{key_prefix}_remark" not in st.session_state:
        st.session_state[f"{key_prefix}_remark"] = ""

    with col1:
        if st.button("✅", key=f"{key_prefix}_yes"):
            st.session_state[f"{key_prefix}_value"] = "✅"
            st.session_state[f"{key_prefix}_remark"] = ""

    with col2:
        if st.button("❌", key=f"{key_prefix}_no"):
            st.session_state[f"{key_prefix}_value"] = "❌"

    with col3:
        if st.session_state[f"{key_prefix}_value"] == "❌":
            st.session_state[f"{key_prefix}_remark"] = st.text_input(
                f"❗ Remarks for {item}", key=f"{key_prefix}_remark_input"
            )

    value = st.session_state[f"{key_prefix}_value"]
    selections[item] = value
    if value == "✅":
        filled += 1
    if value == "❌":
        remarks_dict[item] = st.session_state[f"{key_prefix}_remark"]

# --- Progress Bar ---
total_fields = len(grooming_items)
progress = int((filled / total_fields) * 100) if total_fields > 0 else 0
st.progress(progress, text=f"{filled} / {total_fields} grooming items completed")

# --- Section 5: Safety Checks for Riders ---
safety_checks = {}
if employee_type == "Rider":
    st.subheader("🛡️ Rider Safety Checks")
    for item in ["Helmet", "Mobile Phone", "Handfree", "Gloves"]:
        safety_checks[item] = st.radio(item, ["✅", "❌"], horizontal=True)

# --- Section 6: Documents ---
documents_check = {}
if employee_type == "Rider":
    st.subheader("📄 Required Documents")
    doc_items = ["Motorcycle License", "Registration Papers", "CNIC"]
    if branch in ["DHA-P6", "Wehshi Lab"]:
        doc_items.append("Society Gate Pass")
    for item in doc_items:
        documents_check[item] = st.radio(item, ["✅", "❌"], horizontal=True)

# --- Section 7: Bike Inspection ---
bike_inspection = {}
if employee_type == "Rider":
    st.subheader("🔧 Bike Inspection")
    for item in [
        "Fuel Level", "Tire Condition", "Brakes Working", "Clean Condition",
        "Chain Cover", "Rear-View Mirrors", "Seat Carrier", "Leg Guard"
    ]:
        bike_inspection[item] = st.radio(item, ["✅", "❌"], horizontal=True)

# --- Manager Verification ---
st.subheader("🧾 Manager Verification")
manager_name = st.text_input("Manager Name")
manager_signed = st.checkbox("I verify this information is correct")

# --- Submit Checklist ---
if st.button("✅ Submit Checklist"):
    if not manager_signed:
        st.error("Please verify the checklist before submitting.")
    else:
        data = {
            "branch": branch,
            "employee_type": employee_type,
            "shift": shift_type,
            "date": str(date),
            "gender": gender,
            "role_type": role_type if role_type else "",
            "employee_id": emp_id,
            "employee_name": emp_name,
            "manager_name": manager_name,
            "grooming": selections,
            "remarks": remarks_dict,
            "safety_checks": safety_checks,
            "documents": documents_check,
            "bike_inspection": bike_inspection
        }
        submit_to_firebase(data, rider_photo, bike_photo)
