from fastapi import Request, HTTPException, Depends
from firebase_admin import auth, credentials, initialize_app, firestore
from interfaces.social_link_greeting import SocialLinkGreeting

cred = credentials.Certificate("firebase-secret.json")
initialize_app(cred)
firestore_client = firestore.client()

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
    
async def addSocialGreeting(id:str, body:SocialLinkGreeting):
    print("setting greeting of id",id)
    print(body)
    firestore_client.collection("User").document(id).collection("SocialLinkGreeting").document("greeting").set(body.model_dump())
