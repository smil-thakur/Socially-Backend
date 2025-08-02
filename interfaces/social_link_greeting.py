from pydantic import BaseModel

class SocialLinkGreeting(BaseModel):
    title: str
    body: str