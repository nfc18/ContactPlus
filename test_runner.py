#!/usr/bin/env python3
"""
Comprehensive Test Runner for ContactPlus MVP
"""
import os
import sys
import subprocess
import time
import requests
import docker
from pathlib import Path


class ContactPlusTestRunner:
    """Test runner for ContactPlus MVP"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.services_ready = False
        
    def wait_for_services(self, timeout=120):
        """Wait for all services to be ready"""
        services = {
            "Core API": "http://localhost:8080/api/v1/health",
            "Web Interface": "http://localhost:3000", 
            "Monitor": "http://localhost:9090",
            "Dozzle": "http://localhost:8081"
        }
        
        print("🔍 Waiting for services to be ready...")
        start_time = time.time()
        
        for service_name, url in services.items():
            service_ready = False
            while time.time() - start_time < timeout and not service_ready:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code < 500:
                        print(f"  ✅ {service_name} is ready")
                        service_ready = True
                    else:
                        print(f"  ⏳ {service_name} responding but not ready (status: {response.status_code})")
                except requests.exceptions.RequestException:
                    print(f"  ⏳ Waiting for {service_name}...")
                
                if not service_ready:
                    time.sleep(3)
            
            if not service_ready:
                print(f"  ❌ {service_name} failed to become ready")
                return False
        
        self.services_ready = True
        print("🎉 All services are ready!")
        return True
    
    def check_docker_containers(self):
        """Check Docker container status"""
        try:
            client = docker.from_env()
            containers = client.containers.list()
            
            expected_containers = [
                "contactplus-core",
                "contactplus-web", 
                "contactplus-monitor",
                "dozzle"
            ]
            
            running_containers = [c.name for c in containers if c.status == "running"]
            
            print("🐳 Docker container status:")
            for container_name in expected_containers:
                if container_name in running_containers:
                    print(f"  ✅ {container_name} is running")
                else:
                    print(f"  ❌ {container_name} is not running")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking Docker containers: {e}")
            return False
    
    def run_tests(self, test_category=None, verbose=False):
        """Run test suites"""
        if not self.services_ready:
            print("❌ Services not ready. Run wait_for_services() first.")
            return False
        
        # Install test dependencies
        print("📦 Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(self.tests_dir / "requirements.txt")
        ], check=True)
        
        # Determine which tests to run
        if test_category:
            test_path = self.tests_dir / test_category
            if not test_path.exists():
                print(f"❌ Test category '{test_category}' not found")
                return False
        else:
            test_path = str(self.tests_dir)
        
        # Prepare pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "--tb=short",
            "--durations=10",
            "-v" if verbose else "-q"
        ]
        
        # Add coverage if running all tests
        if not test_category:
            cmd.extend([
                "--cov=contactplus-core",
                "--cov-report=html:htmlcov",
                "--cov-report=term"
            ])
        
        print(f"🧪 Running tests: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("🔗 Running Integration Tests...")
        return self.run_tests("integration", verbose=True)
    
    def run_e2e_tests(self):
        """Run end-to-end tests"""
        print("🎭 Running End-to-End Tests...")
        return self.run_tests("e2e", verbose=True)
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        return self.run_tests("performance", verbose=True)
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🎯 Running Complete Test Suite...")
        return self.run_tests(verbose=True)
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        report_file = self.project_root / "test_report.html"
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir),
            "--html=" + str(report_file),
            "--self-contained-html",
            "--tb=short"
        ]
        
        print(f"📊 Generating test report: {report_file}")
        
        try:
            subprocess.run(cmd, cwd=self.project_root)
            print(f"✅ Test report generated: {report_file}")
            return True
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return False
    
    def validate_logging(self):
        """Validate logging functionality"""
        print("📝 Validating logging functionality...")
        
        # Check if Dozzle is accessible and showing logs
        try:
            response = requests.get("http://localhost:8081", timeout=10)
            if response.status_code == 200:
                print("  ✅ Dozzle is accessible")
                
                # Make some API calls to generate logs
                for i in range(5):
                    requests.get("http://localhost:8080/api/v1/health", timeout=5)
                    requests.get("http://localhost:8080/api/v1/stats", timeout=5)
                    time.sleep(1)
                
                print("  ✅ Generated test log entries")
                return True
            else:
                print(f"  ❌ Dozzle not accessible (status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"  ❌ Error validating logging: {e}")
            return False
    
    def run_smoke_tests(self):
        """Run quick smoke tests to verify basic functionality"""
        print("💨 Running Smoke Tests...")
        
        tests = [
            ("Health Check", lambda: requests.get("http://localhost:8080/api/v1/health").status_code == 200),
            ("Stats Endpoint", lambda: requests.get("http://localhost:8080/api/v1/stats").status_code == 200),
            ("Contacts List", lambda: requests.get("http://localhost:8080/api/v1/contacts").status_code == 200),
            ("Import Status", lambda: requests.get("http://localhost:8080/api/v1/import/status").status_code == 200),
            ("Web Interface", lambda: requests.get("http://localhost:3000").status_code == 200),
            ("Monitor Dashboard", lambda: requests.get("http://localhost:9090").status_code == 200),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                status = "✅" if success else "❌"
                print(f"  {status} {test_name}")
            except Exception as e:
                results.append((test_name, False))
                print(f"  ❌ {test_name}: {e}")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\n💨 Smoke Tests: {passed}/{total} passed")
        return passed == total


def main():
    """Main test runner function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ContactPlus MVP Test Runner")
    parser.add_argument("--category", choices=["integration", "e2e", "performance"], 
                       help="Run specific test category")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--report", action="store_true", help="Generate HTML test report")
    parser.add_argument("--wait", action="store_true", help="Wait for services to be ready")
    parser.add_argument("--skip-docker-check", action="store_true", help="Skip Docker container check")
    
    args = parser.parse_args()
    
    runner = ContactPlusTestRunner()
    
    print("🚀 ContactPlus MVP Test Runner")
    print("=" * 50)
    
    # Check Docker containers
    if not args.skip_docker_check:
        if not runner.check_docker_containers():
            print("❌ Docker containers not ready. Please run 'docker-compose up -d' first.")
            sys.exit(1)
    
    # Wait for services
    if args.wait or not args.smoke:
        if not runner.wait_for_services():
            print("❌ Services failed to become ready")
            sys.exit(1)
    
    # Run smoke tests
    if args.smoke:
        success = runner.run_smoke_tests()
        runner.validate_logging()
        sys.exit(0 if success else 1)
    
    # Validate logging
    runner.validate_logging()
    
    # Run tests
    success = True
    
    if args.category:
        if args.category == "integration":
            success = runner.run_integration_tests()
        elif args.category == "e2e":
            success = runner.run_e2e_tests()
        elif args.category == "performance":
            success = runner.run_performance_tests()
    else:
        success = runner.run_all_tests()
    
    # Generate report
    if args.report:
        runner.generate_test_report()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()