"""
API Integration Tests for ContactPlus
"""
import pytest
import httpx
import json
import tempfile
import os


class TestHealthEndpoints:
    """Test health and system endpoints"""
    
    async def test_health_check(self, api_client):
        """Test health check endpoint"""
        response = await api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "timestamp" in data
        assert "database_connected" in data
        assert "contacts_count" in data
        assert data["version"] == "1.0.0"
    
    async def test_root_endpoint(self, api_client):
        """Test root endpoint"""
        response = await api_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "ContactPlus Core API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    async def test_database_stats(self, api_client):
        """Test database statistics endpoint"""
        response = await api_client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_contacts" in data
        assert "active_contacts" in data
        assert "contacts_by_source" in data
        assert "total_operations" in data
        assert isinstance(data["total_contacts"], int)
        assert isinstance(data["active_contacts"], int)


class TestContactEndpoints:
    """Test contact CRUD operations"""
    
    async def test_list_contacts_empty(self, api_client):
        """Test listing contacts when database is empty"""
        response = await api_client.get("/contacts")
        assert response.status_code == 200
        
        data = response.json()
        assert "contacts" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert isinstance(data["contacts"], list)
    
    async def test_list_contacts_pagination(self, api_client):
        """Test pagination parameters"""
        response = await api_client.get("/contacts?page=1&page_size=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
    
    async def test_invalid_pagination(self, api_client):
        """Test invalid pagination parameters"""
        response = await api_client.get("/contacts?page=0")
        assert response.status_code == 422  # Validation error
        
        response = await api_client.get("/contacts?page_size=0")
        assert response.status_code == 422
    
    async def test_get_nonexistent_contact(self, api_client):
        """Test getting a contact that doesn't exist"""
        response = await api_client.get("/contacts/nonexistent_id")
        assert response.status_code == 404
    
    async def test_update_nonexistent_contact(self, api_client):
        """Test updating a contact that doesn't exist"""
        update_data = {
            "fn": "Updated Name",
            "emails": ["updated@example.com"]
        }
        response = await api_client.put("/contacts/nonexistent_id", json=update_data)
        assert response.status_code == 404
    
    async def test_delete_nonexistent_contact(self, api_client):
        """Test deleting a contact that doesn't exist"""
        response = await api_client.delete("/contacts/nonexistent_id")
        assert response.status_code == 404


class TestSearchEndpoints:
    """Test search functionality"""
    
    async def test_search_contacts_empty_query(self, api_client):
        """Test search with empty query"""
        response = await api_client.get("/contacts/search?query=")
        assert response.status_code == 422  # Should require non-empty query
    
    async def test_search_contacts_no_results(self, api_client):
        """Test search with no matching results"""
        response = await api_client.get("/contacts/search?query=nonexistent_contact_xyz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert len(data["contacts"]) == 0
    
    async def test_search_contacts_with_fields(self, api_client):
        """Test search with specific field filters"""
        response = await api_client.get("/contacts/search?query=test&fields=fn&fields=email")
        assert response.status_code == 200
        
        data = response.json()
        assert "contacts" in data
        assert isinstance(data["contacts"], list)


class TestImportEndpoints:
    """Test import functionality"""
    
    async def test_import_status(self, api_client):
        """Test import status endpoint"""
        response = await api_client.get("/import/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "last_import" in data
        assert "imports_in_progress" in data
    
    async def test_initial_import(self, api_client):
        """Test initial database import"""
        response = await api_client.post("/import/initial")
        assert response.status_code == 200
        
        data = response.json()
        assert "database_name" in data
        assert "total_contacts" in data
        assert "imported_contacts" in data
        assert "compliance_fixes" in data
        assert "errors" in data
        assert "contact_ids" in data
        assert isinstance(data["errors"], list)
        assert isinstance(data["contact_ids"], list)


class TestExportEndpoints:
    """Test export functionality"""
    
    async def test_export_vcf_empty_database(self, api_client):
        """Test exporting VCF from empty database"""
        response = await api_client.get("/export/vcf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/vcard; charset=utf-8"
        assert "attachment; filename=" in response.headers.get("content-disposition", "")
    
    async def test_export_vcf_active_only(self, api_client):
        """Test exporting only active contacts"""
        response = await api_client.get("/export/vcf?active_only=true")
        assert response.status_code == 200
        
        response = await api_client.get("/export/vcf?active_only=false")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    async def test_invalid_json_payload(self, api_client):
        """Test sending invalid JSON"""
        response = await api_client.put(
            "/contacts/test_id",
            content="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    async def test_invalid_content_type(self, api_client):
        """Test sending wrong content type"""
        response = await api_client.put(
            "/contacts/test_id",
            content="some data",
            headers={"content-type": "text/plain"}
        )
        assert response.status_code in [400, 422]
    
    async def test_large_payload(self, api_client):
        """Test handling large payloads"""
        large_data = {
            "fn": "Test" * 1000,
            "notes": "x" * 10000
        }
        response = await api_client.put("/contacts/test_id", json=large_data)
        # Should either accept or reject gracefully
        assert response.status_code in [200, 404, 413, 422]


class TestRateLimiting:
    """Test API rate limiting and performance"""
    
    async def test_concurrent_requests(self, api_client):
        """Test handling concurrent requests"""
        import asyncio
        
        async def make_request():
            return await api_client.get("/health")
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
    
    async def test_sequential_requests(self, api_client):
        """Test handling many sequential requests"""
        for i in range(20):
            response = await api_client.get("/health")
            assert response.status_code == 200


class TestCORS:
    """Test CORS configuration"""
    
    async def test_cors_headers(self, api_base_url):
        """Test CORS headers are present"""
        async with httpx.AsyncClient() as client:
            response = await client.options(
                f"{api_base_url}/health",
                headers={"Origin": "http://localhost:3000"}
            )
            # CORS should be configured
            assert response.status_code in [200, 204]


@pytest.mark.asyncio
class TestWebsocketConnections:
    """Test websocket connections if any"""
    
    async def test_no_websocket_endpoints(self, api_client):
        """Verify no unexpected websocket endpoints"""
        # This is a REST API, should not have websockets
        response = await api_client.get("/ws", headers={"Upgrade": "websocket"})
        assert response.status_code == 404