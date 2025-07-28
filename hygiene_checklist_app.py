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
bike_photo = st.camera_input("🏍️ Capture Bike Photo") if employee_type == "Rider" else None

def checklist_buttons(label):
    st.markdown(f"### 🧾 {label}")  # Show label prominently

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

    # with col3:
    #     if st.button("✍️ Remark", key=f"{key_prefix}_rem"):
    #         st.session_state[f"{key_prefix}_value"] = "✍️"

    selected = st.session_state[f"{key_prefix}_value"]
    st.markdown(f"<span style='font-size:14px;'>**Selected:** {selected or 'None'}</span>", unsafe_allow_html=True)

    if selected == "❌":
        st.session_state[f"{key_prefix}_remark"] = st.text_input(
            f"❗ Remark required for: {label}", key=f"{key_prefix}_text", placeholder="Enter reason..."
        )
    # elif selected == "✍️":
    #     st.session_state[f"{key_prefix}_remark"] = st.text_input(
    #         f"✍️ Optional Remark for: {label}", key=f"{key_prefix}_text", placeholder="Enter note..."
    #     )

    return {
        "selection": selected,
        "remark": st.session_state[f"{key_prefix}_remark"]
    }


# --- Section 3: Grooming Standards ---
st.subheader("🧼 Grooming Standards")

hygiene_fields = {}
for field in [
    "Clean Shirt", "Clean Black Pant", "Wear Black Shoes", "Wear Black Socks",
    "Nail Care", "Oral Hygiene"
]:
    hygiene_fields[field] = checklist_buttons(field)

# Conditional grooming fields
if employee_type == "Rider":
    hygiene_fields["JJ Cap"] = checklist_buttons("JJ Cap")
    hygiene_fields["Hair Grooming"] = checklist_buttons("Hair Grooming")
    if gender == "Male":
        hygiene_fields["Beard Grooming"] = checklist_buttons("Beard Grooming")
    if gender == "Female":
        hygiene_fields["Scarf / Cap Management"] = checklist_buttons("Scarf / Cap Management")

elif employee_type == "Crew":
    if role_type == "FOH":
        hygiene_fields["JJ Cap"] = checklist_buttons("JJ Cap")
        hygiene_fields["Hair Grooming"] = checklist_buttons("Hair Grooming")
        if gender == "Male":
            hygiene_fields["Beard Grooming"] = checklist_buttons("Beard Grooming")
        elif gender == "Female":
            hygiene_fields["Scarf / Cap Management"] = checklist_buttons("Scarf / Cap Management")
    elif role_type == "BOH" and gender == "Female":
        hygiene_fields["Scarf / Cap Management"] = checklist_buttons("Scarf / Cap Management")

# --- Section 5: Safety Checks for Riders ---
safety_checks = {}
if employee_type == "Rider":
    st.subheader("🛡️ Rider Safety Checks")
    for field in ["Helmet", "Mobile Phone", "Handfree", "Gloves"]:
        safety_checks[field] = checklist_buttons(field)

# --- Section 6: Required Documents for Riders ---
documents_check = {}
if employee_type == "Rider":
    st.subheader("📄 Required Documents")
    for field in ["Motorcycle License", "Registration Papers", "CNIC"]:
        documents_check[field] = checklist_buttons(field)
    if branch in ["DHA-P6", "Wehshi Lab"]:
        documents_check["Society Gate Pass"] = checklist_buttons("Society Gate Pass")

# --- Section 7: Bike Inspection for Riders ---
bike_inspection = {}
if employee_type == "Rider":
    st.subheader("🔧 Bike Inspection")
    for field in [
        "Fuel Level", "Tire Condition", "Brakes Working", "Clean Condition",
        "Chain Cover", "Rear-View Mirrors", "Seat Carrier", "Leg Guard"
    ]:
        bike_inspection[field] = checklist_buttons(field)


# --- Calculate Progress ---
all_fields = [*hygiene_fields.items(), *safety_checks.items(), *documents_check.items(), *bike_inspection.items()]
total_items = len(all_fields)
filled_items = sum(1 for _, v in all_fields if v["selection"] in ["✅", "❌", "✍️"])

progress = filled_items / total_items if total_items else 0

st.markdown("### 📊 Checklist Completion Progress")
st.progress(progress)
st.write(f"**{filled_items} of {total_items} items completed ({int(progress * 100)}%)**")


# --- Section 8: Manager Verification ---
st.subheader("🧾 Manager Verification")
manager_name = st.text_input("Manager Name")
manager_signed = st.checkbox("I verify this information is correct")

# --- Submit Button ---
if st.button("✅ Submit Checklist"):
    # 🔍 Validate all ❌ have remarks
    for field_group in [hygiene_fields, safety_checks, documents_check, bike_inspection]:
        for label, result in field_group.items():
            if result["selection"] == "❌" and not result["remark"]:
                st.error(f"❗ Remark is required for ❌ in: {label}")
                st.stop()

    st.success("✅ Checklist captured successfully.")
    st.info("📸 Images and data ready for next phase: Firebase + Imgbb.")
