"""
ContactPlus Core API - FastAPI Application
"""
import os
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import time
import uuid

from logging_config import setup_logging, log_api_call, LoggerMixin
from database.connector import APIConnector
from models.schemas import (
    Contact, ContactList, ContactCreate, ContactUpdate,
    ImportRequest, ImportResponse, DatabaseStats,
    HealthCheck, SearchRequest, OperationResponse,
    ErrorResponse
)

# Setup logging
logger = setup_logging()
app_logger = logging.getLogger("contactplus.app")

# Initialize FastAPI app
app = FastAPI(
    title="ContactPlus Core API",
    description="Professional vCard Contact Management System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    app_logger.info(f"[{request_id}] {request.method} {request.url.path} - Request started")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        app_logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code}, Duration: {duration:.3f}s"
        )
        return response
    except Exception as e:
        duration = time.time() - start_time
        app_logger.error(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"ERROR: {str(e)}, Duration: {duration:.3f}s"
        )
        raise

# Initialize database connector
db = APIConnector()
app_logger.info("ContactPlus Core API starting up...")


@app.get("/", response_model=dict)
@log_api_call
async def root():
    """Root endpoint"""
    app_logger.info("Root endpoint accessed")
    return {
        "name": "ContactPlus Core API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/v1/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        stats = db.get_database_stats()
        return HealthCheck(
            status="healthy",
            timestamp=datetime.now(),
            database_connected=True,
            contacts_count=stats["active_contacts"]
        )
    except Exception as e:
        return HealthCheck(
            status="unhealthy",
            timestamp=datetime.now(),
            database_connected=False,
            contacts_count=0
        )


# Contact Operations

@app.get("/api/v1/contacts", response_model=ContactList)
async def list_contacts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    active_only: bool = Query(True, description="Show only active contacts")
):
    """List all contacts with pagination"""
    try:
        result = db.get_all_contacts(page=page, page_size=page_size, active_only=active_only)
        return ContactList(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/contacts/search", response_model=ContactList)
async def search_contacts(
    query: str = Query(..., description="Search query"),
    fields: List[str] = Query(["fn", "email", "phone", "organization"], description="Fields to search"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)
):
    """Search contacts"""
    try:
        result = db.search_contacts(
            query=query,
            search_fields=fields,
            page=page,
            page_size=page_size
        )
        return ContactList(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/contacts/{contact_id}", response_model=Contact)
async def get_contact(contact_id: str):
    """Get a single contact by ID"""
    contact = db.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.put("/api/v1/contacts/{contact_id}", response_model=OperationResponse)
async def update_contact(contact_id: str, contact_update: ContactUpdate):
    """Update a contact"""
    try:
        # Convert update model to dict, excluding None values
        update_data = contact_update.model_dump(exclude_none=True, by_alias=True)
        
        success = db.update_contact(contact_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return OperationResponse(
            success=True,
            message=f"Contact {contact_id} updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/contacts/{contact_id}", response_model=OperationResponse)
async def delete_contact(contact_id: str):
    """Delete a contact (soft delete)"""
    success = db.delete_contact(contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return OperationResponse(
        success=True,
        message=f"Contact {contact_id} deleted successfully"
    )


# Import/Export Operations

@app.post("/api/v1/import/initial", response_model=ImportResponse)
async def import_initial_databases():
    """One-time import of the 3 source databases"""
    import_results = {
        "database_name": "initial_import",
        "source_file": "multiple",
        "import_session_id": f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "total_contacts": 0,
        "imported_contacts": 0,
        "compliance_fixes": 0,
        "errors": [],
        "contact_ids": []
    }
    
    # Define source databases
    source_databases = [
        ("sara_export", "/app/imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf"),
        ("iphone_contacts", "/app/imports/iPhone_Contacts_Contacts.vcf"),
        ("iphone_suggested", "/app/imports/iPhone_Suggested_Suggested Contacts.vcf")
    ]
    
    for db_name, db_file in source_databases:
        if os.path.exists(db_file):
            try:
                result = db.import_database(db_file, db_name)
                import_results["total_contacts"] += result["total_contacts"]
                import_results["imported_contacts"] += result["imported_contacts"]
                import_results["compliance_fixes"] += result["compliance_fixes"]
                import_results["contact_ids"].extend(result["contact_ids"])
                
                if result["errors"]:
                    import_results["errors"].extend([
                        f"{db_name}: {error}" for error in result["errors"]
                    ])
                    
            except Exception as e:
                import_results["errors"].append(f"Failed to import {db_name}: {str(e)}")
        else:
            import_results["errors"].append(f"Source file not found: {db_file}")
    
    return ImportResponse(**import_results)


@app.get("/api/v1/import/status")
async def get_import_status():
    """Get the status of import operations"""
    # This would track ongoing imports
    return {
        "status": "ready",
        "last_import": None,
        "imports_in_progress": []
    }


@app.get("/api/v1/export/vcf")
async def export_database(active_only: bool = Query(True, description="Export only active contacts")):
    """Export the database as a vCard file"""
    try:
        vcf_content = db.export_database(active_only=active_only)
        
        # Create response with vCard content
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contactplus_export_{timestamp}.vcf"
        
        return Response(
            content=vcf_content,
            media_type="text/vcard",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System Operations

@app.get("/api/v1/stats", response_model=DatabaseStats)
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = db.get_database_stats()
        return DatabaseStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return ErrorResponse(
        error="Not Found",
        detail=str(exc.detail) if hasattr(exc, 'detail') else "Resource not found",
        status_code=404
    )


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred",
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)