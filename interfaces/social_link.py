from pydantic import BaseModel
from typing import Optional

class SocialLink(BaseModel):
    id: str
    url: str
    platform: str
    platformName: str
    icon: str
    color: str
    customIcon: str
    desc: str
    followers: Optional[int] = None
    following: Optional[int] = None
    username: str
    handle: Optional[str] = None