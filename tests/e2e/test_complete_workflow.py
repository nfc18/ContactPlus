"""
End-to-End Workflow Tests for ContactPlus MVP
"""
import pytest
import requests
import time
import tempfile
import os
from pathlib import Path


class TestCompleteWorkflow:
    """Test complete user workflows from start to finish"""
    
    def test_full_contact_lifecycle(self, api_base_url):
        """Test complete contact lifecycle: import -> view -> edit -> export -> delete"""
        
        # Step 1: Check initial state
        response = requests.get(f"{api_base_url}/stats")
        assert response.status_code == 200
        initial_stats = response.json()
        initial_count = initial_stats["active_contacts"]
        
        # Step 2: Import initial databases (if not already done)
        response = requests.post(f"{api_base_url}/import/initial")
        assert response.status_code == 200
        import_result = response.json()
        
        # Wait for import to complete
        time.sleep(2)
        
        # Step 3: Verify contacts were imported
        response = requests.get(f"{api_base_url}/stats")
        assert response.status_code == 200
        new_stats = response.json()
        
        if import_result["imported_contacts"] > 0:
            assert new_stats["active_contacts"] > initial_count
        
        # Step 4: List contacts
        response = requests.get(f"{api_base_url}/contacts?page=1&page_size=5")
        assert response.status_code == 200
        contacts_data = response.json()
        
        if contacts_data["total"] > 0:
            # Step 5: Get a specific contact
            first_contact = contacts_data["contacts"][0]
            contact_id = first_contact["contact_id"]
            
            response = requests.get(f"{api_base_url}/contacts/{contact_id}")
            assert response.status_code == 200
            contact_detail = response.json()
            assert contact_detail["contact_id"] == contact_id
            
            # Step 6: Update the contact
            update_data = {
                "fn": f"Updated {first_contact['formatted_name']}",
                "notes": "Updated via E2E test"
            }
            response = requests.put(f"{api_base_url}/contacts/{contact_id}", json=update_data)
            assert response.status_code == 200
            
            # Step 7: Verify update
            response = requests.get(f"{api_base_url}/contacts/{contact_id}")
            assert response.status_code == 200
            updated_contact = response.json()
            assert "Updated" in updated_contact["formatted_name"]
            assert updated_contact["notes"] == "Updated via E2E test"
            
            # Step 8: Search for the updated contact
            response = requests.get(f"{api_base_url}/contacts/search?query=Updated")
            assert response.status_code == 200
            search_results = response.json()
            found_contact = None
            for contact in search_results["contacts"]:
                if contact["contact_id"] == contact_id:
                    found_contact = contact
                    break
            assert found_contact is not None, "Updated contact not found in search"
        
        # Step 9: Export all contacts
        response = requests.get(f"{api_base_url}/export/vcf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/vcard; charset=utf-8"
        
        vcf_content = response.text
        if new_stats["active_contacts"] > 0:
            assert "BEGIN:VCARD" in vcf_content
            assert "END:VCARD" in vcf_content
        
        print(f"✅ Complete workflow test passed with {new_stats['active_contacts']} contacts")
    
    def test_search_functionality_workflow(self, api_base_url):
        """Test comprehensive search functionality"""
        
        # First ensure we have some contacts
        response = requests.get(f"{api_base_url}/stats")
        assert response.status_code == 200
        stats = response.json()
        
        if stats["active_contacts"] == 0:
            # Import some contacts first
            requests.post(f"{api_base_url}/import/initial")
            time.sleep(2)
        
        # Test various search scenarios
        search_terms = [
            "test",
            "@",  # Should find emails
            "+",  # Should find phone numbers
            "corp",  # Should find organizations
        ]
        
        for term in search_terms:
            response = requests.get(f"{api_base_url}/contacts/search?query={term}")
            assert response.status_code == 200
            results = response.json()
            assert "contacts" in results
            assert "total" in results
            assert isinstance(results["contacts"], list)
        
        # Test search with specific fields
        response = requests.get(f"{api_base_url}/contacts/search?query=test&fields=fn&fields=email")
        assert response.status_code == 200
        
        # Test pagination in search
        response = requests.get(f"{api_base_url}/contacts/search?query=a&page=1&page_size=5")
        assert response.status_code == 200
        results = response.json()
        assert results["page"] == 1
        assert results["page_size"] == 5
    
    def test_error_handling_workflow(self, api_base_url):
        """Test error handling in various scenarios"""
        
        # Test invalid contact ID
        response = requests.get(f"{api_base_url}/contacts/invalid_id_12345")
        assert response.status_code == 404
        
        # Test invalid update data
        invalid_data = {"invalid_field": "value"}
        response = requests.put(f"{api_base_url}/contacts/invalid_id", json=invalid_data)
        assert response.status_code == 404  # Should fail on missing contact first
        
        # Test invalid search query
        response = requests.get(f"{api_base_url}/contacts/search")  # Missing query
        assert response.status_code == 422
        
        # Test invalid pagination
        response = requests.get(f"{api_base_url}/contacts?page=0")
        assert response.status_code == 422
        
        response = requests.get(f"{api_base_url}/contacts?page_size=0")
        assert response.status_code == 422
        
        print("✅ Error handling workflow test passed")
    
    def test_concurrent_operations_workflow(self, api_base_url):
        """Test system behavior under concurrent operations"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_health_check():
            try:
                response = requests.get(f"{api_base_url}/health", timeout=10)
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        def make_stats_request():
            try:
                response = requests.get(f"{api_base_url}/stats", timeout=10)
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        def make_contacts_request():
            try:
                response = requests.get(f"{api_base_url}/contacts?page=1&page_size=5", timeout=10)
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=make_health_check))
            threads.append(threading.Thread(target=make_stats_request))
            threads.append(threading.Thread(target=make_contacts_request))
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=15)
        
        # Check results
        success_count = 0
        error_count = 0
        
        while not results.empty():
            result = results.get()
            if isinstance(result, int) and result == 200:
                success_count += 1
            else:
                error_count += 1
        
        # Most requests should succeed
        total_requests = len(threads)
        success_rate = success_count / total_requests
        assert success_rate >= 0.8, f"Success rate too low: {success_rate} ({success_count}/{total_requests})"
        
        print(f"✅ Concurrent operations test passed: {success_count}/{total_requests} successful")


class TestWebInterfaceWorkflow:
    """Test web interface workflows"""
    
    def test_web_interface_accessibility(self, web_base_url):
        """Test that web interface is accessible and functional"""
        
        # Test main page
        response = requests.get(web_base_url, timeout=10)
        assert response.status_code == 200
        assert "ContactPlus" in response.text
        
        # Test dashboard page
        response = requests.get(f"{web_base_url}/dashboard", timeout=10)
        assert response.status_code == 200
        
        # Test contacts page
        response = requests.get(f"{web_base_url}/contacts", timeout=10)
        assert response.status_code == 200
        
        # Test import page
        response = requests.get(f"{web_base_url}/import", timeout=10)
        assert response.status_code == 200
        
        print("✅ Web interface accessibility test passed")
    
    def test_monitor_dashboard_accessibility(self, monitor_base_url):
        """Test monitor dashboard accessibility"""
        
        response = requests.get(monitor_base_url, timeout=10)
        assert response.status_code == 200
        assert any(keyword in response.text.lower() for keyword in ["monitor", "health", "contactplus"])
        
        print("✅ Monitor dashboard accessibility test passed")
    
    def test_dozzle_accessibility(self, dozzle_base_url):
        """Test Dozzle log viewer accessibility"""
        
        response = requests.get(dozzle_base_url, timeout=10)
        assert response.status_code == 200
        assert any(keyword in response.text.lower() for keyword in ["dozzle", "logs", "containers"])
        
        print("✅ Dozzle accessibility test passed")


class TestDataPersistence:
    """Test data persistence across container restarts"""
    
    def test_data_survives_restart(self, api_base_url, docker_client):
        """Test that data persists after container restart"""
        
        # Get initial stats
        response = requests.get(f"{api_base_url}/stats")
        assert response.status_code == 200
        initial_stats = response.json()
        
        # Import data if needed
        if initial_stats["active_contacts"] == 0:
            requests.post(f"{api_base_url}/import/initial")
            time.sleep(2)
            
            response = requests.get(f"{api_base_url}/stats")
            assert response.status_code == 200
            initial_stats = response.json()
        
        if initial_stats["active_contacts"] > 0:
            # Restart the core container
            container = docker_client.containers.get("contactplus-core")
            container.restart(timeout=30)
            
            # Wait for container to be ready
            max_wait = 60
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                try:
                    response = requests.get(f"{api_base_url}/health", timeout=5)
                    if response.status_code == 200:
                        break
                except:
                    pass
                time.sleep(2)
            else:
                pytest.fail("API not responsive after restart")
            
            # Check data is still there
            response = requests.get(f"{api_base_url}/stats")
            assert response.status_code == 200
            final_stats = response.json()
            
            assert final_stats["active_contacts"] == initial_stats["active_contacts"]
            assert final_stats["total_contacts"] == initial_stats["total_contacts"]
            
            print(f"✅ Data persistence test passed: {final_stats['active_contacts']} contacts preserved")
        else:
            print("⚠️ Data persistence test skipped: no contacts to test with")


class TestPerformanceBaseline:
    """Test basic performance characteristics"""
    
    def test_response_times(self, api_base_url):
        """Test API response times are reasonable"""
        
        endpoints = [
            "/health",
            "/stats", 
            "/contacts?page=1&page_size=10",
            "/import/status"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{api_base_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0, f"Endpoint {endpoint} too slow: {response_time:.2f}s"
            
            print(f"✅ {endpoint}: {response_time:.3f}s")
    
    def test_large_contact_list_performance(self, api_base_url):
        """Test performance with larger contact lists"""
        
        # Test with different page sizes
        page_sizes = [10, 50, 100]
        
        for page_size in page_sizes:
            start_time = time.time()
            response = requests.get(f"{api_base_url}/contacts?page=1&page_size={page_size}", timeout=15)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 10.0, f"Large list (size {page_size}) too slow: {response_time:.2f}s"
            
            data = response.json()
            actual_returned = len(data["contacts"])
            expected_returned = min(page_size, data["total"])
            assert actual_returned <= expected_returned
            
            print(f"✅ Page size {page_size}: {response_time:.3f}s, returned {actual_returned} contacts")