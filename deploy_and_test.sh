#!/bin/bash

echo "🚀 ContactPlus MVP - Local Mac Deployment & Testing Script"
echo "=========================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local timeout=${3:-120}
    local count=0
    
    print_info "Waiting for $name to be ready at $url..."
    
    while [ $count -lt $timeout ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_status "$name is ready!"
            return 0
        fi
        sleep 2
        count=$((count + 2))
        if [ $((count % 20)) -eq 0 ]; then
            print_info "Still waiting for $name... ($count/${timeout}s)"
        fi
    done
    
    print_error "$name failed to become ready within ${timeout} seconds"
    return 1
}

# Step 1: Check Prerequisites
echo ""
echo "🔍 Step 1: Checking Prerequisites"
echo "--------------------------------"

# Check if Docker is installed
if ! command_exists docker; then
    print_error "Docker is not installed!"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

print_status "Docker is installed and running"

# Check if Docker Compose is available
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    print_error "Docker Compose is not available!"
    exit 1
fi

# Use docker-compose or docker compose based on availability
if command_exists docker-compose; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

print_status "Docker Compose is available ($COMPOSE_CMD)"

# Check if Python is installed
if ! command_exists python3; then
    print_error "Python 3 is not installed!"
    echo "Please install Python 3.11+ from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_status "Python is installed (version $PYTHON_VERSION)"

# Step 2: Clean up any existing deployment
echo ""
echo "🧹 Step 2: Cleaning Up Previous Deployment"
echo "------------------------------------------"

print_info "Stopping any existing containers..."
$COMPOSE_CMD down -v 2>/dev/null || true

print_info "Cleaning up Docker system..."
docker system prune -f >/dev/null 2>&1 || true

print_status "Cleanup completed"

# Step 3: Build and Deploy
echo ""
echo "🏗️  Step 3: Building and Deploying ContactPlus MVP"
echo "------------------------------------------------"

print_info "Building Docker images..."
if $COMPOSE_CMD build --no-cache; then
    print_status "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

print_info "Starting all services..."
if $COMPOSE_CMD up -d; then
    print_status "All services started"
else
    print_error "Failed to start services"
    exit 1
fi

# Step 4: Wait for Services
echo ""
echo "⏳ Step 4: Waiting for Services to be Ready"
echo "------------------------------------------"

services=(
    "http://localhost:8080/api/v1/health:Core API"
    "http://localhost:3000:Web Interface"
    "http://localhost:9090:Monitor Dashboard"
    "http://localhost:8081:Dozzle Logs"
)

all_ready=true
for service in "${services[@]}"; do
    url="${service%%:*}"
    name="${service#*:}"
    
    if ! wait_for_service "$url" "$name" 120; then
        all_ready=false
    fi
done

if [ "$all_ready" = false ]; then
    print_error "Some services failed to start properly"
    echo ""
    echo "Checking container status:"
    $COMPOSE_CMD ps
    echo ""
    echo "Recent logs:"
    $COMPOSE_CMD logs --tail=20
    exit 1
fi

# Step 5: Run Quick Validation
echo ""
echo "🧪 Step 5: Running Quick Validation Tests"
echo "----------------------------------------"

if [ -f "quick_test.py" ]; then
    print_info "Running quick validation tests..."
    if python3 quick_test.py; then
        print_status "Quick validation tests passed!"
    else
        print_warning "Some quick validation tests failed, but services are running"
    fi
else
    print_warning "Quick test script not found, skipping quick validation"
fi

# Step 6: Display Service Information
echo ""
echo "🎉 Step 6: Deployment Complete!"
echo "==============================="

print_status "ContactPlus MVP is now running on your Mac!"

echo ""
echo "📱 Access the Services:"
echo "----------------------"
echo "• Web Interface:     http://localhost:3000"
echo "• API Documentation: http://localhost:8080/docs"
echo "• System Monitor:    http://localhost:9090"
echo "• Log Viewer:        http://localhost:8081"

echo ""
echo "🧪 Test the System:"
echo "------------------"
echo "• Quick Test:        python3 quick_test.py"
echo "• Smoke Tests:       python3 test_runner.py --smoke"
echo "• Full Test Suite:   python3 test_runner.py"
echo "• Integration Tests: python3 test_runner.py --category integration"
echo "• E2E Tests:         python3 test_runner.py --category e2e"
echo "• Performance Tests: python3 test_runner.py --category performance"

echo ""
echo "🔧 Management Commands:"
echo "----------------------"
echo "• View Logs:         $COMPOSE_CMD logs -f [service_name]"
echo "• Check Status:      $COMPOSE_CMD ps"
echo "• Restart Service:   $COMPOSE_CMD restart [service_name]"
echo "• Stop All:          $COMPOSE_CMD down"
echo "• Clean Stop:        $COMPOSE_CMD down -v"

echo ""
echo "📊 Container Status:"
echo "-------------------"
$COMPOSE_CMD ps

echo ""
echo "💾 Data Import:"
echo "--------------"
echo "1. Open http://localhost:3000/import"
echo "2. Click 'Start Initial Import'"
echo "3. Wait for import to complete"
echo "4. Browse contacts at http://localhost:3000/contacts"

echo ""
print_info "System is ready for testing and use!"

# Step 7: Optional - Run comprehensive tests
echo ""
echo "🚀 Optional: Run Comprehensive Tests"
echo "====================================="

read -p "Do you want to run the full test suite now? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installing test dependencies..."
    
    # Install test dependencies
    if [ -f "tests/requirements.txt" ]; then
        pip3 install -r tests/requirements.txt >/dev/null 2>&1 || true
    fi
    
    print_info "Running comprehensive test suite..."
    if python3 test_runner.py --wait; then
        print_status "All tests completed successfully!"
        
        # Generate test report if possible
        if python3 test_runner.py --report >/dev/null 2>&1; then
            print_status "Test report generated: test_report.html"
        fi
    else
        print_warning "Some tests may have failed, but the system is operational"
    fi
fi

echo ""
print_status "ContactPlus MVP deployment and testing complete!"
print_info "Happy contact managing! 🎉"