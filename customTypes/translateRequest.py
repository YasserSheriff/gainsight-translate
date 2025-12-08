from pydantic import BaseModel, Field
from typing import Optional, List


class translateRequest(BaseModel):
    text: str = Field(title="Enter the text to translate", description="Translates the text to English")