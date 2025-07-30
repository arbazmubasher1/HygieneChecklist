import firebase_admin
from firebase_admin import credentials, firestore
import requests
import base64
import streamlit as st
from io import BytesIO

# === Initialize Firebase ===
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# === ImgBB API Key ===
IMGBB_API = st.secrets["imgbb"]["api_key"]

# === Upload Image to ImgBB ===
def upload_to_imgbb(image_file):
    if image_file is None:
        print("⚠️ No image provided for upload.")
        return None

    try:
        buffer = BytesIO()
        image_file.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        print("✅ Image converted to bytes. Size:", len(image_bytes))
    except Exception as e:
        print("❌ Failed to convert PIL image:", e)
        try:
            image_bytes = image_file.read()
            print("✅ Used fallback .read() method for file-like object.")
        except Exception as e2:
            print("❌ Could not read image file at all:", e2)
            st.error("Could not prepare image for upload.")
            return None

    try:
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": IMGBB_API,
                "image": encoded
            }
        )
        if response.status_code == 200:
            image_url = response.json()["data"]["url"]
            print("✅ Uploaded to ImgBB:", image_url)
            return image_url
        else:
            print("❌ ImgBB upload failed:", response.text)
            st.error("Failed to upload image to ImgBB.")
            return None
    except Exception as e:
        print("❌ Unexpected error during ImgBB upload:", e)
        return None

# === Submit Final Payload to Firestore ===
def submit_to_firebase(data, image, bike_image=None, manager_signature=None):
    print("📦 Preparing to submit to Firebase...")

    image_links = {}

    if image:
        print("🖼️ Uploading employee photo...")
        image_links["employee_photo_url"] = upload_to_imgbb(image)

    if bike_image:
        print("🏍️ Uploading bike photo...")
        image_links["bike_photo_url"] = upload_to_imgbb(bike_image)

    if manager_signature:
        print("✍️ Uploading manager signature...")
        image_links["manager_signature_url"] = upload_to_imgbb(manager_signature)

    # Merge into main payload
    data.update(image_links)

    # Log final data for inspection
    print("📤 Final Firebase payload:")
    for k, v in data.items():
        print(f" - {k}: {v if isinstance(v, (str, int, float)) else '[object]'}")

    # Push to Firestore
    try:
        db.collection("hygiene_checklist").add(data)
        print("✅ Successfully submitted to Firestore.")
    except Exception as e:
        print("❌ Error pushing to Firestore:", e)
        st.error("Failed to submit data to Firebase.")
