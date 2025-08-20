from fastapi import Request, HTTPException, File
from firebase_admin import auth, credentials, initialize_app, firestore, storage, get_app
from interfaces.social_link_greeting import SocialLinkGreeting
from interfaces.social_link import SocialLink
from interfaces.resumeData import ResumeData
import aiohttp

cred = credentials.Certificate("firebase_secret.json")

initialize_app(cred,{
    "storageBucket": "socially-91ef8.firebasestorage.app"
})
firestore_client = firestore.client()


async def get_current_user_uid(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    app=get_app()
    print(app.project_id)
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
    
async def addSocialGreeting(id:str, body:SocialLinkGreeting):
    firestore_client.collection("User").document(id).collection("SocialLinkGreeting").document("greeting").set(body.model_dump())
    

async def addSocialLinkForUser(id:str, body:SocialLink):
    firestore_client.collection("User").document(id).collection("SocialLinks").add(body.model_dump())
    
async def addProfileForUser(id: str, body:ResumeData):
    firestore_client.collection("User").document(id).collection("Profile").document(id).set(body.model_dump())
    
async def getProfileOfUser(id: str) -> ResumeData:
    doc_ref = firestore_client.collection("User").document(id).collection("Profile").document(id)
    doc_snapshot = doc_ref.get()

    if doc_snapshot.exists:
        data = doc_snapshot.to_dict()
        return ResumeData(**data)
    return None
    
async def uploadIcon(filedata:bytes, fileContentType:str,unique_name:str)->str:
    bucket = storage.bucket()
    blob = bucket.blob(unique_name)
    blob.upload_from_string(filedata, content_type=fileContentType)
    blob.make_public()
    return blob.public_url
    
    
async def saveTexFile(id: str, filedata: bytes, fileContentType: str) -> str:
    bucket = storage.bucket()

    filename = f"user-texs/{id}/resume.tex"

    blob = bucket.blob(filename)
    try:
        blob.delete()  
    except Exception as e:
        pass
    blob.upload_from_string(filedata, content_type=fileContentType)
    blob.make_public()

    firestore_client.collection("User").document(id).collection("Texs").document("resume").set({
        "url": blob.public_url,
        "filename": filename
    })

    return blob.public_url

async def getTexURL(id:str)->str:
    doc_ref = firestore_client.collection("User").document(id).collection("Texs").document("resume")
    doc_snapshot = doc_ref.get()
    if doc_snapshot.exists:
        data = doc_snapshot.to_dict()
        return data['url']
    return None


async def getSavedTexContent(id: str) -> str:
    texURL = await getTexURL(id)  
    
    async with aiohttp.ClientSession() as session:
        async with session.get(texURL) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch file: {response.status}")
            return await response.text()