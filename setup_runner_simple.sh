#!/bin/bash

# Simple GitHub Actions Runner Setup for ContactPlus
echo "🔧 Setting up GitHub Actions Self-Hosted Runner for ContactPlus"
echo "============================================================="

# Configuration
RUNNER_VERSION="2.311.0"
RUNNER_DIR="$HOME/actions-runner"
REPO_URL="https://github.com/nfc18/ContactPlus"
TOKEN="A737XZUHIPUFKP5QBHTU2D3IISO5A"

# Create directories
mkdir -p "$RUNNER_DIR"
mkdir -p "$HOME/ContactPlus_Backups"

# Create deployment script
cat > "$HOME/deploy_contactplus.sh" << 'EOF'
#!/bin/bash

# Quick deployment script for ContactPlus
echo "🚀 Deploying ContactPlus locally..."

cd /Users/$(whoami)/Documents/Developer/Private/ContactPlus

# Stop existing services
docker-compose down || true

# Pull latest changes
git pull origin main || echo "Git pull failed or not needed"

# Start services
docker-compose up -d

# Wait for services
sleep 30

# Check health
if curl -f -s http://localhost:8080/api/v1/health > /dev/null; then
    echo "✅ ContactPlus deployed successfully!"
    echo "🔗 Web: http://localhost:3000"
    echo "🔗 API: http://localhost:8080"
    echo "🔗 Monitor: http://localhost:9090"
    echo "🔗 Logs: http://localhost:8081"
else
    echo "❌ Deployment failed"
    docker-compose logs
fi
EOF

chmod +x "$HOME/deploy_contactplus.sh"

# Create status check script
cat > "$HOME/check_contactplus.sh" << 'EOF'
#!/bin/bash

echo "📊 ContactPlus Status Check"
echo "=========================="

# Check if containers are running
echo "🐳 Docker Containers:"
docker-compose ps 2>/dev/null || echo "No containers running"

echo ""
echo "🔗 Service Health:"

services=(
    "Web Interface:http://localhost:3000"
    "API Backend:http://localhost:8080/api/v1/health"
    "Monitor:http://localhost:9090"
    "Logs:http://localhost:8081"
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    url=$(echo $service | cut -d: -f2-)
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo "✅ $name: OK"
    else
        echo "❌ $name: Not responding"
    fi
done

# Check database stats if API is up
if curl -f -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo ""
    echo "📊 Database Stats:"
    curl -s http://localhost:8080/api/v1/stats | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'Total Contacts: {data.get(\"total_contacts\", 0)}')
    print(f'Active Contacts: {data.get(\"active_contacts\", 0)}')
    for source, count in data.get('contacts_by_source', {}).items():
        print(f'  {source}: {count}')
except:
    print('Unable to parse database stats')
"
fi
EOF

chmod +x "$HOME/check_contactplus.sh"

echo ""
echo "============================================================="
echo "🎯 MANUAL CONFIGURATION REQUIRED"
echo "============================================================="
echo ""
echo "To complete setup, run these commands:"
echo ""
echo "1. Download and extract the runner:"
echo "   cd ~/actions-runner"
echo "   curl -o actions-runner-osx-x64-2.311.0.tar.gz -L \\"
echo "     https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-osx-x64-2.311.0.tar.gz"
echo "   tar xzf ./actions-runner-osx-x64-2.311.0.tar.gz"
echo ""
echo "2. Configure the runner:"
echo "   ./config.sh --url $REPO_URL --token $TOKEN"
echo ""
echo "3. When prompted:"
echo "   - Runner name: ContactPlus-Mac"
echo "   - Runner labels: self-hosted,macOS,ContactPlus"  
echo "   - Work directory: [Press Enter for default]"
echo ""
echo "4. Start the runner:"
echo "   ./run.sh"
echo ""
echo "✅ Management scripts created:"
echo "   - Deploy: ~/deploy_contactplus.sh"
echo "   - Status: ~/check_contactplus.sh"
echo ""
echo "🔗 GitHub Repository: $REPO_URL"
echo "🔗 Actions Dashboard: $REPO_URL/actions"
echo ""
echo "🚀 Once configured, push to main branch to trigger deployment!"