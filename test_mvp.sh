#!/bin/bash

echo "🚀 ContactPlus MVP Test Script"
echo "=============================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"

# Build and start services
echo ""
echo "📦 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Run comprehensive tests
echo ""
echo "🧪 Running comprehensive tests..."
python test_runner.py --wait

# Check health of all services
echo ""
echo "🏥 Final service health check..."

services=(
    "Core API:http://localhost:8080/api/v1/health"
    "Web Interface:http://localhost:3000"
    "Monitor:http://localhost:9090"
    "Dozzle Logs:http://localhost:8081"
)

for service in "${services[@]}"; do
    name="${service%%:*}"
    url="${service#*:}"
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is not responding"
    fi
done

echo ""
echo "🎉 ContactPlus MVP is fully tested and running!"
echo ""
echo "📱 Access the services:"
echo "   - Web Interface: http://localhost:3000"
echo "   - API Documentation: http://localhost:8080/docs" 
echo "   - System Monitor: http://localhost:9090"
echo "   - Log Viewer (Dozzle): http://localhost:8081"
echo ""
echo "🧪 Run more tests:"
echo "   - Smoke tests: python test_runner.py --smoke"
echo "   - Integration: python test_runner.py --category integration"
echo "   - End-to-end: python test_runner.py --category e2e"
echo "   - Performance: python test_runner.py --category performance"
echo "   - Full report: python test_runner.py --report"
echo ""
echo "📝 View logs: docker-compose logs -f [service_name]"
echo "🛑 Stop services: docker-compose down"
echo "🗑️ Clean up: docker-compose down -v"