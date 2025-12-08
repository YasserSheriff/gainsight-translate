from pydantic import BaseModel
from typing import Dict

class langcheckResponse(BaseModel):
    response: Dict