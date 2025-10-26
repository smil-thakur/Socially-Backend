from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import os
from Prompts.ProfileToLatexPrompt import profile_to_latex_prompt
from fastapi import UploadFile
from decouple import Config, RepositoryEnv

if os.getenv("RAILWAY_ENVIRONMENT_NAME"):
    print("loading railway config")
    config = Config(RepositoryEnv(".env"))
    APIKEY = config("APIKEY")
else:
    print("loading local env")
    load_dotenv()
    APIKEY = os.getenv("APIKEY")

class ResumeDataToLatex:
    def __init__(self):
        self.agent = Agent(model=Gemini( api_key=APIKEY,
                id="gemini-2.0-flash"),instructions=profile_to_latex_prompt, markdown=False)
    
    async def get_latex(self,data:UploadFile)-> str:
        response = await self.agent.arun(data)
        return response.content.replace("```latex", "").replace("```", "").strip()