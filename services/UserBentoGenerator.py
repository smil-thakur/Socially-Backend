from agno.agent import Agent
from agno.models.google import Gemini 
from dotenv import load_dotenv
from typing import List, Optional, Literal, Dict
import instructor
from pydantic import BaseModel, Field
from Prompts.dataToBentoPrompt import DataToBentoPrompt
from methods.firebaseMethods import getProfileOfUser
from interfaces.resumeData import ResumeData
import os
import openai
from atomic_agents import BaseIOSchema, AtomicAgent, AgentConfig, BasicChatInputSchema
from decouple import Config, RepositoryEnv


if os.getenv("RAILWAY_ENVIRONMENT_NAME"):
    print("loading railway config")
    config = Config(RepositoryEnv(".env"))
    APIKEY = config("APIKEY")
else:
    print("loading local env")
    load_dotenv()
    APIKEY = os.getenv("APIKEY")

class InnerBento(BaseIOSchema):
    """Inner bento card with optional enhancements"""
    heading: str = Field(..., description="Heading of the inner bento card")
    content: Optional[str] = Field(None, description="Optional content for the inner bento card")
    icon: Optional[str] = Field(None, description="Icon name or emoji")
    badge: Optional[str] = Field(None, description="Small text badge")
    link: Optional[str] = Field(None, description="Optional link")


class Stat(BaseIOSchema):
    """Represents a stat item for stat layout"""
    label: str = Field(..., description="Label of the stat")
    value: str = Field(..., description="Value of the stat")


class Bento(BaseIOSchema):
    """This is a bento element"""
    heading: str = Field(..., description="Heading of the bento card")
    content: str = Field(..., description="The text content of the bento card")
    innerBentos: Optional[List[InnerBento]] = Field(None, description="List of inner bentos like mini cards")
    bigBento: Optional[bool] = Field(None, description="Should bento card take flex:1 (usually for larger content)")

    layout: Optional[Literal['default', 'featured', 'stats', 'timeline', 'gallery', 'contact']] = Field(
        None, description="Layout type of the bento card"
    )
    size: Optional[Literal['small', 'medium', 'large', 'xl']] = Field(
        None, description="Size of the bento card"
    )
    accent: Optional[Literal['primary', 'secondary', 'success', 'warning', 'info']] = Field(
        None, description="Accent color of the bento card"
    )
    icon: Optional[str] = Field(None, description="Optional icon for the bento card")
    image: Optional[str] = Field(None, description="Optional image URL for the bento card")
    tags: Optional[List[str]] = Field(None, description="Tags associated with the bento card")
    stats: Optional[List[Stat]] = Field(None, description="Stats used in 'stats' layout")


class Website(BaseIOSchema):
    """This is website consisting of bentos"""
    elements: List[Bento] = Field(..., description="Bentos required to build the portfolio")


class UserBentoGenerator:
    def __init__(self):
        client = instructor.from_openai(
            openai.AsyncOpenAI(
                api_key=APIKEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            ),
            mode=instructor.Mode.JSON
        )
        model = "gemini-2.0-flash"
        self.agent = AtomicAgent[BasicChatInputSchema, Website](
        config=AgentConfig(
            client=client,
            model=model,
        )
    )
        
    async def get_bento(self , id: str):
        data: ResumeData = await getProfileOfUser(id)
        prompt = BasicChatInputSchema(chat_message=DataToBentoPrompt(data).prompt)
        
        try:
            response = await self.agent.run_async(prompt)
            print(response)
            
            with open("output.json", "w", encoding="utf-8") as file:
                file.write(str(response))
                
            return response.model_dump(mode="json")
            
        except Exception as e:
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Error details: {repr(e)}")
            raise  # Re-raise to see full traceback
    



