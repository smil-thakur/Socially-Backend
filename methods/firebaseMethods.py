from fastapi import Request, HTTPException
from firebase_admin import auth, credentials, initialize_app
from google.cloud import firestore as google_firestore
from google.cloud import storage as google_storage
from interfaces.social_link_greeting import SocialLinkGreeting
from interfaces.social_link import SocialLink
from interfaces.resumeData import ResumeData
import aiohttp
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
import sys




required_keys = [
    "type", "project_id", "private_key_id", "private_key", "client_email",
    "client_id", "auth_uri", "token_uri",
    "auth_provider_x509_cert_url", "client_x509_cert_url", "universe_domain"
]

env_values = {}

if os.getenv("RAILWAY_ENVIRONMENT_NAME"):
    print("loading railway config")
    env_values = {key:os.environ.get(key) for key in required_keys}  
else:
    print("loading local env")
    load_dotenv()
    env_values = {key: os.getenv(key) for key in required_keys}


print("\n🔍 [Firebase ENV Check]")
missing_keys = []
for key, value in env_values.items():
    if value is None or value.strip() == "":
        print(f"❌ Missing: {key}")
        missing_keys.append(key)
    else:
        value = os.getenv(key)
        print(f"✅ Found: {key} -> {value}")

if missing_keys:
    print("\n🚨 ERROR: Missing required Firebase environment variables:")
    print(", ".join(missing_keys))
    sys.exit(1)

firebase_secret = {
    "type": env_values["type"],
    "project_id": env_values["project_id"],
    "private_key_id": env_values["private_key_id"],
    "private_key": env_values["private_key"],
    "client_email": env_values["client_email"],
    "client_id": env_values["client_id"],
    "auth_uri": env_values["auth_uri"],
    "token_uri": env_values["token_uri"],
    "auth_provider_x509_cert_url": env_values["auth_provider_x509_cert_url"],
    "client_x509_cert_url": env_values["client_x509_cert_url"],
    "universe_domain": env_values["universe_domain"]
}

print("\n✅ Firebase secret object successfully built.\n")

creds = service_account.Credentials.from_service_account_info(firebase_secret)
import uuid


cred = credentials.Certificate(firebase_secret)

initialize_app(cred,{
    "projectId": cred.project_id,
    "storageBucket": "socially-91ef8.firebasestorage.app"
})


firestore_client = google_firestore.AsyncClient(credentials=creds,project=creds.project_id)
storage_client = google_storage.Client(credentials=creds,project=creds.project_id)
bucket = storage_client.bucket("socially-91ef8.firebasestorage.app")


async def get_current_user_uid(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    id_token = auth_header
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        return uid
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
async def get_current_user_email(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    id_token = auth_header
    try:
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token["email"]
        return email
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
async def addSocialGreeting(id:str, body:SocialLinkGreeting):
    doc_ref = firestore_client.collection("User").document(id).collection("SocialLinkGreeting").document("greeting")
    await doc_ref.set(body.model_dump())
    

async def addSocialLinkForUser(id:str, body:SocialLink):
    doc_ref = firestore_client.collection("User").document(id).collection("SocialLinks").document(body.id)
    await doc_ref.set(body.model_dump())
    
async def addProfileForUser(id: str, body:ResumeData):
    doc_ref = firestore_client.collection("User").document(id).collection("Profile").document(id)
    await doc_ref.set(body.model_dump())
    
async def getProfileOfUser(id: str) -> ResumeData:
    doc_ref = firestore_client.collection("User").document(id).collection("Profile").document(id)
    doc_snapshot = await doc_ref.get()

    if doc_snapshot.exists:
        data = doc_snapshot.to_dict()
        return ResumeData(**data)
    return None
    
async def uploadIcon(filedata:bytes, fileContentType:str,unique_name:str)->str:
    blob = bucket.blob(unique_name)
    blob.upload_from_string(filedata, content_type=fileContentType)
    blob.make_public()
    return blob.public_url
    
    
async def saveTexFile(id: str, filedata: bytes, fileContentType: str) -> str:
    filename = f"user-texs/{id}/{uuid.uuid4()}_resume.tex"
    folder_prefix = f"user-texs/{id}/"
    blobs = bucket.list_blobs(prefix=folder_prefix)

    for b in blobs:
        if b.name.endswith(".tex"):
            b.delete()

    blob = bucket.blob(filename)

    blob.upload_from_string(filedata, content_type=fileContentType)
    blob.make_public()

    doc_ref = firestore_client.collection("User").document(id).collection("Texs").document("resume")
    await doc_ref.set({
        "url": blob.public_url,
        "filename": filename
    })

    return blob.public_url

async def getTexURL(id:str)->str:
    doc_ref = firestore_client.collection("User").document(id).collection("Texs").document("resume")
    doc_snapshot = await doc_ref.get()
    if doc_snapshot.exists:
        data = doc_snapshot.to_dict()
        return data['url']
    return None


async def getSavedTexContent(id: str) -> str:
    texURL = await getTexURL(id)  
    
    if texURL == None:
        raise Exception("No tex file found for this user")  
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(texURL) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch file: {response.status}")
                return await response.text()
        
async def mapIdToEmail(id: str, email:str)-> str:
    doc_ref = firestore_client.collection("Maps").document("userIdAndEmail")
    await doc_ref.set({
        email:id
    },merge=True)
    
async def getIdFromEmail(email:str)->str:
    doc_ref = firestore_client.collection("Maps").document("userIdAndEmail")
    doc_snapshot = await doc_ref.get()
    if doc_snapshot.exists:
        data = doc_snapshot.to_dict()
        return data.get(email)
    return None


async def deleteSocialLink(uid:str,sid:str):
    doc_ref = firestore_client.collection("User").document(uid).collection("SocialLinks").document(sid)
    doc = await doc_ref.get()
    if doc.exists:
        await doc_ref.delete()
        return {"status": "deleted"}
    else:
        raise HTTPException(status_code=404, detail="SocialLink not found")

async def saveBentoForUser(uid: str, website_data: dict):
    """Save website data for a user"""
    doc_ref = firestore_client.collection("User").document(uid).collection("Bento").document("bento")
    await doc_ref.set(website_data)

async def getBentoWebsite(uid: str) -> dict:
    """Get saved website data for a user"""
    print("getting bento for",uid)
    doc_ref = firestore_client.collection("User").document(uid).collection("Bento").document("bento")
    doc_snapshot = await doc_ref.get()
    
    if doc_snapshot.exists:
        return doc_snapshot.to_dict()
    return None

async def getPdfFromEmail(email: str) -> bytes:

    
    uid = await getIdFromEmail(email)
    if not uid:
        raise HTTPException(status_code=404, detail="User not found for this email")
    
    
    tex_content = await getSavedTexContent(uid)
    if not tex_content:
        raise HTTPException(status_code=404, detail="No tex file found for this user")
    
    
    from services.LatexToPDF import TexToPdfConverter
    converter = TexToPdfConverter()
    
    
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as temp_file:
        temp_file.write(tex_content)
        temp_file_path = temp_file.name
    
    try:
        
        pdf_bytes = await converter.tex_to_pdf_bytes(temp_file_path)
        return pdf_bytes
    finally:
        
        os.unlink(temp_file_path)