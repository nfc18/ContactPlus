#!/usr/bin/env python3
"""
Pre-deployment check for ContactPlus MVP on Mac
Verifies all prerequisites and configuration before deployment
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_command(command, name):
    """Check if a command is available"""
    if shutil.which(command):
        print(f"✅ {name} is installed")
        return True
    else:
        print(f"❌ {name} is NOT installed")
        return False


def check_docker():
    """Check Docker installation and status"""
    print("\n🐳 Checking Docker...")
    
    if not check_command("docker", "Docker"):
        print("   Please install Docker Desktop: https://www.docker.com/products/docker-desktop/")
        return False
    
    try:
        # Check if Docker is running
        result = subprocess.run(["docker", "info"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker is running")
            return True
        else:
            print("❌ Docker is not running")
            print("   Please start Docker Desktop")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False


def check_docker_compose():
    """Check Docker Compose availability"""
    print("\n📦 Checking Docker Compose...")
    
    # Try docker-compose command
    if check_command("docker-compose", "Docker Compose (standalone)"):
        return True
    
    # Try docker compose (plugin)
    try:
        result = subprocess.run(["docker", "compose", "version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker Compose (plugin) is available")
            return True
    except:
        pass
    
    print("❌ Docker Compose is not available")
    print("   Please install Docker Desktop with Compose")
    return False


def check_python():
    """Check Python installation"""
    print("\n🐍 Checking Python...")
    
    if not check_command("python3", "Python 3"):
        print("   Please install Python 3: https://www.python.org/downloads/")
        return False
    
    try:
        result = subprocess.run(["python3", "--version"], 
                              capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✅ {version}")
        
        # Check if version is 3.8+
        version_parts = version.split()[1].split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        
        if major >= 3 and minor >= 8:
            print("✅ Python version is compatible")
            return True
        else:
            print("❌ Python version too old (need 3.8+)")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Python version: {e}")
        return False


def check_ports():
    """Check if required ports are available"""
    print("\n🔌 Checking Port Availability...")
    
    required_ports = [3000, 8080, 8081, 9090]
    available_ports = []
    
    for port in required_ports:
        try:
            result = subprocess.run(["lsof", f"-i:{port}"], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                print(f"❌ Port {port} is in use")
                print(f"   Process: {result.stdout.strip().split()[0]}")
            else:
                print(f"✅ Port {port} is available")
                available_ports.append(port)
        except:
            # If lsof fails, assume port is available
            available_ports.append(port)
    
    return len(available_ports) == len(required_ports)


def check_system_resources():
    """Check system resources"""
    print("\n💻 Checking System Resources...")
    
    try:
        # Check available memory
        result = subprocess.run(["sysctl", "-n", "hw.memsize"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            total_memory_bytes = int(result.stdout.strip())
            total_memory_gb = total_memory_bytes / (1024**3)
            
            if total_memory_gb >= 8:
                print(f"✅ Memory: {total_memory_gb:.1f} GB (sufficient)")
            else:
                print(f"⚠️  Memory: {total_memory_gb:.1f} GB (may be limited)")
        
        # Check available disk space
        statvfs = os.statvfs('.')
        free_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
        
        if free_space_gb >= 10:
            print(f"✅ Disk Space: {free_space_gb:.1f} GB available")
        else:
            print(f"⚠️  Disk Space: {free_space_gb:.1f} GB (may be limited)")
            
        return True
        
    except Exception as e:
        print(f"⚠️  Could not check system resources: {e}")
        return True  # Don't fail on this


def check_project_files():
    """Check if all required project files exist"""
    print("\n📁 Checking Project Files...")
    
    required_files = [
        "docker-compose.yml",
        "contactplus-core/Dockerfile",
        "contactplus-core/main.py",
        "contactplus-web/Dockerfile",
        "contactplus-web/package.json",
        "contactplus-monitor/Dockerfile",
        "deploy_and_test.sh",
        "test_functionality.py",
        "quick_test.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def check_source_data():
    """Check if source data files exist"""
    print("\n📊 Checking Source Data...")
    
    source_files = [
        "Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf",
        "Imports/iPhone_Contacts_Contacts.vcf", 
        "Imports/iPhone_Suggested_Suggested Contacts.vcf"
    ]
    
    available_files = []
    for file_path in source_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"✅ {file_path} ({file_size:.1f} MB)")
            available_files.append(file_path)
        else:
            print(f"⚠️  {file_path} (not found)")
    
    if len(available_files) > 0:
        print(f"✅ {len(available_files)} source file(s) available for import")
        return True
    else:
        print("⚠️  No source files found - import will be empty")
        return True  # Don't fail deployment for this


def main():
    """Run all pre-deployment checks"""
    print("🔍 ContactPlus MVP - Pre-Deployment Check")
    print("=" * 50)
    
    checks = [
        ("Docker Installation", check_docker),
        ("Docker Compose", check_docker_compose), 
        ("Python Installation", check_python),
        ("Port Availability", check_ports),
        ("System Resources", check_system_resources),
        ("Project Files", check_project_files),
        ("Source Data", check_source_data)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 PRE-DEPLOYMENT CHECK SUMMARY")
    print("=" * 50)
    
    passed = 0
    critical_failed = False
    
    for check_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {check_name}")
        
        if success:
            passed += 1
        elif check_name in ["Docker Installation", "Docker Compose", "Python Installation", "Project Files"]:
            critical_failed = True
    
    total = len(results)
    print(f"\nResults: {passed}/{total} checks passed")
    
    if critical_failed:
        print("\n❌ CRITICAL ISSUES FOUND")
        print("Please fix the failed checks before deployment.")
        print("\nHelp:")
        print("• Install Docker Desktop: https://www.docker.com/products/docker-desktop/")
        print("• Install Python 3.8+: https://www.python.org/downloads/")
        print("• Ensure all project files are present")
        return False
        
    elif passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("System is ready for ContactPlus MVP deployment!")
        print("\nNext steps:")
        print("1. Run: ./deploy_and_test.sh")
        print("2. Wait for services to start")
        print("3. Open: http://localhost:3000")
        return True
        
    else:
        print("\n⚠️  MINOR ISSUES DETECTED")
        print("Some non-critical checks failed, but deployment should work.")
        print("You may experience reduced functionality or performance.")
        print("\nYou can proceed with deployment:")
        print("./deploy_and_test.sh")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)