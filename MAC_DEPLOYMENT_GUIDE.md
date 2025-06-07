# ContactPlus MVP - Mac Deployment Guide

## 🍎 **Mac-Specific Deployment Instructions**

### **Prerequisites**

1. **Docker Desktop for Mac**
   ```bash
   # Install via Homebrew
   brew install --cask docker
   
   # OR download from: https://www.docker.com/products/docker-desktop/
   ```

2. **Python 3.11+**
   ```bash
   # Install via Homebrew
   brew install python@3.11
   
   # OR download from: https://www.python.org/downloads/
   ```

3. **System Requirements**
   - macOS 10.15+ (Catalina or newer)
   - 8GB RAM minimum (16GB recommended)
   - 20GB free disk space
   - Intel or Apple Silicon Mac

---

## 🚀 **Quick Deployment**

### **Option 1: Automated Deployment (Recommended)**
```bash
# Navigate to project directory
cd /Users/lk/Documents/Developer/Private/ContactPlus

# Run complete deployment and testing
./deploy_and_test.sh
```

### **Option 2: Manual Deployment**
```bash
# Start Docker Desktop first
open -a Docker

# Wait for Docker to be ready, then:
docker-compose build --no-cache
docker-compose up -d

# Run quick validation
python3 quick_test.py
```

---

## 🔍 **Mac-Specific Verification Steps**

### **1. Docker Desktop Status**
```bash
# Check Docker is running
docker info

# Check available resources
docker system df

# View Docker Desktop GUI
open -a Docker
```

### **2. Service Health Check**
```bash
# Test all services
curl http://localhost:8080/api/v1/health  # Core API
curl http://localhost:3000                # Web Interface  
curl http://localhost:9090                # Monitor
curl http://localhost:8081                # Dozzle Logs
```

### **3. Port Verification**
```bash
# Check ports are open and bound correctly
lsof -i :3000  # Web Interface
lsof -i :8080  # Core API
lsof -i :8081  # Dozzle
lsof -i :9090  # Monitor
```

### **4. Container Status**
```bash
# List running containers
docker ps

# Check container health
docker-compose ps

# View container logs
docker-compose logs contactplus-core
docker-compose logs contactplus-web
```

---

## 🧪 **Testing on Mac**

### **Quick Tests**
```bash
# Basic functionality (30 seconds)
python3 quick_test.py

# Smoke tests
python3 test_runner.py --smoke
```

### **Full Test Suite**
```bash
# Install test dependencies
pip3 install -r tests/requirements.txt

# Run all tests
python3 test_runner.py

# Generate HTML report
python3 test_runner.py --report
open test_report.html  # View in browser
```

### **Performance Testing**
```bash
# Mac-specific performance tests
python3 test_runner.py --category performance

# Monitor system resources
top -pid $(docker-compose ps -q)
```

---

## 🖥️ **Mac System Integration**

### **Browser Testing**
```bash
# Open all interfaces in default browser
open http://localhost:3000    # Web Interface
open http://localhost:8080/docs  # API Docs
open http://localhost:9090    # Monitor
open http://localhost:8081    # Logs
```

### **Activity Monitor Integration**
1. Open Activity Monitor
2. Search for "docker" processes
3. Monitor CPU and memory usage
4. Verify resource consumption is reasonable

### **Finder Integration**
```bash
# Open project directory in Finder
open .

# View Docker volumes in Finder
open ~/Library/Containers/com.docker.docker/Data/vms/0/
```

---

## 🔧 **Mac-Specific Troubleshooting**

### **Docker Desktop Issues**
```bash
# Restart Docker Desktop
osascript -e 'quit app "Docker Desktop"'
sleep 5
open -a Docker

# Reset Docker to factory defaults (if needed)
# Go to Docker Desktop > Troubleshoot > Reset to factory defaults
```

### **Port Conflicts**
```bash
# Check what's using required ports
lsof -i :3000 -i :8080 -i :8081 -i :9090

# Kill processes using ports (if needed)
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8080 | xargs kill -9
```

### **Memory Issues**
```bash
# Check available memory
vm_stat

# Increase Docker memory allocation
# Docker Desktop > Settings > Resources > Memory (set to 8GB+)
```

### **Permission Issues**
```bash
# Fix Docker permissions
sudo chown -R $(whoami) ~/.docker

# Fix file permissions
chmod -R 755 /Users/lk/Documents/Developer/Private/ContactPlus
```

---

## 📊 **Mac Performance Optimization**

### **Docker Settings**
1. **Memory**: Allocate 8GB+ for optimal performance
2. **CPUs**: Use 4+ CPU cores if available
3. **Disk Image Size**: Set to 100GB+ for data storage
4. **Swap**: Enable swap file (2GB recommended)

### **macOS Settings**
```bash
# Disable Spotlight indexing for Docker directory (optional)
sudo mdutil -i off /Users/lk/Documents/Developer/Private/ContactPlus

# Check system load
uptime
sysctl -n hw.ncpu  # Number of CPU cores
sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}'  # RAM
```

---

## 🔐 **Mac Security Considerations**

### **Firewall Settings**
```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Allow Docker if prompted by macOS
# System Preferences > Security & Privacy > Firewall
```

### **Gatekeeper**
```bash
# If scripts are blocked by Gatekeeper
sudo xattr -r -d com.apple.quarantine /Users/lk/Documents/Developer/Private/ContactPlus
```

---

## 📱 **Mac User Experience**

### **Menu Bar Integration**
- Docker Desktop icon shows container status
- Click for quick access to container logs
- Resource usage displayed in real-time

### **Notifications**
- macOS notifications for container health changes
- Docker Desktop notifications for build completion

### **Spotlight Search**
```bash
# Make project searchable in Spotlight
mdfind "ContactPlus"
```

---

## 🚨 **Emergency Procedures**

### **Complete Reset**
```bash
# Stop all services
docker-compose down -v

# Remove all containers and images
docker system prune -a --volumes

# Restart Docker Desktop
osascript -e 'quit app "Docker Desktop"'
open -a Docker

# Redeploy
./deploy_and_test.sh
```

### **Data Recovery**
```bash
# Backup data before reset
docker run --rm -v contactplus_contact_data:/data -v $(pwd):/backup alpine tar czf /backup/contactplus_backup.tar.gz /data

# Restore data after reset
docker run --rm -v contactplus_contact_data:/data -v $(pwd):/backup alpine tar xzf /backup/contactplus_backup.tar.gz -C /
```

---

## ✅ **Mac Deployment Checklist**

### **Pre-Deployment**
- [ ] Docker Desktop installed and running
- [ ] Python 3.11+ installed
- [ ] At least 8GB RAM allocated to Docker
- [ ] 20GB+ free disk space available
- [ ] All required ports (3000, 8080, 8081, 9090) available

### **Deployment**
- [ ] Run `./deploy_and_test.sh` successfully
- [ ] All 4 containers running and healthy
- [ ] All services accessible via browser
- [ ] Quick tests pass (python3 quick_test.py)

### **Post-Deployment**
- [ ] Web interface loads correctly
- [ ] API documentation accessible
- [ ] Monitor dashboard shows system status
- [ ] Dozzle displays container logs
- [ ] Import functionality works
- [ ] Search and CRUD operations functional

### **Performance Validation**
- [ ] Response times < 2 seconds
- [ ] Memory usage < 1GB per container
- [ ] CPU usage reasonable during normal operation
- [ ] No memory leaks during extended use

---

## 🎯 **Mac-Specific Success Criteria**

1. **Native Integration**: Works seamlessly with macOS
2. **Resource Efficiency**: Uses Mac resources optimally
3. **User Experience**: Intuitive access via browser
4. **Performance**: Fast response times on Mac hardware
5. **Stability**: Runs reliably on macOS
6. **Monitoring**: Easy to monitor via Mac tools

Your ContactPlus MVP is now optimized for Mac deployment! 🍎✨