from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from DocsToInfoService import PDFtoInfo
from tempfile import gettempdir
import uuid
import os
import json
from firebaseMethods import get_current_user_uid, addSocialGreeting, addSocialLinkForUser, uploadIcon
from interfaces.social_link_greeting import SocialLinkGreeting
from interfaces.social_link import SocialLink
from datetime import datetime, timezone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
async def read_root():
    return {"message":"hello world"}


@app.post("/scanpdf")
async def scanPDF(file:UploadFile = File(...)):
    temp_dir = gettempdir()
    filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(temp_dir, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    pdfInfo = PDFtoInfo()
    response = await pdfInfo.analysePDF(file_path)  
    
    try: 
        json.dump(response)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid response: not JSON serializable")
    return response


@app.post("/addSocialGreeting")
async def getUserId(greeting:SocialLinkGreeting,uid: str =  Depends(get_current_user_uid)):
    try:
        await addSocialGreeting(uid,greeting)
        return {"message":"greeting added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@app.post("/addSocialLink")
async def addSocialLink(socialLink:SocialLink, uid: str = Depends(get_current_user_uid)):
    try:
        await addSocialLinkForUser(uid,socialLink)
        return {"message" : "Social Link for the user was successfully added"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/uploadIconAndGetURL")
async def uploadIconAndGetURL(uid: str = Depends(get_current_user_uid), file:UploadFile = File(...)):
    try:
        file_ext = file.filename.split('.')[-1]
        unique_name = f"user-icons/{uid}/{datetime.now(timezone.utc).timestamp()}_{uuid.uuid4()}.{file_ext}"
        file_data = await file.read()
        file_content_type = file.content_type
        url = await uploadIcon(file_data,file_content_type,unique_name)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
        