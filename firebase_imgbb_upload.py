import firebase_admin
from firebase_admin import credentials, firestore, storage
import requests
from PIL import Image
import io
import base64
import uuid
import os

# Initialize Firebase app
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # Or use st.secrets["firebase"]
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'zeeshan-s-hygiene-checklist.appspot.com'
    })

db = firestore.client()
bucket = storage.bucket()

IMGUR_API_KEY = "08b53a28b8374832a8ea6c5f20048423"  # You can also load this via st.secrets

def upload_to_imgbb(image_bytes, name):
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGUR_API_KEY,
        "image": base64.b64encode(image_bytes).decode("utf-8"),
        "name": name
    }
    response = requests.post(url, data=payload)
    if response.ok:
        return response.json()["data"]["url"]
    else:
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
