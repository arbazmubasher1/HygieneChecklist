import streamlit as st
from datetime import datetime
from firebase_imgbb_upload import submit_to_firebase  # Make sure this file exists
from PIL import Image

st.set_page_config(page_title="Hygiene Checklist", layout="wide")
st.title("🧼 Daily Inspection: Crew & Rider Hygiene Readiness Checklist")


# --- Optional CSS to resize all images ---
st.markdown("""
    <style>
        img {
            max-height: 500px;
            width: 200;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
""", unsafe_allow_html=True)


# --- Section 1: Filters ---
branch = st.selectbox("📍 Select Branch", [
    "DHA-P6", "DHA-CC", "Cloud Kitchen", "Johar Town", "Bahria", "Wehshi Lab", "Emporium"
])

employee_type = st.selectbox("👷 Select Employee Type", ["Crew", "Rider"])
shift_type = st.selectbox("🕒 Select Shift", ["Morning", "Lunch", "Dinner", "Closing"])
date = st.date_input("📅 Date", value=datetime.today())
gender = st.selectbox("🛋 Select Gender", ["Male", "Female"])
role_type = st.selectbox("🎭 Select Role Type", ["FOH", "BOH"]) if employee_type == "Crew" else None

# --- Section 2: Employee Info ---
st.subheader("👤 Employee Details")
emp_id = st.text_input("Employee ID")
emp_name = st.text_input("Employee Name")

rider_photo = st.camera_input("📸 Capture Employee Photo")
bike_photo = st.camera_input("🏍️ Capture Bike Photo") if employee_type == "Rider" else None

# --- Display Reference Image ---
image = None
caption = ""
if employee_type == "Crew" and gender == "Male":
    image = Image.open("Crew_male.PNG")
    caption = "Crew Male Appearance"
elif employee_type == "Crew" and gender == "Female":
    image = Image.open("Crew_female.PNG")
    caption = "Crew Female Appearance"
elif employee_type == "Rider":
    image = Image.open("Rider_male.PNG")
    caption = "Rider Appearance"
if image:
    st.image(image, caption=caption, use_container_width=True)

# --- Helper: Button Input + Remarks ---
def checklist_buttons(label):
    st.markdown(f"**{label}**")
    col1, col2, col3 = st.columns([1, 1, 2])
    key_prefix = label.replace(" ", "_")

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
                f"❗ Remarks for {label}", key=f"{key_prefix}_remark_input"
            )

    return {
        "selection": st.session_state[f"{key_prefix}_value"],
        "remark": st.session_state[f"{key_prefix}_remark"]
    }

# --- Grooming Standards ---
st.markdown("<h2 style='text-align: center;'>🧼 Grooming Standards</h2>", unsafe_allow_html=True)
grooming_fields = {}
base_grooming = [
    "Clean Shirt", "Clean Black Pant", "Wear Black Belt", "Wear Black Shoes", "Wear Black Socks",
    "Nail Care", "Oral Hygiene"
]
if employee_type == "Rider" or (employee_type == "Crew" and role_type == "FOH"):
    base_grooming += ["JJ Cap", "Hair Grooming"]
if gender == "Male":
    base_grooming += ["Beard Grooming"]
if gender == "Female":
    base_grooming += ["Scarf / Cap Management"]
for field in base_grooming:
    grooming_fields[field] = checklist_buttons(field)

# --- Rider Specific Sections ---
safety_checks = {}
documents_check = {}
bike_inspection = {}
if employee_type == "Rider":
    st.subheader("🛡️ Rider Safety Checks")
    for field in ["Helmet", "Mobile Phone", "Handfree", "Gloves"]:
        safety_checks[field] = checklist_buttons(field)

    st.subheader("📄 Required Documents")
    docs = ["Motorcycle License", "Registration Papers", "CNIC"]
    if branch in ["DHA-P6", "Wehshi Lab"]:
        docs.append("Society Gate Pass")
    for field in docs:
        documents_check[field] = checklist_buttons(field)

    st.subheader("🔧 Bike Inspection")
    for field in [
        "Fuel Level", "Tire Condition", "Brakes Working", "Clean Condition",
        "Chain Cover", "Rear-View Mirrors", "Seat Carrier", "Leg Guard"]:
        bike_inspection[field] = checklist_buttons(field)

# --- Progress Bar ---
all_fields = [*grooming_fields.items(), *safety_checks.items(), *documents_check.items(), *bike_inspection.items()]
total = len(all_fields)
filled = sum(1 for _, v in all_fields if v['selection'] in ["✅", "❌"])
progress = int((filled / total) * 100) if total else 0
st.markdown("### 📊 Checklist Completion Progress")
st.progress(progress / 100, text=f"{filled} / {total} items completed")

# --- Manager Verification ---
st.subheader("🗾️ Manager Verification")
manager_name = st.text_input("Manager Name")
manager_signed = st.checkbox("I verify this information is correct")

# --- Submit Checklist ---
if st.button("✅ Submit Checklist"):
    if not manager_signed:
        st.error("Please verify the checklist before submitting.")
    else:
        for group in [grooming_fields, safety_checks, documents_check, bike_inspection]:
            for label, result in group.items():
                if result["selection"] == "❌" and not result["remark"]:
                    st.error(f"❗ Remark is required for ❌ in: {label}")
                    st.stop()

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
            "grooming": {k: v["selection"] for k, v in grooming_fields.items()},
            "remarks": {k: v["remark"] for k, v in grooming_fields.items() if v["selection"] == "❌"},
            "safety_checks": {k: v["selection"] for k, v in safety_checks.items()},
            "documents": {k: v["selection"] for k, v in documents_check.items()},
            "bike_inspection": {k: v["selection"] for k, v in bike_inspection.items()}
        }
        submit_to_firebase(data, rider_photo, bike_photo)
        st.success("✅ Checklist submitted successfully!")
