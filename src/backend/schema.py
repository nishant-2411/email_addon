from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EmailRecord(BaseModel):
    raw_text: str = Field(..., description="Raw email text (full message)")
    cleaned_text: str = Field(..., description="Cleaned and normalized text")
    sender: Optional[str] = Field(None, description="Email address of sender")
    sender_role: Optional[str] = Field(None, description="Role of sender (customer/vendor/internal)")
    timestamp: Optional[datetime] = Field(None, description="Original message timestamp")
    thread_id: Optional[str] = Field(None, description="Conversation/thread identifier")
    subject: Optional[str] = Field(None, description="Original subject line")
    message_id: Optional[str] = Field(None, description="Email message ID (if available)")
    language: Optional[str] = Field(None, description="Detected language (e.g., 'en')")
    entities: Optional[List[dict]] = Field(None, description="Extracted named entities")
