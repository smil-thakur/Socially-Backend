from fastapi import FastAPI, HTTPException, UploadFile, File, Depends 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
from services.DocsToInfoService import PDFtoInfo
from tempfile import gettempdir
import uuid
from methods.firebaseMethods import get_current_user_uid, get_current_user_email ,addSocialGreeting, addSocialLinkForUser, uploadIcon, addProfileForUser, getProfileOfUser, saveTexFile, getSavedTexContent, mapIdToEmail, getIdFromEmail, deleteSocialLink, getPdfFromEmail
from interfaces.social_link_greeting import SocialLinkGreeting
from interfaces.social_link import SocialLink
from interfaces.resumeData import ResumeData
from datetime import datetime, timezone
from services.LatexToPDF import TexToPdfConverter
from services.ResumeDataToLatex import ResumeDataToLatex
from pathlib import Path


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
    
@app.post("/saveResume")
async def saveResumeTex(uid: str = Depends(get_current_user_uid),file:UploadFile = File(...)):
    try:
        file_ext = file.filename.split(".")[-1]
        if(file_ext != "tex"):
            raise HTTPException(status_code=500,detail="wrong file extension, file should be tex")
        file_data = await file.read()
        file_content_type = file.content_type
        url = await saveTexFile(uid,file_data,file_content_type)
        return url
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@app.get("/getTexContent")
async def getTexContent(uid: str = Depends(get_current_user_uid)):
    try:
        content = await getSavedTexContent(uid)
        return {"latex":content}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    
@app.post("/scanpdf")
async def scanPDF(uid: str = Depends(get_current_user_uid),file:UploadFile = File(...)):
    try:
        pDFtoInfo = PDFtoInfo()
        data =  await pDFtoInfo.analysePDF(file.file)
        return data
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@app.post("/updateProfile")
async def updateProfile(resumeData:ResumeData,uid: str = Depends(get_current_user_uid)):
    try:
        await addProfileForUser(uid,resumeData)
        return {"message" : "user data updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
        

@app.get("/userProfile")
async def getUserProfile(uid: str= Depends(get_current_user_uid)):
    try:
        res = await getProfileOfUser(uid)
        return res
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

        
@app.post("/convert-tex")
async def convert_tex(file: UploadFile = File(...)):
    try:
        converter = TexToPdfConverter()   
        pdf_bytes = await converter.tex_to_pdf_bytes(file)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/getTexFromProfile")
async def getTextFromProfile(file:ResumeData,uid: str = Depends(get_current_user_uid)):
    converter = ResumeDataToLatex()
    try:
        return {"latex": await converter.get_latex(file)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getPdfFromEmail")
async def getPdfFromEmailEndpoint(email: str):
    try:
        pdf_bytes = await getPdfFromEmail(email)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=resume_{email}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/mapEmailToId")
async def mapEmailToId(uid: str= Depends(get_current_user_uid),email: str = Depends(get_current_user_email)):
    try:
        await mapIdToEmail(uid,email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/getIdFromEmail")
async def getIdFromMail(email: str):
    try:
        return {"id":await getIdFromEmail(email)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/deleteSocialLink")
async def deleteSocialLinkAPI(sid:str,uid: str=Depends(get_current_user_uid)):
    try:
        await deleteSocialLink(uid,sid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))