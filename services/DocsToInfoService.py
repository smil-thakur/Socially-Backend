from agno.agent import Agent
from agno.models.google import Gemini 
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from agno.knowledge.reader.pdf_reader import PDFReader
import os
import warnings
from pydantic.json_schema import PydanticJsonSchemaWarning
from decouple import Config, RepositoryEnv

warnings.filterwarnings("ignore", category=PydanticJsonSchemaWarning)

if os.getenv("RAILWAY_ENVIRONMENT_NAME"):
    print("loading railway config")
    config = Config(RepositoryEnv(".env.railway"))
    APIKEY = config("APIKEY")

else:
    print("loading local env")
    load_dotenv()
    APIKEY = os.getenv("APIKEY")

class Education(BaseModel):
    degree: Optional[str] = Field(None, description="degree user is having or pursuing")
    institution: Optional[str] = Field(None, description="institution user has studied from or is pursuing degree from")
    year: Optional[str] = Field(None, description="year of qualification or year user will qualify in string format")

class Experience(BaseModel):
    role: Optional[str] = Field(None, description="role of the user in the current job or job user worked")
    company: Optional[str] = Field(None, description="name of the company user is or was associated with")
    years: Optional[str] = Field(None, description="years of experience in string format")
    summary: Optional[str] = Field(None, description="summary of the experience what you did, reponsibility and tasks")

    
class Project(BaseModel):
    name: Optional[str] = Field(None, description="name of the project user created or worked upon")
    techstack: Optional[List[str]] = Field(None, description="tech stack used in the project")
    year: Optional[str] = Field(None, description="year the project was completed or started in string format")
    summary: Optional[str] = Field(None, description="summary of the project")

class BasicUserData(BaseModel):
    fullName: Optional[str] = Field(None, description="Full name of the user")
    title: Optional[str] = Field(None, description="A title for your user, a catchy oneliner")
    summary: Optional[str] = Field(None, description="summary of the user life journey till now, short and crisp yet explaining important characteristics")
    skills: Optional[List[str]] = Field(None, description="skills that the user has")
    educations: Optional[List[Education]] = Field(None, description="education history")
    experiences: Optional[List[Experience]] = Field(None, description="work experience history")  # Note: keeping your original spelling
    projects: Optional[List[Project]] = Field(None, description="projects worked on")


class PDFtoInfo:
    def __init__(self):
        self.agent = Agent(
            model= Gemini(
                api_key=APIKEY,
                id="gemini-2.0-flash"
            ),
            output_schema=BasicUserData,
        )
    async def analysePDF(self,file:any)->dict[str,Any]:
        reader = PDFReader()
        res = reader.read(file)
        response = await self.agent.arun(f"analyze user data {res}")
        data = response.content.model_dump(mode="json")
        return data
        

        
        
