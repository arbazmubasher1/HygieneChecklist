import firebase_admin
from firebase_admin import credentials, firestore
import requests
import base64
import streamlit as st

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ImgBB API Key from secrets
IMGBB_API = st.secrets["imgbb"]["api_key"]

def upload_to_imgbb(image_file):
    if image_file is None:
        return None
    image_bytes = image_file.getvalue()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": IMGBB_API,
            "image": encoded
        }
    )
    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        st.error("Failed to upload image to ImgBB.")
        return None

def submit_to_firebase(data, rider_photo, bike_photo, manager_signature):
    image_links = {}

    # Upload Employee Photo
    if rider_photo:
        emp_bytes = rider_photo.getvalue()
        image_links["employee_photo_url"] = upload_to_imgbb(emp_bytes, f"emp_{uuid.uuid4()}")
    
    # Upload Bike Photo
    if bike_photo:
        bike_bytes = bike_photo.getvalue()
        image_links["bike_photo_url"] = upload_to_imgbb(bike_bytes, f"bike_{uuid.uuid4()}")

    # Upload Manager Signature (as base64 PNG from canvas)
    if manager_signature:
        signature_bytes = manager_signature.getvalue()
        image_links["signature_url"] = upload_to_imgbb(signature_bytes, f"sign_{uuid.uuid4()}")

    # Append image links to data
    data.update(image_links)

    # Store in Firestore under date/branch/employee_id
    doc_path = f"{data['date']}/{data['branch']}/{data['employee_id']}_{str(uuid.uuid4())[:8]}"
    db.document(f"checklists/{doc_path}").set(data)

    print("✅ Data successfully submitted to Firebase.")