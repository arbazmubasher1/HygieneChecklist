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

def submit_to_firebase(data, rider_image_file=None, bike_image_file=None):
    rider_img_url = upload_to_imgbb(rider_image_file)
    bike_img_url = upload_to_imgbb(bike_image_file) if data["employee_type"] == "Rider" else None

    data["timestamp"] = firestore.SERVER_TIMESTAMP
    data["rider_image_url"] = rider_img_url
    data["bike_image_url"] = bike_img_url

    doc_ref = db.collection("hygiene_checklist").document()
    doc_ref.set(data)
    st.success("✅ Data and images successfully submitted to Firebase.")
