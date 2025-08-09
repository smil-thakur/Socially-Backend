from pydantic import BaseModel
from typing import List

class Education(BaseModel):
    degree: str
    institution: str
    year: str

class Project(BaseModel):
    name: str
    techstack: List[str]
    year: str
    summary: str

class Experience(BaseModel):
    role: str
    company: str
    years: str
    summary:str

class ResumeData(BaseModel):
    fullName: str
    title: str
    summary: str
    skills: List[str]
    educations: List[Education]
    projects: List[Project]
    experiences: List[Experience]
        

    