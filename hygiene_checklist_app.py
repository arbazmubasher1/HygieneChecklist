import streamlit as st
from datetime import datetime
from firebase_imgbb_upload import submit_to_firebase  # Make sure this file exists
from PIL import Image

st.set_page_config(page_title="Hygiene Checklist", layout="wide")
st.title("🧼 Daily Inspection: Crew & Rider Hygiene Readiness Checklist")


# --- Optional CSS to resize all images ---
# Limit image height
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
emp_id = st.number_input("Employee ID")
emp_name = st.text_input("Employee Name")

from PIL import Image
import io

st.subheader("📸 Capture Photos")

# Employee Photo
rider_photo = st.camera_input("📸 Capture Employee Photo")
if rider_photo:
    image = Image.open(rider_photo)
    upscaled = image.resize((600, 600))  # Resize to 600x600 pixels
    st.image(upscaled, caption="Upscaled Employee Photo", use_container_width=True)
else:
    upscaled = None  # In case you want to pass it forward later

# Bike Photo (Only if Rider)
bike_photo = None
bike_upscaled = None
if employee_type == "Rider":
    bike_photo = st.camera_input("🏍️ Capture Bike Photo")
    if bike_photo:
        bike_image = Image.open(bike_photo)
        bike_upscaled = bike_image.resize((600, 600))
        #st.image(bike_upscaled, caption="Upscaled Bike Photo", use_container_width=True)


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
from streamlit_drawable_canvas import st_canvas

st.subheader("🧾 Manager Verification")

manager_name = st.text_input("Manager Name (optional)")

st.markdown("✍️ **Please sign below:**")
signature_canvas = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",  # Transparent background
    stroke_width=2,
    stroke_color="#000000",
    background_color="#ffffff",
    height=150,
    drawing_mode="freedraw",
    key="signature"
)

# Save the signature image if drawn
manager_signature = None
if signature_canvas.image_data is not None:
    signature_image = Image.fromarray(signature_canvas.image_data.astype('uint8'), 'RGBA')
    if signature_image.getbbox():  # Check if something is drawn
        manager_signature = signature_image
        st.image(manager_signature, caption="Manager Signature", use_container_width=True)


if st.button("✅ Submit Checklist"):
    # Collect all checklist dictionaries
    checklist_groups = [grooming_fields, safety_checks, documents_check, bike_inspection]
    incomplete_items = []
    total_checked = 0
    correct_checked = 0

    for group in checklist_groups:
        for item, response in group.items():
            selected_value = response["selection"] if isinstance(response, dict) else response
            if selected_value not in ["✅", "❌"]:
                incomplete_items.append(item)
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

    # Score Calculation
    score_percentage = round((correct_checked / total_checked) * 100, 2)
    st.success("✅ Checklist submitted successfully!")
    st.info(f"🧮 Final Hygiene Score: **{correct_checked} / {total_checked}** ({score_percentage}%)")

    # Build remarks from ❌ selections
    remarks_dict = {
        item: response["remark"]
        for group in checklist_groups
        for item, response in group.items()
        if isinstance(response, dict) and response.get("selection") == "❌"
    }

    # Prepare payload
    data = {
        "branch": branch,
        "employee_type": employee_type,
        "shift": shift_type,
        "date": str(date),
        "gender": gender,
        "role_type": role_type or "",
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

    if bike_image:
        submit_to_firebase(data, image, bike_image, manager_signature)
    else:
        submit_to_firebase(data, image, None, manager_signature)
