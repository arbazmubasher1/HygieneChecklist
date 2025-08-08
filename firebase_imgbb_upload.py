import os
import base64
import requests
import streamlit as st
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, firestore

# === Firebase init (robust) ===
def _init_firebase_once():
    if not firebase_admin._apps:
        sa = dict(st.secrets["firebase"])  # your TOML has [firebase]
        # If you ever paste a key with literal "\n", uncomment:
        # if "\\n" in sa.get("private_key", ""):
        #     sa["private_key"] = sa["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(sa)
        firebase_admin.initialize_app(cred)

_init_firebase_once()
db = firestore.client()

# === ImgBB API Key (robust lookup, no import-time crash) ===
def _get_imgbb_api_key():
    # Prefer Streamlit secrets, fallback to env var
    return st.secrets.get("imgbb", {}).get("api_key") or os.getenv("IMGBB_API_KEY")

# === Upload Image to ImgBB ===
def upload_to_imgbb(image_file):
    """
    Accepts a PIL Image or a file-like object (e.g., Streamlit uploader).
    Returns hosted URL string or None.
    """
    api_key = _get_imgbb_api_key()
    if not api_key:
        st.error(
            "ImgBB API key missing. Add [imgbb].api_key in secrets.toml "
            "or set IMGBB_API_KEY as an environment variable."
        )
        return None

    if image_file is None:
        st.warning("No image provided for upload.")
        return None

    # Convert to bytes (prefer PIL save -> PNG)
    try:
        buffer = BytesIO()
        # If it's a PIL Image, this will work:
        try:
            image_file.save(buffer, format="PNG")
        except AttributeError:
            # Not a PIL Image; try reading bytes (file-like object)
            buffer.write(image_file.read())
        image_bytes = buffer.getvalue()
    except Exception as e:
        st.error(f"Could not prepare image for upload: {e}")
        return None

    try:
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": encoded},
            timeout=20,
        )
        if resp.ok:
            j = resp.json()
            url = j.get("data", {}).get("url")
            if url:
                return url
            st.error("ImgBB response missing URL.")
            return None
        else:
            # Show a trimmed error to the user, keep full text in logs
            st.error(f"ImgBB upload failed (HTTP {resp.status_code}).")
            print("ImgBB error:", resp.text[:2000])
            return None
    except requests.Timeout:
        st.error("ImgBB upload timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"Unexpected error during ImgBB upload: {e}")
        return None

# === Submit Final Payload to Firestore ===
def submit_to_firebase(data, employee_url=None, bike_url=None, signature_img=None):
    """
    Adds a document to the 'hygiene_checklist' collection.
    Optionally uploads signature to ImgBB and stores the URL too.
    """
    payload = dict(data) if isinstance(data, dict) else {}
    image_links = {}

    if employee_url:
        image_links["employee_photo_url"] = employee_url
    if bike_url:
        image_links["bike_photo_url"] = bike_url

    if signature_img is not None:
        sig_url = upload_to_imgbb(signature_img)
        if sig_url:
            image_links["manager_signature_url"] = sig_url

    payload.update(image_links)

    try:
        db.collection("hygiene_checklist").add(payload)
        print("✅ Data pushed to Firebase")
    except Exception as e:
        st.error("❌ Failed to upload to Firebase")
        print("Firebase error:", e)
