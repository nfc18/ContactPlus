#!/bin/bash

echo "📊 ContactPlus Status Check"
echo "=========================="

PROJECT_DIR="/Users/lk/Documents/Developer/Private/ContactPlus"
cd "$PROJECT_DIR"

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

# Check database stats
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

# Show backup information
echo ""
echo "💾 Backup Information:"
BACKUP_DIR="/Users/lk/Documents/Developer/Private/ContactPlus/backups"
if [ -d "$BACKUP_DIR" ]; then
    echo "Backup directory: $BACKUP_DIR"
    echo "Available backups:"
    ls -la "$BACKUP_DIR" | tail -5
else
    echo "No backups found"
fi

# Show runner status
echo ""
echo "🤖 GitHub Actions Runner:"
if launchctl list | grep -q "com.github.actions.runner.contactplus"; then
    echo "✅ Runner service is loaded"
else
    echo "❌ Runner service not found"
fi

echo ""
echo "📁 Directory Structure:"
echo "  📁 Project: $PROJECT_DIR"
echo "  📁 Backups: /Users/lk/Documents/Developer/Private/ContactPlus/backups"
echo "  📁 Runner: /usr/local/var/github-actions-runner"
echo "  📁 Logs: /Users/lk/Library/Logs/ContactPlus"
