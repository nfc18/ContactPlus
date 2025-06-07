"""
Pydantic models for ContactPlus API
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class SourceInfo(BaseModel):
    """Source information for a contact"""
    database_name: str
    source_file: str
    original_index: int
    import_timestamp: str
    import_session_id: str


class ContactBase(BaseModel):
    """Base contact model"""
    formatted_name: str = Field(..., alias="fn")
    emails: List[EmailStr] = []
    phones: List[str] = []
    organization: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    """Model for creating a new contact"""
    vcard_data: Optional[str] = None


class ContactUpdate(ContactBase):
    """Model for updating a contact"""
    formatted_name: Optional[str] = Field(None, alias="fn")


class Contact(ContactBase):
    """Complete contact model with metadata"""
    contact_id: str
    source_info: SourceInfo
    created_at: datetime
    updated_at: datetime
    version: int
    is_active: bool
    
    class Config:
        populate_by_name = True


class ContactList(BaseModel):
    """Paginated contact list response"""
    contacts: List[Contact]
    total: int
    page: int
    page_size: int
    total_pages: int


class ImportRequest(BaseModel):
    """Import request model"""
    database_name: str
    source_file: str


class ImportResponse(BaseModel):
    """Import operation response"""
    database_name: str
    source_file: str
    import_session_id: str
    total_contacts: int
    imported_contacts: int
    compliance_fixes: int
    errors: List[str]
    contact_ids: List[str]


class DatabaseStats(BaseModel):
    """Database statistics"""
    total_contacts: int
    active_contacts: int
    contacts_by_source: Dict[str, int]
    total_operations: int
    database_file: str
    last_operation: Optional[str]


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    database_connected: bool
    contacts_count: int
    version: str = "1.0.0"


class ExportRequest(BaseModel):
    """Export request options"""
    format: str = "vcf"
    active_only: bool = True


class SearchRequest(BaseModel):
    """Search request parameters"""
    query: str
    search_fields: List[str] = ["fn", "email", "phone", "organization"]
    page: int = 1
    page_size: int = 50


class OperationResponse(BaseModel):
    """Generic operation response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    status_code: int