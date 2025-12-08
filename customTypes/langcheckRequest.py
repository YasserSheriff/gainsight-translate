from pydantic import BaseModel, Field
from typing import Optional, List


class langcheckRequest(BaseModel):
    text: str = Field(title="Enter the text to verify", description="Verifies if the text needs to be translated")