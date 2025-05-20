import base64
import uuid
import os

UPLOAD_DIR = "uploads"

def save_base64_image(base64_str: str) -> str:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    img_data = base64.b64decode(base64_str)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(img_data)
    return filepath