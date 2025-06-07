#!/bin/bash
set -e

# ContactPlus Test Runner Script
# Comprehensive testing for local development and CI/CD

echo "🚀 ContactPlus Test Suite Runner"
echo "================================"

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8080/api/v1}"
TIMEOUT="${TIMEOUT:-300}"
TEST_ENVIRONMENT="${TEST_ENVIRONMENT:-local}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --field-parsing)
            RUN_FIELD_PARSING=true
            shift
            ;;
        --api)
            RUN_API=true
            shift
            ;;
        --performance)
            RUN_PERFORMANCE=true
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        --no-build)
            NO_BUILD=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --integration    Run integration tests"
            echo "  --field-parsing  Run field parsing tests"
            echo "  --api           Run API functionality tests"
            echo "  --performance   Run performance tests"
            echo "  --all           Run all test suites"
            echo "  --no-build      Skip Docker build step"
            echo "  --help          Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  BASE_URL        API base URL (default: http://localhost:8080/api/v1)"
            echo "  TIMEOUT         Service readiness timeout in seconds (default: 300)"
            echo "  TEST_ENVIRONMENT Test environment name (default: local)"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Default to running all tests if no specific test is requested
if [[ -z "$RUN_INTEGRATION" && -z "$RUN_FIELD_PARSING" && -z "$RUN_API" && -z "$RUN_PERFORMANCE" && -z "$RUN_ALL" ]]; then
    RUN_ALL=true
fi

if [[ "$RUN_ALL" == "true" ]]; then
    RUN_INTEGRATION=true
    RUN_FIELD_PARSING=true
    RUN_API=true
    RUN_PERFORMANCE=true
fi

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed or not in PATH"
    exit 1
fi

log_success "Prerequisites check completed"

# Ensure we're in the correct directory
if [[ ! -f "docker-compose.yml" ]]; then
    log_error "docker-compose.yml not found. Please run this script from the ContactPlus root directory."
    exit 1
fi

# Create test data directory
mkdir -p tests/test_data

# Install Python dependencies if needed
log_info "Installing Python dependencies..."
python3 -m pip install --quiet requests || {
    log_warning "Failed to install requests. Tests may fail if not already installed."
}

# Build and start services
if [[ "$NO_BUILD" != "true" ]]; then
    log_info "Building Docker images..."
    docker-compose build --parallel || {
        log_error "Failed to build Docker images"
        exit 1
    }
    log_success "Docker images built successfully"
fi

log_info "Starting ContactPlus services..."
docker-compose up -d || {
    log_error "Failed to start services"
    exit 1
}

# Wait for services to be ready
log_info "Waiting for services to be ready..."
for i in {1..30}; do
    if curl -f -s "$BASE_URL/health" > /dev/null 2>&1; then
        log_success "Services are ready!"
        break
    fi
    if [[ $i -eq 30 ]]; then
        log_error "Services failed to start within timeout"
        docker-compose logs
        docker-compose down
        exit 1
    fi
    echo "Waiting... (attempt $i/30)"
    sleep 10
done

# Function to run a test and capture results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_file="$3"
    
    log_info "Running $test_name..."
    
    local start_time=$(date +%s)
    if eval "$test_command" > "tests/test_data/${test_file}_output.log" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_success "$test_name completed successfully (${duration}s)"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_error "$test_name failed (${duration}s)"
        echo "Output saved to: tests/test_data/${test_file}_output.log"
        return 1
    fi
}

# Initialize test results
test_results=()
failed_tests=()

# Run integration tests
if [[ "$RUN_INTEGRATION" == "true" ]]; then
    if run_test "Integration Test Suite" "cd tests && python3 integration_test_suite.py --base-url $BASE_URL --timeout $TIMEOUT" "integration"; then
        test_results+=("✅ Integration Tests")
    else
        test_results+=("❌ Integration Tests")
        failed_tests+=("Integration Tests")
    fi
fi

# Run field parsing tests
if [[ "$RUN_FIELD_PARSING" == "true" ]]; then
    if run_test "Field Parsing Tests" "python3 field_parsing_test.py" "field_parsing"; then
        test_results+=("✅ Field Parsing Tests")
    else
        test_results+=("❌ Field Parsing Tests")
        failed_tests+=("Field Parsing Tests")
    fi
fi

# Run API functionality tests
if [[ "$RUN_API" == "true" ]]; then
    if run_test "API Functionality Tests" "python3 comprehensive_api_test.py" "api_functionality"; then
        test_results+=("✅ API Functionality Tests")
    else
        test_results+=("❌ API Functionality Tests")
        failed_tests+=("API Functionality Tests")
    fi
fi

# Run performance tests
if [[ "$RUN_PERFORMANCE" == "true" ]]; then
    log_info "Running Performance Tests..."
    
    # Create simple performance test
    cat > tests/test_data/simple_performance.py << 'EOF'
import requests
import time
import statistics
import sys

base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/api/v1"

def test_endpoint_performance(url, name, iterations=10):
    times = []
    for _ in range(iterations):
        start = time.time()
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                times.append(time.time() - start)
        except:
            pass
    
    if times:
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        max_time = max(times)
        print(f"{name}: avg={avg_time:.3f}s, median={median_time:.3f}s, max={max_time:.3f}s")
        return avg_time < 2.0  # 2 second threshold
    else:
        print(f"{name}: FAILED - no successful requests")
        return False

# Test key endpoints
results = []
results.append(test_endpoint_performance(f"{base_url}/health", "Health Check"))
results.append(test_endpoint_performance(f"{base_url}/stats", "Database Stats"))
results.append(test_endpoint_performance(f"{base_url}/contacts?page_size=10", "Contact List"))
results.append(test_endpoint_performance(f"{base_url}/contacts/search?query=test", "Contact Search"))

success_rate = sum(results) / len(results)
print(f"Performance test success rate: {success_rate*100:.1f}%")
sys.exit(0 if success_rate >= 0.75 else 1)
EOF

    if run_test "Performance Tests" "python3 tests/test_data/simple_performance.py $BASE_URL" "performance"; then
        test_results+=("✅ Performance Tests")
    else
        test_results+=("❌ Performance Tests")
        failed_tests+=("Performance Tests")
    fi
fi

# Generate summary report
log_info "Generating test summary..."

cat > tests/test_data/test_summary.md << EOF
# ContactPlus Test Summary

**Environment:** $TEST_ENVIRONMENT  
**Date:** $(date)  
**Base URL:** $BASE_URL  

## Test Results

$(printf '%s\n' "${test_results[@]}")

## Summary

- **Total Tests:** ${#test_results[@]}
- **Passed:** $((${#test_results[@]} - ${#failed_tests[@]}))
- **Failed:** ${#failed_tests[@]}
- **Success Rate:** $(echo "scale=1; ($((${#test_results[@]} - ${#failed_tests[@]})) * 100) / ${#test_results[@]}" | bc -l)%

EOF

if [[ ${#failed_tests[@]} -gt 0 ]]; then
    echo "## Failed Tests" >> tests/test_data/test_summary.md
    printf '- %s\n' "${failed_tests[@]}" >> tests/test_data/test_summary.md
fi

# Display results
echo ""
echo "=========================================="
echo "🏁 TEST RESULTS SUMMARY"
echo "=========================================="
printf '%s\n' "${test_results[@]}"
echo ""
echo "📄 Detailed results available in: tests/test_data/"

# Cleanup
log_info "Stopping services..."
docker-compose down > /dev/null 2>&1

# Exit with appropriate code
if [[ ${#failed_tests[@]} -eq 0 ]]; then
    log_success "All tests passed! 🎉"
    exit 0
else
    log_error "${#failed_tests[@]} test(s) failed"
    exit 1
fi