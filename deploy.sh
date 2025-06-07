#!/bin/bash

# Simple ContactPlus Deployment Script
echo "🚀 Deploying ContactPlus locally..."

# Navigate to project directory
cd "$(dirname "$0")"

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Start services
echo "🚀 Starting ContactPlus services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check health
echo "🔍 Checking service health..."
if curl -f -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo ""
    echo "✅ ContactPlus deployed successfully!"
    echo "=================================="
    echo ""
    echo "📊 Services available at:"
    echo "   🌐 Web Interface: http://localhost:3000"
    echo "   📊 API Documentation: http://localhost:8080/docs"
    echo "   💻 System Monitor: http://localhost:9090"
    echo "   📋 Live Logs: http://localhost:8081"
    echo ""
    echo "📈 Quick status check:"
    curl -s http://localhost:8080/api/v1/stats | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'   📞 Total Contacts: {data.get(\"total_contacts\", 0)}')
    print(f'   ✅ Active Contacts: {data.get(\"active_contacts\", 0)}')
    for source, count in data.get('contacts_by_source', {}).items():
        print(f'   📁 {source}: {count}')
except:
    print('   ⚠️  Unable to get database stats')
"
else
    echo ""
    echo "❌ Deployment failed - checking logs..."
    docker-compose logs --tail=20
fi