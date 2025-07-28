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

    # If image_file has getvalue(), use it. Otherwise, assume it's already bytes.
    try:
        image_bytes = image_file.getvalue()
    except AttributeError:
        image_bytes = image_file

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


import uuid

def submit_to_firebase(data, rider_photo, bike_photo, manager_signature):
    image_links = {}

    # Upload Employee Photo
    if rider_photo:
        image_links["employee_photo_url"] = upload_to_imgbb(rider_photo)

    # Upload Bike Photo
    if bike_photo:
        image_links["bike_photo_url"] = upload_to_imgbb(bike_photo)

    # Upload Manager Signature (from BytesIO canvas object)
    if manager_signature:
        image_links["signature_url"] = upload_to_imgbb(manager_signature)

    # Append image links to data
    data.update(image_links)

    # Store in Firestore under date/branch/employee_id
    doc_path = f"{data['date']}/{data['branch']}/{data['employee_id']}_{str(uuid.uuid4())[:8]}"
    db.document(f"checklists/{doc_path}").set(data)

    print("✅ Data successfully submitted to Firebase.")
