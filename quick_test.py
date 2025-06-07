#!/usr/bin/env python3
"""
Quick validation test for ContactPlus MVP
"""
import requests
import time
import sys


def test_core_api():
    """Test core API functionality"""
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8080/api/v1/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        health_data = response.json()
        assert "status" in health_data
        assert "version" in health_data
        print("✅ Core API health check passed")
        
        # Test stats endpoint
        response = requests.get("http://localhost:8080/api/v1/stats", timeout=10)
        assert response.status_code == 200, f"Stats failed: {response.status_code}"
        
        stats_data = response.json()
        assert "total_contacts" in stats_data
        assert "active_contacts" in stats_data
        print("✅ Core API stats endpoint passed")
        
        # Test contacts endpoint
        response = requests.get("http://localhost:8080/api/v1/contacts", timeout=10)
        assert response.status_code == 200, f"Contacts failed: {response.status_code}"
        
        contacts_data = response.json()
        assert "contacts" in contacts_data
        assert "total" in contacts_data
        print("✅ Core API contacts endpoint passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Core API test failed: {e}")
        return False


def test_web_interface():
    """Test web interface accessibility"""
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        assert response.status_code == 200, f"Web interface failed: {response.status_code}"
        
        # Check if it contains expected content
        content = response.text.lower()
        assert "contactplus" in content, "Web interface doesn't contain ContactPlus"
        print("✅ Web interface accessibility passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False


def test_monitor_dashboard():
    """Test monitor dashboard"""
    try:
        response = requests.get("http://localhost:9090", timeout=10)
        assert response.status_code == 200, f"Monitor failed: {response.status_code}"
        
        content = response.text.lower()
        assert any(keyword in content for keyword in ["monitor", "contactplus", "health"]), \
               "Monitor dashboard content invalid"
        print("✅ Monitor dashboard accessibility passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitor dashboard test failed: {e}")
        return False


def test_dozzle_logs():
    """Test Dozzle log viewer"""
    try:
        response = requests.get("http://localhost:8081", timeout=10)
        assert response.status_code == 200, f"Dozzle failed: {response.status_code}"
        
        content = response.text.lower()
        assert any(keyword in content for keyword in ["dozzle", "logs", "containers"]), \
               "Dozzle content invalid"
        print("✅ Dozzle log viewer accessibility passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Dozzle test failed: {e}")
        return False


def test_api_integration():
    """Test basic API integration"""
    try:
        # Test import status
        response = requests.get("http://localhost:8080/api/v1/import/status", timeout=10)
        assert response.status_code == 200, f"Import status failed: {response.status_code}"
        print("✅ Import status endpoint passed")
        
        # Test search (even if no results)
        response = requests.get("http://localhost:8080/api/v1/contacts/search?query=test", timeout=10)
        assert response.status_code == 200, f"Search failed: {response.status_code}"
        
        search_data = response.json()
        assert "contacts" in search_data
        print("✅ Search endpoint passed")
        
        # Test export endpoint
        response = requests.get("http://localhost:8080/api/v1/export/vcf", timeout=10)
        assert response.status_code == 200, f"Export failed: {response.status_code}"
        assert response.headers["content-type"] == "text/vcard; charset=utf-8"
        print("✅ Export endpoint passed")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False


def main():
    """Run all quick tests"""
    print("🧪 ContactPlus MVP Quick Validation Test")
    print("=" * 45)
    
    # Wait a moment for services to be fully ready
    print("⏳ Waiting for services to stabilize...")
    time.sleep(5)
    
    tests = [
        ("Core API", test_core_api),
        ("Web Interface", test_web_interface), 
        ("Monitor Dashboard", test_monitor_dashboard),
        ("Dozzle Logs", test_dozzle_logs),
        ("API Integration", test_api_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! ContactPlus MVP is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total-passed} test(s) failed. Please check the services.")
        return 1


if __name__ == "__main__":
    sys.exit(main())