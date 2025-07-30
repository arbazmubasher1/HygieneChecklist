import streamlit as st
from datetime import datetime
from firebase_imgbb_upload import submit_to_firebase  # Ensure this exists
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# --- Config ---
st.set_page_config(page_title="Hygiene Checklist", layout="wide")
st.title("🧼 Daily Inspection: Crew & Rider Hygiene Readiness Checklist")

# --- CSS ---
st.markdown("""
    <style>
        img {
            max-height: 400px;
            height: auto;
            width: auto;
            display: block;
            margin-left: auto;
            margin-right: auto;
            object-fit: contain;
        }
    </style>
""", unsafe_allow_html=True)

# --- Filters ---
branch = st.selectbox("📍 Select Branch", [
    "DHA-P6", "DHA-CC", "Cloud Kitchen", "Johar Town", "Bahria", "Wehshi Lab", "Emporium"
])

employee_type = st.selectbox("👷 Select Employee Type", ["Crew", "Rider"])
shift_type = st.selectbox("🕒 Select Shift", ["Morning", "Lunch", "Dinner", "Closing"])
date = st.date_input("📅 Date", value=datetime.today())
gender = st.selectbox("🛋 Select Gender", ["Male", "Female"])
role_type = st.selectbox("🎭 Select Role Type", ["FOH", "BOH"], key="role_type") if employee_type == "Crew" else ""

# --- Employee Info ---
st.subheader("👤 Employee Details")
emp_id = st.number_input("Employee ID", step=1, format="%d", key="emp_id")
emp_name = st.text_input("Employee Name", key="emp_name")

# --- Photo Capture ---
st.subheader("📸 Capture Photos")
employee_photo = st.camera_input("📸 Capture Employee Photo", key="employee_photo")
if employee_photo:
    image = Image.open(employee_photo).resize((600, 600))
    st.image(image, caption="Upscaled Employee Photo", use_container_width=True)
else:
    image = None

bike_upscaled = None
if employee_type == "Rider":
    bike_photo = st.camera_input("🏍️ Capture Bike Photo", key="bike_photo")
    if bike_photo:
        bike_upscaled = Image.open(bike_photo).resize((600, 600))

# --- Reference Image ---
reference_image = None
caption = ""
if employee_type == "Crew" and gender == "Male":
    reference_image = Image.open("Crew_male.PNG")
    caption = "Crew Male Appearance"
elif employee_type == "Crew" and gender == "Female":
    reference_image = Image.open("Crew_female.PNG")
    caption = "Crew Female Appearance"
elif employee_type == "Rider":
    reference_image = Image.open("Rider_male.PNG")
    caption = "Rider Appearance"
if reference_image:
    st.image(reference_image, caption=caption, use_container_width=True)

# --- Checklist Helper ---
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

# --- Rider Specific ---
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

# --- Signature ---
st.subheader("🧾 Manager Verification")
manager_name = st.text_input("Manager Name (optional)", key="manager_name")

st.markdown("✍️ **Please sign below:**")
signature_canvas = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#ffffff",
    height=150,
    drawing_mode="freedraw",
    key="signature"
)

manager_signature = None
if signature_canvas.image_data is not None:
    sig_image = Image.fromarray(signature_canvas.image_data.astype('uint8'), 'RGBA')
    if sig_image.getbbox():
        manager_signature = sig_image
        st.image(manager_signature, caption="Manager Signature", use_container_width=True)

# --- Submit ---
if st.button("✅ Submit Checklist"):
    checklist_groups = [grooming_fields, safety_checks, documents_check, bike_inspection]
    incomplete_items = []
    total_checked = 0
    correct_checked = 0

    for group in checklist_groups:
        for item, response in group.items():
            selected_value = response["selection"]
            remark_value = response["remark"]

            if selected_value not in ["✅", "❌"]:
                incomplete_items.append(item)
            elif selected_value == "❌" and not remark_value.strip():
                st.error(f"❗ Remarks are required for ❌ selection: {item}")
                st.stop()
            else:
                total_checked += 1
                if selected_value == "✅":
                    correct_checked += 1

    if incomplete_items:
        st.error(f"❗ Please complete all items before submitting. Missing: {', '.join(incomplete_items)}")
        st.stop()

    if not manager_signature:
        st.error("❗ Please sign in the Manager Verification section.")
        st.stop()

    score_percentage = round((correct_checked / total_checked) * 100, 2)
    st.success("✅ Checklist submitted successfully!")
    st.info(f"🧮 Final Hygiene Score: **{correct_checked} / {total_checked}** ({score_percentage}%)")

    remarks_dict = {
        item: response["remark"]
        for group in checklist_groups
        for item, response in group.items()
        if isinstance(response, dict) and response.get("selection") == "❌"
    }

    data = {
        "branch": branch,
        "employee_type": employee_type,
        "shift": shift_type,
        "date": str(date),
        "gender": gender,
        "role_type": role_type,
        "employee_id": emp_id,
        "employee_name": emp_name,
        "manager_name": manager_name,
        "grooming": grooming_fields,
        "remarks": remarks_dict,
        "safety_checks": safety_checks,
        "documents": documents_check,
        "bike_inspection": bike_inspection,
        "score": {
            "correct": correct_checked,
            "total": total_checked,
            "percentage": score_percentage
        }
    }

    submit_to_firebase(data, image, bike_upscaled, manager_signature)

    # Reset state
    keys_to_clear = list(st.session_state.keys())
    for key in keys_to_clear:
        del st.session_state[key]

    st.rerun()
