# ContactPlus MVP Testing Guide

## 🧪 **Comprehensive Testing Suite**

ContactPlus MVP includes a full testing infrastructure with multiple test categories and automated validation.

### **Test Structure**

```
tests/
├── conftest.py                    # Shared test fixtures
├── requirements.txt               # Test dependencies
├── integration/
│   ├── test_api_endpoints.py     # API integration tests
│   └── test_docker_containers.py # Container health tests
├── e2e/
│   └── test_complete_workflow.py # End-to-end workflows
└── performance/
    └── test_load_testing.py      # Load and stress tests
```

### **Logging & Monitoring**

- **Enhanced Logging**: Structured logging with request IDs and timing
- **Dozzle Integration**: Real-time log viewer at http://localhost:8081
- **Log Rotation**: Automatic log file rotation (10MB files, 5 backups)
- **Multiple Log Files**:
  - `contactplus.log` - Application logs
  - `api_access.log` - API access logs
  - `errors.log` - Error-only logs
  - `database.log` - Database operations

---

## 🚀 **Quick Start Testing**

### **1. Basic Validation**
```bash
# Quick smoke tests (30 seconds)
python quick_test.py

# OR run smoke tests via test runner
python test_runner.py --smoke
```

### **2. Full MVP Test**
```bash
# Complete test including startup and validation
./test_mvp.sh
```

### **3. Comprehensive Testing**
```bash
# All test suites with coverage
python test_runner.py

# Generate HTML report
python test_runner.py --report
```

---

## 📊 **Test Categories**

### **Integration Tests**
```bash
python test_runner.py --category integration
```

**What's Tested:**
- ✅ Health endpoints and system status
- ✅ Contact CRUD operations (Create, Read, Update, Delete)
- ✅ Search functionality with various parameters
- ✅ Import/Export endpoints
- ✅ Error handling and edge cases
- ✅ CORS configuration
- ✅ API rate limiting and concurrency
- ✅ Docker container health and networking
- ✅ Volume management and persistence
- ✅ Service port configuration
- ✅ Container restart behavior
- ✅ Log rotation and Dozzle integration

### **End-to-End Tests**
```bash
python test_runner.py --category e2e
```

**What's Tested:**
- ✅ Complete contact lifecycle (import → view → edit → export → delete)
- ✅ Search functionality across different fields
- ✅ Error handling in user workflows
- ✅ Concurrent operations stability
- ✅ Web interface accessibility
- ✅ Monitor dashboard functionality
- ✅ Data persistence across container restarts
- ✅ Performance baseline measurements

### **Performance Tests**
```bash
python test_runner.py --category performance
```

**What's Tested:**
- ✅ Load testing with 50+ concurrent requests
- ✅ Response time validation (< 2s average)
- ✅ Memory leak detection
- ✅ Stress testing with mixed workloads
- ✅ Rapid-fire request handling
- ✅ Long-running stability (5-minute test)
- ✅ Resource usage monitoring

---

## 🔍 **Specific Test Scenarios**

### **API Functionality Tests**
1. **Health Check**: Validates system health endpoint
2. **Database Stats**: Tests statistics endpoint
3. **Contact Operations**: CRUD operations with validation
4. **Search**: Multiple search patterns and edge cases
5. **Import/Export**: File handling and data integrity
6. **Error Handling**: Invalid requests and edge cases

### **Docker Infrastructure Tests**
1. **Container Status**: All containers running and healthy
2. **Health Checks**: Docker health check functionality
3. **Networking**: Inter-container communication
4. **Volumes**: Data persistence and mounting
5. **Resource Usage**: Memory and CPU consumption
6. **Log Management**: Log rotation and accessibility

### **End-to-End Workflow Tests**
1. **Complete Lifecycle**: Full contact management workflow
2. **Search Workflows**: Comprehensive search testing
3. **Error Scenarios**: Error handling in user flows
4. **Concurrent Usage**: Multiple users/operations
5. **Data Persistence**: Restart and recovery testing

### **Performance & Load Tests**
1. **Concurrent Load**: 50 concurrent API requests
2. **Mixed Workload**: Different operations simultaneously
3. **Rapid Fire**: High-frequency request patterns
4. **Memory Stability**: Memory leak detection
5. **Extended Operation**: Long-running stability
6. **Response Times**: Performance benchmarking

---

## 📈 **Test Results & Metrics**

### **Success Criteria**
- **API Response Time**: < 2 seconds average
- **Success Rate**: > 95% under normal load
- **Memory Usage**: < 1GB per container
- **Container Health**: All containers healthy
- **Data Integrity**: 100% data preservation
- **Error Handling**: Graceful failure modes

### **Performance Benchmarks**
- **Health Endpoint**: < 100ms response time
- **Contact Listing**: < 500ms for 50 contacts
- **Search Operations**: < 1s for complex queries
- **Import Operations**: 7,000+ contacts in < 30s
- **Export Operations**: Full database export in < 10s

### **Load Testing Results**
- **Concurrent Users**: 50+ simultaneous requests
- **Throughput**: 100+ requests/minute sustained
- **Error Rate**: < 5% under stress conditions
- **Recovery Time**: < 30s after restart

---

## 🔧 **Test Configuration**

### **Test Environment**
- **Python**: 3.11+
- **Dependencies**: pytest, httpx, docker, selenium
- **Services**: All 4 containers must be running
- **Network**: containers on same Docker network
- **Volumes**: Persistent data and log volumes

### **Test Data**
- **Sample vCards**: Multiple test contact formats
- **Invalid Data**: Malformed vCard testing
- **Large Datasets**: Performance testing with bulk data
- **Edge Cases**: Empty fields, special characters

### **CI/CD Integration**
```bash
# In CI pipeline
docker-compose up -d
python test_runner.py --wait
python test_runner.py --report
docker-compose down -v
```

---

## 🛠️ **Debugging Test Failures**

### **Common Issues**
1. **Services Not Ready**: Use `python test_runner.py --wait`
2. **Port Conflicts**: Check for existing services on ports 3000, 8080, 8081, 9090
3. **Docker Issues**: Ensure Docker Desktop is running
4. **Memory Limits**: Ensure adequate system memory (4GB+ recommended)
5. **Network Issues**: Check firewall and proxy settings

### **Debugging Commands**
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs contactplus-core
docker-compose logs -f  # Follow logs

# Check resource usage
docker stats

# Restart specific service
docker-compose restart contactplus-core

# Clean restart
docker-compose down -v && docker-compose up -d
```

### **Log Locations**
- **Container Logs**: `docker-compose logs [service]`
- **Application Logs**: http://localhost:8081 (Dozzle)
- **Test Results**: `test_report.html` (when using --report)
- **Coverage Report**: `htmlcov/index.html`

---

## 📋 **Testing Checklist**

### **Before Testing**
- [ ] Docker Desktop running
- [ ] No services on ports 3000, 8080, 8081, 9090
- [ ] Python 3.11+ installed
- [ ] At least 4GB RAM available

### **Quick Validation**
- [ ] Run `python quick_test.py`
- [ ] All 5 basic tests pass
- [ ] All services accessible

### **Full Testing**
- [ ] Run `./test_mvp.sh`
- [ ] All containers healthy
- [ ] Comprehensive tests pass
- [ ] Logging functionality verified

### **Production Readiness**
- [ ] Performance tests pass
- [ ] Load testing successful
- [ ] Memory usage stable
- [ ] Error handling validated
- [ ] Data persistence confirmed

---

## 🎯 **Test Coverage**

The test suite provides comprehensive coverage of:

- **API Endpoints**: 100% of REST API endpoints
- **Docker Infrastructure**: All containers and networking
- **User Workflows**: Complete user journeys
- **Error Scenarios**: Edge cases and failure modes
- **Performance**: Load, stress, and stability testing
- **Data Integrity**: Import, export, and persistence
- **Logging**: All logging and monitoring systems

This ensures the ContactPlus MVP is production-ready with reliable, tested functionality across all components.