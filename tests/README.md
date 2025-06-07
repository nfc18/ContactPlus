# ContactPlus Test Suite

Comprehensive testing framework for ContactPlus MVP with support for local development and CI/CD integration.

## 📋 Test Overview

The ContactPlus test suite includes:

- **Integration Tests**: Complete system validation
- **API Functionality Tests**: All REST endpoints 
- **Field Parsing Tests**: vCard field validation and CRUD operations
- **Performance Tests**: Response time and load testing
- **Unicode Support Tests**: Special character handling
- **Database Integrity Tests**: Data consistency validation

## 🚀 Quick Start

### Run All Tests
```bash
# From project root
./tests/run_tests.sh --all
```

### Run Specific Test Categories
```bash
# Integration tests only
./tests/run_tests.sh --integration

# API functionality tests
./tests/run_tests.sh --api

# Field parsing and CRUD tests
./tests/run_tests.sh --field-parsing

# Performance tests
./tests/run_tests.sh --performance
```

### Advanced Options
```bash
# Skip Docker build (for faster iterations)
./tests/run_tests.sh --all --no-build

# Custom API URL
BASE_URL=http://your-server:8080/api/v1 ./tests/run_tests.sh --integration

# Custom timeout
TIMEOUT=600 ./tests/run_tests.sh --all
```

## 📁 Test Structure

```
tests/
├── README.md                    # This file
├── run_tests.sh                 # Main test runner script
├── integration_test_suite.py    # Comprehensive integration tests
├── test_data/                   # Test data and results
│   ├── integration_test.vcf     # Sample test contacts
│   ├── unicode_test.vcf         # Unicode test data
│   └── test_reports/            # Generated test reports
└── ..                          # Individual test files
```

## 🧪 Test Categories

### 1. Integration Tests (`integration_test_suite.py`)

**Purpose**: Validate complete system functionality  
**Coverage**:
- Infrastructure (all 4 services)
- Database operations
- Search functionality
- Field parsing accuracy
- CRUD operations
- Export functionality
- Unicode support
- Performance characteristics

**Usage**:
```bash
cd tests
python integration_test_suite.py --base-url http://localhost:8080/api/v1
```

**Output**: JSON report with detailed results

### 2. API Functionality Tests (`comprehensive_api_test.py`)

**Purpose**: Test all REST API endpoints  
**Coverage**:
- Health check
- Database statistics
- Contact listing and pagination
- Search functionality
- Individual contact retrieval
- Contact creation (when implemented)
- Contact updates
- Contact deletion
- Export functionality
- Error handling
- Performance benchmarks

**Usage**:
```bash
python comprehensive_api_test.py
```

**Expected Results**: 85%+ success rate

### 3. Field Parsing Tests (`field_parsing_test.py`)

**Purpose**: Validate vCard field parsing and CRUD operations  
**Coverage**:
- Comprehensive field parsing (FN, N, EMAIL, TEL, ORG, etc.)
- Multiple email/phone handling
- Field modifications
- Soft deletion
- Database integrity
- Special characters and encoding

**Usage**:
```bash
python field_parsing_test.py
```

**Test Data**: Creates comprehensive vCards with all field types

### 4. Performance Tests

**Purpose**: Validate system performance under load  
**Coverage**:
- Response time benchmarks
- Concurrent request handling
- Memory usage validation
- Large dataset operations

**Thresholds**:
- Health check: < 100ms
- API operations: < 2s
- Search operations: < 1s (for 6K+ contacts)
- Export: < 30s (full database)

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
export BASE_URL="http://localhost:8080/api/v1"
export TIMEOUT=300

# Test Environment
export TEST_ENVIRONMENT="development"

# Docker Configuration
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

### Test Data

Tests automatically create temporary test data:
- Comprehensive vCards with all field types
- Unicode test contacts
- Invalid vCard samples for validation testing
- Performance test datasets

## 📊 Test Reports

### Automated Reports

Tests generate multiple report formats:

1. **Console Output**: Real-time progress and results
2. **JSON Reports**: Machine-readable results for CI/CD
3. **HTML Reports**: Human-readable summaries
4. **Log Files**: Detailed execution logs

### Report Locations

```
tests/test_data/
├── integration_test_report.json    # Integration test results
├── api_test_report.json           # API test results  
├── field_parsing_report.json      # Field parsing results
├── test_summary.md                # Overall summary
└── logs/                          # Detailed logs
```

## 🐳 CI/CD Integration

### GitHub Actions

The test suite includes a complete GitHub Actions workflow:

**File**: `.github/workflows/integration_tests.yml`

**Features**:
- Automated testing on push/PR
- Docker image caching
- Parallel test execution
- Artifact collection
- Performance testing
- Detailed reporting

**Usage**:
```yaml
# Triggered automatically on:
- push to main/develop
- pull requests to main
- manual workflow dispatch
```

### Manual CI Testing

```bash
# Simulate CI environment
TEST_ENVIRONMENT=ci ./tests/run_tests.sh --all

# Test with custom deployment
BASE_URL=http://your-nas:8080/api/v1 ./tests/run_tests.sh --integration
```

## 🛠️ Development Workflow

### Test-Driven Development

1. **Before Changes**: Run baseline tests
   ```bash
   ./tests/run_tests.sh --api
   ```

2. **After Changes**: Validate functionality
   ```bash
   ./tests/run_tests.sh --integration
   ```

3. **Before Deployment**: Full validation
   ```bash
   ./tests/run_tests.sh --all
   ```

### Debugging Failed Tests

1. **Check Logs**:
   ```bash
   ls tests/test_data/*_output.log
   ```

2. **Run Individual Tests**:
   ```bash
   python tests/integration_test_suite.py
   ```

3. **Debug Container Issues**:
   ```bash
   docker-compose logs contactplus-core
   ```

## 📋 Success Criteria

### Integration Tests
- **95%+ pass rate** for production deployment
- **90%+ pass rate** for development validation
- All infrastructure tests must pass
- Database integrity tests must pass

### Performance Tests
- API response times < 2s
- Search operations < 1s
- Export operations < 30s
- Memory usage < 1GB per container

### Field Parsing Tests
- 100% compliance with RFC 2426
- All vCard fields correctly parsed
- CRUD operations working
- Unicode support validated

## 🔍 Troubleshooting

### Common Issues

1. **Services Not Ready**
   - Increase timeout: `TIMEOUT=600`
   - Check Docker resources
   - Verify port availability

2. **Import/Export Failures**
   - Check file permissions
   - Verify vCard format
   - Check container logs

3. **Performance Issues**
   - Increase Docker memory limits
   - Check system resources
   - Optimize database queries

### Debug Commands

```bash
# Check service health
curl http://localhost:8080/api/v1/health

# Verify database stats
curl http://localhost:8080/api/v1/stats

# Check container status
docker-compose ps

# View logs
docker-compose logs contactplus-core
```

## 🚀 Deployment Validation

### Pre-Deployment Checklist

- [ ] All integration tests pass
- [ ] Performance benchmarks met
- [ ] Field parsing validated
- [ ] Unicode support confirmed
- [ ] Export functionality verified
- [ ] Database integrity maintained

### Post-Deployment Validation

```bash
# Test deployed system
BASE_URL=http://your-deployment:8080/api/v1 ./tests/run_tests.sh --integration

# Performance validation
BASE_URL=http://your-deployment:8080/api/v1 ./tests/run_tests.sh --performance
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8080/docs
- **vCard Specification**: RFC 2426
- **Docker Compose**: Local service orchestration
- **GitHub Actions**: CI/CD pipeline documentation

---

**Ready to test your ContactPlus deployment? Run `./tests/run_tests.sh --all` to get started!** 🚀