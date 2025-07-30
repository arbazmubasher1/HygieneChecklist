import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from firebase_imgbb_upload import upload_to_imgbb, submit_to_firebase

# === CONFIG ===
st.set_page_config(page_title="Hygiene Checklist", layout="wide")
st.title("🧼 Daily Inspection: Crew & Rider Hygiene Readiness Checklist")

# === STYLES ===
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

# === SECTION 1: FILTERS ===
branch = st.selectbox("📍 Select Branch", [
    "DHA-P6", "DHA-CC", "Cloud Kitchen", "Johar Town", "Bahria", "Wehshi Lab", "Emporium"
])
employee_type = st.selectbox("👷 Select Employee Type", ["Crew", "Rider"])
shift_type = st.selectbox("🕒 Select Shift", ["Morning", "Lunch", "Dinner", "Closing"])
date = st.date_input("📅 Date", value=datetime.today())
gender = st.selectbox("🛋 Select Gender", ["Male", "Female"])
role_type = st.selectbox("🎭 Select Role Type", ["FOH", "BOH"], key="role_type") if employee_type == "Crew" else ""

# === SECTION 2: EMPLOYEE INFO ===
st.subheader("👤 Employee Details")
emp_id = st.number_input("Employee ID", step=1, format="%d", key="emp_id")
emp_name = st.text_input("Employee Name", key="emp_name")

# === SECTION 3: PHOTO CAPTURE WITH IMMEDIATE UPLOAD ===
st.subheader("📸 Capture Photos")

def photo_capture_section(label, session_key):
    placeholder = st.empty()

    if st.session_state.get(f"{session_key}_url"):
        st.success(f"{label} photo uploaded ✅")
        return

    if placeholder.button(f"📸 Take {label} Photo", key=f"{session_key}_btn"):
        cam = placeholder.camera_input(f"Capture {label} Photo", key=f"{session_key}_cam")
        if cam:
            img = Image.open(cam).resize((600, 600))
            st.info(f"Uploading {label.lower()} photo...")
            url = upload_to_imgbb(img)
            if url:
                st.session_state[f"{session_key}_url"] = url
                st.success(f"{label} photo uploaded ✅")
            else:
                st.error(f"Failed to upload {label.lower()} photo.")
            placeholder.empty()

photo_capture_section("Employee", "employee_photo")
if employee_type == "Rider":
    photo_capture_section("Bike", "bike_photo")

# === SECTION 4: REFERENCE IMAGE ===
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

# === SECTION 5: CHECKLIST BUTTONS ===
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

# === SECTION 6: CHECKLIST FIELDS ===
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

safety_checks, documents_check, bike_inspection = {}, {}, {}
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

# === SECTION 7: PROGRESS BAR ===
all_fields = [*grooming_fields.items(), *safety_checks.items(), *documents_check.items(), *bike_inspection.items()]
total = len(all_fields)
filled = sum(1 for _, v in all_fields if v['selection'] in ["✅", "❌"])
progress = int((filled / total) * 100) if total else 0
st.markdown("### 📊 Checklist Completion Progress")
st.progress(progress / 100, text=f"{filled} / {total} items completed")

# === SECTION 8: MANAGER SIGNATURE ===
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
    sig_img = Image.fromarray(signature_canvas.image_data.astype('uint8'), 'RGBA')
    if sig_img.getbbox():
        manager_signature = sig_img

# === SECTION 9: SUBMIT ===
if st.button("✅ Submit Checklist"):
    checklist_groups = [grooming_fields, safety_checks, documents_check, bike_inspection]
    incomplete_items, total_checked, correct_checked = [], 0, 0

    for group in checklist_groups:
        for item, response in group.items():
            val, remark = response["selection"], response["remark"]
            if val not in ["✅", "❌"]:
                incomplete_items.append(item)
            elif val == "❌" and not remark.strip():
                st.error(f"❗ Remarks required for ❌: {item}")
                st.stop()
            else:
                total_checked += 1
                if val == "✅":
                    correct_checked += 1

    if incomplete_items:
        st.error(f"❗ Please complete all items: {', '.join(incomplete_items)}")
        st.stop()

    if not manager_signature:
        st.error("❗ Please sign in the Manager Verification section.")
        st.stop()

    # Get uploaded image URLs from session_state
    employee_url = st.session_state.get("employee_photo_url")
    bike_url = st.session_state.get("bike_photo_url")

    score_percentage = round((correct_checked / total_checked) * 100, 2)
    remarks_dict = {
        item: response["remark"]
        for group in checklist_groups
        for item, response in group.items()
        if response.get("selection") == "❌"
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

    submit_to_firebase(data, employee_url, bike_url, manager_signature)

    st.success("✅ Checklist submitted successfully!")
    st.info(f"🧮 Final Hygiene Score: **{correct_checked} / {total_checked}** ({score_percentage}%)")

    # Force full refresh
    st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)
