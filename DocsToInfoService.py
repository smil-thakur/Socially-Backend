from agno.agent import Agent
from agno.models.google import Gemini 
from typing import List
from agno.utils.pprint import pprint_run_response
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from agno.document.reader import pdf_reader
import os
import warnings
from pydantic.json_schema import PydanticJsonSchemaWarning

warnings.filterwarnings("ignore", category=PydanticJsonSchemaWarning)

load_dotenv()

APIKEY = os.getenv("APIKEY")

class Education(BaseModel):
    degree: str = Field(...,description="degree user is having or persuing"),
    institution: str = Field(...,description="insitution user has studied from or is persuing degree from")
    year: str = Field(...,description="year of qualification or year user will qualify")

class Experience(BaseModel):
    role: str = Field(...,description="role of the user in the current job or job user worked"),
    company: str = Field(...,description="name of the company user is or was associated with"),
    years: str = Field(...,description="years of experience")
    
class Project(BaseModel):
    name: str = Field(...,description="name of the project user created or worked upon"),
    techstack: List[str] = Field(...,description="tech stack used in the project"),
    year: str = Field(...,description="year the project was completed or started"),
    summary: str = Field(...,description="summary of the project")

class BasicUserData(BaseModel):
    fullName: str = Field(...,description="Full name of the user"),
    title: str = Field(..., description="A title for your user, a catchy oneliner"),
    summary: str = Field(..., description="summary of the user life jouney till now, short and crisp yet explaining important characteristics"),
    skills: List[str] = Field(...,description="skills that the user has"),
    educations: List[Education]
    experinces: List[Experience]
    projects: List[Project]
    



class PDFtoInfo:
    def __init__(self):
        self.agent = Agent(
            model= Gemini(
                api_key=APIKEY,
                id="gemini-2.0-flash"
            ),
            response_model=BasicUserData,
            use_json_mode=True
        )
    async def analysePDF(self,file:str):
        reader = pdf_reader.PDFReader()
        res = reader.read(file)
        response = await self.agent.arun(f"analyze user data and provide pure json format with ```json f{res}")
        return response.content
        
         
        
        
        
