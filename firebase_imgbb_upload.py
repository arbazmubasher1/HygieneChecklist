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

from io import BytesIO

def upload_to_imgbb(image_file):
    if image_file is None:
        return None

    # Handle either uploaded image (bytes) or PIL image
    if hasattr(image_file, "read"):  # Camera or file uploader
        image_bytes = image_file.read()
    else:
        # Assume it's a PIL image, convert to bytes
        buffer = BytesIO()
        image_file.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

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

def submit_to_firebase(data, image, bike_image=None, manager_signature=None):
    image_links = {}

    if image:
        image_links["employee_photo_url"] = upload_to_imgbb(image)

    if bike_image:  # This will skip upload if it's None
        image_links["bike_photo_url"] = upload_to_imgbb(bike_image)

    if manager_signature:
        image_links["manager_signature_url"] = upload_to_imgbb(manager_signature)

    # Merge image links into the main data payload
    data.update(image_links)

    # Push to Firestore
    db = firestore.client()
    db.collection("hygiene_checklist").add(data)