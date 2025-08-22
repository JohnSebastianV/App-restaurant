from supabase import create_client
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

def upload_image_to_supabase(file, folder="restaurants"):
    try:
        # generar nombre único
        unique_name = f"{folder}/{uuid.uuid4().hex}_{file.filename}"
        
        # leer en bytes
        file_content = file.read()
        
        # subir al bucket (debes tener un bucket llamado restaurant-images en Supabase)
        supabase.storage.from_("images").upload(unique_name, file_content)
        
        # generar URL pública
        public_url = f"{supabase.storage.from_('images').get_public_url(unique_name)}"
        return public_url
    except Exception as e:
        print("Error subiendo imagen:", e)
        return None
